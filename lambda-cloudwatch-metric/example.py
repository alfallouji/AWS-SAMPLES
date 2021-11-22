# A simple lambda function that check if a port on a host is open and pushes a cloudwatch metric

import json
import boto3
import socket

def lambda_handler(event, context):
  
    # Check if port is open or not (try to connect to a port on a server - timeout set to 1 sec)
    ip = event['ip']
    port = event['port']
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        if (0 == result):
            portOpen = 1
        else:
            portOpen = 0
    except: 
        portOpen = 0

    print("portOpen = " + str(portOpen))

    # You can force value for testing purpose
    portOpen = 1
    print("forcing value to: " + str(portOpen))

    cloudwatch = boto3.client('cloudwatch')
    response = cloudwatch.put_metric_data(
        MetricData = [
            {
                'MetricName': 'FsxServerStatus',
                'Dimensions': [
                    {
                        'Name': 'FSX_SERVER_TYPE',
                        'Value': 'Primary'
                    },
                    {
                        'Name': 'FSX_SERVER_HOST',
                        'Value': event['host']
                    }
                ],
                'Unit': 'None',
                'Value': portOpen
            },
        ],
        Namespace='FSX'
    )    
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
