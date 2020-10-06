#
# Sample code that will query vpcflows logs via Athena to retrieve the ports used for a specific ENI in AWS
# It will then attempt to come up with a set of port ranges - this can serve as a base to create CIDR for your security groups
# 
# Requires : Adequate role / permission to query AWS Athena
# 
# Refer to https://docs.aws.amazon.com/athena/latest/ug/vpc-flow-logs.html for instructions how to create the table in Athena to parse vpc flow logs

# Import all packages needed    
import sys, getopt
import vpc_analyzer

# Main function invoked in CLI
def main(argv):
    # Default values
    maxInboundRules = 20
    maxOpenPorts = 500
    interfaceId = 'eni-abcdefghijk'
    database = 'test'
    table = 'vpc_flow_logs'
    bucket = 'my_bucket'
    path = 'athena/'
    region = 'ap-southeast-2'
    limit = None

    # Get arguments values
    try:
        opts, args = getopt.getopt(argv, "heltmrg", ["eni=", "limit=", "maxInboundRules=", "maxOpenPorts=", "region=", "logGroup=", "bucket=", "path=", "tablename=",  "database=",  "help"])
    except getopt.GetoptError:
        print('index.py --eni=ENI --limit=10 --maxInboundRules=5 --maxOpenPorts=50 --region=ap-southeast-2 --database=dbtest --tablename=tblvpc')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("\nQuery an Amazon Athena table containing VPC Flow Logs for a specific ENI and attempt to identify a set of port ranges and individual ports to create your security groups in AWS.\n")
            print("\tUsage:\n\t======")
            print('\t\tpython athena.py --eni=eni-1234567890 --limit=10 --maxInboundRules=5 --region=ap-southeast-2 --database=dbtest --tablename=tblvpc')
            print("\n\tOptions:\n\t========");
            print("\t\t--eni : AWS eni (network interface)")
            print("\t\t--limit : Set a limit of items to be returned by the query")
            print("\t\t--maxInboundRules : Maximum number of ranges and invidual ports (inbound rules) to be returned")
            print("\t\t--maxOpenPorts : Maximum number of individual ports that can be skipped (left open) to build a single range")
            print("\t\t--region : AWS region (e.g. ap-southeast-2)")
            print("\t\t--database : Athena database")
            print("\t\t--tablename : Athena tablename (refer to https://docs.aws.amazon.com/athena/latest/ug/vpc-flow-logs.html for instructions on how to create the table)")
            print("\t\t--bucket : S3 bucket to store Athena query output")
            print("\t\t--path : S3 path to store Athena query output")
            print("")
            sys.exit()
        elif opt in ("--eni"):
            interfaceId = arg
        elif opt in ("--limit"):
            limit = arg
        elif opt in ("--database"):
            database = arg    
        elif opt in ("--tablename"):
            tablename = arg   
        elif opt in ("--bucket"):
            bucket = arg   
        elif opt in ("--path"):
            path = arg   
        elif opt in ("--database"):
            database = arg               
        elif opt in ("--region"):
            region = arg                
        elif opt in ("--maxInboundRules"):
            maxInboundRules = int(arg)
        elif opt in ("--maxOpenPorts"):
            maxOpenPorts = int(arg)

    query = "SELECT distinct sourceport FROM \"" + database + "\".\"" + table + "\" where action = 'ACCEPT' and protocol = 6 and interfaceid = '" + interfaceId + "' order by sourceport"
    if (limit != None):
        query = query + " limit " + str(limit)

    params = {
        'region': region,
        'database': database,
        'bucket': bucket,
        'path': path,
        'query': query
    }
    
    ## Fucntion for obtaining query results and location 
    location, response = vpc_analyzer.query_aws_athena(params)
    
    # Remove first row (which contains column name)
    response["Rows"].pop(0)
    
    # Parse result and build data array
    data = []
    for values in response["Rows"]:
        data.append(int(values["Data"][0]["VarCharValue"]))
    
    # Data must be sorted prior to optimization
    data.sort()
    
    # Search for optimal ranges
    ranges, leftovers, unusedPorts = vpc_analyzer.optimize(data, maxInboundRules, maxOpenPorts)
    
    # Display result
    print("Data (", len(data), "): ", data)
    print("Algorithm attempted to come up with a combination of maximum", maxInboundRules)
    print("\n---- RESULT ----")
    if (len(ranges) > 0 or len(leftovers) > 0):
        print("Ranges (", len(ranges), "):\n", ranges)
        print("\nSingle port (/32) (", len(leftovers), "):\n", leftovers)
        print("\nExtra / Unused ports that are open and shouldnt (", len(unusedPorts), "):\n", unusedPorts, "\n")
    else:
        print("Couldnt find a combination - you may want to consider increasing the values for maxInboundRules or maxOpenPorts\n")
        
if __name__ == "__main__":
   main(sys.argv[1:])
