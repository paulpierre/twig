```
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
```

# Introduction

twig.py is a tool that helps web3 marketers find very engaged users within a commmunity's twitter profile.

> ℹ️ "Twig" is a portmanteau of "Twitter" and "Pig". [Truffle pigs or hogs](https://en.wikipedia.org/wiki/Truffle_hog) are domesticated animals used for finding truffle mushrooms. Twig surfaces a Twitter account's most engaged and therefore valuable users.

### 🔥 Features
> - 🗓️ **Date ranger filter** - Support for date ranges for when a target account's tweets were posted
> - 🎒 **Caching** - Raw files are cached and loaded within the `client` directory
> - 📈 **Likes, Retweets, Commenters** - Get all metrics of engagement for a tweet on a per-user basis
> - 📎 **CSV output** - Save the metrics and dimensions all in a single spreadsheet so you can analyze later in real time as they're processed
> - 🚓 **Rate-limit regulator** - Rate-limiting supported so you can just run it indefinitely on your machine
> - 👌 **Simple** - No classes, no libraries, < 500 lines of functioning shit


# 🤔 How it works

### 🔎 What does it sniff for?

> 1. Twig pulls all tweets in a time range from the target account
>   
> 2. Twig then extracts users who engaged based on:
>   - 🧻 Paper engagement - Users who liked the tweet
>   - 😷 Super spreader - Users who retweeted the tweet
>   - 😈 Instigator - Users who commented on a tweet
>   - ☢️ Theremonuclear engagement - All of the above
> 
> 3. Twig stores this data in a single CSV for you containing metadata like
>   - Twitter handle
>   - Follower count
>   - Following count
>   - Do they follow the target account
>   - Total life time of likes
>   - Total lifetime of retweets
>   - Total lifetime of comments

### 🤷 Why does this matter?
> In web3 communities are everything. Even if your product is great, token utility phenomoenal, a project's community is highly dependent on community and stewards of said community.
> 
> Twig's purpose is to help you surface engaged users or "influencers" so they can be incentivized to help bootstrap and grow your web3 community. Twig can also be used for competitive analysis and research for understand what type of engagement posts are most effective.
> 
> If you're interested in advanced and industry-leading web3 user acquisition tools, check out [Conductive.ai](https://conductive.ai). If you're a buolder interested in the intersection of web3 and growth automation, [Conductive.ai is hiring!](https://hk.linkedin.com/company/conductiveai)

# 📝 Get started

### Setup
- Open your terminal of choice
- Create your virtual environment `python -m venv env` or `python3 -m venv env` 
- Install python dependencies `pip install -r requirements.txt` or `pip3 install -r requirements.txt`
- Head to the [Twitter Developer portal](https://developer.twitter.com/en/portal/dashboard) to signup and get your API credentials
- Create your environment file `touch .env` and edit it. Enter the following values:
```
TWITTER_BEARER_TOKEN=
TWITTER_CONSUMER_KEY=
TWITTER_CONSUMER_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=
TARGET_USER_NAME=<twitter handle of target account>
```
### Usage
- Edit your `.env` file and set the twitter account you want to analyze in the `TARGET_USER_NAME` var
- In the `main()` function, edit the values of `date_to` and `date_from` by default it analyzes tweets from the last 90 days
- Simply run `python twig.py` or `python3 twig.py` and it will start doing its thing:
![twig.py](https://github.com/paulpierre/twig/blob/main/img/twig.png?raw=true)
- When it is complete you should see the following in the terminal:
`✅ Finished process tweets, engaged users data saved to clients/<target_twitter_handle>/<client_handle>_engaged_users.csv`

### Rate limits
> Let's be honest, Twitter has shit rate limits and pre-modern API design. I might eventually refactor this to do raw scraping to make raw data acquisition more efficient and faster.
> 
> With all that said you can find the [API rate limits here](https://developer.twitter.com/en/docs/twitter-api/rate-limits). twig.py handles adhereing to these limits for you automatically.

# 📊 Data

### CSV column
- `tweet_id` - id of the tweet, viewable by visiting https://twitter.com/ `<target_account>` /status/ `<tweet_id>`
- `tweet_created_at` - when the tweet was posted
- `tweet_text` - the contents of thet weet
- `user_id` - the twitter user ID of the engaging user
- `username` - the twitter handle of the engage user
- `is_follower` - whether they are following the `<target_account>` or not
- `engagement_type` - each type of engagement gets their own row values are `liker`,`retweet`, or `comment`
- `comment_text` - if it is `engagement_type` of `comment`, text of what was said
- `comment_retweet_count` - number of times the comment was retweeted
- `comment_favorite_count` - number of times the comment was favorited
- `retweet_id` - tweet ID of the retweet
- `retweet_like_count` - number of likes of the retweet
- `retweet_retweet_count` - number of times the retweet was retweeted
- `user_followers_count` - number of users following the engage user
- `user_following_count` - number of users the engaged user is following
- `user_tweet_count` - lifetime number of tweets posted by engaged user
- `user_likes_count` - lifetime number of like on the engaged user's account
- `user_created_at` - when the engaged user's account was created / age
- `user_verified` - whether the user is verified or not
- `created_at` - timestamp of row localized to UTC
### Directory structure

Each analysis gets its own folder for caching purposes. Additionally each date range gets it's own cache

```
./clients
└── /<TARGET_TWITTER_HANDLE>/ (folder of twitter account analyzed)
  │ ├── /<TWEET_ID_1>/ (first tweet folder)
  │ │   ├── commenters.json (all tweet commenter meta data)
  │ │   ├── likers.json (all tweet liker meta data)
  │ │   └── retweeters.json (all tweet retweeter meta data)
  │ │
  │ ├── /<TWEET_ID_2>/ (second tweet folder)
  │ │
  │ └── ... etc.
  │
  ├── <TARGET_TWITTER_HANDLE>_engaged_users.csv (final output)
  ├── client.json (basic target twitter account metadata)
  └── tweets-<TARGET_TWITTER_HANDLE>-2022-08-04_2022-11-02.json (cache of tweets)
```

# 📝 TODO
- QA larger accounts to test cursor pagination
- Fix 100 result limit for certain end-points
- Add comment ID column
- Add SQL lite support for better metrics
- Add SQLalchemy for db support
- Add webserver for better analysis, UX and streaming progress
- API support for webserver
- CLI interface via Typer
- Multiple developer account support for batch processing
- Queuing and celery support for batch processing

### Ah yes ..
![twig.py](https://media1.giphy.com/media/eP4zLawRGHJWt5ailn/giphy.gif?cid=ecf05e475zfqzn8erlr60p4bqv0ikof2sco7bnsbj7nwu2ut&rid=giphy.gif&ct=g)

Oink oink, there is nothing like the smell of some community growth alpha lurking in the swamps of Twitter

# Acknowledgements
- [Tweepy](https://www.tweepy.org/) - Twitter API library
- [Conductive.ai](https://conductive.ai/) - Proof of concept built in a few hrs for [Conductive.ai](https://conductive.ai/) marketing team. Check us out, we're hiring!


# Copyright
Copyright (c) 2020 Paul Pierre Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in allcopies or substantial portions of the Software. THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.