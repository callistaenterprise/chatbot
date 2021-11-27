---
categories: blogg teknik 
layout: "details-blog"
published: false
topstory: true
comments: true
heading: Building Microservices, part 5. Correlate log events in a distributed environment
authors: 
  - magnuslarsson
tags: microservices spring-cloud netflix-oss log correlation-id MDC
---

One of the trickiest problems in distributed systems (e.g. a system landscape of microservices) is to understand what is going on and even more important what is going wrong, where and why. In this blog post we will see how we can configure our microservices to use correlation-ids to identify log-events that are related to each other.

-[readmore]-

[comment]: # (Links)
[blog series]: https://callistaenterprise.se/blogg/teknik/2015/05/20/blog-series-building-microservices/
[Logstash]: https://www.elastic.co/products/logstash
[generating unique ids]: http://www.javapractices.com/topic/TopicAction.do?Id=56
[JavaDoc UUID.randomUUID]: http://docs.oracle.com/javase/8/docs/api/java/util/UUID.html#randomUUID--
[spring-cloud-sleuth]: http://cloud.spring.io/spring-cloud-sleuth/
[issue-39]: https://github.com/spring-cloud/spring-cloud-sleuth/issues/39
[spring-cloud]: http://projects.spring.io/spring-cloud/
[ThreadLocal]: http://docs.oracle.com/javase/8/docs/api/java/lang/ThreadLocal.html
[slf4j-MDC]: http://www.slf4j.org/manual.html#mdc
[ClientHttpRequestInterceptor]: https://docs.spring.io/spring/docs/current/javadoc-api/org/springframework/http/client/ClientHttpRequestInterceptor.html
[Servlet Filter]: http://www.oracle.com/technetwork/java/filters-137243.html
[RestTemplate]: https://docs.spring.io/spring/docs/current/javadoc-api/org/springframework/web/client/RestTemplate.html
[Netflix Hystrix]: https://github.com/Netflix/hystrix
[HystrixConcurrencyStrategy]: https://netflix.github.io/Hystrix/javadoc/com/netflix/hystrix/strategy/concurrency/HystrixConcurrencyStrategy.html

[comment]: # (Images)
[system landscape]: /assets/blogg/build-microservices-part-5/log-events.png
[implementation-1]: /assets/blogg/build-microservices-part-5/implementation-1.png
[implementation-2]: /assets/blogg/build-microservices-part-5/implementation-2.png

## Problem description

Let's start with recapturing our small microservice landscape from our [blog series]: 

![system landscape][system landscape]

As the picture illustrates each microservice write log information to a local file. 

> **OMFORMULERA:** Assume that we use some tooling like [Logstash] to collect the log files to a central place. Also assuming that there is a lot of concurrent activities going on in the system landscape it will be very hard to identify what log events that are related to each other, i.g. belonging to one and the same processing of a request like the one illustrated in the picture with the red line. 

> **LÄGG TILL**: Google spec och begrepp, http://research.google.com/pubs/pub36356.html

To be able to find related log events we need to mark them with a id that is unique for each processing flow of such a request. We call this id a ***correlation-id***.

## High level design
 
The logic for implementing a distributed correlation-id can look like:

**ASSUMING HTTP**


1. The first microservice in a processing flow that receives a new request (the Product API service in the picture) creates a unique id, and use it as its correlation id for every log message it writes during the processing of the request.  
 
    When the first microservice call other microservices (the Product Composite service in the picture) it adds the correlation-id to a HTTP header with a well known name.

2. All other microservices takes the id from the HTTP header mentioned above in the incoming requests and use it as its correlation-id, i.e. they use the correlation-id for logging and when calling other microservices in the same way as the first microservice did.

To simplify the logic a bit we can generalise the initial processing to:

* Look for the HTTP header in the incoming request. If found use it, otherwise create a unique id.

This means that we can provide one common implementation for handling correlation-id independent of whether the microservice happens to be the first in a processing flow or if it is called from another microservice that already has set the correlation-id in the HTTP request header.

## Implementation strategy

First (of course), let's look for an already existing implementation!

Since earlier this year it actually exists a [spring-cloud] project targeting our needs: [spring-cloud-sleuth]  
(I had to lookup the meaning of sleuth, it means a detective ;-)

