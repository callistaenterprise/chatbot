---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Go Microservices blog series, part 1.
authors: 
  - eriklupander
tags: go microservices docker swarm docker spring cloud netflix oss
topstory: true
comments: true

---

In this blog series we'll build Microservices using the [Go](https://golang.org/) programming language and piece by piece add the necessary integrations to make them run nicely on [Docker in swarm mode](https://www.docker.com/products/docker-swarm) within a [Spring Cloud / Netflix OSS](https://cloud.spring.io/spring-cloud-netflix/) landscape.

If you're unsure what a microservice is, I suggest reading Martin Fowler's [article](https://martinfowler.com/articles/microservices.html) about them. For more about the operations model for microservices, [this blog post](https://callistaenterprise.se/blogg/teknik/2015/03/25/an-operations-model-for-microservices/) from my colleague [Magnus](https://callistaenterprise.se/om/medarbetare/magnuslarsson/) explains the key concepts really well.
 
This blog series won't be a beginner's guide to coding in Go, though we will nevertheless write some code as we progress through the series and I'll explain some key Go concepts along the way. We'll be looking at a lot of code especially during the first parts where we'll cover basic functionality, unit testing and other core topics.

Part one will be an introduction to key concepts and the rationale for exploring the possibilities with Go-based microservices.

_Note: When referring to "Docker Swarm" in this blog series, I am referring to running Docker 1.12 or later in [swarm mode](https://docs.docker.com/engine/swarm/). "[Docker Swarm](https://docs.docker.com/swarm/)" as a standalone concept was discontinued with the release of Docker 1.12._

## Parts
- Part 1: Introduction and rationale for Go microservices (this part)
- [Part 2: Building our first Go microservice](/blogg/teknik/2017/02/21/go-blog-series-part2)
- [Part 3: Embedding a data store and serving JSON](/blogg/teknik/2017/02/27/go-blog-series-part3)
- [Part 4: Unit testing HTTP services with GoConvey](/blogg/teknik/2017/03/03/go-blog-series-part4)
- [Part 5: Deploying on Docker Swarm](/blogg/teknik/2017/03/09/go-blog-series-part5)
- [Part 6: Adding Health checks](/blogg/teknik/2017/03/22/go-blog-series-part6)
- [Part 7: Service Discovery & Load-balancing](/blogg/teknik/2017/04/24/go-blog-series-part7)
- [Part 8: Centralized configuration using Spring Cloud config and Viper](/blogg/teknik/2017/05/15/go-blog-series-part8)
- [Part 9: Messaging with AMQP](/blogg/teknik/2017/06/08/go-blog-series-part9)
- [Part 10: Logging to a LaaS with Logrus and Docker's log drivers](/blogg/teknik/2017/08/02/go-blog-series-part10)
- [Part 11: Circuit Breakers and resilience with Netflix Hystrix](/blogg/teknik/2017/09/11/go-blog-series-part11)
- [Part 12: Distributed tracing with Zipkin](/blogg/teknik/2017/10/25/go-blog-series-part12/)
- [Part 13: Distributed persistence with CockroachDB and GORM](https://callistaenterprise.se/blogg/teknik/2018/02/14/go-blog-series-part13)
- [Part 14: GraphQL with Go](https://callistaenterprise.se/blogg/teknik/2018/05/07/go-blog-series-part14/)
- [Part 15: Monitoring with Prometheus and Grafana](https://callistaenterprise.se/blogg/teknik/2018/09/12/go-blog-series-part15/)
- [Part 16: It's 2019, time for a rewrite!](https://callistaenterprise.se/blogg/teknik/2019/07/29/go-blog-series-part16/)
- _More to come..._

## Landscape overview
The image below provides an overall view of the system landscape we'll be building throughout this blog series. However, we'll start by writing our first Go microservice from scratch and then as we progress along the parts of the blog series, we'll get closer and closer to what the image below represents.

![landscape overview](/assets/blogg/goblog/part1-overview.png)
The legend is basically:

- The dashed white box: A logical Docker Swarm cluster, running on one or more nodes.
- Blue boxes: Supporting service from the Spring Cloud / Netflix OSS stack or some other service such as Zipkin.
- Sand-colored / white box: An actual microservice.

It's more or less the same landscape used in [Magnus Larssons microservices blog series](https://callistaenterprise.se/blogg/teknik/2015/05/20/blog-series-building-microservices/), with the main difference being that the actual microservices are implemented in Go instead of Java. The _quotes-service_ is the exception as it provides us with a JVM-based microservice we can use for comparison as well as a testbed for seamless integration with our Go-based services.

## The rationale - runtime footprint
Why would we want to write microservices in Go, one might ask? Besides being a quite fun and productive language to work with, the main rationale for building microservices in Go is the tiny memory footprint Go programs comes with. Let's take a look at the screenshot below where we are running several Go microservices as well as a Microservice based on [Spring Boot](https://projects.spring.io/spring-boot/) and Spring Cloud infrastructure on Docker Swarm:

![Memory footprint](/assets/blogg/goblog/part-1-stats.png)

The _quotes-service_ is the Sprint Boot one while the _compservice_ and _accountservice_ ones are Go-based. Both are basically HTTP servers with a lot of libraries deployed to handle integration with the Spring Cloud infrastructure.

Does this really matter in 2017? Arn't we deploying on servers these days with many gigabytes of RAM that easily fits an impressive number of let's say Java-based applications in memory? That's true - but a large enterprise isn't running tens of services - they could very well be running hundreds or even thousands of containerized (micro)services on a cloud provider. When running a huge amount of containers, being resource-efficient can save your company a lot of money over time. 

Let's take a look at Amazon EC2 pricing for general purpose on-demand instances (per 2017-02-15):

![pricing](/assets/blogg/goblog/part1-amazon-ec2.png)

Comparing the various t2 instances, we see that for a given CPU core count, doubling the amount of RAM (for example: 4 to 8 GB from t2.medium to t2.large) also _doubles_ the hourly rate. If you're not CPU-constrained, being able to fit twice the amount of microservices into a given instance could theoretically halve your cloud provider bill. As we'll see in later blog posts, even when under load our Go services use a _lot_ less RAM than an idling Spring Boot-based one.

## Non-functional requirements on a microservice
This blog series is not just about how to build a microservice using Go - it's just as much about having it behave nicely within a Spring Cloud environment and conform to the qualities a production-ready microservice landscape will require of it.
 
Consider (in no particular order):

- Centralized configuration
- Service Discovery
- Logging
- Distributed Tracing
- Circuit Breaking
- Load balancing
- Edge
- Monitoring
- Security

All of these are things I think you must take into account when deciding to go for a microservice architecture regardless if you're going to code it in Go, Java, js, python, C# or whatever's your liking. In this blog series I'll try to cover all these topics from the Go perspective.

Another perspective are things _within_ your actual microservice implementation. Regardless of where you're coming from, you probably have worked with libraries that provides things such as:

- HTTP / RPC / REST / SOAP / Whatever APIs
- Persistence APIs (DB clients, JDBC, O/R mappers)
- Messaging APIs (MQTT, AMQP, JMS)
- Testability (Unit / Integration / System / Acceptance)
- Build tools / CI / CD
- More...

I won't touch on all of these topics. If I would, I could just as well write a book instead of a blog series. I'll cover at least a few of them.

## Running on Docker Swarm

A basic premise of the system landscape of this blog series is that Docker Swarm will be our runtime environment which means all services - be it the supporting ones (config server, edge etc.) or our actual microservice implementations will be deployed as [Docker Swarm services](https://docs.docker.com/engine/swarm/how-swarm-mode-works/services/). When we're at the end of the blog series, the following Docker command:

    docker service ls
 
Will show us a list of all services deployed in the sample landscape, each having one replica.
   
![Service list](/assets/blogg/goblog/part1-swarm-services.png)    

Again - please note that the services listed above includes a lot more services than we'll have when we'll setup up our Swarm cluster in [Part 5](/blogg/teknik/2017/03/09/go-blog-series-part5) of the blog series.

## Performance

Ok - so Go microservices has a small memory footprint - but will they perform? Benchmarking programming languages against each other in a meaningful way can be quite difficult. That said, if one looks at a site such as [Benchmarkgame](https://benchmarksgame.alioth.debian.org/u64q/go.html) where people can submit implementations of explicit algorithms for a variety of languages and have them benchmarked against each other, Go is typically slightly faster than Java 8 with a few notable exceptions. Go in it's turn, is typically almost on par with C++ or - in the case of a few benchmarks - a lot slower. That said - Go typically performs just fine for typical "microservice" workloads - serving HTTP/RPC, serializing/deserializing data structures, handling network IO etc.

Another rather important attribute of Go is that it is a garbage collected language. After the major rewrite of the Garbage Collector for Go 1.5 GC pauses should typically be a few milliseconds at most. If you're coming from the world of JVMs (as I do myself), the Go garbage collector is perhaps not as mature but it does seem to be very reliable after changes introduced somewhere after Go 1.2 or so. It's also is a miracle of non-configurability - there is exactly _one_ knob ([GOGC](https://dave.cheney.net/2015/11/29/a-whirlwind-tour-of-gos-runtime-environment-variables)) you can tweak regarding GC behaviour in Go which controls the total size of the heap relative to the size of reachable objects.

However - keeping track of performance impact as we'll build our first microservice and then add things like circuit breakers, tracing, logging etc. to it can be very interesting so we'll use a [Gatling](http://gatling.io/) test in upcoming blog posts to see how performance develops as we add more and more functionality to the microservices.

## Boot time
Another nice characteristic of your typical Go application is that it starts _really_ fast. A simple HTTP server with a bit of routing, JSON serialization etc. typically starts in a few hundred milliseconds at the most. When we start running our Go microservices within Docker containers, we'll see them healthy and ready to serve in a few seconds at most, while our reference Spring Boot-based microservice typically needs at least 10 seconds until ready. Perhaps not the singularly most important characteristic, although it can certainly be beneficial when your environment needs to handle unexpected surges in traffic volumes by quickly scaling up. 

## Statically linked binaries

Another big upside with Go-based microservices in Docker containers is that we get a [statically linked](https://en.wikipedia.org/wiki/Static_library) binary with all dependencies in a single executable binary. While the file isn't very compact (typically 10-20 mb for a real microservice), the big upside is that we get really simple Dockerfiles and that we can use very bare base Docker images. I'm using a base image called [iron/base](https://hub.docker.com/r/iron/base/) that weighs in at just ~6 mb.

    FROM iron/base
    
    EXPOSE 6868
    ADD eventservice-linux-amd64 /
    ENTRYPOINT ["./eventservice-linux-amd64", "-profile=test"]

In other words - no JVM or other runtime component is required except for the standard C library (libc) which is included in the base image.

We'll go into more detail about how to build our binaries and that _-profile=test_ thing in later blog posts.

## Summary

In this blog post, we introduced some of the key reasons for building microservices using Go such as small memory footprint, good performance and the convenience of statically linked binaries.

In the [next part](/blogg/teknik/2017/02/21/go-blog-series-part2), we'll build our first Go-based microservice.
