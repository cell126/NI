/**
 Licensed to the Apache Software Foundation (ASF) under one or more
 contributor license agreements.  See the NOTICE file distributed with
 this work for additional information regarding copyright ownership.
 The ASF licenses this file to You under the Apache License, Version 2.0
 (the "License"); you may not use this file except in compliance with
 the License.  You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 limitations under the License.
 */

package com.navinfo.flume.sink;

import kafka.javaapi.producer.Producer;
import kafka.producer.KeyedMessage;
import kafka.producer.ProducerConfig;

import org.apache.commons.io.comparator.DirectoryFileComparator;
import org.apache.flume.*;
import org.apache.flume.conf.Configurable;
import org.apache.flume.sink.AbstractSink;
import org.apache.flume.source.EventDrivenSourceRunner;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.base.Preconditions;
import com.google.common.io.Files;

import com.navinfo.flume.sink.Constants;
import com.thoughtworks.paranamer.BytecodeReadingParanamer;

import java.io.File;
import java.io.IOException;
import java.util.Map;
import java.util.Properties;
import java.util.Random;

/**
 * A Flume Sink that can publish messages to Kafka.
 * This is a general implementation that can be used with any Flume agent and a channel.
 * This supports key and messages of type String.
 * Extension points are provided to for users to implement custom key and topic extraction
 * logic based on the message content as well as the Flume context.
 * Without implementing this extension point(MessagePreprocessor), it's possible to publish
 * messages based on a static topic. In this case messages will be published to a random
 * partition.
 */
public class FileSink extends AbstractSink implements Configurable {

    private static final Logger logger = LoggerFactory.getLogger(FileSink.class);
    private Properties producerProps;
    private Producer<String, String> producer;

    private String topic;
    private String body;
    private Context context;
    
    private Random ran = new Random();
    private String directory;
    
    @Override
    public Status process() throws EventDeliveryException {
        Status result = Status.READY;
        Channel channel = getChannel();
        Transaction transaction = channel.getTransaction();
        Event event = null;
        Map<String, String> eventHeader = null;
        String fileName = null;
        
        String eventTopic = topic;
        String eventKey = null;

        try {
            transaction.begin();

            event = channel.take();
            
            if (event != null) {
                if ( this.directory != null && !this.directory.isEmpty() ) {
                    byte[] eventData = event.getBody();
                    eventHeader = event.getHeaders();
                    
                    if ( eventHeader != null && eventHeader.containsKey("basename") ) {
                        fileName = eventHeader.get("basename");
                    } 
                    else {
                        fileName = String.format("data%04d.jpg", ran.nextInt(10000));
                    }

                
                    File dir = new File(this.directory);    
                 
                    if  (dir.exists() && dir.isDirectory()) {
                        this.demoFileWrite(directory + File.separator + fileName, eventData);
                    }
                }
               
                // create a message
                KeyedMessage<String, String> data;
                String eventBody = new String(event.getBody());
                if (body != null && !body.isEmpty()) {
                    data = new KeyedMessage<String, String>(topic, "", body);
                    logger.debug(topic + ":" + body);
                } 
                else {
                    data = new KeyedMessage<String, String>(topic, "", eventBody);
                    logger.debug(topic + ":" + eventBody);
                }
                // publish
                producer.send(data);
            } 
            else {
                // No event found, request back-off semantics from the sink runner
                result = Status.BACKOFF;
            }
            // publishing is successful. Commit.
            transaction.commit();

        } catch (Exception ex) {
            transaction.rollback();
            String errorMsg = "Failed to publish event: " + event;
            logger.error(errorMsg);
            throw new EventDeliveryException(errorMsg, ex);

        } finally {
            transaction.close();
        }

        return result;
    }

	@Override
    public synchronized void start() {
        // instantiate the producer
        ProducerConfig config = new ProducerConfig(producerProps);
        producer = new Producer<String, String>(config);
        super.start();
    }

    @Override
    public synchronized void stop() {
        producer.close();
        super.stop();
    }


    @Override
    public void configure(Context context) {
		
		this.context = context;
 	
        // read the properties for Kafka Producer
        // any property that has the prefix "kafka" in the key will be considered as a property that is passed when
        // instantiating the producer.
        // For example, kafka.metadata.broker.list = localhost:9092 is a property that is processed here, but not
        // sinks.k1.type = com.thilinamb.flume.sink.KafkaSink.
        Map<String, String> params = context.getParameters();
        producerProps = new Properties();
        for (String key : params.keySet()) {
            String value = params.get(key).trim();
            key = key.trim();
            if (key.startsWith(Constants.PROPERTY_PREFIX)) {
                // remove the prefix
                key = key.substring(Constants.PROPERTY_PREFIX.length() + 1, key.length());
                producerProps.put(key.trim(), value);
                if (logger.isDebugEnabled()) {
                    logger.debug("Reading a Kafka Producer Property: key: " + key + ", value: " + value);
                }
            }
        }

        // 如果配置了消息内容，则向Kafka传入配置的内容
        body = context.getString(Constants.BODY);

        topic = context.getString(Constants.TOPIC, Constants.DEFAULT_TOPIC);
        
        directory = context.getString(Constants.DIRECTORY, Constants.DEFAULT_DIRECTORY);
    }
    
    private synchronized void demoFileWrite(final String fileName, final byte[] contents) throws IOException
    {
       Preconditions.checkNotNull(fileName, "Provided file name for writing must NOT be null.");
       Preconditions.checkNotNull(contents, "Unable to write null contents.");
       final File newFile = new File(fileName);
       try
       {
          Files.write(contents, newFile);
       }
       catch (IOException fileIoEx)
       {
    	   logger.error(  "ERROR trying to write to file '" + fileName + "' - "
                      + fileIoEx.toString());
    	   throw(fileIoEx);
       }
       
    }
}
