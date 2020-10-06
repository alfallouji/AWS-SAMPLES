#
# Sample code that will query cloudwatch log to retrieve the ports used for a specific ENI in AWS
# It will then attempt to come up with a set of port ranges - this can serve as a base to create CIDR for your security groups
# 
# Requires : Adequate role / permission to query AWS cloudwatch logs
#

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

# Reduce number of cidr to a maximum of totalElement by accepting unused values (with a limit of how many values can be skipped)
# Ensure data array is sorted prior to calling this function
def optimize(data, totalElement, limit = 10):
    currentMaxSkipStep = 0
    while (currentMaxSkipStep <= limit):
        ranges, leftovers, unusedPorts = parse(data, currentMaxSkipStep)
        if (len(ranges) + len(leftovers) <= totalElement):
            print("Number of unused/open ports tolerated for a single interval = ", currentMaxSkipStep)
            return ranges, leftovers, unusedPorts
        currentMaxSkipStep = currentMaxSkipStep + 1
        
    return [], [], []
    
# Query AWS cloudwatch log 
def query_aws(query, log_group, region):
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
    
# Import all packages needed    
import boto3, sys, getopt
from datetime import datetime, timedelta
import time

# Main function invoked in CLI
def main(argv):
    # Default values
    totalElement = 10
    maxSkipStep = 100
    interfaceId = 'eni-abcdefghijk'
    logGroup = '/vpcflowlogs/demo'
    region = 'ap-southeast-2'
    limit = 20

    # Get arguments values
    try:
        opts, args = getopt.getopt(argv, "heltmrg", ["eni=", "limit=", "totalElement=", "maxSkipStep=", "region=", "logGroup="])
    except getopt.GetoptError:
        print('index.py --eni=ENI --limit=10 --totalElement=5')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('index.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-e", "--eni"):
            interfaceId = arg
        elif opt in ("-limit", "--limit"):
            limit = arg
        elif opt in ("-g", "--logGroup"):
            logGroup = arg    
        elif opt in ("-r", "--region"):
            region = arg                
        elif opt in ("-t", "--totalElement"):
            totalElement = int(arg)
        elif opt in ("-m", "--maxSkipStep"):
            maxSkipStep = int(arg)

    # Query AWS cloudwatch log
    query = "fields @timestamp, interfaceId, srcAddr, dstAddr, protocol, srcPort, dstPort, action | filter interfaceId = '" + interfaceId + "' | filter action = 'ACCEPT' | stats count(*) as countTotal by srcPort, dstPort, srcAddr, dstAddr, action | sort by dstPort desc | limit " + str(limit)
    response = query_aws(query, logGroup, region)
    data = []
    for values in response["results"]:
        data.append(int(values[1]["value"]))
    
    # Data must be sorted prior to optimization
    data.sort()
    
    # Search for optimal ranges
    ranges, leftovers, unusedPorts = optimize(data, totalElement, maxSkipStep)
    
    # Display result
    print("Data (", len(data), "): ", data)
    print("Algorithm attempted to come up with a combination of maximum", totalElement)
    if (len(ranges) > 0 or len(leftovers) > 0):
        print("Ranges found (", len(ranges), "):", ranges)
        print("Single port (/32) (", len(leftovers), "):", leftovers)
        print("Extra / Unused (", len(unusedPorts), "):", unusedPorts)
    else:
        print("Couldnt find a combination - you may want to consider increasing the values for totalElement or maxSkipStep")
        
if __name__ == "__main__":
   main(sys.argv[1:])
