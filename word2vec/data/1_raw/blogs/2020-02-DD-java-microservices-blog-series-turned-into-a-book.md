---
categories: blogg teknik 
layout: "details-blog"
published: false
topstory: true
comments: true
authors: 
  - magnuslarsson
tags: Java spring-boot spring-cloud containers Docker Kubernetes service-mesh Istio
heading: The blog series on Java based microservices turned into a book
---

**TODO: KORTARE MENINGAR**

Back in 2015-2017 I wrote a [blog series](https://callistaenterprise.se/blogg/teknik/2015/05/20/blog-series-building-microservices/) on how to develop and manage a landscape of cooperating Java based microservices using primarily Spring Boot, Spring Cloud and Docker. In 2018 I was contacted by [Packt Publishing](https://www.packtpub.com) and they asked me if I could write a hands-on book based on the  blog series but updated and expanded a bit, also covering Kubernetes and Istio.

In September 2019, the book was published. In this blog post I will go through briefly what you can learn by reading it.

-[readmore]-

The book cover looks like:

<a href="https://www.packtpub.com/web-development/hands-on-microservices-with-spring-boot-and-spring-cloud"><img src="/assets/blogg/build-microservices-part-9/front-cover.png" width="400"></a>

The book covers both how to develop microservices but most important how to handle the challenges that comes with cooperating microservices. The following picture summarize capabilities required to handle the challenges:

<img src="/assets/blogg/build-microservices-part-9/challenges-with-microservices.png" width="600">

**TODO: ADD A LINE PER CHALLENGE**

In a large scaled system landscape with microservice, it must be possible to:

1. Keep track of all running microservices and its instances using a ***Discovery Server***.
2. Secure and route public APIs to the corresponding miorservcies using an ***Edge Server***.
3. Centralize management of the configuration of the microservices using a ***Configuration Server***.
4. Collect, store and analyse log output from the microservices.
5. Continuously check the health of the microservice instances and automatically restart unhealthy microservices, e.g. microservices instances that has hanged or crashed.
6. Collect and visualize metrics for resource usage per microservice isntance.
7. Observe the traffic that flows through the microservices, either synchronously API requests or as asynchronous message passing.
8. Manage how traffic is routed between the microservices, e.g. to be able to perform a rolling upgrade and if required a rollback if the upgrade failed.
9. Trace distributed call chains through the microservice landscape to be able to identify root causes of errors and find performance bottlenecks.
10. Minimize the effect of temporary networks errors to prevent that unnecessary large parts of the system landscape is affected using resilience mechanisms, e.g. timeouts, retries and circuit breakers.

The book consists of three sections:

**TODO**: Markera verktyg med *italic* ed?

# Section 1, Spring Boot 
In this section you will learn how to use Spring Boot 2.1 to build microservices that:

1. communicates using either RESTful APIs over HTTP or by sending events using a message broker like RabbitMQ or Kafka. **TOGETHER WITH SPRING CLOUD STREAM???**
1. document their exposed APIs using SpringFox to create Swagger definitions.
1. store their data in a database using Spring Data, either in MongoDB or MySQL.
1. are reactive, i.e. synchronous communication over the API is done using non blocking I/O and event passing is done asynchronously. ...using the Reactor project, Spring WebFlux and Spring Cloud Stream.
1. run as containers using Docker and uses Docker Compose to bring up a system landscape of cooperating microservices.

# Section 2, Spring Cloud
In this section you will learn how to make a system landscape of cooperating microservices scalable, resilient and manageable using Spring Cloud, Greenwich release. It covers: **TODO: MER TEXT**

1. service discovery using Netflix Eureka
1. hiding private APIs and exposing public APIs using Spring Cloud Gateway 
1. protecting the public APIs using OAuth 2.0 and OpenID Connect
1. central management of microservices configuration using Spring Cloud Config Server
1. making the microservices resilient by using Resilience4J
1. distributed tracing using Spring Cloud Sleuth and Zipkin

# Section 3, Kubernetes and Istio
In this section you will learn how to use Kubernetes as a *container orchestrator* and and Istio as a *service mesh*. Together they provide an excellent platform for deploying microservices in production. This section covers:

1. deploying and running microservices in Kubernetes
1. using the features in Istio for improved security, observability, traffic management.
1. replacing many of the the Spring Cloud services with standard functionality in Kubernetes and Istio, simplifying the system landscape
1. using Prometheus and Grafana for monitoring and alerts
1. using the EFK stack (i.e. **E**lasticsearch, **F**luentd and **K**ibana) for centralized log analysis 

# How the tools work together...

These tools together covers the required capabilities mentioned above. This is illustrated by the following picture:

<img src="/assets/blogg/build-microservices-part-9/capability-mappings.png" width="600">

As we can see some tool overlaps for some capabilities. For example, both Spring Cloud, Kubernetes and IStio comes with tools that can act as an edge server, while service management only is covered by Kubernetes. The book also cover how to reason what tool to choose to these capabilities. 

**TODO** ADD TABLE HERE AND SOM EXPLANATION FROM THE PPT
<img src="/assets/blogg/build-microservices-part-9/overlaps.png" width="600">

selections...

<img src="/assets/blogg/build-microservices-part-9/overlaps-selections.png" width="600">



**TODO** Each chapter builds on the previous chapters and add a new technology... the sample code in the book is based on four cooperating microservices:

<img src="/assets/blogg/build-microservices-part-9/p1.1.7-sample-microservice-landscape.png" width="400">

In the end after adding features from Spring CLoud, Kubernetes and Istio we will have a system landscape tat looks like the following:

**TODO**: Bakgrundsfärg, add Spring Cloud Sleuth! Size?

<img src="/assets/blogg/build-microservices-part-9/cadec-2020-overview.png" width="600">
 
**TODO**: Lägg in mängdlärabild där valen syns + tabellen!

If you are interested, the book is available at [Packt web site](https://www.packtpub.com/web-development/hands-on-microservices-with-spring-boot-and-spring-cloud) but also on [Amazon](https://www.amazon.com/Hands-Microservices-Spring-Boot-Cloud-ebook/dp/B07T1Y2JRJ) and [Google Books](https://books.google.se/books?id=QFqxDwAAQBAJ&dq=Hands-On+Microservices+with+Spring+Boot+and+Spring+Cloud:+Build+and+deploy+Java+microservices+using+Spring+Cloud,+Istio,+and+Kubernetes&hl=sv&source=gbs_navlinks_s).

Happy Reading!

# Next up...

In the coming blog posts we will go through a bit more what we can learn from each section in the book!

For more blog posts on new ..., see the blog series - [building microservices](/blogg/teknik/2015/05/20/blog-series-building-microservices/).

