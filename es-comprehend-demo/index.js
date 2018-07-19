var AWS = require('aws-sdk');
var uuid = require('uuid');
var Feed = require('rss-to-json');

// Url of the RSS field to process
var rssUrl = 'https://www.wired.com/feed/rss';

// ElasticSearch host URL
var host = '';

let client = require('elasticsearch').Client({
  hosts: [ host ],
  connectionClass: require('http-aws-es')
});

exports.handler = (event, context, callback) => {
    console.log('starting');
    var comprehend = new AWS.Comprehend({apiVersion: '2017-11-27'});
    const sessionId = uuid();

/**
 * Un-comment to empty index
    console.log('deindexing');
    client.deleteByQuery({
        index: 'demo',
        q: '*'
    }, function (error, response) {
        // ...
    });
 
    callback(null, 'deindex');
    return true;
 */

    Feed.load(rssUrl, function(err, rss) {
        if (err) {
            console.log('Failed rss:', err);
            callback(null, 'error while fetching rss feed');
        }

        var cpt = 0;    
        var body = [];
        rss.items.forEach(function (item) {
            var text = item.title + ' ' + item.description;                
            var params = {
                LanguageCode: 'en',
                Text: text
            };

            comprehend.detectEntities(params, function(err, data) {
                if (err) {
                    console.log('Failed detext Entities:', err);
                    callback(null, 'error');
        
                } else {
                    console.log(text);
            
                    comprehend.detectSentiment(params, function(err, dataSentiment) {
                        if (err) { 
                            console.log('Failed detect sentiment:', err);
                            return;
                        }
                        
                        var doc = {
                            sessionId: sessionId, 
                            entities: data.Entities, 
                            text: text, 
                            link: item.link, 
                            createdAt: item.created, 
                            sentiment: dataSentiment.Sentiment,
                            format: 'rss'
                        }; 
                        
                        console.log('doc:', doc); 
                        
                        body.push({ index:  { _index: 'demo', _type: 'mytype', _id: item.link } });
                        body.push(doc);
                        
                        ++cpt;
                        if (cpt == rss.items.length) {
                            console.log(body);
                            client.bulk({
                                body: body
                            }, function (err, resp) {
                                console.log('Failed bulk update:', resp);
                            });
                        }
                    });
                }
               callback(null, 'done...');
           }); 
        });
    });
};