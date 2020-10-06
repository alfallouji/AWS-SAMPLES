#
# Sample code that will query cloudwatch log to retrieve the ports used for a specific ENI in AWS
# It will then attempt to come up with a set of port ranges - this can serve as a base to create CIDR for your security groups
# 
# Requires : Adequate role / permission to query AWS cloudwatch logs
#

# Import all packages needed    
import sys, getopt
import vpc_analyzer

# Main function invoked in CLI
def main(argv):
    # Default values
    maxInboundRules = 10
    maxOpenPorts = 100
    interfaceId = 'eni-abcdefghijk'
    logGroup = '/vpcflowlogs/demo'
    region = 'ap-southeast-2'
    limit = None

    # Get arguments values
    try:
        opts, args = getopt.getopt(argv, "h", ["eni=", "limit=", "maxInboundRules=", "maxOpenPorts=", "region=", "logGroup=", "help"])
    except getopt.GetoptError:
        print('cloudwatchlogs.py --eni=ENI --maxInboundRules=5 --limit=20 --region=ap-southeast-2 --logGroup=grp1 --maxOpenPorts=20')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("\nQuery Amnazon Cloudwatch Logs containing VPC Flow Logs for a specific ENI and attempt to identify a set of port ranges and individual ports to create the inbound rules of your security groups in AWS.\n")
            print("\tUsage:\n\t======")
            print('\t\tpython cloudwatchlogs.py --eni=eni-1234567890 --limit=10 --maxInboundRules=5 --region=ap-southeast-2 --logGroup=grp1 --maxOpenPorts=20')
            print("\n\tOptions:\n\t========");
            print("\t\t--eni : AWS eni (network interface)")
            print("\t\t--limit : Set a limit of items to be returned by the query")
            print("\t\t--maxInboundRules : Maximum number of ranges and invidual ports (inbound rules) to be returned")
            print("\t\t--maxOpenPorts : Maximum number of individual ports that can be skipped (left open) to build a single range")
            print("\t\t--region : AWS region (e.g. ap-southeast-2)")
            print("\t\t--logGroup : Cloudwatch log group")
            print("")            
            sys.exit()
        elif opt in ("--eni"):
            interfaceId = arg
        elif opt in ("--limit"):
            limit = arg
        elif opt in ("--logGroup"):
            logGroup = arg    
        elif opt in ("--region"):
            region = arg                
        elif opt in ("--maxInboundRules"):
            maxInboundRules = int(arg)
        elif opt in ("--maxOpenPorts"):
            maxOpenPorts = int(arg)

    # Query AWS cloudwatch log
    query = "fields @timestamp, interfaceId, srcAddr, dstAddr, protocol, srcPort, dstPort, action | filter interfaceId = '" + interfaceId + "' | filter action = 'ACCEPT' | stats count(*) as countTotal by srcPort, dstPort, srcAddr, dstAddr, action | sort by dstPort desc"
    if (limit != None):
        query = query + " | limit " + str(limit)
    response = vpc_analyzer.query_aws_cloudwatch(query, logGroup, region)
    data = []
    for values in response["results"]:
        data.append(int(values[1]["value"]))
    
    # Data must be sorted prior to optimization
    data.sort()
    
    # Search for optimal ranges
    ranges, leftovers, unusedPorts = vpc_analyzer.optimize(data, maxInboundRules, maxOpenPorts)
    
    # Display result
    print("Data (", len(data), "): ", data)
    print("Algorithm attempted to come up with a combination of maximum", maxInboundRules)
    if (len(ranges) > 0 or len(leftovers) > 0):
        print("\n---- RESULT ----")        
        print("Ranges (", len(ranges), "):", ranges)
        print("Single port (/32) (", len(leftovers), "):", leftovers)
        print("Extra / Unused (", len(unusedPorts), "):", unusedPorts, "\n")
    else:
        print("Couldnt find a combination - you may want to consider increasing the values for maxInboundRules or maxOpenPorts\n")
    
if __name__ == "__main__":
   main(sys.argv[1:])
