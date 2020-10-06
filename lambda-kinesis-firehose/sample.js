/** Sample lambda function to be used with kinesis firehose for data transformation */
/** Sample of input received :
    {
      "invocationId": "invocationIdExample",
      "deliveryStreamArn": "arn:aws:kinesis:EXAMPLE",
      "region": "eu-central-1",
      "records": [
        {
          "recordId": "49546986683135544286507457936321625675700192471156785154",
          "approximateArrivalTimestamp": 1495072949453,
          "data": "eyJ0aWNrZXJfc3ltYm9sIjoiUVhaIiwgInNlY3RvciI6IkhFQUxUSENBUkUiLCAiY2hhbmdlIjotMC4wNSwgInByaWNlIjo4NC41MX0="
        }
      ]
    }
*/
console.log('Loading function');

exports.handler = async (event, context) => {
    /* Process the list of records and transform them */
    var items = [];
    for (var i = 0, len = event.records.length; i < len; i++) {
        var record = event.records[i];
        
        // Decoding base64 string
        let buff = Buffer.from(record.data, 'base64'); 
        let decodedBuffer = buff.toString('utf-8');
        
        // Parsing JSON
        let decodedRecord = JSON.parse(decodedBuffer);
        
        // Adding / Transforming record
        decodedRecord.newField = 'a new value';
        
        // Pushing transformed record
        var encodedRecord = Buffer.from(JSON.stringify(decodedRecord)).toString('base64');
        items.push({
            recordId: record.recordId,
            result: 'Ok',
            data: encodedRecord
        });
    }
    
    console.log(`Processing completed.  Successful records ${items.length}.`);
    return { records: items };
};
