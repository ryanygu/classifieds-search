# Classifieds Search

A personal use Python script that uses Python Reddit API Wrapper (PRAW) to check for new postings on monitored classifieds subreddits. 

The script has been refactored into a microservice using AWS Lambda, AWS EventBridge, AWS S3, and AWS SNS.

Note: currently only supports [Reddit](reddit.com).


Current AWS configuration:

- AWS EventBridge runs the scraping microservice (a Lambda function) every 10 minutes
- A Lambda trigger watches the S3 bucket for any changes (PUTs)
- The trigger calls another Lambda function that checks the latest two `.csv` files in S3 and checks for new posts
- If there are new posts, the function uses AWS SNS to send out an email
- JSON input for the scraper is in the following format (also in `queries.json`):
```
{
  "data": [
    {
      "subreddit": "AVExchange",
      "queries": [
        "LCD-2",
        "LCD 2"
      ]
    },
    {
      "subreddit": "mechmarket",
      "queries": [
        "GMK Olivia"
      ]
    },
    ...
  ]
}
```

<br>

## Dependencies

---

```
praw==7.4.0
pandas==1.4.3
```

This code runs on Lambda with a Python 3.8 environment.

See `requirements.txt` for more info.

Note: PRAW is only supported on Python 3.7+. See [github.com/praw-dev/praw](github.com/praw-dev/praw) for more info.

<br>

## Acknowledgements

---

Big thanks to [keithrozario/Klayers](github.com/keithrozario/Klayers) for the prebuilt AWS Lambda layers for `NumPy` and `Pandas`.

<br>

## Future work

---

- Currently only keeps track of one specific query combination (i.e. the example JSON query format above) at a time. In the future, will add support for multiple wishlist items by making them tracked separately.
  - Possible solution: use individual folders or filenames to differentiate and aggregate results in a Lambda function when needed
- SNS emails are relatively barebones, can try to integrate SES, SendGrid, or another email/notification service (i.e. Twilio or Firebase) for more richly formatted messages (i.e. clickable links)
- Add support for other classifieds sites (Kijiji, Craigslist, Canuck Audio Mart, etc.)
- Dockerize the app and deploy to AWS ECS instead, this would circumvent the Lambda layers issue that was encountered
- Link this microservice to a full stack application, allowing users to log in and keep track of their watchlist.
