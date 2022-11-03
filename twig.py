from dotenv import load_dotenv
from datetime import timedelta
from datetime import datetime
import logging
import tweepy
import json
import os
import pytz
import csv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
screen_name = os.getenv('TARGET_USER_NAME')

auth = tweepy.OAuth1UserHandler(
   consumer_key, consumer_secret, access_token, access_token_secret
)

api = tweepy.API(auth, wait_on_rate_limit=True)
client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

BANNER = ''' 
---------------------------------------
       ▀█▀ █░█░█ █ █▀▀ ░ █▀█ █▄█
       ░█░ ▀▄▀▄▀ █ █▄█ ▄ █▀▀ ░█░
  🔍 a twitter influencer truffle pig
---------------------------------------
           __,---.__   
        ,-'         `-.__ 
....  &/           `._\ _\ ............
....  /               ''._  ...........
....  |   ,             (") ...........
.💩.  |__,'`-..--|__|--'' ....... 💎 ..
'''
print(BANNER)

'''
--------------------
Hanyu's requirements
--------------------
1. Get last three months of tweets
2. For each tweet get users who
    - Liked the tweet
    - Retweeted the tweet
    - Commented on the tweet
3. For each user store
    - Twitter handle
    - Follower count
    - Following count
    - Do they follow the screen_name account
    - Total number of likes for screen_name account
    - Total number of retweets for screen_name account
    - Total number of comments for screen_name account
'''


# --------------------------------
# Create a dir if it doesn't exist
# --------------------------------
def mkdir(path=None):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


# -------------------------------------------------
# Fetch a list of an account's tweets by date range
# -------------------------------------------------
def get_tweets(username=None, date_from=None, date_to=None, dir=''):

    dir_path = mkdir(dir)

    if username is None:
        raise ValueError('Username cannot be None')

    date_from = datetime.now(pytz.utc) - timedelta(days=90) if not date_from else date_from
    date_to = datetime.now(pytz.utc) if not date_to else date_to

    data = list()

    file_name_date = f'-{date_from.strftime("%Y-%m-%d")}_{date_to.strftime("%Y-%m-%d")}' if date_from and date_to else ''
    file_name = f'{dir_path}/tweets-{username}{file_name_date}.json'

    # check if cache exists
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            data = json.load(f)
        return data

    # Get tweets between date_from and date_to
    for tweet in api.user_timeline(screen_name=username, include_rts=True, exclude_replies=True, count=200):
        # compare tweet date with date_from and date_to with timezone awareness
        if tweet.created_at.replace(tzinfo=pytz.utc) >= date_from and tweet.created_at.replace(tzinfo=pytz.utc) <= date_to:
            data.append(tweet._json)

    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4, default=str)

    return data


# -------------------------------
# Fetch users who like a tweet_id
# -------------------------------
def get_tweet_likers(tweet_id=None):

    user_list = list()
    result = client.get_liking_users(tweet_id, max_results=100)
    while result[0]:
        users = result[0]
        next_token = result[3]['next_token'] if 'next_token' in result[3] and result[3]['next_token'] else None
        for user in users:
            user = api.get_user(screen_name=user)._json
            user_list.append(user)
        if not next_token:
            break
        result = client.get_liking_users(tweet_id, max_results=100, pagination_token=next_token)

    return user_list


# -------------------------------------
# Fetch users who commented on tweet_id
# -------------------------------------
def get_tweet_commenters(tweet_id=None, screen_name=screen_name):
    replies = list()
    for tweet in tweepy.Cursor(api.search_tweets,q=f'to:{screen_name}', result_type='recent').items(1000):
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if tweet.in_reply_to_status_id_str and int(tweet.in_reply_to_status_id_str)==int(tweet_id):
                replies.append(tweet._json)
    return replies


# -------------------------------------------------------
# Determine if user_followed is followed by user_follower
# -------------------------------------------------------

def is_following(user_followed=None, user_follower=None):
    if not user_followed or not user_follower:
        raise Exception('user_followed and user_follower cannot be None')

    res = api.get_friendship(source_screen_name=user_followed, target_screen_name=user_follower)
    rel = res[1]._json

    return rel['following']


