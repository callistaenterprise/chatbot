---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: >-
  Project Reactor - Reactive Programming with Spring,
  Part 2.
authors:
  - annaeriksson
tags: project reactor spring
---

This is the second part of my [blog series on reactive programming](https://callistaenterprise.se/blogg/teknik/2020/05/24/blog-series-reactive-programming/), providing an overview of Project Reactor, a reactive library based on the Reactive Streams specification. Part 1 covered [an introduction to reactive programming](https://callistaenterprise.se/blogg/teknik/2020/05/24/blog-series-reactive-programming-part-1/).

-[readmore]-


## 1. An introduction to Project Reactor
 
Reactive programming is supported by Spring Framework since version 5. That support is built on top of Project Reactor.

Project Reactor (or just Reactor) is a Reactive library for building non-blocking applications on the JVM and is based on the Reactive Streams Specification. Reactor is the foundation of the reactive stack in the Spring ecosystem and it is being developed in close collaboration with Spring. WebFlux, Spring's reactive-stack web framework, requires Reactor as a core dependency. 
 

### 1.1 Reactor modules
Project Reactor consist of a set of modules as listed in the [Reactor documentation](https://projectreactor.io/docs).
The modules are embeddable and interoperable. The main artifact is `Reactor Core` which holds the reactive types Flux and Mono, that implement the Reactive Stream's Publisher interface (for details see [the first blog post of this series](https://callistaenterprise.se/blogg/teknik/2020/05/24/blog-series-reactive-programming-part-1/)) and a set of operators that can be applied on these.

Some other modules are:
- `Reactor Test` - which provides some utilities for testing reactive streams
- `Reactor Extra` - that provides some additional Flux operators
- `Reactor Netty` - non-blocking and backpressure-ready TCP, HTTP, and UDP clients and servers - based on the Netty framework
- `Reactor Adapter` -  for adapting to/from other reactive libraries such as RxJava2 and Akka Streams
- `Reactor Kafka` - a reactive API for Kafka which enables messages to be published to and consumed from Kafka

### 1.2 Set up a project
Before we continue, if you want to set up a project and run some of the code samples below, generate a new Spring Boot application using [Spring Initializr](https://start.spring.io).
As dependency select Spring Reactive Web. After importing the project in your IDE have a look at the POM file and you will see that the spring-boot-starter-webflux dependency is added which will also bring in the reactor-core dependeny. Also reactor-test has been added as a dependency.
Now you are ready to run the coming code examples.

```xml
...	
        <dependencies>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-webflux</artifactId>
		</dependency>

		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-test</artifactId>
			<scope>test</scope>
			<exclusions>
				<exclusion>
					<groupId>org.junit.vintage</groupId>
					<artifactId>junit-vintage-engine</artifactId>
				</exclusion>
			</exclusions>
		</dependency>
		<dependency>
			<groupId>io.projectreactor</groupId>
			<artifactId>reactor-test</artifactId>
			<scope>test</scope>
		</dependency>
	</dependencies>
...
```

## 2. Reactor Core features
Reactor Core defines the reactive types Flux and Mono.

### 2.1 Flux vs Mono
A Flux is a Publisher that can emit 0 to N elements, while a Mono can emit 0 to 1 element.
They are both terminated either by a completion signal or an error and they call a downstream Subscriber’s onNext, onComplete and onError methods. 
Besides implementing the functionality described by the Reactive Streams specification, Flux and Mono provide a set of operators to support transformations, filtering and error handling.

As a first exercise, go to the test class generated in your new project, add the following example and run it:

```java
@Test
void simpleFluxExample() {
    Flux<String> fluxColors = Flux.just("red", "green", "blue");
    fluxColors.subscribe(System.out::println);
}
```
The just method creates a Flux that emits the provided elements and then completes.
Nothing is emitted until someone subscribes to it. To subscribe to it, we invoke the subscribe method and in this case we just print out the emitted items. Creating a Mono can also be done with the just method, the only difference being that only one parameter is allowed.

### 2.2 Chaining operators
Take a look at the [Flux API](https://projectreactor.io/docs/core/release/api/reactor/core/publisher/Flux.html) and you will see that almost all methods return a Flux or a Mono, meaning that operators can be chained.
Each operator adds behavior to a Publisher (Flux or Mono) and wraps the previous step’s Publisher into a new instance. Data originates from the first Publisher and moves down the chain, transformed by each operator. Eventually, a Subscriber finishes the process. Note that nothing happens until a Subscriber actually subscribes to a Publisher.

There is an operator called log() which provides logging of all Reactive Streams signals taking place behind the scenes. 
Just change the last line of the above example to 
```java
fluxColors.log().subscribe(System.out::println);
```

and rerun the test. You will now see the following being added to the output:

```text
2020-09-12 16:16:39.779  INFO 6252 --- [           main] reactor.Flux.Array.1                     : | onSubscribe([Synchronous Fuseable] FluxArray.ArraySubscription)
2020-09-12 16:16:39.781  INFO 6252 --- [           main] reactor.Flux.Array.1                     : | request(unbounded)
2020-09-12 16:16:39.781  INFO 6252 --- [           main] reactor.Flux.Array.1                     : | onNext(red)
red
2020-09-12 16:16:39.781  INFO 6252 --- [           main] reactor.Flux.Array.1                     : | onNext(green)
green
2020-09-12 16:16:39.781  INFO 6252 --- [           main] reactor.Flux.Array.1                     : | onNext(blue)
blue
2020-09-12 16:16:39.782  INFO 6252 --- [           main] reactor.Flux.Array.1                     : | onComplete()
```

Now, to see what happens if you exclude the call to subscribe(), again modify the last code line to the following and rerun the test:

```java
fluxColors.log();
```
As you will see from the log output, no items are now emitted - since there is no Subscriber initiating the process.

### 2.3 Finding the right operator

Reactor provides a long list of operators and as a help to find the right one for a given use case there is a dedicated [appendix](https://projectreactor.io/docs/core/release/reference/index.html#which-operator)  in the Reactor reference documentation. 
It is divided into different categories as shown in the table below.

| Operator category  | Examples  | 
|---|---|
| Creating a new sequence | just, fromArray, fromIterable, fromStream  |
| Transforming an existing sequence | map, flatMap, startWith, concatWith |
| Peeking into a sequence | doOnNext, doOnComplete, doOnError, doOnCancel |
| Filtering a sequence | filter, ignoreElements, distinct, elementAt, takeLast |
| Handling errors | onErrorReturn, onErrorResume, retry |
| Working with time | elapsed, interval, timestamp, timeout |
| Splitting a Flux | buffer, groupBy, window |
| Going back to the synchronous world | block, blockFirst, blockLast, toIterable, toStream |
| Multicasting a Flux to several Subscribers | publish, cache, replay |

Now feel free to go ahead and create some small examples that use some of these operators and see what happens when you run them.
For example using the map operator (which transforms the items emitted by applying a synchronous function to each item):

```java
@Test
void mapExample() {
    Flux<String> fluxColors = Flux.just("red", "green", "blue");
    fluxColors.map(color -> color.charAt(0)).subscribe(System.out::println);
}
```

Or the zip operator, which zips multiple sources togheter (waiting for all the sources to emit one element and combining them into a Tuple):

```java
@Test
void zipExample() {
    Flux<String> fluxFruits = Flux.just("apple", "pear", "plum");
    Flux<String> fluxColors = Flux.just("red", "green", "blue");
    Flux<Integer> fluxAmounts = Flux.just(10, 20, 30);
    Flux.zip(fluxFruits, fluxColors, fluxAmounts).subscribe(System.out::println);
}
```

## 3. Error handling
As described in my previous blog post, in Reactive Streams errors are terminal events. When an error occurs, it stops the whole sequence and the error gets propagated to the Subscriber's onError method, which should always be defined. If not defined, onError will throw an UnsupportedOperationException.

As you see running the following example, the third value is never emitted, since the second value results in an error:

```java
@Test
public void onErrorExample() {
    Flux<String> fluxCalc = Flux.just(-1, 0, 1)
        .map(i -> "10 / " + i + " = " + (10 / i));
    
    fluxCalc.subscribe(value -> System.out.println("Next: " + value),
        error -> System.err.println("Error: " + error));
}
```
The output will look like:

```text
Next: 10 / -1 = -10
Error: java.lang.ArithmeticException: / by zero
```

It is also possible to deal with errors in the middle of a reactive chain, using error-handling operators:

The `onErrorReturn` method will emit a fallback value when an error of the specified type is observed. 
It can be compared to catching an Exception and returning a static fallback value in imperative programming.
See the example below:

```java
@Test
public void onErrorReturnExample() {
    Flux<String> fluxCalc = Flux.just(-1, 0, 1)
	    .map(i -> "10 / " + i + " = " + (10 / i))
		.onErrorReturn(ArithmeticException.class, "Division by 0 not allowed");

    fluxCalc.subscribe(value -> System.out.println("Next: " + value),
	    error -> System.err.println("Error: " + error));

}
```

and the resulting output:
```text
Next: 10 / -1 = -10
Next: Division by 0 not allowed
```

As you can see, using an  error-handling operator this way still does not let the original reactive sequence continue (the third value is not emitted here either), it rather substitutes it. 
If it's not enough to just return some default value, you can use the `onErrorResume` method, to subscribe to a fallback Publisher when an error occurs.
This could be compared to catching an exception and invoking a fallback method in imperative programming. 
If for example a call to an external service fails, the onErrorResume implementation could be to fetch the data from a local cache.

## 4. Testing
The Reactor Test module provides utilities that are helpful in testing how your Flux or Mono behaves. There is an API called the StepVerifier API that helps out with this. You create a StepVerifier and pass it the Publisher to be tested. The StepVerifier will subscribe to the Publisher when the verify method is called and then it compares the emitted values to your defined expectations.

See the following example:

```java
@Test
public void stepVerifierTest() {
    Flux<String> fluxCalc = Flux.just(-1, 0, 1)
        .map(i -> "10 / " + i + " = " + (10 / i));

    StepVerifier.create(fluxCalc)
        .expectNextCount(1)
        .expectError(ArithmeticException.class)
        .verify();
}
```

A StepVerifier is created for the `fluxCalc` and two expectations are defined - first one String is is expected to be emitted and then an error should be emitted with the type ArithmeticException. 
With the verify call, the StepVerifier starts subscribing to the Flux and the flow is initiated.

StepVerifier also has other features such as enabling post-execution assertions and support for virtual time to avoid long run times for tests related to time-based operators. 

The Reactor Test module also provides another API, the `TestPublisher` which is a Publisher that you can directly manipulate, triggering onNext, onComplete and onError events, for testing purposes. 


## 5. Concurrency model
As you might already have noticed from the log output of the simpleFluxExample, so far our Publisher has been executing on the main thread, just as the Subscriber. This is because Reactor does not enforce a concurrency model. Instead, the execution will for most of the operators continue on the same thread, leaving the choice to the developer. The execution model is determined by the `Scheduler` that is being used. 

There are two ways of switching the execution context in a reactive chain: publishOn and subscribeOn. 
What differs is the following:
- `publishOn(Scheduler scheduler)` affects the exeuction for all subsequent operators (as far as nothing else is specified)
- `subscribeOn(Scheduler scheduler)` changes the thread from which the whole chain of operators subscribes, based on the earliest subscribeOn call in the chain. It does not affect the behavior of subsequent calls to publishOn

The `Schedulers` class holds static methods to provide an execution context, such as:
- `parallel()`  -  A fixed pool of workers that is tuned for parallel work, creating as many workers as there are CPU cores.
- `single()` -  A single, reusable thread. This method reuses the same thread for all callers, until the Scheduler is disposed. If you instead want a per-call dedicated thread, you can use Schedulers.newSingle() for each call.
- `boundedElastic()` - Dynamically creates a bounded number of workers. It has a limit on the number of backing threads it can create and can enqueue tasks to be re-scheduled when a thread becomes available. This is a good choice for wrapping synchronous, blocking calls.                                                                                                                                                   
- `immediate()` - immediately runs on the executing thread, not swithcing execution context
- `fromExecutorService(ExecutorService)` -  can be used to create a Scheduler out of any existing ExecutorService

Run the following example and observe the behavior:

```java
@Test
public void publishSubscribeExample() {
    Scheduler schedulerA = Schedulers.newParallel("Scheduler A");
    Scheduler schedulerB = Schedulers.newParallel("Scheduler B");
    Scheduler schedulerC = Schedulers.newParallel("Scheduler C");
        
    Flux.just(1)
        .map(i -> {
            System.out.println("First map: " + Thread.currentThread().getName());
            return i;
        })
        .subscribeOn(schedulerA)
        .map(i -> {
            System.out.println("Second map: " + Thread.currentThread().getName());
            return i;
        })
        .publishOn(schedulerB)
        .map(i -> {
            System.out.println("Third map: " + Thread.currentThread().getName());
            return i;
        })
        .subscribeOn(schedulerC)
        .map(i -> {
            System.out.println("Fourth map: " + Thread.currentThread().getName());
            return i;
        })
        .publishOn(schedulerA)
        .map(i -> {
            System.out.println("Fifth map: " + Thread.currentThread().getName());
            return i;
        })
        .blockLast();
}
```
Taking a look at the output (as below) you can see that the first and second map are executed in a thread from Scheduler A, since the first subscribeOn in the chain switches to this scheduler and it affects the whole chain.
Before the third map there is a publishOn switching the execution context to Scheduler B, making the third and fourth map being executed in this context (since the second subscribeOn will not have any effect). And finally there is a new publishOn switching back to Scheduler A before the last map operation.
```text
First map: Scheduler A-4
Second map: Scheduler A-4
Third map: Scheduler B-3
Fourth map: Scheduler B-3
Fifth map: Scheduler A-1
```

## 6. Backpressure
As you might recall from the first part of this blog series, backpressure is the ability for the consumer to signal to the producer what rate of emission it can handle, so it does not get overwhelmed.

The example below demonstrates how the Subscriber can control the pace of emission by invoking the `request(n)` method on the Subscription.

```java
@Test
public void backpressureExample() {
    Flux.range(1,5)
        .subscribe(new Subscriber<Integer>() {
            private Subscription s;
            int counter;
            
            @Override
            public void onSubscribe(Subscription s) {
                System.out.println("onSubscribe");
                this.s = s;
                System.out.println("Requesting 2 emissions");
                s.request(2);
            }
            
            @Override
            public void onNext(Integer i) {
                System.out.println("onNext " + i);
                counter++;
                if (counter % 2 == 0) {
                    System.out.println("Requesting 2 emissions");
                    s.request(2);
                }
            }

            @Override
            public void onError(Throwable t) {
                System.err.println("onError");
            }

            @Override
            public void onComplete() {
                System.out.println("onComplete");
            }
    });
}
```

Run it and you will see that two values are emitted at a time as requested:

```text
onSubscribe
Requesting 2 emissions
onNext 1
onNext 2
Requesting 2 emissions
onNext 3
onNext 4
Requesting 2 emissions
onNext 5
onComplete
```

The Subscription also has a `cancel` method available to request the Publisher to stop the emission and clean up resources.

## 7. Cold vs Hot Publishers
There are two types of Publishers available - cold and hot Publishers.
So far we have focused on the cold Publishers.
As we stated earlier, nothing happens until we subscribe - but this is actually only true for the cold Publishers.

A cold Publisher generates new data for each subscription. If there is no subscription, data never gets generated.
On the contrary, a hot Publisher does not depend on having Subscribers. It can start publishing data without any Subscribers. If a Subscriber subscribes after the Publisher has started emitting values, it will only receive the values emitted after its subscription.

Publishers in Reactor are cold by default.
One way of creating a hot Publisher is by calling the `publish()` method on a Flux. This will return a `ConnectableFlux<T>` which has a connect() method to trigger the emission of values. The Subscribers should then subscribe to this ConnectableFlux instead of the original Flux.

Let's have a look at a simple cold vs hot Publisher to observe the different behavior. In the coldPublisherExample below, the interval operator is used to create a Flux that emits long values starting at 0.

```java
@Test
public void coldPublisherExample() throws InterruptedException {
    Flux<Long> intervalFlux = Flux.interval(Duration.ofSeconds(1));
    Thread.sleep(2000);
    intervalFlux.subscribe(i -> System.out.println(String.format("Subscriber A, value: %d", i)));
    Thread.sleep(2000);
    intervalFlux.subscribe(i -> System.out.println(String.format("Subscriber B, value: %d", i)));
    Thread.sleep(3000);
}

```

Running this will generate the following output:

```text
Subscriber A, value: 0
Subscriber A, value: 1
Subscriber A, value: 2
Subscriber B, value: 0
Subscriber A, value: 3
Subscriber B, value: 1
Subscriber A, value: 4
Subscriber B, value: 2
```

Now you might wonder why anything happens when the main thread is asleep, but that is because the interval operator by default runs on the Schedulers.parallel() Scheduler.
As you can see both Subscribers will get the values starting from 0.

Now let's look at what happens when we use a ConnectableFlux:

```java
@Test
public void hotPublisherExample() throws InterruptedException {
    Flux<Long> intervalFlux = Flux.interval(Duration.ofSeconds(1));
    ConnectableFlux<Long> intervalCF = intervalFlux.publish();
    intervalCF.connect();
    Thread.sleep(2000);
    intervalCF.subscribe(i -> System.out.println(String.format("Subscriber A, value: %d", i)));
    Thread.sleep(2000);
    intervalCF.subscribe(i -> System.out.println(String.format("Subscriber B, value: %d", i)));
    Thread.sleep(3000);
}
```
This time we get the following output:
```text
Subscriber A, value: 2
Subscriber A, value: 3
Subscriber A, value: 4
Subscriber B, value: 4
Subscriber A, value: 5
Subscriber B, value: 5
Subscriber A, value: 6
Subscriber B, value: 6
```
As we can see, this time none of the Subscribers get the initially emitted values 0 and 1.
They get the values that are emitted after they subscribe.
Instead of manually triggering the publishing it is also possible to configure the ConnectableFlux so that it starts after n subscriptions have been made, using the `autoConnect(n)` method.



## 8. Other features

 
### 8.1 Wrapping a synchronous, blocking call
When there is a need to use a source of information that is synchronous and blocking, the recommended pattern to use in Reactor is as follows:

```java
Mono blockingWrapper = Mono.fromCallable(() -> { 
    return /* make a remote synchronous call */ 
});
blockingWrapper = blockingWrapper.subscribeOn(Schedulers.boundedElastic()); 
```

The `fromCallable` method creates a Mono that produces its value using the provided Callable.
By using the Schedulers.boundedElastic() we ensure that each subscription happens on a dedicated single-threaded worker, not impacting other non-blocking processing.

### 8.2 Context
Sometimes there is a need to propagate some additional, usually more technical data, through a reactive pipeline. Compare this to associating some state with a thread using ThreadLocal in the imperative world.

Reactor has a feature that is somewhat comparable to ThreadLocal but can be applied to a Flux or a Mono instead of a Thread, called a `Context`.
This is an interface similar to a Map, where you can store key-value pairs and fetch a value by its key. The Context is transparently propagated throughout the whole reactive pipeline and can be easily accessed at any moment by calling the Mono.subscriberContext() method.

The context can be populated at subscription time by adding either the `subscriberContext(Function)` or the `subscriberContext(Context)` method invocation at the end of your reactive pipeline, as shown in the test method below.

```java
@Test
public void contextTest() {
    String key = "key";
    Mono<String> mono = Mono.just("anything")
	    .flatMap(s -> Mono.subscriberContext()
                .map(ctx -> "Value stored in context: " + ctx.get(key)))
            .subscriberContext(ctx -> ctx.put(key, "myValue"));
    
    StepVerifier.create(mono)
        .expectNext("Value stored in context: myValue")
        .verifyComplete();
}
```

### 8.3 Sinks
Rector also offers a possibility to create a Flux or a Mono by programmatically defining the onNext, onError, and onComplete events. 
To do this a so called sink API is exposed to trigger the events. Some different sink variants exist, to learn more about it read further in the reference documentation:
[Programmatically creating a sequence](https://projectreactor.io/docs/core/release/reference/#producing)


### 8.4 Debugging
Debugging reactive code could become a challenge because of its functional, declarative style where the actual declaration (or "assembly") and signal processing ("execution") do not happen at the same time.
The regular Java stack trace that is generated from a Reactor application will not include any references to the assembly code which makes it hard to identify what was the actual root cause of a propagated error.

To get a more meaningful stack trace, that includes the assembly information (also called a traceback), you can add a call to `Hooks.onOperatorDebug()` in your application.
This cannot be used in a production environment though, because it involves a heavy-weight stack walking and would have a negative impact on performance.

For use in production, Project Reactor provides a separate Java Agent that instruments your code and adds debugging info without paying the cost of capturing the stacktrace on every operator call.
To use it you need to add the `reactor-tools` artifact to your dependencies and initialize it at the startup of your Spring Boot application:
```java
public static void main(String[] args) {
    ReactorDebugAgent.init();
    SpringApplication.run(Application.class, args);
}
```
### 8.5 Metrics
Reactor provides built-in support to enable and expose metrics both for Schedulers and Publishers. For more details, take a look at the [Metrics](https://projectreactor.io/docs/core/release/reference/#metrics) section of the Reference guide.

## 9. To summarize...
This blog post provided an overview to Project Reactor, mainly focusing on Reactor Core features. The next blog post in this series will be about WebFlux - Spring's reactive web framework which uses Reactor as its reactive library!  

## References

[Project Reactor](https://projectreactor.io)

[Spring Web Reactive Framework](https://docs.spring.io/spring/docs/current/spring-framework-reference/web-reactive.html#webflux)

[Reactor Debugging Experience](https://spring.io/blog/2019/03/28/reactor-debugging-experience)

[Flight of the Flux 1 - Assembly vs Subscription](https://spring.io/blog/2019/03/06/flight-of-the-flux-1-assembly-vs-subscription)