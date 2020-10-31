import json
import logging
import os
from datetime import datetime, timedelta

import boto3
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Line の設定
LINE_POST_URL = os.environ['LINE_POST_URL']
LINE_TOKEN = os.environ['LINE_TOKEN']

client = boto3.client('cloudwatch', region_name='us-east-1')

get_metric_statistics = client.get_metric_statistics(
    Namespace='AWS/Billing',
    MetricName='EstimatedCharges',
    Dimensions=[
        {
            'Name': 'Currency',
            'Value': 'USD'
        }
    ],
    StartTime=datetime.today() - timedelta(days=1),
    EndTime=datetime.today(),
    Period=86400,
    Statistics=['Maximum']
)


def build_message(cost, date):
    text = "{}までのAWS料金は、${}です。".format(date, cost)

    return text


def lambda_handler(event, context):

    print('get_metric_statistics', get_metric_statistics)
    cost = get_metric_statistics['Datapoints'][0]['Maximum']
    date = get_metric_statistics['Datapoints'][0]['Timestamp'].strftime('%Y-%m-%d')

    message = build_message(cost, date)

    # LINEにPOST
    try:
        headers = {'Authorization': 'Bearer {}'.format(LINE_TOKEN)}
        payload = {'message': message}
        # LINE通知
        requests.post(LINE_POST_URL, headers=headers, params=payload)

    except requests.exceptional.RequestException as e:
        logger.error("Request failed: {}".format(e))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "success",
        }),
    }
