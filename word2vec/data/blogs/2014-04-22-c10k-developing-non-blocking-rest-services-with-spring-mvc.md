---
layout: details-blog
published: true
categories: blogg teknik
heading: "C10k: Developing non-blocking REST services with Spring MVC"
authors:
  - magnuslarsson
tags: c10k java, nio nonblockingio rest scalability servlet
topstory: true
comments: true
---

In this blog we will show you how to develop non-blocking REST services using [Spring MVC](http://docs.spring.io/spring/docs/current/spring-framework-reference/html/mvc.html). We will also demonstrate the vast difference in scalability that non-blocking services provide compared to traditional blocking services.

We will use [Spring Boot](/blogg/teknik/2014/04/15/a-first-look-at-spring-boot/) to create a web app for deployment in a [Servlet 3.0](https://jcp.org/aboutJava/communityprocess/final/jsr315/) compliant web-server and [Gradle](/blogg/teknik/2014/04/14/a-first-look-at-gradle/) to build and execute the web app. Finally we will use [Gatling](/blogg/teknik/2014/04/16/a-first-look-at-gatling-a-dsl-based-load-test-tool/) to load test the REST services.

-[readmore]-

But first some background on history and theory on the subject…

## Background
With an ever increasing number of connected devices, e.g. mobile devices and [Internet of Things](http://en.wikipedia.org/wiki/Internet_of_things), the requirement of handling large number of concurrent requests in the application servers becomes more critical in many projects.

The key technology for an application server to meet this requirement is the capability to handle requests in a non-blocking way, i.e. without allocating a thread to each request. This is equally important for both incoming and outgoing requests.

Non-blocking I/O has been supported by the Java platform since 2002 with Java SE v1.4 and its API’s called [New I/O (NIO)](http://en.wikipedia.org/wiki/New_I/O). It was initially hard to use, specifically with portability in mind. A number of Java based web servers and frameworks for HTTP, such as [Jetty](http://jetty.codehaus.org/jetty/) and [Netty](https://netty.io/), evolved to fill the gaps and today they provide a solid ground for non-blocking I/O, but with product specific API’s.

In December 2009 the [Servlet 3.0](https://jcp.org/aboutJava/communityprocess/final/jsr315/) specification was released as a part of [Java EE 6](https://jcp.org/aboutJava/communityprocess/final/jsr316/index.html). This was an important release in terms of standardization of how to perform non-blocking processing towards the underlying web servers and frameworks. With Servlet 3.0 a non-blocking application can be deployed on any web server that supports the specification, e.g. [GlassFish](https://glassfish.java.net/), [Tomcat](http://tomcat.apache.org/), [Jetty](http://jetty.codehaus.org/jetty/), [Resin](http://caucho.com/) or any of the commercial alternatives.

In December 2013 [Spring 4.0](https://spring.io/blog/2013/12/12/announcing-spring-framework-4-0-ga-release) was released with an unparalleled simplicity for developing non-blocking REST services using Spring MVC and deploying them on any Servlet 3.0 compliant web server using [Spring Boot](http://projects.spring.io/spring-boot/).

Before we jump into the code let’s look into, from an architectural perspective, how Spring MVC handles blocking and non-blocking REST services.

### Blocking and non-blocking REST services with Spring MVC
Developing a traditional blocking style REST service with Spring MVC is very straightforward:

Blocking REST service with Spring MVC

~~~ java
@RestController
public class ProcessingController {

  @RequestMapping("/process-blocking")
  public ProcessingStatus blockingProcessing(...) {
    ...
    return new ProcessingStatus(...);
  }
}
~~~

The code is compact and simple to understand since the annotations handles all the REST, JSON and XML machinery. The problem, from a scalability perspective, is that the request thread is locked during the processing of this method. If the method needs to make a long running call to an external resource, such as another REST or SOAP service or a database, the request thread will be blocked during the wait for the external resource to respond. The following picture illustrates this:

![](/assets/blogg/c10k-developing-non-blocking-rest-services-with-spring-mvc/Blocking-Request-Blocking-Resource.jpg)

To avoid the blocking of the request thread the programming model is changed to a callback model. The REST service doesn’t return the actual result to the Servlet container but instead an object, called a `DeferredResult`, that will receive the result at some time in the future. The result will be filled in by some other thread, typically using a callback-object. Spring MVC will hand over the result to the Servlet container that sends it back to the client. In the REST service we have to initiate this processing before we return the `DeferredResult` object to the Servlet container like:

Non-blocking REST service with Spring MVC

~~~ java
@RestController
public class ProcessingController {

  @RequestMapping("/process-non-blocking")
  public DeferredResult<ProcessingStatus> nonBlockingProcessing(...) {

    // Initiate the processing in another thread
    DeferredResult<ProcessingStatus> deferredResult = new DeferredResult<>();
    ProcessingTask task = new ProcessingTask(deferredResult, ...);
    dispatch(task);

    // Return to let go of the precious thread we are holding on to...
    return deferredResult;
  }
}
~~~

The callback object will be called some time in the future and it will then set the response in the `DeferredResult` object to complete the processing of the request:

Callback class for on-blocking REST service with Spring MVC

~~~ java
public class ProcessingTask extends SomeCallbackInterface {

  private DeferredResult<ProcessingStatus> deferredResult;

  public ProcessingTask(DeferredResult<ProcessingStatus> deferredResult, ...) {
    this.deferredResult = deferredResult;
    ...
  }

  @Override
  public void done() {
    if (deferredResult.isSetOrExpired()) {
      LOG.warn("Processing of non-blocking request already expired");
    } else {
      boolean deferredStatus = deferredResult.setResult(new ProcessingStatus(...));
    }
  }
}
~~~

…under the hood this maps up to the Servlet 3.0 specification with its corresponding support for Asynchronous Servlets.

Now a long running call to an external resource can take place without blocking the request thread.

Typically there are two scenarios to consider:

#### 1. The external resource API is also non-blocking.
This case it’ straight forward, we just have to ensure that the callback from the external resource API fills in the `DeferredResult` object on its completion. This will, as described above, notify the Servlet container of the completion of the request.

![](/assets/blogg/c10k-developing-non-blocking-rest-services-with-spring-mvc/Non-blocking-Request-Non-blocking-Resource.jpg)

#### 2. The external resource API is blocking.
For blocking API’s we need to allocate a thread for the blocking processing, typically coming from a Thread pool allocated for the specific external resource.

![](/assets/blogg/c10k-developing-non-blocking-rest-services-with-spring-mvc/Non-blocking-Request-Blocking-Resource.jpg)

**Note:** If we only perform calls to one and the same external resource using a blocking resource API in our REST Services we have actually more or less moved the problem one step back and not solved much of the scalability problem. In most cases however there is a mix of processing in the various REST services in a web server. Some don’t need access to resources at all, other can access resources using a non blocking API and some need to access resources using a blocking API. So overall the scalability will improve significantly if the blocking of threads can be moved back to the specific resource API’s that require blocking execution.

With this in mind let’s look at some real code!

## Walk through of the source code
The source code in this blog is based on the [blog](/blogg/teknik/2014/04/15/a-first-look-at-spring-boot/) regarding Spring Boot. We will only go through the parts of the code added specifically for this blog. Please read through the [Spring Boot blog](/blogg/teknik/2014/04/15/a-first-look-at-spring-boot/) for background information.

### Get the source code
If you want to check out the source code and test it on your own you need to have Java SE 7 and Git installed. Then perform:

~~~
$ git clone https://github.com/callistaenterprise/blog-non-blocking-rest-service-with-spring-mvc.git
$ cd blog-non-blocking-rest-service-with-spring-mvc/spring-mvc-asynch-teststub
$ git checkout -b my-branch-1.0 v1.0
$ tree
~~~

This should result in a tree structure like:

~~~
├── build.gradle
├── docs
│   └── …
├── gatling
│   └── spring-mvc-asynch-teststub-simulation.scala
├── gradle
│   └── …
├── gradlew
├── gradlew.bat
└── src
    └── main
        ├── java
        │   └── se
        │       └── callista
        │           └── springmvc
        │               └── asynch
        │                   └── teststub
        │                       ├── Application.java
        │                       ├── MyEmbeddedServletContainerCustomizer.java
        │                       ├── ProcessingController.java
        │                       ├── ProcessingStatus.java
        │                       └── ProcessingTask.java
        └── resources
            ├── application.properties
            └── logback.xml
~~~

### Spring MVC REST service – non-blocking style
In the [Spring Boot blog](/blogg/teknik/2014/04/15/a-first-look-at-spring-boot/) we developed a blocking REST service as a plain [Spring MVC Rest Controller](http://docs.spring.io/spring/docs/current/spring-framework-reference/html/mvc.html#mvc-ann-restcontroller). The service takes two query parameters, `minMs` and `maxMs`, that defines the boundaries of the processing time of the service. The blocking service simulates a response time between the given boundaries simply by calling `Thread.sleep()`. We will not go through the code in this blog but you can find it in the method `ProcessingController.blockingProcessing()`.

To simulate that our non-blocking REST service waits on an external resource we can’t use `Thread.sleep()` since it will block our request thread. Instead we use the Java SE Scheduler that we ask to invoke our callback object when the simulated waiting of the external resource is over.

First we create our `DeferredResult` that we use to initiate the callback object, task. Finally we schedule the task object for the calculated time-period:

Non-blocking REST Service

~~~ java
@RestController
public class ProcessingController {

  @RequestMapping("/process-non-blocking")
  public DeferredResult<ProcessingStatus> nonBlockingProcessing(
    @RequestParam(value = "minMs", required = false, defaultValue = "0") int minMs,
    @RequestParam(value = "maxMs", required = false, defaultValue = "0") int maxMs) {

    int processingTimeMs = calculateProcessingTime(minMs, maxMs);

    // Create the deferredResult and initiate a callback object, task, with it
    DeferredResult<ProcessingStatus> deferredResult = new DeferredResult<>();
    ProcessingTask task = new ProcessingTask(reqId, processingTimeMs, deferredResult);

    // Schedule the task for asynch completion in the future
    timer.schedule(task, processingTimeMs);

    // Return to let go of the precious thread we are holding on to...
    return deferredResult;
  }
}
~~~

When the time period has elapsed the `run()`-method in our task object will be invoked by the Java SE Scheduler and the task object will create a simulated answer from the external resource and set it on the `DeferredResult` object. This will cause the Servlet container to wake up and finalize the corresponding request by sending back the response we set on the `DeferredResult` object:

Callback for the non-blocking REST Service

~~~ java
public class ProcessingTask extends TimerTask {

  private static final Logger LOG = LoggerFactory.getLogger(ProcessingTask.class);
  private long reqId;
  private DeferredResult<ProcessingStatus> deferredResult;
  private int processingTimeMs;

  public ProcessingTask(long reqId, int processingTimeMs, DeferredResult<ProcessingStatus> deferredResult) {
    this.reqId = reqId;
    this.processingTimeMs = processingTimeMs;
    this.deferredResult = deferredResult;
  }

  @Override
  public void run() {
    if (deferredResult.isSetOrExpired()) {
      LOG.warn("Processing of non-blocking request #{} already expired", reqId);
    } else {
      boolean deferredStatus = deferredResult.setResult(new ProcessingStatus("Ok", processingTimeMs));
     LOG.debug("Processing of non-blocking request #{} done, deferredStatus = {}", reqId, deferredStatus);
    }
  }
}
~~~

Time for a test run before we start the heavy lifting!

A test run
Start the web app in an embedded Tomcat instance with the command:

~~~
./gradlew bootRun
~~~

Note: We are using Gradle as out build tool. If you want to know more about it, please read our [blog about Gradle](/blogg/teknik/2014/04/14/a-first-look-at-gradle/).

Now, try out the blocking REST service with a command like:

~~~
$ curl "http://localhost:9090/process-blocking?minMs=1000&maxMs=2000"

{"status":"Ok","processingTimeMs":1374}
~~~

Here we ask the blocking service to process our request and respond in between 1 and 2 secs. The response reports that the internal processing actually took 1374 ms.

Ok, lets try the non-blocking version as well:

~~~
$ curl "http://localhost:9090/process-non-blocking?minMs=1000&maxMs=2000"

{"status":"Ok","processingTimeMs":1506}
~~~

Not that exiting, it simply works in the same way (it will become a bit more exiting when we put it under some load however…)

Great, single requests works both for the blocking and the non-block service. Time to put the services under some pressure!

## Load test
We will use Gatling as our load test tool. If you want to know more about Gatling and how we performed the tests, please read our [Gatling blog](/blogg/teknik/2014/04/16/a-first-look-at-gatling-a-dsl-based-load-test-tool/).

As described in the blog, the blocking REST service is not very sustainable to increasing numbers of concurrent users. Even if we increase its request thread pool to very high values it hits the roof after a while and gets unresponsive. A load test for a blocking service typically looks like (copied from the blog):

![](/assets/blogg/c10k-developing-non-blocking-rest-services-with-spring-mvc/c10k-3-blocking-io-fails.png)

As you can see from the figure above we ramp up the number of concurrent users to 5000 (the **orange**{: style="color: #f9a743"} line). In the beginning the blocking REST service runs fine (the **green**{: style="color: #a5b33c"} line) but fairly soon the number of concurrent requests flatten out at 400 reqs/sec meaning that we are starting to build up a request queue inside the Servlet container. A short while later the delays caused by the request queue results in timeouts (the **red**{: style="color: #fb0219"} line) and the number of successful request falls down to below 50 reqs/sec.

If we look at the actual response times it actually looks even worse:

![](/assets/blogg/c10k-developing-non-blocking-rest-services-with-spring-mvc/c10k-3-blocking-io-fatal-response-times.png)

Initially the response times are as expected, between 1 – 2 secs but very soon they starts to raise (that’s when the thread pool runs out of available threads) and after a while most requests turns into red.

You can find a full Gatling report in the folder `spring-mvc-asynch-teststub/docs/blocking` together with a screen shot from JConsole demonstrating the constant use of 500 threads during the load test.

Not so impressive…

Over to the non-blocking REST service!

To make it a bit more challenging we lowered the maximum threads in the request pool to 50, a tenth of what the blocking REST service was allowed to consume.

The following picture says it all:

![](/assets/blogg/c10k-developing-non-blocking-rest-services-with-spring-mvc/c10k-3-non-blocking-io-scales-just-fine.png)

Not a glitch during the whole load test. After the ramp up period the non-blocking REST service handles some 1400 requests/sec without any problems!

If we look at the response times it gets even more impressive:

![](/assets/blogg/c10k-developing-non-blocking-rest-services-with-spring-mvc/c10k-3-non-blocking-response-times-rock-solid.png)

The response times is, except for a few small exceptions, within the configures response time 1-2 secs!

If you look into the full test report in `spring-mvc-asynch-teststub/docs/non-blocking` you will find that the 99th percentile is at 1990 ms.

So even if it only got a tenth of the resources (in terms of threads) it outperformed the blocking version when the load went up, exactly according to the theory!

## Summary
We have seen how elegantly and efficiently Spring MVC and Spring Boot can help us to develop highly scalable non-blocking REST services that can be deployed on any Servlet 3.0 compliant web server!

In the next blog we will focus on how external resources are used from non-blocking REST services, both using blocking API’s and non-blocking API’s. If external resources are used incorrectly we can easily loose the scalability capabilities that we just achieved from using Spring MVC and its support for non-blocking I/O. So this is a very important aspect. Stay tuned…
