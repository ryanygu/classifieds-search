#! /usr/bin/env python3
# code for 'RunClassifiedsSearch' Lambda function
import praw
import pandas as pd
import datetime as dt
import os
import sys
import boto3
from io import StringIO
    
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
PRAW_CLIENT_ID = os.getenv('PRAW_CLIENT_ID')
PRAW_CLIENT_SECRET = os.getenv('PRAW_CLIENT_SECRET')
PRAW_USER_AGENT = os.getenv('PRAW_USER_AGENT')

def get_date(created):
    """
    Converts a date from the UNIX timestamp to a readable string.
    """
    return dt.datetime.fromtimestamp(created)

# TODO: complete this function
def validation_checks(data):
    return True

def parse_input(data):
    """
    Parse and validate input JSON.
    """
    if (validation_checks(data) is False):
        sys.exit('FAIL: input json is invalid.')
        
    d = {}
    for obj in data['data']:
        d[obj['subreddit']] = obj['queries']
    
    return d
           
def upload_csv_s3(df, s3_bucket_name, csv_filename):
    """
    Converts pandas dataframe to .csv and uploads it to s3.
    """
    
    file_buffer = StringIO()
    df.to_csv(file_buffer, index=False)
    
    # create connection
    client = boto3.client('s3')
    
    # upload to s3, file_buffer.getvalue() is the csv body for the file
    client.put_object(Bucket=s3_bucket_name, Body=file_buffer.getvalue(), Key=csv_filename)
    print('LOG: done uploading to S3.')
    
    
def lambda_handler(event, context):
    # setup     
    input_data = parse_input(event)
    subreddit_names = list(input_data.keys())

    reddit = praw.Reddit(client_id=PRAW_CLIENT_ID, client_secret=PRAW_CLIENT_SECRET, user_agent=PRAW_USER_AGENT)
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
    print('LOG: collected reddit data')

    # (1) remove duplicates by id
    df = df.drop_duplicates(subset='id', keep='last').reset_index(drop=True)
    # (2) remove '[removed]' or '[deleted]' posts
    indexNames = df[(df.body == '[removed]') | (df.body == '[deleted]')].index
    df.drop(indexNames, inplace=True)
    print('LOG: cleaned up data')
    
    dt_string = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    csv_filename = 'reddit-data-' + dt_string + '.csv'
    upload_csv_s3(df, AWS_S3_BUCKET, csv_filename)
    return 'SUCCESS: uploaded scraped data to s3.'