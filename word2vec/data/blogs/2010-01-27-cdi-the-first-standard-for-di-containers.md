---
layout: details-blog
published: true
categories: blogg teknik
heading: CDI - The first standard for DI containers
authors:
  - johaneltes
tags: javaee opensource
topstory: true
comments: true
---

## What is it?

CDI is an abbreviation of "Contexts and Dependency Injection for the Java EE platform". First of all, I'd like to stress that CDI is not only for Java EE environments. It is equally applicable to Java SE applications, unit tests and other out-of-container environments.

The specification (JSR-299) defines its declared capabilities as follows:

> This specification defines a powerful set of complementary services that help improve the structure of application code.
>
> - A well-defined lifecycle for state-ful objects bound to lifecycle contexts, where the set of contexts is extensible
> - A sophisticated, type safe dependency injection mechanism, including the ability to select dependencies at either development or deployment time, without verbose configuration
> - Support for Java EE modularity and the Java EE component architecture---the modular structure of a Java EE application is taken into account when resolving dependencies between Java EE components
> - Integration with the Unified Expression Language (EL), allowing any contextual object to be used directly within a JSF or JSP page
> - The ability to decorate injected objects
> - The ability to associate interceptors to objects via type safe interceptor bindings
> - An event notification model
> - A web conversation context in addition to the three standard web contexts defined by the Java Servlets specification
> - An SPI allowing portable extensions to integrate cleanly with the contain

