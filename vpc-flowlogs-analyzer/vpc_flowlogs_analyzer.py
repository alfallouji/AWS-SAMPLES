#
# Sample code to show how to query cloudwatch log and Athena to retrieve the ports used for a specific ENI in AWS
# It will then attempt to come up with a set of port ranges - this can serve as a base to create CIDR for your security groups
# 
# Requires : Adequate role / permission to query AWS cloudwatch logs and/or Athena
#

# Import all packages needed    
import boto3, time
from datetime import datetime, timedelta

# Data must be sorted prior to calling this function
def parse(data, maxSkipStep = 0):
    ranges = []
    leftovers = []
    rangeStart = None
    rangeEnd = None
    previousPort = None
    unusedPorts = []
    
    for port in data:
        if (previousPort != None and (port <= previousPort + 1 + maxSkipStep or port == previousPort + 1)):
            if (port <= previousPort + 1 + maxSkipStep and port != previousPort + 1):
                unusedPorts.extend(range(previousPort + 1, port, 1))
            if (rangeStart == None):
                rangeStart = previousPort    
            rangeEnd = port
            previousPort = port
        else:
            if (rangeStart != None and rangeEnd != None):
                ranges.append({'start': rangeStart, 'end': rangeEnd})
            else:
                if (previousPort != None):
                    leftovers.append(previousPort)
            rangeStart = None
            rangeEnd = None
            previousPort = port
        
    if (rangeStart != None and rangeEnd != None):
        ranges.append({'start': rangeStart, 'end': rangeEnd})

    if (previousPort != None and rangeEnd == None):
        leftovers.append(previousPort)

    return ranges, leftovers, unusedPorts

# Reduce number of cidr to a maximum of maxInboundRules by accepting unused values (with a limit of how many values can be skipped)
# Ensure data array is sorted prior to calling this functionboto
def optimize(data, maxInboundRules, limit = 10):
    currentMaxSkipStep = 0
    while (currentMaxSkipStep <= limit):
        ranges, leftovers, unusedPorts = parse(data, currentMaxSkipStep)
        if (len(ranges) + len(leftovers) <= maxInboundRules):
            print("Number of unused/open ports tolerated for a single interval = ", currentMaxSkipStep)
            return ranges, leftovers, unusedPorts
        currentMaxSkipStep = currentMaxSkipStep + 1
        
    return [], [], []
    
# Query AWS cloudwatch log 
def query_aws_cloudwatch(query, log_group, region):
    client = boto3.client('logs', region_name=region)
    
    start_query_response = client.start_query(
        logGroupName=log_group,
        startTime=int((datetime.today() - timedelta(hours=5)).timestamp()),
        endTime=int(datetime.now().timestamp()),
        queryString=query,
    )
    
    query_id = start_query_response['queryId']
    response = None
    while response == None or response['status'] == 'Running':
        print('Waiting for query to complete ...')
        time.sleep(1)
        response = client.get_query_results(
            queryId=query_id
        )
    
    return response

# Query AWS Athena
def query_aws_athena(params):
    # Creating the Client for Athena
    client = boto3.client('athena',  region_name=params['region'])
    
    print(params)
    # This function executes the query and returns the query execution ID
    response_query_execution_id = client.start_query_execution(
        QueryString = params['query'],
        QueryExecutionContext = {
            'Database' : params['database']
        },
        ResultConfiguration = {
            'OutputLocation': 's3://' + params['bucket'] + '/' + params['path']
        }
    )

    # This function takes query execution id as input and returns the details of the query executed
    response_get_query_details = client.get_query_execution(
        QueryExecutionId = response_query_execution_id['QueryExecutionId']
    )

    print(response_get_query_details)

    # time.sleep(1)
    # Condition for checking the details of response
    status = 'RUNNING'
    iterations = 10

    while (iterations > 0):
        iterations = iterations - 1
        response_get_query_details = client.get_query_execution(QueryExecutionId = response_query_execution_id['QueryExecutionId'])
        status = response_get_query_details['QueryExecution']['Status']['State']
        print(status)
        if (status == 'FAILED') or (status == 'CANCELLED') :
            print(response_get_query_details)
            return False, False
            
        elif status == 'SUCCEEDED':
            location = response_get_query_details['QueryExecution']['ResultConfiguration']['OutputLocation']

            # Function to get output results
            response_query_result = client.get_query_results(
                QueryExecutionId = response_query_execution_id['QueryExecutionId']
            )
            result_data = response_query_result['ResultSet']
            
            return location, result_data
        else:
            time.sleep(2)
        
    return False
