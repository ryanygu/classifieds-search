#! /usr/bin/env python3
import praw
import pandas as pd
import datetime as dt
import os

# convert date from UNIX timestamp to readable string
def get_date(created):
    return dt.datetime.fromtimestamp(created)

# parse queries.txt
def parse_input():
    data = {}
    with open('./queries.txt', 'r') as f:
        recent_key = ''
        for _,line in enumerate(f):
            if ('===' in line.strip()):
                data[line[3:-1]] = []
                recent_key = line[3:-1]
            else:
                data[recent_key].append(line.strip())
                
    return data

# returns the difference between old reddit post ids and new ones
def get_new_post_ids(old_ids, new_ids):
    
    # checking membership of a set is O(1) whereas checking membership of a list is O(n)
    s = set(old_ids)
    diff = [x for x in new_ids if x not in s]  # list of any new posts
    
    return diff
           
           
# setup     
input_data = parse_input()
subreddit_names = list(input_data.keys())

reddit = praw.Reddit(client_id='7aPZyvmcVWgYZpF3Cz9_MQ', client_secret='eJeNi4cCqIVROWQsBeB8e-t-BFGl9Q', user_agent='classifieds_scraper')
posts = {'id':[], 'title':[], 'body':[], 'created':[], 'query': [], 'url':[]}

# collect data
for sr in subreddit_names:
    subreddit = reddit.subreddit(sr)
    for q in input_data[sr]:
        for post in subreddit.search(query=q, sort='new', time_filter='month', limit=20):
            posts['id'].append(post.id)
            posts['title'].append(post.title)
            posts['body'].append(post.selftext)
            posts['created'].append(get_date(post.created))
            posts['query'].append(q)
            posts['url'].append(post.url)
df = pd.DataFrame(posts)

# cleanup data
# (1) remove duplicates by id
df = df.drop_duplicates(subset='id', keep='last').reset_index(drop=True)
# (2) remove '[removed]' or '[deleted]' posts
indexNames = df[(df.body == '[removed]') | (df.body == '[deleted]')].index
df.drop(indexNames, inplace=True)

# export new data
print('Search returned ' +str(len(df.index))+ ' results.')
if (os.path.exists('./data.csv')):
    os.rename('./data.csv', './old_data.csv')
df.to_csv('data.csv', index=False)

# check the differences between the old data and the new data
old_df = pd.read_csv('old_data.csv')

old_ids = old_df['id'].to_list()
new_ids = df['id'].to_list()

new_post_ids = get_new_post_ids(old_ids, new_ids)
new_posts_df = df[df['id'].isin(new_post_ids)]
new_posts_df.to_csv('new_posts.csv', index=False)

print('There are ' +str(len(new_post_ids))+ ' new posts. Check new_posts.csv for more info.')




        