---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Apache Camel vs Spring Integration
authors: 
  - bjornbeskow
tags: spring integration apache camel frameworks
topstory: true
comments: true

---

Full-stack Enterprise Service Buses ([ESB]s) like BizTalk, WebSphere MB, Mule, ServiceMix et.al have been dominating the Enterprise Integration scene for quite some time. But with the rise of [Microservices] and its enabling tools such as [Spring Boot] and [Docker],  light-weight Integration Frameworks are becoming more and more attractive. In this post, we'll compare the two most popular frameworks, [Apache Camel] and [Spring Integration] in terms of expressiveness and conciseness.

-[readmore]-

[comment]: # (Links)
[Spring Integration]: http://projects.spring.io/spring-integration/
[Spring Integration Cafe Example]: https://github.com/spring-projects/spring-integration-samples/tree/master/dsl/cafe-dsl
[Apache Camel]: http://camel.apache.org/
[Apache Camel Cafe Example]: http://camel.apache.org/cafe-example.html
[ESB]: https://en.wikipedia.org/wiki/Enterprise_service_bus
[Microservices]: https://callistaenterprise.se/blogg/teknik/2015/05/20/blog-series-building-microservices/
[Spring Boot]: http://projects.spring.io/spring-boot/
[Docker]: https://www.docker.com/
[Enterprise Integration Patterns]: http://www.enterpriseintegrationpatterns.com/
[Ramblings]: http://www.eaipatterns.com/ramblings.html

[comment]: # (Images)
[EIP-book]: /assets/blogg/apache-camel-vs-spring-integration/eip-book.png
[cafe-example]: /assets/blogg/apache-camel-vs-spring-integration/cafe-example.png

Integrating Enterprise Applications is challenging, but luckily the challenges are often well known and understood. [Enterprise Integration Patterns], the seminal work by Gregor Hophe and Bobby Woolf, provides a catalogue of typical, recurring challenges and software patterns to address them.

![EIP Book][EIP-book]

Implementing these patterns can be a daunting task, though. This is where an Integration Framework can be of great help. While there are quite some Integration Frameworks out there, two of them have gained broad adoption: [Apache Camel] and [Spring Integration]. These two frameworks both share the same goal: to provide an easy-to-use mechanism for implementing typical integration tasks (such as mediation, routing, protocol adaptation), in a non-obtrusive way with small footprint and overhead, embeddable in your existing application infrastructure. Out of the box, you get a fair amount of (and steadily growing) transport adapters, ready-made implementations of EIPs, as well as basic management support via JMX. Hence from a functionality point of view, the two frameworks are quite equal.

Apache Camel was released in version 1.0 in 2007. Already from version 1.0, it came with a Java DSL as well as an XML DSL built on top of Spring XML. Now being at version 2.15, there are additional DSLs in a wide variety of languages (among them Groovy and Scala). Spring Integration was released in version 1.0.0 two years later, in 2009. Being part of the Spring family, XML-based configuration was initially the only option, but since recently Spring Integration also provides a Java DSL.

While one can argue that one particular syntax is better than another (verbose XML versus fluent Java/Groovy), these are just a matter of personal preference. What is more interesting are the *semantic* differences. And here I find a subtle, yet to me quite important difference between Apache Camel and Spring Integration: While the expressive power is roughly the same, the Spring Integration DSL exposes the lower level EIPs (such as Channels, Gateways etc.), where the Camel DSL seem to focus more on the *intention* of the integration. Since Integration code (just like most other code) are typically being *read* for more often than it is written, the ability to clearly and concisely communicate its intention is a key discriminating factor.

