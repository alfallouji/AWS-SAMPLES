# VPC Flowlogs analyzer

## Warning
This code is just provided as a sample / example and hasn't been tested extensively. Please keep that in mind if you decide to use it.

## Description

Sample code to show how to query cloudwatch log and Athena to retrieve the source ports used for a specific ENI in AWS.

It will then attempt to come up with a set of port ranges and individual ports that will cover all those source ports - this can serve as a base to create the inbound rules of  your security groups. 

In an ideal world, we should always try to restrict the number of ports left open within a security group. However, there could be cases where this ends up as a difficult task to accomplish and we need to compromise between the number of inbound rules vs the number of ports left open. Some applications may use thousands of ports. We also have to consider certain limits regarding security groups (e.g. default limit of 60 inbound ules per security group) : https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html#vpc-limits-security-groups

This script implements an algorithm that will attempt to give you an optimized result.

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
 - from 80 to 86
 - from 1001 to 1002
 
individual ports : 
 - 1020
 
extra/unused ports (ports that are open and shouldnt) :
 - 83, 84
```

In the previous example, we end up with two ranges and one individual port. There are 2 ports that would be open and shouldn't (ports 83 and 84). This is a compromise that we may decide to accept if we want to only have a maximum of 3 inbound rules defined in the security group. 

If we decide to run the optimizer with maxInboundRules = 10 and maxOpenPorts of 3, we would get the following result : 

```
ranges : 
 - from 80 to 82
 - from 85 to 86
 - from 1001 to 1002
 
individual ports : 
 - 1020
 
extra/unused ports (ports that are open and shouldnt) :
 - (none)
```

In this case, the optimizer is suggesting three ranges and one individual ports. This means a total of four inbound rules (which respects our constraints of being below 10 rules). There is no extra port left open. 

If we decide to run the optimizer with maxInboundRules = 1  and maxOpenPorts of 3, we would get the following result : 

```
Couldnt find a combination - you may want to consider increasing the values for totalElement or maxSkipStep
```

The optimizer has no magic power (yet) and is simply unable to come up with a solution with those constraints.

If we decide to run the optimizer with maxInboundRules = 1  and maxOpenPorts of 1000, we would get the following result : 


```
ranges : 
 - from 80 to 1020
 
individual ports : 
 - (none)
 
extra/unused ports (ports that are open and shouldnt) :
 - 83, 84, 87, 88, 89, 90, ..., ..., ..., 999, 1000, ..., ..., 1018, 1019
```

In this example, the optimizer is giving one single range (as requested). However, there will hundreds of ports left open (which is below the value of maxOpenPorts of 1000). 

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
