---
categories: blogg teknik 
layout: "details-blog"
published: true
topstory: true
comments: true
heading: Blog Series - Building Microservices
authors: 
  - magnuslarsson
  - eriklupander
tags: microservices operations spring-cloud netflix-oss ELK
---

This blog series cover various aspects of building microservices using Java and Go with supporting services from [Spring Cloud](http://projects.spring.io/spring-cloud/), [Netflix OSS](http://netflix.github.io) and the [ELK-stack](https://www.elastic.co) (Elasticsearch, Logstash and Kibana). The series also cover how to deploy microservices in both the cloud and on premises using application platforms and infrastructures for [Docker](https://www.docker.com) containers, e.g. container orchestration tools.

-[readmore]-


## Introduction blog post

[An operations model for Microservices](/blogg/teknik/2015/03/25/an-operations-model-for-microservices/) - An introduction blog post that motivates why supporting services from *Spring Cloud* and *Netflix OSS* are required in a microservices based system landscape.

## Language specific blog posts

| Java  | Go  | 
|---|---|
| [Part 1: Using Netflix Eureka, Ribbon and Zuul](/blogg/teknik/2015/04/10/building-microservices-with-spring-cloud-and-netflix-oss-part-1/) |  [Part 1: Introduction and rationale for Go microservices](/blogg/teknik/2017/02/17/go-blog-series-part1/) |
| [Part 2: Trying out the circuit breaker, Netflix Hystrix ](/blogg/teknik/2015/04/15/building-microservices-with-spring-cloud-and-netflix-oss-part-2/) | [Part 2: Building our first Go microservice](/blogg/teknik/2017/02/21/go-blog-series-part2) |
| [Part 3: Secure API's with OAuth 2.0](/blogg/teknik/2015/04/27/building-microservices-part-3-secure-APIs-with-OAuth/) | [Part 3: Embedding a data store and serving JSON](/blogg/teknik/2017/02/27/go-blog-series-part3) |
| [Part 4: Dockerize your Microservices](/blogg/teknik/2015/06/08/building-microservices-part-4-dockerize-your-microservices/) | [Part 4: Unit testing HTTP services with GoConvey](/blogg/teknik/2017/03/03/go-blog-series-part4) |
| [Part 5: Upgrade to Spring Cloud 1.1 & Docker for Mac](/blogg/teknik/2016/09/30/building-microservices-part-5-springcloud11-docker4mac/) | [Part 5: Deploying on Docker Swarm](/blogg/teknik/2017/03/09/go-blog-series-part5) |
| [Part 6: Adding a Configuration Server](/blogg/teknik/2017/05/12/building-microservices-part-6-configuration-server/) | [Part 6: Adding health checks](/blogg/teknik/2017/03/22/go-blog-series-part6) |
| [Part 7: Distributed tracing with Zipkin and Spring Cloud Sleuth](/blogg/teknik/2017/07/29/building-microservices-part-7-distributed-tracing/) | [Part 7: Service Discovery & Load-balancing](/blogg/teknik/2017/04/24/go-blog-series-part7)
| [Part 8: Centralized logging with the ELK stack](/blogg/teknik/2017/09/13/building-microservices-part-8-logging-with-ELK/) | [Part 8: Centralized configuration using Spring Cloud config and Viper](/blogg/teknik/2017/05/15/go-blog-series-part8) |
|  | [Part 9: Messaging with AMQP](/blogg/teknik/2017/06/08/go-blog-series-part9) |
|  | [Part 10: Logging to a LaaS with Logrus and Docker's log drivers](/blogg/teknik/2017/08/02/go-blog-series-part10) |
|  | [Part 11: Circuit Breakers and resilience with Hystrix](/blogg/teknik/2017/09/11/go-blog-series-part11) |
|  | [Part 12: Distributed tracing with Zipkin](/blogg/teknik/2017/10/25/go-blog-series-part12/) |
|  | [Part 13: Distributed persistence with CockroachDB and GORM](https://callistaenterprise.se/blogg/teknik/2018/02/14/go-blog-series-part13) |
|  | [Part 14: GraphQL with Go](https://callistaenterprise.se/blogg/teknik/2018/05/07/go-blog-series-part14/) |
|  | [Part 15: Monitoring with Prometheus and Grafana](https://callistaenterprise.se/blogg/teknik/2018/09/12/go-blog-series-part15/) |
|  | [Part 16: It's 2019, time for a rewrite!](https://callistaenterprise.se/blogg/teknik/2019/07/29/go-blog-series-part16/) |

Stay tuned for more posts!

If you want to learn about new features in Docker, take a look at the blog series - [Trying out new features in Docker](/blogg/teknik/2017/12/17/blog-series-docker-news/).
