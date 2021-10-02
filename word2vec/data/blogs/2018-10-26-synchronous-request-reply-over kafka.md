---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Synchronous Request-Reply using Apache Kafka
authors: 
  - bjornbeskow
tags: spring rest apache kafka event driven architecture synchronous request reply
topstory: true
comments: true

---

[Event Driven Architectures] in general and [Apache Kafka] specifically have gained lots of attention lately. To realize the full benefits of an Event Driven Architecture, the event delegation mechanism must be inherently asynchronous. There may however be some specific use cases/flows where a Synchronous Request-Reply semantics is needed. This blog post shows how to realize [Request Reply] using Apache Kafka.

-[readmore]-

[comment]: # (Links)
[Apache Kafka]: Https://kafka.apache.org/
[Event Driven Architectures]: https://martinfowler.com/articles/201701-event-driven.html
[Request Reply]: https://www.enterpriseintegrationpatterns.com/patterns/messaging/RequestReply.html
[Return Address]: https://www.enterpriseintegrationpatterns.com/patterns/messaging/ReturnAddress.html
[Spring Kafka]: https://spring.io/projects/spring-kafka
[github.com/callistaenterprise/blog-synchronous-kafka]: https://github.com/callistaenterprise/blog-synchronous-kafka

Apache Kafka is by design inherently asynchronous. Hence Request-Reply semantics is not natural in Apache Kafka. This challenge is however not new. The [Request Reply] Enterprise Integration Pattern provides a proven mechanism for synchronous message exchange over asynchonous channels:

![Request Reply](https://www.enterpriseintegrationpatterns.com/img/RequestReply.gif)

The [Return Address] pattern complements [Request Reply] with a mechanism for the requestor to specify to which address the reply should be sent:

![Return Addess](https://www.enterpriseintegrationpatterns.com/img/ReturnAddressSolution.gif)

Recently, [Spring Kafka] 2.1.3 added support for the Request Reply pattern out-of-the box, and version 2.2 polished some of it's rough edges. Let's have a look at how that support works:

### Client Side: ReplyingKafkaTemplate

The well known **`Template`** abstraction forms the basis for the client-side part of the Spring Request-Reply mechanism.

~~~ java
  @Bean
  public ReplyingKafkaTemplate<String, Request, Reply> replyKafkaTemplate(ProducerFactory<String, Request> pf, KafkaMessageListenerContainer<String, Reply> lc) {
  return new ReplyingKafkaTemplate<>(pf, lc);
  }
~~~

That's fairly straight forward: We setup a ReplyingKafkaTemplate that sends Request messages with String keys, and receives Reply messages with String keys. The ReplyingKafkaTemplate however needs to be backed by a Request ProducerFactory, a ReplyConsumerFactory and a MessageListenerContainer, with corresponding consumer and producer configs. Hence the needed config is rather extensive:

~~~ java
  @Value("${kafka.topic.car.reply}")
  private String replyTopic;

  @Bean
  public Map<String, Object> consumerConfigs() {
    Map<String, Object> props = new HashMap<>();
    props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class);
    props.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);

    return props;
  }

  @Bean
  public Map<String, Object> producerConfigs() {
    Map<String, Object> props = new HashMap<>();
    props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
    props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
    props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
    return props;
  }

  @Bean
  public ProducerFactory<String, Request> requestProducerFactory() {
    return new DefaultKafkaProducerFactory<>(producerConfigs());
  }

  @Bean
  public ConsumerFactory<String, Reply> replyConsumerFactory() {
    return new DefaultKafkaConsumerFactory<>(consumerConfigs(), new StringDeserializer(),
        new JsonSerializer<Reply>());
  }

  @Bean
  public KafkaMessageListenerContainer<String, Reply> replyListenerContainer() {
    ContainerProperties containerProperties = new ContainerProperties(replyTopic);
    return new KafkaMessageListenerContainer<>(replyConsumerFactory(), containerProperties);
  }
~~~

With that in place, using the replyKafkaTemplate to send a synchronous reqeust and get a reply back looks like this:

