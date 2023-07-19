import json
from slack_sdk import WebClient

def lambda_handler(event, context):
    print(event)
    msg = event['msg']
    channel_ids = event['channel_ids']
    
    # get TeamID from dyanmoDB table
    SLACK_BOT_TOKEN = event["team_id"]
    
    # send message to request channel(s), notify user what was sent and which channels received it
    print(f"msg: {msg}")
    print(f"channel_ids: {channel_ids}")
     
    SLACK_MSG = msg 
    client = WebClient(token=SLACK_BOT_TOKEN)
    for i in range(len(channel_ids)):
        client.chat_postMessage(channel=channel_ids[i], text=SLACK_MSG)
    
    return {
        'statusCode': 200,
        'body': 'OK'
    }
