# VPC Flowlogs analyzer

## Warning
This code is just provided as a sample / example and hasn't been tested extensively. Please keep that in mind if you decide to use it.

## Description

Sample code to show how to query cloudwatch log and Athena to retrieve the source ports used for a specific ENI in AWS.

It will then attempt to come up with a set of port ranges and individual ports that will cover all those source ports - this can serve as a base to create CIDR for your security groups. 

In an ideal world, we should always try to restrict the number of ports left open within a security groups. However, there could be cases where this is ends up as a difficult task to accomplish and we need to compromise between the number of inbound rules vs the number of open ports.

This script implements an algorithm that will attempt to give you an optimized result.. 

Requires : Adequate role / permission to query AWS cloudwatch logs and/or Athena

## Setup

- Must have python installed (version 3+)
- Just run `pip install -r requirements.txt`

## Example

Assuming vpc flowlogs have returned the following source port used by a specific ENI : 

```80
81
82
85
86
1001
1002
1020
```

Running the optimizer with maxInboundRules of 3 and maxOpenPorts of 3 (maximum number of open ports left within a range), it would give the following result :

```
ranges : 
 - from 81 to 86
 - from 1001 to 1002
 
individual ports : 
 - 1020
 
 extra/unused ports (ports that are open and shouldnt) :
 - 83, 84
```


## Usage 

### cloudwatchlogs.py - Cloudwatch logs

Query cloudwatch logs containing vpc flow logs and attempt to identify a set of port ranges and individual ports to create your security groups in AWS.

Refer to this documentation on how to publish vpc flowlogs to cloudwatch logs : 

https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html

**Example**
```
python cloudwatchlogs.py --eni=eni-1234567890 --limit=10 --maxInboundRules=5 --region=ap-southeast-2 --logGroup=grp1 --maxOpenPorts=20
```

**Options**
```
--eni : AWS eni (network interface)
--limit : Set a limit of items to be returned by the query
--maxInboundRules : Maximum number of ranges and invidual ports to be returned
--maxOpenPorts : Maximum number of individual ports that can be skipped (left open) to build a single range
--region : AWS region (e.g. ap-southeast-2)
--logGroup : Cloudwatch log group
```

### athena.py - Athena

Query an athena table containing vpc flow logs and attempt to identify a set of port ranges and individual ports to create your security groups in AWS.

Refer to this documentation on how to create the table in Athena :

https://docs.aws.amazon.com/athena/latest/ug/vpc-flow-logs.html 

**Usage**
```
python athena.py --eni=eni-1234567890 --limit=10 --maxInboundRules=5 --region=ap-southeast-2 --database=dbtest --tablename=tblvpc
```

**Options**
```
--eni : AWS eni (network interface)
--limit : Set a limit of items to be returned by the query
--maxInboundRules : Maximum number of ranges and invidual ports to be returned
--maxOpenPorts : Maximum number of individual ports that can be skipped to build a single range
--region : AWS region (e.g. ap-southeast-2)
--database : Athena database
--tablename : Athena tablename (refer to https://docs.aws.amazon.com/athena/latest/ug/vpc-flow-logs.html for instructions on how to create the table)
--bucket : S3 bucket to store Athena query output
--path : S3 path to store Athena query output
```

## References

For instructions on how to create the table in Athena to parse vpc flow logs :

https://docs.aws.amazon.com/athena/latest/ug/vpc-flow-logs.html 

For details around the query syntax to be used to query cloudwatch logs : 

https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html