~~~ java
  @Value("${kafka.topic.car.request}")
  private String requestTopic;

  @Value("${kafka.topic.car.reply}")
  private String replyTopic;

  @Autowired
  private ReplyingKafkaTemplate<String, Request, Reply> requestReplyKafkaTemplate;

...
  RequestReply request = RequestReply.request(...);
  // create producer record
  ProducerRecord<String, Request> record = new ProducerRecord<String, Request>(requestTopic, request);
  // set reply topic in header
  record.headers().add(new RecordHeader(KafkaHeaders.REPLY_TOPIC, requestReplyTopic.getBytes()));
  // post requst to kafka topic, and asynchronously get reply on the specified reply topic
  RequestReplyFuture<String, Request, Reply> sendAndReceive = requestReplyKafkaTemplate.sendAndReceive(record);
  sendAndReceive.addCallback(new ListenableFutureCallback<ConsumerRecord<String, Reply>>() {
      @Override
      public void onSuccess(ConsumerRecord<String, Reply> result) {
        // get consumer record value
        Reply reply = result.value();
        System.out.println("Reply: " + reply.toString());
      }
  });
~~~

Lots of boiler plate code and low level api's there as well, and that old `ListenableFuture` API instead of the modern CompletableFuture. The requestReplyKafkaTemplate takes care of generating and setting a `KafkaHeaders.CORRELATION_ID` header, but we have to set the `KafkaHeaders.REPLY_TOPIC` header on the request explicitly. Note also that this same reply topic was redundantly wired into the replyListenerContainer above. Yuck. Not quite what I expected from a Spring abstraction.

### Server Side: @SendTo

On the server side, a regular KafkaListener listening on the request topic is decorated with an additional `@SendTo` annotation, to provide the reply message. The object returned by the listener method is automatically wrapped into a reply message, the `CORRELATION_ID` added, and the reply is posted on the topic specified by the `REPLY_TOPIC`.

~~~ java
  @Bean
  public Map<String, Object> consumerConfigs() {
    Map<String, Object> props = new HashMap<>();
    props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonSerializer.class);
    props.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);

    return props;
  }

  @Bean
  public Map<String, Object> producerConfigs() {
    Map<String, Object> props = new HashMap<>();
    props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
    props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
    props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);

    return props;
  }

  @Bean
  public ConsumerFactory<String, Request> requestConsumerFactory() {
    return new DefaultKafkaConsumerFactory<>(consumerConfigs(), new StringDeserializer(),
        new JsonSerializer<Request>());
  }

  @Bean
  public KafkaListenerContainerFactory<ConcurrentMessageListenerContainer<String, Request>> requestListenerContainerFactory() {
    ConcurrentKafkaListenerContainerFactory<String, Request> factory =
        new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(requestConsumerFactory());
    factory.setReplyTemplate(replyTemplate());
    return factory;
  }

  @Bean
  public ProducerFactory<String, Reply> replyProducerFactory() {
    return new DefaultKafkaProducerFactory<>(producerConfigs());
  }

  @Bean
  public KafkaTemplate<String, Reply> replyTemplate() {
    return new KafkaTemplate<>(replyProducerFactory());
  }
~~~

Also quite some configuration needed, but configuration of the listener is easier:

~~~ java
  @KafkaListener(topics = "${kafka.topic.car.request}", containerFactory = "requestListenerContainerFactory")
  @SendTo()
  public Reply receive(Request request) {
    Reply reply = ...;
    return reply;
  }
~~~

### But what about multiple consumer instances?

It sort of works, as long as we don't use multiple consumer instances. If we have multiple client instances, we must make sure that the reply is sent back to the correct client instance. The Spring Kafka documentation suggests that each consumer may use a unique topic, or that an additional `KafkaHeaders.REPLY_PARTITION` header value is sent with the request, a four byte field containing a BIG-ENDIAN representation of the partition integer. Using separate topics for different clients is clearly not very flexible, hence we opt for setting the `REPLY_PARTITION` explicitly. The client will then need to know which partition it is assigned to. The documentation suggests using explicit configuration to select a specific partition. Let's add that to our example:

