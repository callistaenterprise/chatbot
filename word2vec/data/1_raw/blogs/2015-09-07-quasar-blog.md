---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Dawn of the thread
authors:
  - torbjornclaesson
tags: ""
topstory: true
comments: true
---

### Quasar
Create highly concurrent software that is very easy to write and reason about.
-[readmore]-

### TL;DR

I have spent some time using Google’s Go language, so I was thrilled when I stumbled upon Parallel Universe’s [Quasar](http://www.paralleluniverse.co/quasar/) framework. If you have been using Go then you are quite familiar with its Channels and go-routines.

Well, now it’s seems like we can use the same way of writing our software on the JVM with Quasar fibers and channels.


To make things somewhat more clear an explanation might be in order.
Depending on what language background you have this is most likely nothing new to you, but you might be used to other names for these features. As mentioned earlier Go has named these features Channels and Go-rutines. In Erlang you spawn processes, I could continue listing other implementations since it’s seems like every language has their own implementation, heck there is even a couple of other implementations for Java then Quasar Fibers.
I guess I have to mention Haskell threads and sparks not to get my inbox filled with angry Haskellers emails.

So what is a Fiber or any other implementation of the same functionality?
Well if you were old enough to us Java 1.1 then you have already seen them on the JVM under the name Green threads, but was later removed due to various reasons.
A Fiber or lightweight-thread (throwing in another name, for the sake of confusion) is a M:N (hybrid threading) thread mapping, meaning that its maps a M number of application threads onto N number of threads in the operating system.
While Java today uses 1:1 mapping meaning that an application-level thread maps to one os thread. And that’s one of the reasons we see non-blocking programing becoming yet again more and more popular since in todays Java, blocking a thread on application-level actual means blocking resources on os level which is quite resource consuming.

I thought about writing something on how the Quasar Framework achieves these lightweight-threads. But if you are anything like me you will just scroll past all this text in search for a block of code. If you should be interested in how they do the short answer is that they implement continuations using bytecode instrumentation and using a separate stack to hold state. The long answer you can get from [Ron Presslers presentation at JVMLS](http://www.paralleluniverse.co/quasar/).

So now we got some idea what a Fiber is, but what problem do they solve?

#### Concurrency!

Using the multithreaded approach that’s been the de facto standard for some years now have some problems when it comes to handling concurrency. To be clear I’m talking about Java, so Node folks no need to flame.
It’s not uncommon that we see thread-pool starvation and high memory consumption due to “one-request-one-thread” mapping.  
One way of solving these issues is using non-blocking techniques like callbacks and monads. The problem with these techniques is not that they don’t work, but they can be quite hard to understand and debug if you as most of us are used to the old way of understanding what will happen when by just looking at the code.
Quasar fibers gives you a programming model that you already are familiar with but does not hog all your os resources.


If you are more interested in reading about non-blocking techniques and reactive frameworks I truly recommend my colleges great [presentation](https://callistaenterprise.se/blogg/presentationer/2015/01/28/reactive/) and [blog post](https://callistaenterprise.se/blogg/teknik/2014/04/22/c10k-developing-non-blocking-rest-services-with-spring-mvc/).


### API-Gateway

To demonstrate how we can use fibers in a real life situation we are going to build ourselves a simple API-Gateway, a well now pattern for fronting for example [microservices](https://callistaenterprise.se/blogg/teknik/2015/05/20/blog-series-building-microservices/).
The idea is that one request leads to multiple internal API calls and we have a gateway facing the user to be able to customize the outer API to fit the need.
For example we might want to keep down the amount of API calls for mobile users to lower the round trips by mashing multiple internal responses to one external. It also gives us the possibility to provide a more fine-grained API to lower the cost of bandwidth.

![API-Gateway](/assets/blogg/apigateway.png)

We will deploy our gateway on Tomcat 8.



First of we need to modify which class loader Tomcat should use for loading our webapp.  
Easiest way to do that is to download **comsat-tomcat-loader.jar** and drop it into you shared lib folder. Then update your **META-INF/context.xml** like.

~~~ xml
<Loader loaderClass="co.paralleluniverse.comsat.tomcat.QuasarWebAppClassLoader"/>
~~~

To get started here is the content of my build.gradle file.

~~~ java
apply plugin: 'java'
apply plugin: 'war'

repositories {
    mavenCentral()
}

dependencies {
    compile 'org.slf4j:slf4j-api:1.7.5'

    compile 'co.paralleluniverse:quasar-core:0.7.2:jdk8'
    compile 'co.paralleluniverse:comsat-httpclient:0.4.0'
    compile 'co.paralleluniverse:comsat-jersey-server:0.4.0'

    compile 'javax.ws.rs:javax.ws.rs-api:2.0.1'

    compile 'com.fasterxml.jackson.jr:jackson-jr-objects:2.6.1'

    providedCompile 'org.apache.tomcat:tomcat-servlet-api:8.0.23'
}
~~~

As you see there is something called comsat that keeps showing up, Comsat is an open-source set of libraries that integrates with Quasar. The reason for using these are because if we would do an actual thread blocking operation inside a fiber it would actually block the underlying os thread, thus it would be pointless to run it in a fiber instead of an actual thread.

We will be using Jersey to define our REST-Services and for that we will use the comsat-jersey-server to make our services fiber aware.  
**WEB-INF/web.xml**

~~~ xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_3_0.xsd"
         version="3.0"
         metadata-complete="false">
    <display-name>Dawn of the thread</display-name>
    <servlet>
        <display-name>fiber</display-name>
        <servlet-name>fiber</servlet-name>
        <servlet-class>co.paralleluniverse.fibers.jersey.ServletContainer</servlet-class>
        <async-supported>true</async-supported>
        <init-param>
            <param-name>javax.ws.rs.Application</param-name>
            <param-value>se.callistaenterprise.RestApplication</param-value>
        </init-param>
        <init-param>
            <param-name>jersey.config.server.provider.packages</param-name>
            <param-value>se.callistaenterprise.c</param-value>
        </init-param>
        <load-on-startup>1</load-on-startup>
    </servlet>
    <servlet-mapping>
        <servlet-name>fiber</servlet-name>
        <url-pattern>/api/*</url-pattern>
    </servlet-mapping>
</web-app>
~~~

So now everything is setup and it’s time for us to write our first REST service.

~~~ java
@Path("mobile")
@Singleton
public class MobileServicesImpl {

   private static final int MAX_ROUTE = 10000;
   private static final int MAX_CONN = 10000;

   private final HttpClient client =
           FiberHttpClientBuilder.create(2)
                   .setMaxConnPerRoute(MAX_ROUTE).setMaxConnTotal(MAX_CONN).build();

   private final ArrayList<Endpoints> endpoints = new ArrayList<>();

   @PostConstruct
   protected void init() {
      // Long list of internal endpoints
      endpoints.add(..)
   }

   @GET
   @Path("frontpage")
   @Produces(MediaType.APPLICATION_JSON)
   @Suspendable
   public JsonElement getFrontpage() throws IOException, InterruptedException, SuspendExecution {
      final JsonObject obj = new JsonObject();
      endpoints.forEach(e -> {
          try {
              final String resp = EntityUtils.
                toString(client.execute(new HttpGet(e)).getEntity());
                //Apply logic and add to response object
          } catch (IOException err) {
              //Handle error
          }
      });
      return obj;
   }
 }
~~~

This might be the naïve first approach to creating a gateway.
We have a list of some endpoints that we iterate over and sum up the response that’s then returned.
If we were to run this service in a default servlet container each user of this service would hold one os thread for as long as it took to get the response from all the endpoints in our list.
But we have configured to use the comsat servlet container. Which instead of fetching a thread from the pool for each user, spawns a new fiber. I have annotated get function with `@Suspendable` which is one way of telling Quasar what method to instrument.

If you have a keen eye you would see that I initiate the Apache HttpClient with the **FiberHttpClientBuilder** provided by the comsat Apache HttpClient library. This is because as I mentioned earlier that if we were to do a blocking IO operation as **HttpClient.execute** does we would block the underlying os thread. What **FiberHttpClientBuilder** does is to wrap Apache **HttpAsyncClient** and letting us operate on it as if it were a blocking operation.

To speed this method up we are now going to spawn new Fibers for each Http request and use Quasar Channels to safely communicate between fibers to collect and build the response.

~~~ java
@GET
@Path("frontpage")
@Produces(MediaType.APPLICATION_JSON)
@Suspendable
public JsonElement getFrontpage() throws IOException, InterruptedException, SuspendExecution {
  final Channel<JsonElement> ch = Channels.newChannel(0, BLOCK, false, true);
      endpoints.forEach(e -> {
          new Fiber<Void>(() -> {
              try {
                  final String resp = EntityUtils.
                    toString(client.execute(new HttpGet(e)).getEntity());
                  //Apply logic and transform to JsonElement then send to Channel  
                  ch.send(..)
              } catch (Exception err) {
                  ch.send(..) //send error element
              }
          }).start();
      });

      //Read from channel same amount of times as size of endpoints
      //ch.recive is a fiber blocking operation thus make preemption possible
      final JsonObject obj = new JsonObject();
      for(int i = 0; i < endpoints.size(); i++) {
          obj.add(ch.receive(10, TimeUnit.SECONDS)); //10 sec timeout
      }
      ch.close();
      return obj;
}
~~~

So with not much effort and easy to read code, we are able to handle a higher number of concurrency without having to resort to complex asynchronous API’s. Quasar hides that for us and gives us the possibility to work with a programming model we are quite familiar with.


### Conclusions, if any.
Quasar is a fairly new framework, as of now version 0.7 is out, but it is gaining some traction.
I think it’s really interesting and it’s worth keeping an eye on.
The biggest concern I have is that you have to make 3d-party libraries work in a Fiber context trough wrapping its aync-api. Parallel Universe provides good documentation and support classes to do so, but I would still write my software asynchronous from top to bottom, and it’s not that hard to do given that you have the right tools to do so.

I would recommend everyone to give it a go, since it shows a lot of potential and lets you write easy to read and write code in a programming model that might fit you.