# ------------------------------------
# Fetch all users engaging with tweets
# ------------------------------------
def get_users_engaging_with_tweet(tweet_id=None, is_overwrite=False, dir=''):
    if tweet_id is None:
        raise ValueError('Tweet ID cannot be None')

    dir_path = mkdir(f'{dir}')

    # ----------
    # Get likers
    # ----------
    file_name = f'{dir_path}/likers.json'
    if os.path.exists(file_name) and not is_overwrite:
        with open(file_name, 'r') as f:
            likers = json.load(f)
    else:
        likers = [user for user in get_tweet_likers(tweet_id=tweet_id)]

        with open(file_name, 'w') as f:
            json.dump(likers, f, indent=4, default=str)

    # --------------
    # Get retweeters
    # --------------
    logger.info(f'🐷 ...sniffing for engaged retweeters of tweet_id: {tweet_id}')

    file_name = f'{dir_path}/retweeters.json'
    if os.path.exists(file_name) and not is_overwrite:
        with open(file_name, 'r') as f:
            retweeters = json.load(f)
    else:
        retweeters = [user for user in api.get_retweets(tweet_id, count=100)]

        with open(file_name, 'w') as f:
            json.dump(retweeters, f, indent=4, default=str)

    # --------------
    # Get commenters
    # --------------
    logger.info(f'🐷 ...sniffing for engaged commenters of tweet_id: {tweet_id}')
    file_name = f'{dir_path}/commenters.json'
    if os.path.exists(file_name) and not is_overwrite:
        with open(file_name, 'r') as f:
            commenters = json.load(f)
    else:
        commenters = [user for user in get_tweet_commenters(tweet_id=tweet_id, screen_name=screen_name)]
        with open(file_name, 'w') as f:
            json.dump(commenters, f, indent=4, default=str)

    if likers or retweeters or commenters:
        logger.info(f'✅ ...found {len(likers)} 👤 likers, {len(retweeters)} 👤 retweeters, and {len(commenters)} 👤 commenters')
    else:
        logger.info(f'❌ ...found no engaged users for tweet')

    return {
        'likers': likers,
        'retweeters': retweeters,
        'commenters': commenters
    }


# --------------------------------
# Fetch client profile information
# --------------------------------
def get_client(username=None):
    if username is None:
        raise ValueError('Username cannot be None')

    client_folder = mkdir('clients')
    client_path = mkdir(f'{client_folder}/{username}')

    file_name = f'{client_path}/client.json'

    client_user = api.get_user(screen_name=username)

    client_data = {
        'user_id': client_user.id,
        'username': client_user.screen_name,
        'followers_count': client_user.followers_count,
        'following_count': client_user.friends_count,
        'tweet_count': client_user.statuses_count,
        'likes_count': client_user.favourites_count,
        'created_at': client_user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'verified': client_user.verified,
    }
    # write to file
    with open(file_name, 'w') as f:
        json.dump(client_data, f, indent=4, default=str)
    f.close()

    return client_data