I will walk you through all the above with samples on the upcoming [Cadec 2010](http://www.callistaenterprise.se/cadec/cadec2010.html). In this blog entry, I'd like to give you a sense of the power of type-safe dependency injection in CDI.

## Type-safe dependency injection

If you are used to [Spring](http://www.springframework.org) you know that there are basically two ways of resolving a dependency: by auto-wireing and by referencing a particular bean by name. CDI builds on the new JSR for Dependency Injection (JSR-330). Spring 3.0 implements JSR-330, so the following sample should apply to Spring 3 as well as any full CDI implementation. I've verified my samples using the reference implementation of CDI: The [Weld container](http://docs.jboss.org/weld/reference/1.0.0/en-US/html/).

Type-safe dependency injection is about qualifying the requested bean among several possible ones, using annotations. Let's look at an example: injection of Spring JMS templates. Some applications use JMS extensively. There are many JMS service endpoints to interact with and there a also JMS endpoints for dealing with QoS, like destinations dedicated for logging and destinations dedicated for inbound business messages that could not be processed. The end result is the need for a potentially large number of pre-defined JMSTemplates - one for each destination.

Some destinations may need transitions, others don't. Oneway services will require XA support. RequestResponse services, Log services and error services will not.

Pre-CDI one would typically use configure each JMSTemplate as a named bean  and then reference the name using an annotation (`org.springframework.beans.factory.annotation.Qualifier`)

~~~ java
@Autowired @Qualifier("error-dest-jmstemplate")
JmsTemplate myService1JmsTemplate;
~~~

The template XML configuration would then reference an appropriate connection factory configuration (XA, NONE-XA etc).

With CDI, there is no standardized XML / externalized configuration language. The idea is to use annotations and Java code:

~~~ java
private @Inject @JmsPolicy(ERROR) JmsTemplate errorQeueTemplate;
~~~

In this case, we assume that there is single JmsTemplate defined to be used to send failed inbound messages to an error destination.

`@Inject` simply means (JSR-330) that the field is subject for dependency injection. Autoinjection is default in CDI. There are several options for restricting the injection target among those that match the type of the field, one of being custom qualifiers. A custom qualifier is a custom annotation type that itself is annotated with the `javax.inject.Qualifier` annotation. Here's the source code for the `@JmsPolicy` annotation that allows us to express which `JmsTemplate` that we expect to be injected, using  the semantics of a policy:

~~~ java
@Qualifier
@Target( { METHOD, FIELD, PARAMETER, TYPE })
@Retention(RUNTIME)
public @interface JmsPolicy {
  JmsPolicyEnum value();
  enum JmsPolicyEnum {
    ERROR,
    LOG
  }
}
~~~

When defining the JmsTemplate bean, we will annotate it with the same "policy", which is to say: "This JmsTemplate declaration conforms to the policy of an error destination" (timeout, Xa-support...).

## The JmsTemplate factory

Since there is no external configuration language for bean instances in CDI, we will have to define the CDI correspondence of a Spring bean factory using Java annotations. In CDI, a bean factory is called a producer. A producer is implemented as a method annotated with @producer, which will return an instance of a JmsTemplate. For this simple sample, it was handy to define a single class that hosts all JmsTemplate producer methods along with declarations of the ConnectionFactories that needs to be injected into et producer method parameters:

~~~ java
public class JmsTemplateProducers {

  @Produces @Resource @ResourceXaPolicy(NO_XA) ConnectionFactory noxa_cf;
  @Produces @Resource @ResourceXaPolicy(XA) ConnectionFactory xacf;

  @Produces @JmsPolicy(ERROR)
  public JmsTemplate getErrorQueueTemplate(
      @JmsTemplateConfig(defaultDestinationName = "errorQueue", timeout = 3600)
      JmsTemplate template,
      @ResourceXaPolicy(NO_XA) ConnectionFactory cf) {
    template.setConnectionFactory(cf);
    return template;
  }

  @Produces @JmsPolicy(LOG)
  public JmsTemplate getLogQueueTemplate(
      @JmsTemplateConfig(defaultDestinationName = "logQueue", timeout = 100)
      JmsTemplate template,
      ResourceXaPolicy(NO_XA) ConnectionFactory cf) {
    template.setConnectionFactory(cf);
    return template;
  }

  @Produces @Named("service1")
  public JmsTemplate getService1QueueTemplate(
      @JmsTemplateConfig(defaultDestinationName = "service1", timeout = 100)
      JmsTemplate template,
      @ResourceXaPolicy(XA) ConnectionFactory cf) {
    template.setConnectionFactory(cf);
    return template;
  }

  @Produces @Named("service2")
  public JmsTemplate getService2QueueTemplate(
      @JmsTemplateConfig(defaultDestinationName = "service2", timeout = 100)
      JmsTemplate template,
      @ResourceXaPolicy(XA) ConnectionFactory cf) {
    template.setConnectionFactory(cf);
    return template;
  }
}
~~~

We see another example of a producer: a field that is injected as a `@resource` and at the same time made available for injection into other beans (and thus being a producer).

The abstraction of policies have been used once more so that a semantic policy declaration in the form of a custom qualifier annotation could be used to specify the capabilities of the connection factory for each of the templates.

This translates into:

The service bean that processes an inbound JMS message says:

> I need a JmsTemplate that qualifies for sending error message

The producer method for JmsTemplates that claims to support the error handling policy says:

> I need a connection factory that is compatible with my policy for transaction handling, which is XA-enlisting.

The code also shows an example of a JmsTemplate producer that support a log policy. The log policy defines a substantially shorter timeout for invocation of the log service than does the error template producer.

Finally, there are samples of JmsTemplate producers for business service endpoints (service1, service2). They are defined using a pre-defined (JSR-330) qualifier annotation type, that is convenient to use when there is no added value of abstracting the matching of an injection point with a bean.

## Meta-programming in CDI

The `@JmsTemplateConfig` annotation used in the producer samples, is a custom annotation used in conjunction with the mata-programming capabilities of the CDI SPI, extend the annotation-based configuration language for our purpose (a real case would include all properties of the Spring JmsTemplate):

~~~ java
@Qualifier
@Target( { METHOD, FIELD, PARAMETER, TYPE })
@Retention(RUNTIME)
public @interface JmsTemplateConfig {
  @Nonbinding
  String defaultDestinationName() default "";

  @Nonbinding
  int timeout() default 0;
}
~~~

The annotation is processed by a class that utilizes parts of the CDI SPI for meta programming:

~~~ java
public class JmsTemplateConfigurationProducer {

  @Produces
  @JmsTemplateConfig
  public JmsTemplate produceJmsTemplate(InjectionPoint injectionPoint) {
    JmsTemplateConfig t = injectionPoint.getAnnotated().getAnnotation(JmsTemplateConfig.class);
    JmsTemplate tmp = new JmsTemplate();
    tmp.setDefaultDestinationName(t.defaultDestinationName());
    tmp.setReceiveTimeout(t.timeout());
    return tmp;
  }
}
~~~

## Summary

The idea of having a 100% java-based dependency injection model, based on annotations require some innovation to take place. CDI is a good example of what it takes. CDI also raises the bar in terms of type-safe dependency injection. There are several interesting innovations to explore in CDI.
