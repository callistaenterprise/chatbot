---
categories: blogg teknik 
layout: "details-blog"
published: false
topstory: true
comments: true
authors: 
  - magnuslarsson
tags: Java spring-boot spring-cloud containers Docker Kubernetes service-mesh Istio
heading: Looking into part 1-3 of the hands-on book on developing microservices 
---

Y3 intro...

-[readmore]-	

## Part 1, building basic microservices using Spring Boot

This part is mainly about mainly about building cooperating microservices using Spring Boot and running them as containers using Docker Compose. It covers:

1. Create skeleton code for a microservice using Spring Initializr and its CLI tool `spring init`. A sample command to create skeleton code for a microservice named `product-service` looks like:

    ```
    spring init \
      --boot-version=2.1.0 \
      --build=gradle \
      --java-version=1.8 \
      --packaging=jar \
      --name=product-service \
      --package-name=se.magnus.microservices.core.product \
      --groupId=se.magnus.microservices.core.product \
      --dependencies=actuator,webflux \
      --version=1.0.0-SNAPSHOT \
        product-service
    ```

2. Making the microservices reactive by developing:
   1.  *non blocking* synchronous REST APIs with WebFlux and *non blocking* API clients using the reactive WebClient. and 
   2.  *event driven* asynchronous services using Spring Cloud Stream, together with both RabbitMQ and Kafka.

  This is illustrated by the following figure:

  ![reactive-1](/assets/blogg/build-microservices-part-9/ch7-0-overview.png)


3. Documenting the APIs based on Swagger using SpringFox:

![reactive-1](/assets/blogg/build-microservices-part-9/ch6-swagger.png)

4. Making the microservices storing its data persistent using Spring Data together with both a no SQL database, MongoDB, and a traditional relational database, MySQL.

<img src="/assets/blogg/build-microservices-part-9/ch6-layers.png" width="600">

5. Running the microservices as Docker containers using Docker COpose:

<img src="/assets/blogg/build-microservices-part-9/ch4.4-output-12.png" width="600">

Each area also covers how to write proper tests that cover unit testing, integration testing and end-to-end tests. The end-to-end tests verifies that the cooperating microservices not only works on their own but also together.

## Part 2, using Spring Cloud to make microservices scalable, resilient and manageable

This part of the book focus on how to use Spring Cloud to handle the challenges with a system landscape of cooperating microservices.

In the middle of writing this book Spring Cloud 2.1 was released, placing many of my favorite Netflix OSS components that Spring Cloud initially was based on in maintenance mode, i.e. Hystrix, Zuul and Ribbon. The book is based on the suggested replacements:

In January 2019 Spring Cloud 2.1 was released, placing many of my favorite Netflix OSS components that Spring Cloud initially was based on in maintenance mode, i.e. Hystrix, Zuul and Ribbon. 

Suggested replacements:

| Netflix OSS component       | Replacement                       |
| --------------------------- | --------------------------------- |
| Zuul                        | Spring Cloud Gateway              |
| Ribbon                      | Spring Cloud LoadBalancer         |
| Hystrix                     | Resilience4J                      |
| Hystrix Dashboard / Turbine	| Micrometer + Prometheus + Grafana | 

For details, see <https://spring.io/blog/2019/01/23/spring-cloud-greenwich-release-is-now-available>. 

The following areas of Spring Cloud are covered in this part of the book:

1. Using Netflix Eureka for service discovery

**TODO**...

![eureka-1](/assets/blogg/build-microservices-part-9/ch10-2-eureka.png)

1 Using Spring CLoud Gateway as an edge server

![gateway-1](/assets/blogg/build-microservices-part-9/ch10-1-edge.png)

1. Securing the APIs with OAuth and OIDC with Spring Security

    The chapter learn both how to:
      1. use a local authorization server for development and tests based on Spring Security:
      
          ![oidc-1](/assets/blogg/build-microservices-part-9/ch11-1-overview.png)

      2.  and also how to configure the microservices to use an OIDC provider, Auth0.

          <img src="/assets/blogg/build-microservices-part-9/ch11-7-auth0-implicit-login.png" width="400">

    **TODO**: The chapter also demonstrates how to use the various grant flows that Auth0 supports, both the common code grant and implicit grant flows but also the client credentials grant flow that is very useful when running automated tests for acquiring an access token without involving an end user

1. Using Spring Cloud Config server for centralized configuration

    ```
    spring.rabbitmq.password:
    '{cipher}17fcf0ae5b8c5cf87de6875b699be4a1746dd493a99d926c7a26a68c42
    2117ef'
    ```

