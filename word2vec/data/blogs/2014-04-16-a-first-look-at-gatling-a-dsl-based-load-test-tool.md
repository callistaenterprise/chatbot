---
layout: details-blog
published: true
categories: blogg teknik
heading: A first look at Gatling, a DSL based load test tool
authors:
  - magnuslarsson
topstory: true
comments: true
---

Over the years I have been looking for an open source based load test tool that I feel comfortable with.

I've been using either low level Linux commands (that I never remember how to use the next time I need them) or I have been struggling with tools of which the graphical user interfaces are cumbersome to use and prevents me to see the big picture of my tests. I constantly have to look into a number of different dialogs to ensure that all pieces are setup correctly.

Recently, a colleague of mine demonstrated [Gatling](http://gatling-tool.org) on a conference and I realized that this is what I have been looking for!

-[readmore]-

Gatling, built using [Scala](http://www.scala-lang.org), defines a [DSL](http://en.wikipedia.org/wiki/Domain-specific_language) designed for expressing load tests in a compact and elegant way. The load test scrips are actually Scala code, so to really enjoy the benefits of Gatling you need some level of development skills, or at least not find source code discouraging :-).

In this blog I'll use Gatling to load test the REST service we developed in the [blog about Spring Boot](/blogg/teknik/2014/04/15/a-first-look-at-spring-boot/). But first we have to understand how to install it...

## Get the source code
As mentioned above we will be reusing the source code from this [blog](/blogg/teknik/2014/04/15/a-first-look-at-spring-boot/). Ensure that you have Java SE 7 and Git installed and then check out the code with the following commands:

~~~
$ git clone git@github.com:callistaenterprise/blog-a-first-look-at-spring-boot.git
$ cd blog-a-first-look-at-spring-boot/spring-boot-one
~~~

## Install Gatling
Gatling can be installed and configured by the following steps:

- Install Gatling by simply download [Gatling 1.5.3](http://goo.gl/2vCZbe) and unzip it to a folder that we call `$GATLING_HOME` for now.
- To configure Gatling you edit the configuration file `$GATLING_HOME/conf/gatling.conf`
	* For example set the parameter `requestTimeoutInMs` to 10000.

~~~
http {
  requestTimeoutInMs = 10000
~~~

If you are on a Linux or Unix system you will most likely hit the limit of the max number of open files that are allowed at the same time (one open TCP socket is seen as one open file in this context). This can be prevented by:

* In each command window where you start Gatling or the web app under test first run the command:

~~~
$ ulimit -n 20000
~~~

* If you are on OS X, you also need set the following parameters (only done once after starting the OS), e.g.:

~~~
$ sudo sysctl -w kern.maxfilesperproc=20000
$ sudo sysctl -w kern.maxfiles=40000
~~~

## Load test a REST service
To load test the REST service we need to:

* Build and start the web app
* Setup the load test
* Run the load test
* Increase the load a bit...

### Build and start the web app
The web app use Gradle as its build tool. Therefore the web app is built and started with the following command: (don't worry if you don't have Gradle already installed, the wrapper-script gradlew will automatically download and install it, read this blog for more info regarding Gradle)

~~~
$ ./gradlew bootRun
~~~

In the end it should result in something like:

~~~
2014-04-03 21:41:48 INFO  main o.s.b.c.e.t.TomcatEmbeddedServletContainer:139 - Tomcat started on port(s): 9090/http
2014-04-03 21:41:48 INFO  main s.c.w.s.a.t.Application:61 - Started Application in 2.755 seconds (JVM running for 3.55)
~~~

You can verify that the web app works with the following command:

~~~
$ curl "http://localhost:9090/process?minMs=1000&amp;maxMs=2000"
{"status":"Ok","processingTimeMs":1374}
~~~

### Setup the load test
Gatling use a Scala based DSL where the core element is a scenario and it can be defined like:

~~~ scala
val scn = scenario(scenarioName)
  .during(testTimeSecs) {
    exec(
      http(requestName)
        .get(URI)
        .headers(http_headers)
        .check(status.is(200))
      )
      .pause(minWaitMs, maxWaitMs)
  }
~~~

The scenario `scn` defines the following;

- A duration of the test
- A HTTP GET request
- HTTP headers to use in the request
- A check to verify that the response is as expected
- A pause interval between the requests

The scenario is launched using the `setUp` method like:

~~~ scala
setUp(scn.users(noOfUsers).ramp(rampUpTimeSecs).protocolConfig(httpConf))
~~~

Where we also define:

- The number of concurrent users in the test
- The ramp up time used to start up the users
- General configuration of the HTTP protocol
  (we use it to provide a base - URL for the URI's specified above)

For more detailed information of how you can set up a load test read the [Gatling Wiki](https://github.com/excilys/gatling/wiki).

For our test create a file called `spring-boot-one-simulation.scala` in the folder `$GATLING_HOME/user-files/simulations/basic` with the following content:

~~~ scala
package basic

import com.excilys.ebi.gatling.core.Predef._
import com.excilys.ebi.gatling.http.Predef._
import com.excilys.ebi.gatling.jdbc.Predef._
import com.excilys.ebi.gatling.http.Headers.Names._
import akka.util.duration._
import bootstrap._

class SpringBootOneSimulation extends Simulation {

  val rampUpTimeSecs = 20
  val testTimeSecs   = 60
  val noOfUsers      = 1000
  val minWaitMs      = 1000 milliseconds
  val maxWaitMs      = 3000 milliseconds

  val baseURL      = "http://localhost:9090"
  val baseName     = "spring-boot-one"
  val requestName  = baseName + "-request"
  val scenarioName = baseName + "-scenario"
  val URI          = "/process?minMs=500&maxMs=1000"

  val httpConf = httpConfig.baseURL(baseURL)

  val http_headers = Map(
    "Accept-Encoding" -> "gzip,deflate",
    "Content-Type" -> "text/json;charset=UTF-8",
    "Keep-Alive" -> "115")

  val scn = scenario(scenarioName)
    .during(testTimeSecs) {
      exec(
        http(requestName)
          .get(URI)
          .headers(http_headers)
          .check(status.is(200))
      )
      .pause(minWaitMs, maxWaitMs)
    }
  setUp(scn.users(noOfUsers).ramp(rampUpTimeSecs).protocolConfig(httpConf))
}
~~~

This setup will use a 20 second ramp up phase, then during one minute send requests from 1000 concurrent users. Each user will wait randomly one to three seconds between each request. The REST Service is asked to simulate a response time between 0.5 and 1 sec.

### Run the load test
If you want to you can start a JMX tool, such as JConsole, to monitor the resource usage of the web app.

Then give the following command in the folder $GATLING_HOME/bin to start the load test:

~~~
$ cd $GATLING_HOME/bin
$ ./gatling.sh -s "basic.SpringBootOneSimulation"
~~~

The test will print out a log like:

~~~
GATLING_HOME is set to /Users/magnus/Applications/gatling-charts-highcharts-1.5.3
Simulation basic.SpringBootOneSimulation started...
22:50:59.491 [INFO ] c.e.e.g.h.a.HttpRequestAction - Sending Request 'spring-boot-one-	request': Scenario 'spring-boot-one-scenario', UserId #1
22:50:59.526 [INFO ] c.e.e.g.h.a.HttpRequestAction - Sending Request 'spring-boot-one-	request': Scenario 'spring-boot-one-scenario', UserId #3
22:50:59.528 [INFO ] c.e.e.g.h.a.HttpRequestAction - Sending Request 'spring-boot-one-	request': Scenario 'spring-boot-one-scenario', UserId #2
.
.
.
================================================================================
2014-04-13 21:47:57                                                  83s elapsed
---- spring-boot-one-scenario --------------------------------------------------
Users  : [#################################################################]100%
          waiting:0     / running:0     / done:1000
---- Requests ------------------------------------------------------------------
> Global                                                     OK=22342  KO=0
> spring-boot-one-request                                    OK=22342  KO=0
================================================================================
~~~

A test report will be available in the folder `$GATLING_HOME/results`.

In the test report you can, for example, find graphs over the number of requests per second during the test:

![](/assets/blogg/a-first-look-at-gatling-a-dsl-based-load-test-tool/gatling-req-per-sec.png)

...and the response times during the test:

![](/assets/blogg/a-first-look-at-gatling-a-dsl-based-load-test-tool/gatling-response-time.png)

As you can see in the test reports the response times from the REST service are as expected, we asked it to respond in between 500 and 1000 ms. With 1000 users and some 350 reqs/sec it was not a problem to achieve.

That looks good but there is a problem, we are close to run into major problems. Since our REST service is implemented in a blocking style we will lock one thread per request. If we look at the JConsole output for this test we can see a potential problem ahead of us:

![](/assets/blogg/a-first-look-at-gatling-a-dsl-based-load-test-tool/gatling-jconsole.png)

We are steadily consuming over 300 threads in this test. Tomcat by default only allow us to use 200 threads (which is a lot in normal cases). If you look into the [Spring Boot blog](http://blog.callistaenterprise.se/2014/04/15/a-first-look-at-spring-boot/) from where we took the REST service implementation you can see that we have increased the max number of threads for Tomcat to 500. But this only works as a temporary solution. If we increase the load a bit more the test will crash and burn. So let's do that :-)

### Increase the load a bit...
Let's raise the number of concurrent users and simulate a slightly slower REST service (this will block the thread a longer time making the blocking issue worse). We will also run the test for a few more minutes. Change the load test script to the following values:

~~~
val rampUpTimeSecs = 60
val testTimeSecs   = 360
val noOfUsers      = 5000
val URI            = "/process?minMs=1000&maxMs=2000"
~~~

Rerun the test and you will very soon get an awful amount of timeout errors. The resulting test reports will report major problems (marked in **red**{: style="color: red"}) like:

![](/assets/blogg/a-first-look-at-gatling-a-dsl-based-load-test-tool/c10k-3-blocking-io-fails.png)

...and:

![](/assets/blogg/a-first-look-at-gatling-a-dsl-based-load-test-tool/c10k-3-blocking-io-fatal-response-times.png)

JConsole will reveal the issue:

![](/assets/blogg/a-first-look-at-gatling-a-dsl-based-load-test-tool/c10k-3-blocking-io-fails-JConsole.png)

The thread pool gets exhausted by the load (`MaxThreads = 500`) and a wait queue builds up until the 10 sec timeout is reached in the Gatling HTTP clients and errors are starting to be reported...

Theoretically we could continue to increase the thread pool but that is known for being both very costly and fragile so that is not the way to go!

Our Gating tests have clearly indicated that this REST service needs to be redesigned to be able to handle a large number of concurrent users.

Good for Gatling, not so good for our REST service :-)

## Summary
We have seen Gatling in action with its compact and elegant DSL where you can understand a load test script by just reading the script, without looking at the documentation first!

It also provides us with very useful test reports (we have seen a few of them in this blog) where we can see important characteristics of the test results such as requests/sec and response times.

We also used Gatling to point out a sever scalability issue with the REST service that we used in the test.

In an upcoming blog we will address this scalability issue by replacing the blocking design used in the REST service with a non-blocking design.

...and of cause use Gatling to prove that the non-blocking design provides an improved scalability!

Stay tuned...
