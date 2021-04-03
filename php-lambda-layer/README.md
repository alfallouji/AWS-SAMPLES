# Description

To deploy the lambda layers : 

```
aws lambda publish-layer-version --layer-name php-runtime --zip-file fileb://runtime.zip --region us-east-1
```

To deploy vendor packages layer : 

```
aws lambda publish-layer-version --layer-name php-vendor --zip-file fileb://vendor.zip --region us-east-1
```
