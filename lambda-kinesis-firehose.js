/** Sample lambda function to be used with kinesis firehose for data transformation */

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
