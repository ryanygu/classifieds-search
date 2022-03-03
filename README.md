# Classifieds Search

Uses Python Reddit API Wrapper (PRAW) for Reddit web crawling. PRAW is only supported on Python 3.7+, see [github.com/praw-dev/praw](github.com/praw-dev/praw) for more info.

Note: currently only supports [Reddit](reddit.com).

## Running the script

In the project's root directory, run ```python3 reddit_search.py```

## Setup

In `queries.txt`, format your parameter as follows:
```
===<subreddit1_to_search>
<query_for_subreddit1>
<query_for_subreddit1>
===<subreddit2_to_search>
<query_for_subreddit2>
```
See the included `queries.txt` for an example.

## Files

- `new_posts.csv` contains a list of all new posts from the last time the script was ran
- `data.csv` and `old_data.csv` are used internally in the script but can be viewed for more details
- `queries.txt` contains the search parameters


## Future plans

- Add support for other classifieds sites (Kijiji, Craigslist, Canuck Audio Mart, etc.)
- Implement a server to rerun the script at set intervals
- Better user input methods
