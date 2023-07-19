import json
import base64
import os
from urllib.parse import parse_qs 
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr


# get slack bot token from teamID
def get_token_for_team(team):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('token')
    #client = boto3.client('dynamodb')
    # response = table.get_item(
    #     Key={
    #         'team_id': team
    #     }
    # )
    # response = table.query(
    #     KeyConditionExpression=Key('team_id').eq(team)
    # )
    print(f"team to scan: {str(team[0])}") 
    response = table.scan(
        TableName = 'token',
        FilterExpression = Attr('team_id').eq(team[0])
        #IndexName = team[0]
        #AttributesToGet = [team[0]]
        #ProjectionExpression = ''
    )
    print(response)
    return response['Items'][0]["token"]

def lambda_handler(event, context):
    # ACK request from Slack and respond, send work to kiSendSNSWorker
    # to process the messages.
    print(event)

    event = base64.b64decode(event["body"])
    event = parse_qs(event.decode("utf-8"))

    print('Slash command called with params: ', event)
    
    # get TeamID from dyanmoDB table
    team_id = event["team_id"]
    SLACK_BOT_TOKEN = get_token_for_team(team_id) 
    
    # parse message, find channel ID(s) and message to send
    str_text = event['text']
    text = listToStr = ' '.join([str(elem) for elem in str_text])
    channel_ids = []
    msg = ""
    for i in range(len(text)):
        cur_c = text[i];
        if cur_c == "<":
            cur_chnnl_id = ""
            while text[i] != ">" and text[i] != "|" and i < len(text):
                if text[i] != "<" and i != 0 and text[i] != "#":
                    cur_chnnl_id += text[i]
                i += 1
            channel_ids.append(cur_chnnl_id)
        else:
            msg += text[i]
    
    # clean up msg
    count = len(channel_ids)
    msg_len = len(msg.split(" ")) 
    msg = msg.split(" ")[-(msg_len-count):] 
    msg = ' '.join(msg)
    
    # send msg and channel_ids to kiSendWorker via SNS 
    # publish SNS message to delegate the actual work to worker lambda function
    message = {
        "msg": msg,
        "channel_ids": channel_ids,
        "team_id": SLACK_BOT_TOKEN
    }

    lambda_client = boto3.client('lambda')
    invoke_response = lambda_client.invoke(FunctionName="kiSendWorker", InvocationType="Event", Payload=json.dumps(message))
    print(invoke_response)
    
    return {
        'statusCode': 200,
        'body': 'OK'
    }
