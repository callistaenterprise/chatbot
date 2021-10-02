---
layout: details-blog
published: false
categories: blogg teknik
heading: C10k: Patterns for non-blocking services in the land of callback hell
authors:
  - magnuslarsson
tags: c10k java test nio nonblockingio rest scalability servlet
topstory: false
comments: true
---

## TEXT ALT #1

c10k: Patterns for non blocking services in the land of callback hell

In the previous blog we demonstrated the benifits, from a scalability perspective, of writing non blocking services compared to traditional blocking servcies. This is specifically important if the services has wait for responses from external resources (e.g. databases or other services) before it can send a response back to ist caller. Using standards such as the Servlet 3.1 specification and frameworks like Spring MVC makes the seource code both simple to write and test and maybe most important portable, i.e. not locked into a specific web server product.

We were also introduced to a new programming model that comes with the non-blocks approach, the callback model. Instead of just waiting in our code, blocking a precois thread, for the externa resoruce to respond we setup a callback method that will be called (in a separate thread) once the external resource is done. This way we don't need to block any thread dirig the wait for the responce of the external resource.

The callback model introduce a more complex programming model then the tradidional blocking model so this means that we have to be carefull avoiding writing code that bemoces wery costly to maintain over time.

In this blog we will look into three very common patterns were the non-blocking aproach have a great potential for imporoving scalability and we will compare different approaches for minimize the complexity introduced by the callback model.

...

## TEXT ALT #2

In the previous blog we described how to develop non-blocking REST services using Spring MVC and Spring Boot. In this blog we will look into consequences of programming model based on callbacks that is imposed by the asynchronous programming model.

Three common patterns that we will implement in a asynchronous way using non-blocking I/O:

1. Routing
2. Aggregation
3. Routing Slip

# Pattern for non-blocking routing

![](/assets/blogg/c10k-patterns-for-non-blocking-services-in-the-land-of-callback-hell/Router.png)

## RouterController.java
``` java
@RestController
public class RouterController {

    @RequestMapping("/route-non-blocking")
    public DeferredResult<String> nonBlockingRouter(...) {

        LOG.logStartNonBlocking();

        DeferredResult<String> deferredResult = new DeferredResult<String>();

        asyncHttpClient.prepareGet(SP_NON_BLOCKING_URL + "?minMs=" + minMs + "&maxMs=" + maxMs).execute(
            new RouterCallback(LOG, deferredResult));

        LOG.logLeaveThreadNonBlocking();

        // Return to let go of the precious thread we are holding on to...
        return deferredResult;
    }

```

## RouterCallback.java

``` java
public class RouterCallback extends AsyncCompletionHandler<Response> {

    private final LogHelper log;
    private DeferredResult<String> deferredResult;

    public RouterCallback(LogHelper log, DeferredResult<String> deferredResult) {
        this.log = log;
        this.deferredResult = deferredResult;
    }

    @Override
    public Response onCompleted(Response response) throws Exception{

        if (deferredResult.isSetOrExpired()) {
            log.logAlreadyExpiredNonBlocking();

        } else {
            boolean deferredStatus = deferredResult.setResult(response.getResponseBody());
            log.logEndNonBlocking(httpStatus, deferredStatus);
        }
        return response;
    }
```
# Pattern for non-blocking aggregation

![](/assets/blogg/c10k-patterns-for-non-blocking-services-in-the-land-of-callback-hell/Aggregator.png)

## AggregatorController.java

``` java
@RestController
public class AggregatorController {

    @RequestMapping("/aggregate-non-blocking")
    public DeferredResult<String> nonBlockingAggregator(...) {

        LOG.logStartNonBlocking();

        DeferredResult<String> deferredResult = new DeferredResult<String>();

        dbThreadPoolExecutor.execute(new DbLookupRunnable(id, deferredResult));

        LOG.logLeaveThreadNonBlocking();

        // Return to let go of the precious thread we are holding on to...
        return deferredResult;
    }
```

## DbLookupRunnable.java

``` java
public class DbLookupRunnable implements Runnable {

    @Override
	public void run() {
        //seconds later in another thread...
        calls = execute();
        AggregatorEventHandler aeh = new AggregatorEventHandler(calls, deferredResult);
        aeh.onStart();
	}
```

## AggregatorEventHandler.java

``` java
public class AggregatorEventHandler {

    public void onStart() {
        try {
	        LOG.logStartNonBlocking();

			for (int i = 0; i < noOfCalls; i++) {
                String url = ...;
                asyncHttpClient.prepareGet(url).execute(new AggregatorCallback(i, this));
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        // FIXME. ML. kickoff a timer as well + configuration...
    }

    public void onResult(int id, Response response) {

        try {

            // Count down, aggregate answer and return if all answers (also cancel timer)...
            int noOfRes = noOfResults.incrementAndGet();

            // Perform the aggregation...
            result += response.getResponseBody() + '\n';

            if (noOfRes >= noOfCalls) {
                onAllCompleted();
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void onAllCompleted() {

        if (deferredResult.isSetOrExpired()) {
            log.logAlreadyExpiredNonBlocking();

        } else {
            boolean deferredStatus = deferredResult.setResult(result);
            log.logEndNonBlocking(httpStatus, deferredStatus);
        }
    }
```

# Pattern for a non-blocking routing slip

![](/assets/blogg/c10k-patterns-for-non-blocking-services-in-the-land-of-callback-hell/RoutingSlip.png)

![](/assets/blogg/c10k-patterns-for-non-blocking-services-in-the-land-of-callback-hell/RoutingSlip-ClassDiagram.jpg)

## RoutingSlipController.java
``` java
@RestController
public class RoutingSlipController {

    @RequestMapping("/routing-slip-non-blocking")
    public DeferredResult<String> nonBlockingRoutingSlip() throws IOException {

        LOG.logStartNonBlocking();

        // Create a deferred result
        final DeferredResult<String> deferredResult = new DeferredResult<>();

        // Kick off the asynch processing of a number of sequentially executed asynch processing steps
        Iterator<Processor> processingSteps = configuration.getProcessingSteps(...);

        stateMachine.initProcessing(processingSteps, new DeferredResultStateMachineCallback(deferredResult));

        LOG.logLeaveThreadNonBlocking();

        // Return to let go of the precious thread we are holding on to...
        return deferredResult;
    }
```