~~~ java
  @Value("${kafka.topic.car.reply.partition}")
  private int replyPartition;
  
  ...
  
    @Bean
  public KafkaMessageListenerContainer<String, RequestReply> replyListenerContainer() {
    ContainerProperties containerProperties = new ContainerProperties(replyTopic);
    TopicPartitionInitialOffset initialOffset = new TopicPartitionInitialOffset(replyTopic, replyPartition);
    return new KafkaMessageListenerContainer<>(replyConsumerFactory(), containerProperties, initialOffset);
  }
~~~

~~~ java
  private static byte[] intToBytesBigEndian(final int data) {
    return new byte[] {(byte) ((data >> 24) & 0xff), (byte) ((data >> 16) & 0xff),
        (byte) ((data >> 8) & 0xff), (byte) ((data >> 0) & 0xff),};
  }

  ...
  record.headers().add(new RecordHeader(KafkaHeaders.REPLY_TOPIC, requestReplyTopic.getBytes()));
  record.headers().add(new RecordHeader(KafkaHeaders.REPLY_PARTITION, intToBytesBigEndian(replyPartition)));
  RequestReplyFuture<String, RequestReply, RequestReply> sendAndReceive = requestReplyKafkaTemplate.sendAndReceive(record);
  ...
~~~

Not pretty, but it works. The configuration needed is extensive, and the APIs are kind of low level. The need for explicit partition configuration adds complexity if we need to dynamically scale number of clients. Clearly, we could do better.

### Encapsulating reply topic and partition handling

Let's start with encapsulating the [Return Address] pattern, passing along the reply topic and partition. The Reply topic needs to be wired into the RequestReplyTemplate, and hence shouldn't be present in the API at all. When it comes to the reply partition, let's do it the other way around: Retrieve which partition(s) the reply topic listener has been assigned, and pass that partition along automatically. This eliminates the need for the client to care about these headers.

While doing this, let's also complete the API to resemble the standard KafkaTemplate (overloading the sendAndReceive() method with simplified parameters, and adding corresponding overloaded methods which use a configured default topic):

~~~ java
public class PartitionAwareReplyingKafkaTemplate<K, V, R> extends ReplyingKafkaTemplate<K, V, R> {

  public PartitionAwareReplyingKafkaTemplate(ProducerFactory<K, V> producerFactory,
      GenericMessageListenerContainer<K, R> replyContainer) {
    super(producerFactory, replyContainer);
  }

  private TopicPartition getFirstAssignedReplyTopicPartition() {
    if (getAssignedReplyTopicPartitions() != null &&
        getAssignedReplyTopicPartitions().iterator().hasNext()) {
      TopicPartition replyPartition = getAssignedReplyTopicPartitions().iterator().next();
      if (this.logger.isDebugEnabled()) {
        this.logger.debug("Using partition " + replyPartition.partition());
      }
      return replyPartition;
    } else {
      throw new KafkaException("Illegal state: No reply partition is assigned to this instance");
    }
  }

  private static byte[] intToBytesBigEndian(final int data) {
    return new byte[] {(byte) ((data >> 24) & 0xff), (byte) ((data >> 16) & 0xff),
        (byte) ((data >> 8) & 0xff), (byte) ((data >> 0) & 0xff),};
  }

  public RequestReplyFuture<K, V, R> sendAndReceiveDefault(@Nullable V data) {
    return sendAndReceive(getDefaultTopic(), data);
  }

  public RequestReplyFuture<K, V, R> sendAndReceiveDefault(K key, @Nullable V data) {
    return sendAndReceive(getDefaultTopic(), key, data);
  }

  ...
  
  public RequestReplyFuture<K, V, R> sendAndReceive(String topic, @Nullable V data) {
    ProducerRecord<K, V> record = new ProducerRecord<>(topic, data);
    return doSendAndReceive(record);
  }

  public RequestReplyFuture<K, V, R> sendAndReceive(String topic, K key, @Nullable V data) {
    ProducerRecord<K, V> record = new ProducerRecord<>(topic, key, data);
    return doSendAndReceive(record);
  }

  ...
  
  @Override
  public RequestReplyFuture<K, V, R> sendAndReceive(ProducerRecord<K, V> record) {
    return doSendAndReceive(record);
  }
  