def main():

    # Get the client's account information
    client_user = get_client(username=screen_name)
    logger.debug(f'👽 Client account: {json.dumps(client_user, indent=4, default=str)}')

    client_path = mkdir(f'clients/{screen_name}')

    # get tweets from the last 3 months
    date_to = datetime.now(pytz.utc)
    date_from = date_to - timedelta(days=90)
    tweets = get_tweets(username=screen_name, date_from=date_from, date_to=date_to, dir=client_path)

    logger.info(f'⌛ Fetching {len(tweets)} tweets for {screen_name}...')

    # create a csv file to store the data
    csv_file = f'{client_path}/{screen_name}_engaged_users.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'tweet_id',
            'tweet_created_at',
            'tweet_text',
            'user_id',
            'username',
            'is_follower',
            'engagement_type',
            'comment_text',
            'comment_retweet_count',
            'comment_favorite_count',
            'retweet_id',
            'retweet_like_count',
            'retweet_retweet_count',
            'user_followers_count',
            'user_following_count',
            'user_tweet_count',
            'user_likes_count',
            'user_created_at',
            'user_verified',
            'created_at'
        ])

        for tweet in tweets:

            dir_path = mkdir(f'{client_path}/{tweet["id"]}')

            tweet_id = tweet['id']
            tweet_created_at = tweet['created_at']
            tweet_text = tweet['text']

            retweet_id = ''
            retweet_like_count = 0
            retweet_retweet_count = 0
            
            comment_text = ''
            comment_retweet_count = 0
            comment_favorite_count = 0

            # get users who liked, retweeted and commented on the tweet
            logger.info(f'🐦 fetching tweet with id {tweet_id}')
            users = get_users_engaging_with_tweet(tweet_id=tweet_id, dir=dir_path, is_overwrite=True)

            for user in users['likers']:
                logger.debug(f' 👤 liker user: {json.dumps(user, indent=4, default=str)}')
                engagement_type = 'like'
                user_id = user['id']
                username = user['screen_name']
                user_followers_count = user['followers_count']
                user_following_count = user['friends_count']
                user_tweet_count = user['statuses_count']
                user_likes_count = user['favourites_count']
                user_created_at = user['created_at']
                user_verified = user['verified']
                created_at = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')

                is_follower = is_following(user_followed=screen_name, user_follower=username)

                writer.writerow([
                    tweet_id,
                    tweet_created_at,
                    tweet_text,
                    user_id,
                    username,
                    is_follower,
                    engagement_type,
                    comment_text,
                    comment_retweet_count,
                    comment_favorite_count,
                    retweet_id,
                    retweet_like_count,
                    retweet_retweet_count,
                    user_followers_count,
                    user_following_count,
                    user_tweet_count,
                    user_likes_count,
                    user_created_at,
                    user_verified,
                    created_at
                ])

            for retweet in users['retweeters']:
                retweet = retweet._json
                user = retweet['user']
                logger.debug(f' 👤 retweeting user: {json.dumps(user, indent=4, default=str)}')
                # user = api.get_user(screen_name=user)._json

                retweet_id = retweet['id']
                retweet_like_count = retweet['favorite_count']
                retweet_retweet_count = retweet['retweet_count']

                engagement_type = 'retweet'
                user_id = user['id']
                username = user['screen_name']
                user_followers_count = user['followers_count']
                user_following_count = user['friends_count']
                user_tweet_count = user['statuses_count']
                user_likes_count = user['favourites_count']
                user_created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d %H:%M:%S')
                user_verified = user['verified']
                created_at = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')

                is_follower = is_following(user_followed=screen_name, user_follower=username)

                writer.writerow([
                    tweet_id,
                    tweet_created_at,
                    tweet_text,
                    user_id,
                    username,
                    is_follower,
                    engagement_type,
                    comment_text,
                    comment_retweet_count,
                    comment_favorite_count,
                    retweet_id,
                    retweet_like_count,
                    retweet_retweet_count,
                    user_followers_count,
                    user_following_count,
                    user_tweet_count,
                    user_likes_count,
                    user_created_at,
                    user_verified,
                    created_at
                ])
            
            for comment in users['commenters']:
                logger.info(f' 👤 commenter user: {json.dumps(user, indent=4, default=str)}')
                # user = api.get_user(screen_name=user)._json
                engagement_type = 'comment'
                user = comment['user']
                user_id = user['id']
                username = user['screen_name']
                user_followers_count = user['followers_count']
                user_following_count = user['friends_count']
                user_tweet_count = user['statuses_count']
                user_likes_count = user['favourites_count']
                user_created_at = user['created_at']
                user_verified = user['verified']
                created_at = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')

                is_follower = is_following(user_followed=screen_name, user_follower=username)

                writer.writerow([
                    tweet_id,
                    tweet_created_at,
                    tweet_text,
                    user_id,
                    username,
                    is_follower,
                    engagement_type,
                    comment_text,
                    comment_retweet_count,
                    comment_favorite_count,
                    retweet_id,
                    retweet_like_count,
                    retweet_retweet_count,
                    user_followers_count,
                    user_following_count,
                    user_tweet_count,
                    user_likes_count,
                    user_created_at,
                    user_verified,
                    created_at
                ])

    f.close()

    logger.info(f'✅ Finished process tweets, engaged users data saved to {csv_file}')

if __name__ == '__main__':
    main()