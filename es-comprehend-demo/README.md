# Amazon Comprehend - ElasticSearch Demo
This is a sample code for a Lambda function that will download an RSS feed, parse it, send it to Comprehend for enrichment and then index it into ElasticSearch.

## Warning
This code is just provided as a sample / example and hasn't been tested. Please keep that in mind if you decide to use it.

## How to use
- Make sure to have the adequate role created for the Lambda function which will require to have access to the Comprehend service and to ElasticSearch REST API.

- You will need to run `npm install` to install the dependencies and upload the whole folder as a zip when creating the Lambda function.

- Make sure to update the ElasticSearch host accordingly also (var host).

