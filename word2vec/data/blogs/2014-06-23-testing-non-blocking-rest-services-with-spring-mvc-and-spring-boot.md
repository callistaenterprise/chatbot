---
layout: details-blog
published: true
categories: blogg teknik
authors:
  - magnuslarsson
heading: Testing non-blocking REST services with Spring MVC and Spring Boot
tags: java test nio nonblockingio rest scalability servlet
topstory: true
comments: true
---

In a [previous blog](/blogg/teknik/2014/04/22/c10k-developing-non-blocking-rest-services-with-spring-mvc/) we described how to develop non-blocking REST services using Spring MVC and Spring Boot. In this blog we will add the aspect of testing non-blocking REST services.

Testing a REST service includes not only basic unit testing of the business logic inside the service, but also ensuring that communication aspects are handled correctly. For example, verifying that the asynchronous machinery works as expected in a non-blocking service and that HTTP headers are handled correctly.

-[readmore]-

Testing a traditional blocking REST service using [Spring MVC Test Framework](http://docs.spring.io/spring/docs/current/spring-framework-reference/html/testing.html#spring-mvc-test-framework) is straightforward using its fluent API. See the following example copied from the link above:

~~~ java
@RunWith(SpringJUnit4ClassRunner.class)
@WebAppConfiguration
@ContextConfiguration("test-servlet-context.xml")
public class ExampleTests {

    @Autowired
    private WebApplicationContext wac;

    private MockMvc mockMvc;

    @Before
    public void setup() {
        this.mockMvc = MockMvcBuilders.webAppContextSetup(this.wac).build();
    }

    @Test
    public void getAccount() throws Exception {
        this.mockMvc.perform(get("/accounts/1").accept(MediaType.parseMediaType("application/json;charset=UTF-8")))
            .andExpect(status().isOk())
            .andExpect(content().contentType("application/json"))
            .andExpect(jsonPath("$.name").value("Lee"));
    }

}
~~~

If we try to apply this approach to non-blocking REST Services developed with Spring MVC and Spring Boot we run into two problems:

1. When using Spring Boot we typically have no configuration file to specify when using the `@ContextConfiguration` annotation.
2. The non-blocking program model in Spring MVC results in that the `MockMvc` `perform` method will return before the request is processed, i.e. we have to instruct the test to wait for the completion of the asynchronous processing before we can perform any assertions on the test result.

Let's see how we can handle these problems!

## No XML configuration files with Spring Boot
Instead of using `@ContextConfiguration` and a classic XML-configuration file Spring Boot provides a corresponding annotation, `@SpringApplicationConfiguration`. This annotation can be used to load and configure a Spring `ApplicationContext` for integration tests using Spring Boot `@SpringApplicationContextLoader` and specifying the  Spring Boot main class of the application, e.g. `Application.class`.

With that explained, the only thing we need to do is to replace the annotation `@ContextConfiguration("test-servlet-context.xml")` with `@SpringApplicationConfiguration(classes = Application.class)`. An example from our sample code:

~~~ java
@RunWith(SpringJUnit4ClassRunner.class)
@WebAppConfiguration
@SpringApplicationConfiguration(classes = Application.class)
public class ProcessingControllerTest {
~~~

## The non-blocking program model in Spring MVC
To wait for the asynchronous completion of the request processing our test can use a helper method `asyncDispatch` in the class `MockMvcRequestBuilders`, see its [javadoc](http://docs.spring.io/spring/docs/4.0.3.RELEASE/javadoc-api/org/springframework/test/web/servlet/request/MockMvcRequestBuilders.html#asyncDispatch-org.springframework.test.web.servlet.MvcResult-) for details. The key thing is to split the usage of fluent API in the example above in two separate statements like:

~~~ java
@Test
public void testProcessNonBlocking() throws Exception {

    MvcResult mvcResult = this.mockMvc.perform(get("/process-non-blocking?minMs=2000&maxMs=2000"))
        .andExpect(request().asyncStarted())
        .andReturn();

    this.mockMvc.perform(asyncDispatch(mvcResult))
        .andExpect(status().isOk())
        .andExpect(content().contentType("application/json;charset=UTF-8"))
        .andExpect(content().string(expectedResult));
}
~~~

However, from my own experiences, this construct doesn't seem to work in all cases. After searching for similar issues on Internet, I found a lot of recent bug-fixes in the MVC Test Framework regarding handling non-blocking, deferred asynchronous results. So we seems to be on the bleeding edge here. Hopefully this will be sorted out in near time, but until then we need a robust workaround.

A number of possible workarounds are suggested, but the one that always seem to work is to add an extra statement in between the two above: `mvcResult.getAsyncResult();`. This statement doesn't complete until the asynchronous processing is done so after it returns it is safe to perform the assertions on the result.

The revised code looks like:

~~~ java
@Test
public void testProcessNonBlocking() throws Exception {

    MvcResult mvcResult = this.mockMvc.perform(get("/process-non-blocking?minMs=2000&maxMs=2000"))
        .andExpect(request().asyncStarted())
        .andReturn();

    mvcResult.getAsyncResult();

    this.mockMvc.perform(asyncDispatch(mvcResult))
        .andExpect(status().isOk())
        .andExpect(content().contentType("application/json;charset=UTF-8"))
        .andExpect(content().string(expectedResult));
}
~~~

##Try it out!
Do you want to try it out on your own?

Please, check out our code example and try it yourself:

~~~ bash
$ git clone git@github.com:callistaenterprise/blog-non-blocking-rest-service-with-spring-mvc.git
$ cd blog-non-blocking-rest-service-with-spring-mvc/spring-mvc-asynch-teststub
$ git checkout -b my-branch-1.1 v1.1
$ ./gradlew test
~~~

A test run typically produce an output like:

~~~
:clean
:compileJava
:processResources
:classes
:compileTestJava
:processTestResources UP-TO-DATE
:testClasses
:test
2014-06-22 08:45:01.918 INFO  Thread-4 o.s.w.c.s.GenericWebApplicationContext:873 - Closing org.springframework.web.context.support.GenericWebApplicationContext@4450c45f: startup date [Sun Jun 22 08:44:56 CEST 2014]; root of context hierarchy

BUILD SUCCESSFUL

Total time: 11.81 secs
~~~

A proper test report is also created, see `build/reports/tests/index.html`:

![Test Report](/assets/blogg/testing-non-blocking-rest-services-with-spring-mvc-and-spring-boot/test-report.png)

##Summary
With some minor changes to your test code you can keep on writing tests based on [Spring MVC Test Framework](http://docs.spring.io/spring/docs/current/spring-framework-reference/html/testing.html#spring-mvc-test-framework) also for asynchronous REST services. With a replacement of one annotation in the test class we also can enjoy the Spring Boot programming model, e.g. avoid using XML based Spring configuration files!
