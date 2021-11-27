---
categories: blogg teknik
layout: "details-blog"
published: true
heading: ArchConf 2017 - a short summary of Spring Cloud Contract
authors: 
  - eriklupander
tags: restdocs cloudcontract archconf spring clearwater
topstory: true
comments: true

---

This is a brief summary of [Spring Cloud Contract](https://cloud.spring.io/spring-cloud-contract/) based on a presentation given at [ArchConf 2017](https://archconf.com/conference/clearwater/2017/12/home) in Clearwater Beach, Florida.

### Testing Microservices with Spring Cloud Contract

Given the premise that reliable integration testing of a microservices landscape can be a difficult and complex task, it may be preferable to write tests on a per-service basis and use frameworks such as [MockMVC](https://docs.spring.io/spring-security/site/docs/current/reference/html/test-mockmvc.html) to stub or mock calls to other microservices or external APIs. [Craig Walls](https://archconf.com/conference/clearwater/2017/12/speakers/craig_walls) from Pivotal held a talk on Spring Cloud Contract and how the framework may be beneficial for both consumers and the producer of an API. Even though the title used the ubiquitous "microservice" word, the technology and concepts should apply to HTTP APIs and testing those in general. 

![Craig Walls](/assets/blogg/archconf2017/el-craigwalls.jpg)
_Craig Walls from Pivotal held a number of Spring-related talks during the conference_

[Spring Cloud Contract](https://cloud.spring.io/spring-cloud-contract/) is an attempt from Spring to sort of "flip" the way one might typically declare and program stub behaviour by letting the _producer_ service be the one providing stubs for its API in the form of Maven artifacts. The formal name seems to be "Consumer-Driven-Contracts".

The premise of the producer-side of an API publishing stubs for its services isn't strictly unique, but usually one writes and defines mocks for external services in one's test code rather than pulling in a binary testability (e.g. stubs) dependency provided by the service producer providing both API correctness and hopefully covering most if not all possible outcomes for a given service. Spending time testing _your_ service instead of writing mocks for another service (be it internal or external) seems like a really great idea!

Anyway - from a more technical perspective the stubs and their behaviour is declared using a Groovy-based DSL. In principle:
 
    "given a request having these characteristics, respond with a response that looks like this." 
 
Nothing unique - it's a very common pattern seen from other frameworks and language such as [nock](https://github.com/node-nock/nock) from the world of NodeJS.

A simple example where we use an API to check whether a person should be allowed to buy beer given their age (US laws!):

    request {
        description("User is not old enough to buy beer")
        method 'POST'
        url '/check'
        body(age: value(consumer(regex('[0-1][0-9]'))))
        headers {
            header 'Content-Type', 'application/json'
        }
    }
    response {
        status 200
        body( "{"status": "NOT_OK"}")
        headers {
          header(
             'Content-Type', value(consumer('application/json'),producer(regex('application/json.*')))
          )
        }
    }

Pretty straightforward, right? Note the regular expression checking if the age is 0-19. In this case there will be no beer for the requestor. The maven plug-in will then compile and generate stub classes packaged into a .jar file that may be uploaded to a Maven repository (Nexus etc.).

In actual test code running JUnit or whatever, you write your tests as always and declare an _@AutoConfigureStubRunner_ annotation on the test class level, feeding it the maven unique identifier - with support for versioning wildcards. E.g:

    @RunWith(SpringRunner.class)
    @SpringBootTest
    @AutoConfigureStubRunner(ids = {"com.example:http-server:+:stubs:8080"})
    public class BeerApplicationServiceTests {

On a slightly higher level, there's definitely an interesting upside to this approach for API developers. When releasing a new version of your API - possbily with breaking changes - you could definitely consider simultaneously releasing a Spring Cloud Contracts stub jar file your consumer can plug directly into their unit/integration tests. Craig used Facebook as an example - Facebook has lots of APIs with lots of new releases, where changes in new versions are communicated using release notes. One can envision the benefit for consumers if Facebook said:

    "Hey guys, in three months version 6.0 of the adverts API will go live. Feel free to download "com.facebook:adverts-contracts:6.0" from maven central anytime you feel like starting work on using the new API. It's available today."
    
Of course the example is my personal interpretation and I have not idea whether there exists an "adverts API" of if Facebook uses that kind of informal communication, but I think you get the general idea I'm (as proxy from Craig) trying to convey. I'm sure an approach similar to this example would be useful for many devs out there.

On a personal level I find the reasoning behind Spring Cloud Contracts quite appealing and it is definitely something I will consider adopting in the future - either in my current project or in some future endeavour. 

It should be noted that while Spring Cloud Contracts on the framework level may seem to be somewhat bound to the JVM, Spring, MockMVC, RestAssuredMockMvc etc. and the Maven ecosystem (there's a [gradle plugin](https://github.com/spring-cloud/spring-cloud-contract/tree/master/spring-cloud-contract-tools/spring-cloud-contract-gradle-plugin) as well), there are possibilities to use the [stub runner](https://github.com/spring-cloud/spring-cloud-contract/tree/master/spring-cloud-contract-stub-runner) that may start a real server running the stubs using WireMock. I.e - you can deploy the stubs as a standalone service that your services can use in integration tests just as if they were real ones.

One can also generate java-based tests using EXPLICIT mode (see testMode [here](https://cloud.spring.io/spring-cloud-contract/multi/multi__spring_cloud_contract_verifier_setup.html#gradle-configuration-options)) (sounds pretty similar to [this feature](https://github.com/node-nock/nock#enabledisable-real-http-request) in nock) that will perform real HTTP calls which can be useful to let some of the services being called in a test be stubbed out while others are not.

I will however definitely consider applying the core concepts to my [Go-microservices](https://callistaenterprise.se/blogg/teknik/2017/02/17/go-blog-series-part1/) landscape. Given that dependencies in Go typically are handled by importing source code, it could be interesting to see if [gock](https://github.com/h2non/gock)-based HTTP mocks could be supplied from producer microservices as an importable artifact into the unit tests of consumer services.
