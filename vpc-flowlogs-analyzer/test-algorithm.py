#
# Sample code to test the algorithm
# 

# Import all packages needed    
import sys, getopt
import vpc_flowlogs_analyzer

# Main function invoked in CLI
def main(argv):
    # Default values
    maxInboundRules = 20
    maxOpenPorts = 500

    # Get arguments values
    try:
        opts, args = getopt.getopt(argv, "", ["maxInboundRules=", "maxOpenPorts=", "help"])
    except getopt.GetoptError:
        print('test-algorithm.py --maxInboundRules=5 --maxOpenPorts=50')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("--help"):
            print("\nTest script for the algorithm to attempt to identify a set of port ranges and individual ports to create your security groups in AWS.\n")
            print("\tUsage:\n\t======")
            print('\t\tpython test-algorithm.py --maxInboundRules=5 --maxOpenPorts=10')
            print("\n\tOptions:\n\t========");
            print("\t\t--maxInboundRules : Maximum number of ranges and invidual ports (inbound rules) to be returned")
            print("\t\t--maxOpenPorts : Maximum number of unneeded ports that can be skipped (left open) to build a single range")

            print("")
            sys.exit()
        elif opt in ("--maxInboundRules"):
            maxInboundRules = int(arg)
        elif opt in ("--maxOpenPorts"):
            maxOpenPorts = int(arg)

    # Parse result and build data array
    data = [
        81,
        82,
        85,
        86,
        1001,
        1002,
        1020
    ]

    # Data must be sorted prior to optimization
    data.sort()
    
    # Search for optimal ranges
    ranges, leftovers, unusedPorts = vpc_flowlogs_analyzer.optimize(data, maxInboundRules, maxOpenPorts)
    
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
