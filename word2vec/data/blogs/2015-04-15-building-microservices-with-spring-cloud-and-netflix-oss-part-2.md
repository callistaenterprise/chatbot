---
categories: blogg teknik 
layout: "details-blog"
published: true
topstory: true
comments: true
heading: Building microservices with Spring Cloud and Netflix OSS, part 2

authors: 
  - magnuslarsson
tags: microservices operations spring-cloud netflix-oss hystrix turbine
---

In [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/) we used core components in [Spring Cloud](http://projects.spring.io/spring-cloud/) and [Netflix OSS](http://netflix.github.io), i.e. *Eureka*, *Ribbon* and *Zuul*, to partially implement our [operations model](/blogg/teknik/2015/03/25/an-operations-model-for-microservices/), enabling separately deployed microservices to communicate with each other. In this blog post we will focus on fault handling in a microservice landscape, improving resilience using *Hystrix*, Netflix circuit breaker.

-[readmore]-

Now bad things will start to happen in the system landscape that we established in [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/). Some of the core services that the composite service depends on will suddenly not respond, jeopardizing the composite service if faults are not handled correctly. 

In general we call this type of problem a *chain of failures*, where an error in one component can cause errors to occur in other components that depend on the failing component. This needs special attention in a microservice based system landscape where, potentially a large number of, separately deployed microservices communicate with each other. One common solution to this problem is to apply a *circuit breaker* pattern, for details see the book [Release It!](https://pragprog.com/book/mnee/release-it) or read the blog post [Fowler - Circuit Breaker](http://martinfowler.com/bliki/CircuitBreaker.html). A *circuit breaker* typically applies state transitions like:

<img src="https://callistaenterprise.se/assets/blogg/build-microservices-part-2/circuit-breaker.png" width="600" />
(**Source:** [Release It!](https://pragprog.com/book/mnee/release-it))

Enter *Netflix Hystrix* and some powerful annotations provided by *Spring Cloud*!

## 1. Spring Cloud and Netflix OSS

From the table presented in [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/) we will cover: *Hystrix*, *Hystrix dashboard* and *Turbine*. 

<img src="https://callistaenterprise.se/assets/blogg/build-microservices-part-1/mapping-table.png" width="500" />

* **Netflix Hystrix** - Circuit breaker
Netflix Hystrix provides circuit breaker capabilities to a service consumer. If a service doesn't respond (e.g. due to a timeout or a communication error), Hystrix can redirect the call to an internal fallback method in the service consumer. If a service repeatedly fails to respond, Hystrix will open the circuit and fast fail (i.e. call the internal fallback method without trying to call the service) on every subsequent call until the service is available again. To determine wether the service is available again Hystrix allow some requests to try out the service even if the circuit is open. Hystrix executes embedded within its service consumer.

* **Netflix Hystrix dashboard and Netflix Turbine** - Monitor Dashboard
Hystrix dashboard can be used to provide a graphical overview of circuit breakers and Turbine can, based on information in Eureka, provide the dashboard with information from all circuit breakers in a system landscape. A sample screenshot from Hystrix dashboard and Turbine in action:

![Hystrix](/assets/blogg/build-microservices-part-2/hystrix-sample.png)

## 2. The system landscape

The system landscape from [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/) is complemented with supporting infrastructure servers for *Hystrix dashboard* and *Turbine*. The service *product-composite* is also enhanced with a *Hystrix* based circuit breaker. The two new components are marked with a red line in the updated picture below: 

![system-landscape](/assets/blogg/build-microservices-part-2/system-landscape.png)

> As in [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/), we emphasize the differences between microservices and monolithic applications by running each service in a separate microservice, i.e. in separate processes.

## 3. Build from source

As in [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/) we use Java SE 8, Git and Gradle. So, to access the source code and build it perform:

~~~
$ git clone https://github.com/callistaenterprise/blog-microservices.git
$ cd blog-microservices
$ git checkout -b B2 M2.1
$ ./build-all.sh
~~~

> If you are on **Windows** you can execute the corresponding bat-file `build-all.bat`!

Two new source code components have been added since [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/): *monitor-dashboard* and *turbine*:

![source-code](/assets/blogg/build-microservices-part-2/source-code.png)

The build should result in eight log messages that all says: 

~~~
BUILD SUCCESSFUL
~~~

## 4. Source code walkthrough

New from [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/) is the use of Hystrix as a circuit breaker in the microservice product-composite, so we will focus on the additional source code required to put the circuit breaker in place.

### 4.1 Gradle dependencies

We now have a couple of Hystrix-based starter dependencies to drag into our build files. Since Hysteric use [RabbitMQ](https://www.rabbitmq.com) to communicate between circuit breakers and dashboards we also need to setup dependencies for that as well. 

For a service consumer, that want to use Hystrix as a circuit breaker, we need to add:

~~~
    compile("org.springframework.cloud:spring-cloud-starter-hystrix:1.0.0.RELEASE")
    compile("org.springframework.cloud:spring-cloud-starter-bus-amqp:1.0.0.RELEASE")
    compile("org.springframework.cloud:spring-cloud-netflix-hystrix-amqp:1.0.0.RELEASE")
~~~

For a complete example see [product-composite-service/build.gradle](https://github.com/callistaenterprise/blog-microservices/blob/B2/microservices/composite/product-composite-service/build.gradle).

To be able to setup an Turbine server add the following dependency:

~~~
    compile('org.springframework.cloud:spring-cloud-starter-turbine-amqp:1.0.0.RELEASE')
~~~

For a complete example see [turbine/build.gradle](https://github.com/callistaenterprise/blog-microservices/blob/B2/microservices/support/turbine/build.gradle).

### 4.2. Infrastructure servers

Set up a Turbine server by adding the annotation `@EnableTurbineAmqp` to a standard Spring Boot application:

~~~
@SpringBootApplication
@EnableTurbineAmqp
@EnableDiscoveryClient
public class TurbineApplication {

    public static void main(String[] args) {
        SpringApplication.run(TurbineApplication.class, args);
    }

}
~~~

For a complete example see [TurbineApplication.java](https://github.com/callistaenterprise/blog-microservices/blob/B2/microservices/support/turbine/src/main/java/se/callista/microservises/support/turbine/TurbineApplication.java).

To setup a Hystrix Dashboard add the annotation `@EnableHystrixDashboard` instead. For a complete example see [HystrixDashboardApplication.java](https://github.com/callistaenterprise/blog-microservices/blob/B2/microservices/support/monitor-dashboard/src/main/java/se/callista/microservises/support/monitordashboard/HystrixDashboardApplication.java).

With these simple annotation you get a default server configuration that makes you get started. When needed, the default configurations can be overridden with specific settings.

### 4.3 Business services

To enable Hystrix, add a `@EnableCircuitBreaker`-annotation to your Spring Boot application. To actually put Hystrix in action, annotate the method that Hystrix shall monitor with `@HystrixCommand` where we also can specify a fallback-method, e.g.:

~~~
    @HystrixCommand(fallbackMethod = "defaultReviews")
    public ResponseEntity<List<Review>> getReviews(int productId) {
        ...
    }

    public ResponseEntity<List<Review>> defaultReviews(int productId) {
        ...
    }
~~~

The fallback method is used by Hystrix in case of an error (call to the service fails or a timeout occurs) or to fast fail if the circuit is open. For a complete example see [ProductCompositeIntegration.java](https://github.com/callistaenterprise/blog-microservices/blob/B2/microservices/composite/product-composite-service/src/main/java/se/callista/microservices/composite/product/service/ProductCompositeIntegration.java).

## 5. Start up the system landscape

> As in [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/), we will start the microservices as java processes in our local development environment and you need to have the [cURL](http://curl.haxx.se) and [jq](http://stedolan.github.io/jq/) tools installed to be able to run some of the commands below. 

As already mentioned, Hystrix use RabbitMQ for internal communication so we need to have it installed and running before we can start up our system landscape. Follow the instructions at [Downloading and Installing](https://www.rabbitmq.com/download.html). Then start RabbitMQ use the `rabbitmq-server` program in the `sbin`-folder of your installation.

~~~
$ ~/Applications/rabbitmq_server-3.4.3/sbin/rabbitmq-server

              RabbitMQ 3.4.3. Copyright (C) 2007-2014 GoPivotal, Inc.
  ##  ##      Licensed under the MPL.  See http://www.rabbitmq.com/
  ##  ##
  ##########  Logs: /Users/magnus/Applications/rabbitmq_server-3.4.3/sbin/../var/log/rabbitmq/rabbit@Magnus-MacBook-Pro.log
  ######  ##        /Users/magnus/Applications/rabbitmq_server-3.4.3/sbin/../var/log/rabbitmq/rabbit@Magnus-MacBook-Pro-sasl.log
  ##########
              Starting broker... completed with 6 plugins.
~~~

> If you are on **Windows** use Windows Services to ensure that the RabbitMQ service is started!

We are now ready to start up the system landscape. Each microservice is started using the command `./gradlew bootRun`.

First start the infrastructure microservices, e.g.:

~~~
$ cd support/discovery-server;  ./gradlew bootRun
$ cd support/edge-server;       ./gradlew bootRun
$ cd support/monitor-dashboard; ./gradlew bootRun
$ cd support/turbine;           ./gradlew bootRun
~~~

Once they are started up, launch the business microservices:

~~~
$ cd core/product-service;                ./gradlew bootRun
$ cd core/recommendation-service;         ./gradlew bootRun
$ cd core/review-service;                 ./gradlew bootRun
$ cd composite/product-composite-service; ./gradlew bootRun 
~~~

> If you are on **Windows** you can execute the corresponding bat-file `start-all.bat`!

Once the microservices are started up and registered with the service discovery server they should write the following in the log:

~~~
DiscoveryClient ... - registration status: 204
~~~

As in [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/), we should be able to see our four business services and the edge-server in the service discovery web app ([http://localhost:8761](http://localhost:8761)):

![Eureka](/assets/blogg/build-microservices-part-1/eureka.png)

Finally ensure that the circuit breakers are operational, e.g. *closed*. Try a call to the composite service through the edge-server as in [Part 1](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/) (shortened for brevity:

~~~javascript
$ curl -s localhost:8765/productcomposite/product/1 | jq .
{
    "name": "name",
    "productId": 1,
    "recommendations": [
        {
            "author": "Author 1",
            "rate": 1,
            "recommendationId": 0
        },
        ...
    ],
    "reviews": [
        {
            "author": "Author 1",
            "reviewId": 1,
            "subject": "Subject 1"
        },
        ...
    ],
    "weight": 123
}
~~~

Go to the url [http://localhost:7979](http://localhost:7979) in a web browser, enter the url [http://localhost:8989/turbine.stream](http://localhost:8989/turbine.stream) and click on the “*Monitor Stream*” – button):

![Hystrix](/assets/blogg/build-microservices-part-2/hystrix.png)

We can see that the composite service have three circuit breakers operational, one for each core service it depends on. They are all fine, i.e. *closed*. We are now ready to try out a negative test to see the circuit breaker in action!

## 6. Something goes wrong

Stop the `review` microservice and retry the command above:

~~~
$ curl -s localhost:8765/productcomposite/product/1 | jq .
{
    "name": "name",
    "productId": 1,
    "recommendations": [
        {
            "author": "Author 1",
            "rate": 1,
            "recommendationId": 0
        },
        ...
    ],
    "reviews": null,
    "weight": 123
}
~~~

The **review** - part of the response is now empty, but the rest of the reply remains intact! Look at the log of the `product-composite` services and you will find warnings:

~~~
2015-04-02 15:13:36.344  INFO 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : GetRecommendations...
2015-04-02 15:13:36.497  INFO 29901 --- [teIntegration-2] s.c.m.c.p.s.ProductCompositeIntegration  : GetReviews...
2015-04-02 15:13:36.498  WARN 29901 --- [teIntegration-2] s.c.m.composite.product.service.Util     : Failed to resolve serviceId 'review'. Fallback to URL 'http://localhost:8081/review'.
2015-04-02 15:13:36.500  WARN 29901 --- [teIntegration-2] s.c.m.c.p.s.ProductCompositeIntegration  : Using fallback method for review-service
~~~

I.e. the circuit breaker has detected a problem with the `review` service and routed the caller to the fallback method in the service consumer. In this case we simply return null but we could, for example, return data from a local cache to provide a best effort result when the `review` service is unavailable.

The circuit is still closed since the error is not that frequent:

![Hystrix](/assets/blogg/build-microservices-part-2/circuit-closed-on-minor-error.png)

Let's increase the error frequency over the limits where Hystrix will open the circuit and start to fast fail (we use Hystrix default values to keep the blog post short...). We use the [Apache HTTP server benchmarking tool](http://httpd.apache.org/docs/2.4/programs/ab.html) for this:

~~~
ab -n 30 -c 5 localhost:8765/productcomposite/product/1
~~~

Now the circuit will be opened:

![Hystrix](/assets/blogg/build-microservices-part-2/circuit-open-on-major-error.png)

...and subsequent calls will fast fail, i.e. the circuit breaker will redirect the caller directly to its fallback method without trying to get the reviews from the `review` service. The log will no longer contain a message that says `GetReviews...`: 

~~~
2015-04-02 15:14:03.930  INFO 29901 --- [teIntegration-5] s.c.m.c.p.s.ProductCompositeIntegration  : GetRecommendations...
2015-04-02 15:14:03.984  WARN 29901 --- [ XNIO-2 task-62] s.c.m.c.p.s.ProductCompositeIntegration  : Using fallback method for review-service
~~~

However, from time to time it will let some calls pass through to see if they succeeds, i.e. to see if the `review` service is available again. We can see that by repeating the curl call a number of times and look in the log of the `product-composite` service:

~~~
2015-04-02 15:17:33.587  INFO 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : GetRecommendations...
2015-04-02 15:17:33.769  INFO 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : GetReviews...
2015-04-02 15:17:33.769  WARN 29901 --- [eIntegration-10] s.c.m.composite.product.service.Util     : Failed to resolve serviceId 'review'. Fallback to URL 'http://localhost:8081/review'.
2015-04-02 15:17:33.770  WARN 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : Using fallback method for review-service
2015-04-02 15:17:34.431  INFO 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : GetRecommendations...
2015-04-02 15:17:34.569  WARN 29901 --- [ XNIO-2 task-18] s.c.m.c.p.s.ProductCompositeIntegration  : Using fallback method for review-service
2015-04-02 15:17:35.209  INFO 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : GetRecommendations...
2015-04-02 15:17:35.402  WARN 29901 --- [ XNIO-2 task-20] s.c.m.c.p.s.ProductCompositeIntegration  : Using fallback method for review-service
2015-04-02 15:17:36.043  INFO 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : GetRecommendations...
2015-04-02 15:17:36.192  WARN 29901 --- [ XNIO-2 task-21] s.c.m.c.p.s.ProductCompositeIntegration  : Using fallback method for review-service
2015-04-02 15:17:36.874  INFO 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : GetRecommendations...
2015-04-02 15:17:37.031  WARN 29901 --- [ XNIO-2 task-22] s.c.m.c.p.s.ProductCompositeIntegration  : Using fallback method for review-service
2015-04-02 15:17:41.148  INFO 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : GetRecommendations...
2015-04-02 15:17:41.340  INFO 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : GetReviews...
2015-04-02 15:17:41.340  WARN 29901 --- [eIntegration-10] s.c.m.composite.product.service.Util     : Failed to resolve serviceId 'review'. Fallback to URL 'http://localhost:8081/review'.
2015-04-02 15:17:41.341  WARN 29901 --- [eIntegration-10] s.c.m.c.p.s.ProductCompositeIntegration  : Using fallback method for review-service
~~~

As we can see from the log output, every fifth call is allowed to try to call the `review` service (still without success...).

Let's start the `review` service again and try calling the composite service!

**Note:** You might need to be a bit patient here (max 1 min), both the service discovery server (Eureka) and the dynamic router (Ribbon) must be made aware of that a `review` service instance is available again before the call succeeds.

Now we can see that the response is ok, i.e. the review part is back in the response, and the circuit is closed again:

![Hystrix](/assets/blogg/build-microservices-part-2/circuit-closed-again.png)
 
## 7. Summary

We have seen how *Netflix Hystrix* can be used as a *circuit breaker* to efficiently handle the problem with *chain of failures*, i.e. where a failing microservice potentially can cause a system outage of a large part of a microservice landscape due to propagating errors. Thanks to the annotations and starter dependencies available in Spring Cloud it is very easy to get started with Hystrix in a Spring environment. Finally the dashboard capabilities provided by Hystrix dashboard and Turbine makes it possible to monitor a large number of circuit breakers in a system landscape.

## 8. Next step

In the next blog post in the [Blog Series - Building Microservices](/blogg/teknik/2015/05/20/blog-series-building-microservices/) we will look at how to use OAuth 2.0 to restrict access to microservices that expose an external API.

Stay tuned!