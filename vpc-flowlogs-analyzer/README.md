# VPC Flowlog analyzer

## Warning
This code is just provided as a sample / example and hasn't been tested extensively. Please keep that in mind if you decide to use it.

## Description

Sample code to show how to query cloudwatch log and Athena to retrieve the ports used for a specific ENI in AWS.
It will then attempt to come up with a set of port ranges - this can serve as a base to create CIDR for your security groups

Requires : Adequate role / permission to query AWS cloudwatch logs and/or Athena

## Setup

- Must have python installed (version 3+)
- Just run `pip install -r requirements.txt`

## Usage 

### cloudwatchlogs.py - Cloudwatch logs

Query cloudwatch logs containing vpc flow logs and attempt to identify a set of port ranges and individual ports to create your security groups in AWS.

Refer to this documentation on how to publish vpc flowlogs to cloudwatch logs : 

https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html

**Example**
```
python cloudwatchlogs.py --eni=eni-1234567890 --limit=10 --totalElement=5 --region=ap-southeast-2 --logGroup=grp1 --maxSkipStep=20
```

**Options**
```
--eni : AWS eni (network interface)
--limit : Set a limit of items to be returned by the query
--totalElement : Maximum number of ranges and invidual ports to be returned
--maxSkipStep : Maximum number of individual ports that can be skipped to build a single range
--region : AWS region (e.g. ap-southeast-2)
--logGroup : Cloudwatch log group
```

### athena.py - Athena

Query an athena table containing vpc flow logs and attempt to identify a set of port ranges and individual ports to create your security groups in AWS.

Refer to this documentation on how to create the table in Athena :

https://docs.aws.amazon.com/athena/latest/ug/vpc-flow-logs.html 

**Usage**
```
python athena.py --eni=eni-1234567890 --limit=10 --totalElement=5 --region=ap-southeast-2 --database=dbtest --tablename=tblvpc
```

**Options**
```
--eni : AWS eni (network interface)
--limit : Set a limit of items to be returned by the query
--totalElement : Maximum number of ranges and invidual ports to be returned
--maxSkipStep : Maximum number of individual ports that can be skipped to build a single range
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