1. Making the microservices resilient using 

    cb, timeout, retry, (overload bulkhead?

    <img src="/assets/blogg/build-microservices-part-9/ch8-7-circuit-breaker.png" width="300">


1. Using Spring Cloud SLeuth and Zipkin for distributed tracing

    An example based on both synchronous API calls and asynchronous sending of events:

![zipkin-1](/assets/blogg/build-microservices-part-9/ch14.3.delete-12345.2.png)

In the end of this chapter we have added many supporting services to the four microservices:

<img src="/assets/blogg/build-microservices-part-9/ch14.landscape.png" width="400">

We actually have more supporting services (5) then actual microservices (4). In the next part of the book this is handled...

Let's see how CO & SM can provide a platform for executing microservices where we don't need to package all the supporting services ourself!

## Part 3, adding a container orchestrator, Kubernetes, and a service mesh, Istio

Ths focus on this part of the book is how to run a set of cooperating ms in production where you typically need a cluster of servers that run Docker for both scalability and high availability reasons. To manage and monitor microservices running in containers on these server you need a container orchestrator. 

<img src="/assets/blogg/build-microservices-part-9/p1.2.7-pattern-controller-manager.png" width="400">

The most popular CO is K8S. 

![k8s-1](/assets/blogg/build-microservices-part-9/ch15.0.kubernetes-architecture-overview.png)

Recently the concept of a SM has been introduced providing improved capabilities for observability, security, routing et al. One of the most popular SM product is IStio. 


Istio comes bundled with:

* Kiali that brings observability to a new level
* Jaeger used for distributed tracing
* Prometheus for collecting and storing time series based metrics
* Grafana used for visualizing metrics and also for setting up alarms on these metrics

![istio-1](/assets/blogg/build-microservices-part-9/ch18.2.istio-components.png)

My favorites when all work together
Observability using Istio/Kiali


## k8s


kustomize, deploy to dev,test,qa and prod...

## SM & Istio 

**TODO**: Describe picture!!

![x](/assets/blogg/build-microservices-part-9/kiali-1.png)

Simplifies the deployment, less component to deploy, configure and run as containers...

Reduces the need for Gateway, Eureka, Config and Zipkin. Replaced by... + Cert Manager

| Spring Cloud component | Replacement when using Kubernetes & Istio |
| --------------- | ----------- |
| Spring Cloud Gateway | Kubernetes Ingress or Istio Ingress Gateway |
| Netflix Eureka | Kubernetes Service and kube-proxy |
| Spring Cloud Config Server | Kubernetes Config Maps and Secrets |
| Zipkin | Jaeger, bundled in Istio  |

Cert Manager is also described...

Distributed Tracing of sync/asynch processing using Jaeger similar to Zipkin...

![jaeger](/assets/blogg/build-microservices-part-9/ch18.30.kiali.6.png)

## Log analysis + tracing of related messages using EFK
Picture#3Picture#4

![x](/assets/blogg/build-microservices-part-9/ch19.40.kibana-1-piechart-2-annotated.png)
![x](/assets/blogg/build-microservices-part-9/ch19.40.kibana-3-root-cause-3.png)

## Monitoring & Alerts

e.g. on circuit breaker using Prometheus/Grafana

Istio Mesh Dashboard:

![istio mesh](/assets/blogg/build-microservices-part-9/ch20.8.siege-in-action-2.png)

JVM Dashboard

![JVM Dashboard](/assets/blogg/build-microservices-part-9/ch20.8.siege-in-action-1.png)

Dashboard for retries and CB:

![retry+cb](/assets/blogg/build-microservices-part-9/ch20.5.CB-in-action.png)

Alert Dashboard:

![alert](/assets/blogg/build-microservices-part-9/ch20.9.16.ok.png)

Alerts email:

<img src="/assets/blogg/build-microservices-part-9/ch20.9.16.alert-mail.png" width="400">

If you are interested, the book is available at [Packt web site](https://www.packtpub.com/web-development/hands-on-microservices-with-spring-boot-and-spring-cloud) but also on [Amazon](https://www.amazon.com/Hands-Microservices-Spring-Boot-Cloud-ebook/dp/B07T1Y2JRJ) and [Google Books](https://books.google.se/books?id=QFqxDwAAQBAJ&dq=Hands-On+Microservices+with+Spring+Boot+and+Spring+Cloud:+Build+and+deploy+Java+microservices+using+Spring+Cloud,+Istio,+and+Kubernetes&hl=sv&source=gbs_navlinks_s).

Happy Reading!



# Next up...

For more blog posts on new ..., see the blog series - [building microservices](/blogg/teknik/2015/05/20/blog-series-building-microservices/).