  protected RequestReplyFuture<K, V, R> doSendAndReceive(ProducerRecord<K, V> record) {
    TopicPartition replyPartition = getFirstAssignedReplyTopicPartition();
    record.headers()
        .add(new RecordHeader(KafkaHeaders.REPLY_TOPIC, replyPartition.topic().getBytes()))
        .add(new RecordHeader(KafkaHeaders.REPLY_PARTITION,
            intToBytesBigEndian(replyPartition.partition())));
    return super.sendAndReceive(record);
  }  

}
~~~

Next step: Let's adapt the ListenableFuture to the more modern CompletableFuture.

~~~ java
public class CompletableFutureReplyingKafkaTemplate<K, V, R> extends PartitionAwareReplyingKafkaTemplate<K, V, R> {

  public CompletableFutureReplyingKafkaTemplate(ProducerFactory<K, V> producerFactory,
      GenericMessageListenerContainer<K, R> replyContainer) {
    super(producerFactory, replyContainer);
  }

  public CompletableFuture<R> requestReplyDefault(V value) {
    return adapt(sendAndReceiveDefault(value));
  }

  public CompletableFuture<R> requestReplyDefault(K key, V value) {
    return adapt(sendAndReceiveDefault(key, value));
  }

  ...
  
  public CompletableFuture<R> requestReply(String topic, V value) {
    return adapt(sendAndReceive(topic, value));
  }

  public CompletableFuture<R> requestReply(String topic, K key, V value) {
    return adapt(sendAndReceive(topic, key, value));
  }

  ...
  
  private CompletableFuture<R> adapt(RequestReplyFuture<K, V, R> requestReplyFuture) {
    CompletableFuture<R> completableResult = new CompletableFuture<R>() {
      @Override
      public boolean cancel(boolean mayInterruptIfRunning) {
        boolean result = requestReplyFuture.cancel(mayInterruptIfRunning);
        super.cancel(mayInterruptIfRunning);
        return result;
      }
    };
    // Add callback to the request sending result
    requestReplyFuture.getSendFuture().addCallback(new ListenableFutureCallback<SendResult<K, V>>() {
      @Override
      public void onSuccess(SendResult<K, V> sendResult) {
        // NOOP
      }
      @Override
      public void onFailure(Throwable t) {
        completableResult.completeExceptionally(t);
      }
    });
    // Add callback to the reply
    requestReplyFuture.addCallback(new ListenableFutureCallback<ConsumerRecord<K, R>>() {
      @Override
      public void onSuccess(ConsumerRecord<K, R> result) {
        completableResult.complete(result.value());
      }
      @Override
      public void onFailure(Throwable t) {
        completableResult.completeExceptionally(t);
      }
    });
    return completableResult;
  }

}
~~~

Pack that up in a utility library, and we now have an API that is much more in line with the general Convention over Configuration design philosophy of Spring. This is the resulting client code:

~~~ java
  @Autowired
  private CompletableFutureReplyingKafkaTemplate<String,Request,Reply> requestReplyKafkaTemplate;

...

  requestReplyKafkaTemplate.requestReply(request).thenAccept(reply ->
    System.out.println("Reply: " + reply.toString())
  );
~~~

### Summing up

To summarize, Spring for Kafka 2.2 provides a fully functional implementation of the Request-Reply pattern over Apache Kafka, but the API still have some rough edges. In this blog post, we have seen that some additional abstractions and API adaptations can give a more consistent, high-level API.

__Caveat 1__: One of the principal benefits of an Event Driven Architecture is the decoupling of event producers and consumers, allowing for much more flexible and evolvable systems. Relying on a synchronous Request-Reply semantics is the exact opposite, where the requestor and replyer are tightly coupled. Hence it should be used only when needed.

__Caveat 2__: If synchronous Request-Reply is required, an HTTP-based protocol is much simpler and more efficient than using an asynchronous channel like Apache Kafka.

Still, there may be scenarios when synchronous Request-Reply over Kafka makes sense. Choose wisely the best tool for the job.

A fully working example can be found at [github.com/callistaenterprise/blog-synchronous-kafka].