The often used Cafe example (based on one of Gregor Hophe's [Ramblings]) can illustrate the difference. The domain is that of a Cafe, and illustrates Routing, Splitting and Aggregation.

![Camel Alternatives][cafe-example]

Both Spring Integration and Apache Camel includes this example as part of their sample projects. In the [Spring Integration Cafe Example], the integration flow looks like this:

~~~ Java
  @MessagingGateway
  public interface Cafe {
  	@Gateway(requestChannel = "orders.input")
  	void placeOrder(Order order);
  }

  private AtomicInteger hotDrinkCounter = new AtomicInteger();
  private AtomicInteger coldDrinkCounter = new AtomicInteger();

  @Bean(name = PollerMetadata.DEFAULT_POLLER)
  public PollerMetadata poller() {
  	return Pollers.fixedDelay(1000).get();
  }

  @Bean
  public IntegrationFlow orders() {
  	return f -> f
  	  .split(Order.class, Order::getItems)
  	  .channel(c -> c.executor(Executors.newCachedThreadPool()))
  	  .<OrderItem, Boolean>route(OrderItem::isIced, mapping -> mapping
  	    .subFlowMapping("true", sf -> sf
  	      .channel(c -> c.queue(10))
  	      .publishSubscribeChannel(c -> c
  	        .subscribe(s ->
  	          s.handle(m -> sleepUninterruptibly(1, TimeUnit.SECONDS)))
  	        .subscribe(sub -> sub
  	          .<OrderItem, String>transform(item ->
  	            Thread.currentThread().getName()
  	              + " prepared cold drink #"
  	              + this.coldDrinkCounter.incrementAndGet()
  	              + " for order #" + item.getOrderNumber()
  	              + ": " + item)
  	          .handle(m -> System.out.println(m.getPayload())))))
  	    .subFlowMapping("false", sf -> sf
  	      .channel(c -> c.queue(10))
  	      .publishSubscribeChannel(c -> c
  	        .subscribe(s ->
  	          s.handle(m -> sleepUninterruptibly(5, TimeUnit.SECONDS)))
  	        .subscribe(sub -> sub
  	          .<OrderItem, String>transform(item ->
  	            Thread.currentThread().getName()
  	              + " prepared hot drink #"
  	              + this.hotDrinkCounter.incrementAndGet()
  	              + " for order #" + item.getOrderNumber()
  	              + ": " + item)
  	          .handle(m -> System.out.println(m.getPayload()))))))
  	  .<OrderItem, Drink>transform(orderItem ->
  	    new Drink(orderItem.getOrderNumber(),
  	      orderItem.getDrinkType(),
  	      orderItem.isIced(),
  	      orderItem.getShots()))
  	  .aggregate(aggregator -> aggregator
  	    .outputProcessor(group ->
  	      new Delivery(group.getMessages()
  	        .stream()
  	        .map(message -> (Drink) message.getPayload())
  	        .collect(Collectors.toList())))
  	    .correlationStrategy(m ->
  	      ((Drink) m.getPayload()).getOrderNumber()), null)
  	  .handle(CharacterStreamWritingMessageHandler.stdout());
  }

}
~~~

There are quite a lot of details in there (and the use of Java 8 syntax, which might not be familiar to everyone yet), but the key point here is the fundamental use of Gateways and Channels to implement the higher-level EIPs.

In contrast, the [Apache Camel Cafe Example] focus on the higher-level EIPs, using a vocabulary that is more close to the "business" than the technical domain: 

~~~ Java
public void configure() {

  from("direct:cafe")
    .split().method("orderSplitter")
    .to("direct:drink");
    
  from("direct:drink").recipientList().method("drinkRouter");
  
  from("seda:coldDrinks?concurrentConsumers=2")
    .to("bean:barista?method=prepareColdDrink")
    .to("direct:deliveries");
  from("seda:hotDrinks?concurrentConsumers=3")
    .to("bean:barista?method=prepareHotDrink")
    .to("direct:deliveries");
    
  from("direct:deliveries")
    .aggregate(new CafeAggregationStrategy())
      .method("waiter", "checkOrder").completionTimeout(5 * 1000L)
    .to("bean:waiter?method=prepareDelivery")
    .to("bean:waiter?method=deliverCafes");
 
}
~~~

Agreed, the two examples are not directly comparable (the Spring Integration example contains more functionality and more details and hence looks more complex), but I think the fundamental difference in approach is clearly visible.

Spring Integration and Apache Camel are both well-designed and highly capable light-weight integration frameworks. From a feature perspective, they are more or less equal. Any of them would be an excellent choice in the assignment I'm currently working on. But if you, like me, have the luxury to choose between them, I think the semantic expressiveness of the Apache Camel DSL, its ability to clearly communicate the intention of a particular integration flow, is an important competitive edge.