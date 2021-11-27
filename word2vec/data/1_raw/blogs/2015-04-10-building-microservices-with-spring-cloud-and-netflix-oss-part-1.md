---
categories: blogg teknik 
layout: "details-blog"
published: true
topstory: true
comments: true
heading: Building microservices with Spring Cloud and Netflix OSS, part 1

authors: 
  - magnuslarsson
tags: microservices operations spring-cloud netflix-oss eureka ribbon zuul
---

In the [previous blog post](/blogg/teknik/2015/03/25/an-operations-model-for-microservices/) we defined an operations model for usage of microservices. In this blog post we will start to look at how we can implement the model using [Spring Cloud](http://projects.spring.io/spring-cloud/) and [Netflix OSS](http://netflix.github.io). From the operations model we will cover the core parts: *service discovery*, *dynamic routing*, *load balancing* and to some extend an *edge server*, leaving the other parts to upcoming blog posts.

-[readmore]-

We will use some core components from Spring Cloud and Netflix OSS to allow separately deployed microservices to communicate with each other with no manual administration required, e.g. keeping track of what ports each microservice use or manual configuration of routing rules. To avoid problems with port conflicts, our microservices will dynamically allocate free ports from a port range at startup. To allow simple access to the microservices we will use an edge server that provides a well known entry point to the microservice landscape.

After a quick introduction of the Spring Cloud and Netflix OSS components we will present a system landscape that we will use throughout the blog series. We will go through how to access the source code and build it. We will also make a brief walkthrough of the source code pointing out the most important parts. Finally we wrap up by running through some test cases on how to access the services and also demonstrate how simple it is to bring up a new instance of a microservice and get the load balancer to start to use it, again without any manual configuration required.

## 1. Spring Cloud and Netflix OSS

Spring Cloud is a [new project](https://spring.io/blog/2015/03/04/spring-cloud-1-0-0-available-now) in the [spring.io family](http://spring.io/projects) with a set of components that can be used to implement our operations model. To a large extent Spring Cloud 1.0 is based on components from [Netflix OSS](http://netflix.github.io). Spring Cloud integrates the Netflix components in the Spring environment in a very nice way using auto configuration and convention over configuration similar to how [Spring Boot](/blogg/teknik/2014/04/15/a-first-look-at-spring-boot/) works. 

The table below maps the generic components in the [operations model]((/blogg/teknik/2015/03/25/an-operations-model-for-microservices/)) to the actual components that we will use throughout this blog series:

<img src="https://callistaenterprise.se/assets/blogg/build-microservices-part-1/mapping-table.png" width="500" />

In this blog post we will cover *Eureka*, *Ribbon* and to some extent *Zuul*:

* **Netflix Eureka** - Service Discovery Server
Netflix Eureka allows microservices to register themselves at runtime as they appear in the system landscape. 

* **Netflix Ribbon** - Dynamic Routing and Load Balancer
Netflix Ribbon can be used by service consumers to lookup services at runtime. Ribbon uses the information available in Eureka to locate appropriate service instances. If more than one instance is found, Ribbon will apply load balancing to spread the requests over the available instances. Ribbon does not run as a separate service but instead as an embedded component in each service consumer.

* **Netflix Zuul** - Edge Server
Zuul is (of course) our [gatekeeper](http://ghostbusters.wikia.com/wiki/Zuul) to the outside world, not allowing any unauthorized external requests pass through. Zulu also provides a well known entry point to the microservices in the system landscape. Using dynamically allocated ports is convenient to avoid port conflicts and to minimize administration but it makes it of course harder for any given service consumer. Zuul uses Ribbon to lookup available services and routes the external request to an appropriate service instance. In this blog post we will only use Zuul to provide a well known entry point, leaving the security aspects for coming blog posts. 

**Note:** The microservices that are allowed to be accessed externally through the edge server can be seen as an [API](http://www.programmableweb.com/apis/directory) to the system landscape.

## 2. A system landscape

To be able to test the components we need a system landscape to play with. For the scope of this blog post we have developed a landscape that looks like:

![system-landscape](/assets/blogg/build-microservices-part-1/system-landscape.png)

It contains four business services (*green boxes*):

* Three core services responsible for handling information regarding **products**, **recommendations** and **reviews**.  
* One composite service, **product-composite**, that can aggregate information from the three core services and compose a view of product information together with reviews and recommendations of a product.

To support the business services we use the following infrastructure services and components (*blue boxes*):

* **Service Discovery Server** (Netflix Eureka)

* **Dynamic Routing and Load Balancer** (Netflix Ribbon)

* **Edge Server** (Netflix Zuul)

> To emphasize the differences between microservices and monolithic applications we will run each service in a separate microservice, i.e. in separate processes. In a large scale system landscape it will most probably be inconvenient with this type of fine grained microservices. Instead, a number of related services will probably be grouped in one and the same microservice to keep the number of microservices at a manageable level. But still without falling back into huge monolithic applications...

## 3. Build from source

If you want to check out the source code and test it on your own you need to have Java SE 8 and Git installed. Then perform:

~~~
$ git clone https://github.com/callistaenterprise/blog-microservices.git
$ cd blog-microservices
$ git checkout -b B1 M1.1
~~~

This will result in the following structure of components:

![source-code](/assets/blogg/build-microservices-part-1/source-code.png)

Each component is built separately (remember that we no longer are building monolithic applications :-) so each component have their own build file. We use [Gradle](/blogg/teknik/2014/04/14/a-first-look-at-gradle/) as the build system, if you don't have Gradle installed the build file will download it for you. To simplify the process we have a small shell script that you can use to build the components:

~~~
$ ./build-all.sh
~~~

> If you are on **Windows** you can execute the corresponding bat-file `build-all.bat`!

It should result in six log messages that all says: 

~~~
BUILD SUCCESSFUL
~~~

## 4. Source code walkthrough

Let's take a quick look at some key source code construct. Each microservice is developed as standalone [Spring Boot](/blogg/teknik/2014/04/15/a-first-look-at-spring-boot/) application and uses [Undertow](http://undertow.io), a lightweight Servlet 3.1 container, as its web server. [Spring MVC](http://docs.spring.io/spring/docs/current/spring-framework-reference/html/mvc.html) is used to implement the REST based services and [Spring RestTemplate](https://spring.io/blog/2009/03/27/rest-in-spring-3-resttemplate) is used to perform outgoing calls. If you want to know more about these core technologies you can for example take a look at the following [blog post](/blogg/teknik/2014/04/22/c10k-developing-non-blocking-rest-services-with-spring-mvc/).

Instead let us focus on how to use the functionality in Spring Cloud and Netflix OSS!

**Note:** We have intentionally made the implementation as simple as possible to make the source code easy to grasp and understand.

### 4.1 Gradle dependencies

In the spirit of Spring Boot, Spring Cloud has defined a set of starter dependencies making it very easy to bring in the dependencies you need for a specific feature. To use Eureka and Ribbon in a microservice to register and/or call other services simply add the following to the build file:

~~~
    compile("org.springframework.cloud:spring-cloud-starter-eureka:1.0.0.RELEASE")
~~~

For a complete example see [product-service/build.gradle](https://github.com/callistaenterprise/blog-microservices/blob/B1/microservices/core/product-service/build.gradle).

To be able to setup an Eureka server add the following dependency:

~~~
    compile('org.springframework.cloud:spring-cloud-starter-eureka-server:1.0.0.RELEASE')
~~~

For a complete example see [discovery-server/build.gradle](https://github.com/callistaenterprise/blog-microservices/blob/B1/microservices/support/discovery-server/build.gradle).

### 4.2. Infrastructure servers

Setting up an infrastructure server based on Spring Cloud and Netflix OSS is really easy. E.g. for a Eureka server add the annotation `@EnableEurekaServer` to a standard Spring Boot application:

~~~ java
@SpringBootApplication
@EnableEurekaServer
public class EurekaApplication {

    public static void main(String[] args) {
        SpringApplication.run(EurekaApplication.class, args);
    }
}
~~~

For a complete example see [EurekaApplication.java](https://github.com/callistaenterprise/blog-microservices/blob/B1/microservices/support/discovery-server/src/main/java/se/callista/microservises/support/discovery/EurekaApplication.java).

To bring up a Zuul server you add a `@EnableZuulProxy` - annotation instead. For a complete example see [ZuulApplication.java](https://github.com/callistaenterprise/blog-microservices/blob/B1/microservices/support/edge-server/src/main/java/se/callista/microservises/support/edge/ZuulApplication.java).

With these simple annotations you get a default server configurations that gets yo started. When needed, the default configurations can be overridden with specific settings. One example of overriding the default configuration is where we have limited what services that the edge server is allowed to route calls to. By default Zuul set up a route to every service it can find in Eureka. With the following configuration in the `application.yml` - file we have limited the routes to only allow calls to the composite product service:

~~~yml
zuul:
  ignoredServices: "*"
  routes:
    productcomposite:
      path: /productcomposite/**
~~~

For a complete example see [edge-server/application.yml](https://github.com/callistaenterprise/blog-microservices/blob/B1/microservices/support/edge-server/src/main/resources/application.yml).

### 4.3 Business services

To auto register microservices with Eureka, add a `@EnableDiscoveryClient` - annotation to the Spring Boot application.

~~~java
@SpringBootApplication
@EnableDiscoveryClient
public class ProductServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(ProductServiceApplication.class, args);
    }
}
~~~

For a complete example see [ProductServiceApplication.java](https://github.com/callistaenterprise/blog-microservices/blob/B1/microservices/core/product-service/src/main/java/se/callista/microservises/core/product/ProductServiceApplication.java).

To lookup and call an instance of a microservice, use Ribbon and for example a Spring RestTemplate like:

~~~ java
    @Autowired
    private LoadBalancerClient loadBalancer;
    ...
    public ResponseEntity<List<Recommendation>> getReviews(int productId) {
    
            ServiceInstance instance = loadBalancer.choose("review");
            URI uri = instance.getUri();
		...
            response = restTemplate.getForEntity(url, String.class);
~~~

The service consumer only need to know about the name of the service (`review` in the example above), Ribbon (i.e. the `LoadBalancerClient` class) will find a service instance and return its URI to the service consumer.

For a complete example see [Util.java](https://github.com/callistaenterprise/blog-microservices/blob/B1/microservices/composite/product-composite-service/src/main/java/se/callista/microservices/composite/product/service/Util.java) and [ProductCompositeIntegration.java](https://github.com/callistaenterprise/blog-microservices/blob/B1/microservices/composite/product-composite-service/src/main/java/se/callista/microservices/composite/product/service/ProductCompositeIntegration.java).

## 5. Start up the system landscape

> In this blog post we will start the microservices as java processes in our local development environment. In followup blog posts we will describe how to deploy microservices to both cloud infrastructures and Docker containers!

To be able to run some of the commands used below you need to have the tools [cURL](http://curl.haxx.se) and [jq](http://stedolan.github.io/jq/) installed.

Each microservice is started using the command `./gradlew bootRun`.

First start the infrastructure microservices, e.g.:

~~~
$ cd .../blog-microservices/microservices

$ cd support/discovery-server;  ./gradlew bootRun
$ cd support/edge-server;       ./gradlew bootRun
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

In the service discovery web app we should now be able to see our four business services and the edge server ([http://localhost:8761](http://localhost:8761)):

![Eureka](/assets/blogg/build-microservices-part-1/eureka.png)

To find out more details about our services, e.g. what ip addresses and ports they use, we can use the Eureka REST API, e.g.:

~~~javascript
$ curl -s -H "Accept: application/json" http://localhost:8761/eureka/apps | jq '.applications.application[] | {service: .name, ip: .instance.ipAddr, port: .instance.port."$"}'
{
  "service": "PRODUCT",
  "ip": "192.168.0.116",
  "port": "59745"
}
{
  "service": "REVIEW",
  "ip": "192.168.0.116",
  "port": "59178"
}
{
  "service": "RECOMMENDATION",
  "ip": "192.168.0.116",
  "port": "48014"
}
{
  "service": "PRODUCTCOMPOSITE",
  "ip": "192.168.0.116",
  "port": "51658"
}
{
  "service": "EDGESERVER",
  "ip": "192.168.0.116",
  "port": "8765"
}
~~~

We are now ready to try some test cases, first some happy days tests to verify that we can reach our services and then we will se how we can bring up a new instance of a microservice and get Ribbon to load balance requests over multiple instances of that service.

**Note:** In coming blog posts we will also try failure scenarios to demonstrate how a circuit breaker works. 

### 5.1 Happy days

Start to call the composite service through the edge server, The edge server is found on the port 8765 (see its application.yml file) and as we have seen above we can use the path `/productcomposite/**` to reach the product-composite service through our edge server. The should return a composite response (shortened for brevity) like:

~~~javascript
$ curl -s localhost:8765/productcomposite/product/1 | jq .
{
    "name": "name",
    "productId": 1,
    "recommendations": [
        {
            "author": "Author 1",
            "rate": 1,
            "recommendationId": 1
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

...if we are on the inside of the microservice landscape we can actually call the services directly without going through the edge server. The problem is of course that we don't know on what ports the services runs on since they are allocated dynamically. But if we look at the output from the call to the eureka rest api we can find out what ports they listen to. To call the composite service and then the three core services we should be able to use the following commands (given the port information in the response from the call to the eureka rest api above)

~~~
$ curl -s localhost:51658/product/1 | jq .
$ curl -s localhost:59745/product/1 | jq .
$ curl -s localhost:59178/review?productId=1 | jq .
$ curl -s localhost:48014/recommendation?productId=1 | jq .
~~~

Try it out in your own environment!

### 5.2 Dynamic load balancing

To avoid service outage due to a failing service or temporary network problems it is very common to have more than one service instance of the same type running and using a load balancer to spread the incoming calls over the instances. Since we are using dynamic allocated ports and a service discovery server it is very easy to add a new instance. For example simply start a new review service and it will allocate a new port dynamically and register itself to the service discovery server. 

~~~
$ cd .../blog-microservices/microservices/core/review-service
$ ./gradlew bootRun
~~~

After a short while you can see the second instance in the service discovery web app ([http://localhost:8761](http://localhost:8761)):

![eureka](/assets/blogg/build-microservices-part-1/eureka-2-review-instances.png)

If you run the previous curl command (`curl -s localhost:8765/productcomposite/product/1 | jq .`) a couple of times and look into the logs of the two review instances you will see how the load balancer automatically spread in calls over the two instances without any manual configuration required:

![Hystrix](/assets/blogg/build-microservices-part-1/log-from-2-review.instances.png)
 
## 6. Summary

We have seen how Spring Cloud and Netflix OSS components can be used to simplify making separately deployed microservices to work together with no manual administration in terms of keeping track of what ports each microservice use or manual configuration of routing rules. When new instances are started they are automatically detected by the load balancer through the service discovery server and can start to receive requests. Using the edge server we can control what microservices that are exposed externally, establishing av API for the system landscape.

## 7. Next step

Ok, so happy days scenarios looks great! 

But a lot of questions remains unanswered, e.g.:

* What about something goes wrong, like a failing microservice? 
* How do we prevent unauthorized access to our API ()through the edge server)? 
* How do we get a good consolidated picture of what is going on in the microservice landscape, e.g. why isn't order #123456 delivered yet?

In upcoming blog posts in the [Blog Series - Building Microservices](/blogg/teknik/2015/05/20/blog-series-building-microservices/) we will look at how to increase resilience using a circuit breaker, use OAuth 2 to restrict external access. We will also look into how we can user the ELK stack to collect and present log entries from all the microservices in a centralized and consolidated way and more. 

Stay tuned!