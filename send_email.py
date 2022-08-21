# code for 'ProcessClassifiedsSearchData' Lambda function

import json
import os
import boto3
import pandas as pd
# from io import BytesIO

AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_SNS_TOPIC_ARN = os.getenv("AWS_SNS_TOPIC_ARN")

def get_last_two_s3_objects(bucket_name, prefix):
    """
    Fetches the most recently saved two .csv files and returns them.
    TODO: need pagination for when there are more than 1000 objects
    Note 1: currently, we will assume the s3 bucket will have less than 1000 objects
    and will manually clear the data every so often to keep this condition true
    Note 2: needs s3:ListBucket policy either in IAM or S3 bucket
    """
    s3 = boto3.client('s3')
    objs = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)['Contents']
    
    if (len(objs) < 2):
        return None
    
    get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))
    sortedObjects = [obj['Key'] for obj in sorted(objs, key=get_last_modified)]
    mostRecent = s3.get_object(Bucket=bucket_name, Key=sortedObjects[-1])
    secondMostRecent = s3.get_object(Bucket=bucket_name, Key=sortedObjects[-2])
    print('LOG: successfully fetched last two S3 objects.')
    
    return [mostRecent, secondMostRecent]
    
    
def send_sns(links):
    """
    Publishes a message to a topic through SNS.
    Note: Lambda's IAM role needs AmazonSNSFullAccess policy
    """
    sns = boto3.client('sns')
    message = '\n'.join(links)
    
    try:
        response = sns.publish(
            TopicArn=AWS_SNS_TOPIC_ARN,
            Message=message,
            Subject='Your watchlist has ' + str(len(links)) + ' new posts!'
        )
        print('LOG: SNS successfully sent an email.')
    except Exception as e:
        print(e)
    else:
        return response
        
        
def get_new_post_ids(old_ids, recent_ids):
    """
    Returns the difference between old reddit post ids and new ones
    """
    s = set(old_ids)  # checking set membership is O(1)
    diff = [x for x in recent_ids if x not in s]
    
    return diff
    
    
def get_new_posts(old_data, recent_data):
    """
    Compares both .csv files and returns a pandas dataframe containing
    data for all new posts.
    """
    df_old = pd.read_csv(old_data['Body'], sep=',')
    df_recent = pd.read_csv(recent_data['Body'], sep=',')
    # method 2: df_old = pd.read_csv(BytesIO(old_data['Body'].read().decode('utf-8')))
    
    old_ids = df_old['id'].to_list()
    recent_ids = df_recent['id'].to_list()

    new_ids = get_new_post_ids(old_ids, recent_ids)
    new_df = df_recent[df_recent['id'].isin(new_ids)]
    print('LOG: processed new posts')

    return new_df
    

def lambda_handler(event, context):
    
    csv_files = get_last_two_s3_objects(AWS_S3_BUCKET, '')
    if (csv_files is None):
        return 'FAILED: need at least two .csv files in the bucket.'
        
    new_data = csv_files[0]
    old_data = csv_files[1]
    
    new_df = get_new_posts(old_data, new_data)
    
    if (len(new_df.index) == 0):
        return 'SUCCESS: no new posts so notifications were not sent.'

    
    links = new_df['url'].to_list()
    send_sns(links)

    return 'SUCCESS: data processed and sent notifications.'