[spring-cloud-sleuth] was recently released in v1.0, but has some shortcomings that prevents us from using it. Specifically, it lacks the capability of passing correlation ids through Hystrix, see: [issue #39][issue-39]. This is a capability that we unfortunately need for a fully working solution.

So, for the time being, we have to implement this our selfs :-(

But, as it turns out, is not that hard and can also be done in a fairly generic way almost transparent for developers of a microservice!

At a high level we need:

1. An interceptor for incoming requests, where we can pick up (from the incoming request) the correlation-id or if not found create a new one.

1. A place where we can store the correlation-id during the processing.

1. A mechanism for automatically adding the correlation-id to log events, making it transparent to the developer of a microservice how the correlation-id is added to the log event.

1. An interceptor for outgoing requests, where we can add a header in the outgoing request for the currently used correlation-id


## Implementation

To meet these requirements we can use:

1. A [Servlet Filter] to intercept incoming requests

1. A (pseudo) unique UUID created by the static method [UUID.randomUUID()][JavaDoc UUID.randomUUID]. For more advanced ways to create unique ids see [generating unique ids][generating unique ids].

1. [Slf4j MDC][slf4j-MDC] to store the correlation-id (in a [ThreadLocal] variable) and automatically write the correlation-id to log-events

1. A configuration for the log framwork used (LogBack in our case) that writes the correlation-id in the log-messages

1. A Spring [ClientHttpRequestInterceptor] to intercept outgoing request submitted using Spring [RestTemplate].

### This approach, however, has a flaw!

It assumes that all processing for a specific request within a microservice is performed within one and the same thread. That assumption is fine in cases where we only use blocking I/O for outgoing requests and in no other ways change thread during the processing of a request. 

Our code base is (for the time being) based on blocking I/O so that should not be a problem. 

But the circuit breaker, [Netflix Hystrix], use a thread-pool to be able to supervise the executution and optionally interrupt it due to detected problems, e.g. a timeout. So the request made by our composite service to the three core services are actually performed in a thread from a thread pool allocated by Hystrix.

**NOTE ON** not using thread pool in Hystrix, results in no timeout capability...

This means that the ThreadLocal variable, the MDC, is lost when Hystrix change thread for the processing of the request. If we loose the MDC we alos loose the correlation-id...

Fortunately this problem is relatively simple to fix. Using a [HystrixConcurrencyStrategy], Hystrix allow us to register a listener for when the thread switch happens and we can at that time transfer the MDC object to the allocated thread from the thread pool.

## In summary

To summerize the implementation:

1. A Servlet filter is used to handle incoming HTTP requests
1. The correlation id is stored in the Slf4j MDC (as a ThreadLocal variable)
1. LogBack is configured to always write the correlation id to log messages
1. The Hystrix Circuit Breaker is configured to transfer the MDC between threads used in the processing
1. An interceptor in RestTemplate sets the correlation id in outgoing HTTP requests

The first case with no correlation-id in the incoming request can be illustrated as:

![implementation-1][implementation-1]

The second case with a correlation-id in the incoming request can be illustrated as::

![implementation-2][implementation-2]

## Try it out

* build...
* run...
* observe...

## Source Code

### Frontend - the servlet filter

The servlet filter is setup in the `util` project and the class `se.callista.microservices.util.LogConfiguration` where we can find its declaration:

    @Bean
    public Filter logFilter() {
        LOG.debug("Declare my logFilter");
        return logFilter;
    }

The `logFilter` has the following parts of special interest (for its full source code see GitHub):

    private LambdaServletFilter logFilter = (ServletRequest req, ServletResponse resp, FilterChain chain) -> {

        ...

        if (corrId == null || corrId.length() == 0) {
            corrId = UUID.randomUUID().toString();
            LOG.debug("Initiate corrId to {}", corrId);
        }

        LOG.debug("Storing in MDC: {} = {} and {} = {}", mdc_key_corrId, corrId, mdc_key_component, componentName);
        MDC.put(mdc_key_corrId, corrId);
        MDC.put(mdc_key_component, componentName);

        ...

        try {
            chain.doFilter(req, resp);

        } finally {
            if (LOG.isDebugEnabled()) {
                LOG.debug("Remove from MDC: {} = {} and {} = {}",
                    mdc_key_corrId, MDC.get(mdc_key_corrId),
                    mdc_key_component, MDC.get(mdc_key_component));
            }
            MDC.remove(mdc_key_corrId);
            MDC.remove(mdc_key_component);

            ...
        }
    };

### LogBack configuration

All microservices now have a `logback.xml` - file in its folder `src/main/resource`. They all include a common configuration file found in `util/src/main/resources/defaultLogbackConfig.xml`. This file defines a common log format where the correlation id is taken from the MDC and is printed in each log message based on:

      <property name="LOG_PATTERN" value="%d{yyyy-MM-dd HH:mm:ss.SSS} %X{corrId} %X{component} %X{user} %-5p %t %c{1}:%L - %m%n"/>
    

### Circuit Breaker - Thread Switch

Two microservices use a Hystric Circuit Breaker, the `product-api-service` and the `product-composite-service`. The main-method in both services register a MDC-aware `HystrixConcurrencyStrategy` like:
 
    public static void main(String[] args) {
        ...
        HystrixPlugins.getInstance().registerConcurrencyStrategy(new MDCHystrixConcurrencyStrategy());
        ...
    }

The `MDCHystrixConcurrencyStrategy` - class is found in the util-project. Its only purpose is to register a wrapper class for calls to the Circuit Breaker:
    
    public class MDCHystrixConcurrencyStrategy extends HystrixConcurrencyStrategy {
        @Override
        public <T> Callable<T> wrapCallable(Callable<T> callable) {
            return new MDCHystrixContextCallable<>(callable);
        }
    }


Its the wrapper class `MDCHystrixContextCallable` that makes the heavy lifting by injecting the MDC in the thread allocated by Hystrix:

    public class MDCHystrixContextCallable<K> implements Callable {
        
        private final Callable<K> actual;
        private final Map parentMDC;
    
        public MDCHystrixContextCallable(Callable<K> actual) {
            this.actual = actual;
            this.parentMDC = MDC.getCopyOfContextMap();
        }
    
        @Override
        public K call() throws Exception {
            Map childMDC = MDC.getCopyOfContextMap();
    
            try {
                MDC.setContextMap(parentMDC);
                return actual.call();
            } finally {
                MDC.setContextMap(childMDC);
            }
        }
    }

The constructor is called by Hystrix in the parent thread before each processing and it copies the MDC. The call - method is called in the allocated thread and injects the parents MDC in the thread before it calls the actual implementation (that's why it's called a wrapper :-). 

To initialize the machinery we also need to init and shutdown the Hystrix context. We use a SErvlet filter to do that. In the `util` project and the class `se.callista.microservices.util.LogConfiguration` we can find:

    @Bean
    public Filter hystrixFilter() {
        return hystrixFilter;
    }

    private LambdaServletFilter hystrixFilter = (ServletRequest req, ServletResponse resp, FilterChain chain) -> {

        HystrixRequestContext ctx = HystrixRequestContext.initializeContext();
        try {
            chain.doFilter(req, resp);
        } finally {
            ctx.shutdown();
        }
    };

That completes the handling of passing the MDC between threads allocated by Hystix :-)

### Backend - The RestTemplate interceptor

In the `util` project and the class `se.callista.microservices.util.LogConfiguration` we can see how the RestTemplate is injected with a `logInterceptor`:

    @Bean
    public RestTemplate restTemplateWithLogInterceptor() {
        ...
        restTemplate.getInterceptors().add(logInterceptor);
        return restTemplate;
    }

The `logInterceptor` sets the correlation id header in the outgoing HTTP request as:

    private ClientHttpRequestInterceptor logInterceptor = (HttpRequest request, byte[] body, ClientHttpRequestExecution execution) -> {

        String corrId = MDC.get(mdc_key_corrId);
        LOG.debug("Add {} {} to HTTP header {}", mdc_key_corrId, corrId, http_header_corrId);
        HttpHeaders headers = request.getHeaders();
        headers.add(http_header_corrId, corrId);
        return execution.execute(request, body);
    };
    
# Wrap up the blog post with a reference to the upcoming blog post reagarding the ELK stack!