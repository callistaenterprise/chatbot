---
layout: details-blog
published: true
categories: blogg teknik
heading: Lightweight messaging development using Active MQ
authors:
  - johannescarlen
tags: opensource
topstory: true
comments: true
---

This is a guide to setting up a lightweight messaging development environment with [Active MQ](http://activemq.apache.org/) using [Tomcat](http://tomcat.apache.org/) as the application server. This tips might be of help to you regardless you are using another platform such as Websphere MQ or just want to try out JMS in your web or Java application.

When integrating enterprise applications and services, Websphere MQ as messaging backbone is a common choice. While Websphere MQ is a valid, stable platform for production environments, the same platform makes a large, clumsy footprint in the development environment, making testing of services almost impossible in a sensible way. This is totally the opposite way of agile development methods where unit testing and test automation plays an important role. A quite easy way to help you out is to replace WMQ in your development environment with a more lightweight alternative /platform such as Active MQ /Spring / Tomcat.

Design wise there are three main different scenarios to think about.

1. You are the service
2. You are the caller making an asynchronous call
3. You are the caller making a synchronous call (Request-Reply)

We begin with a look at the first scenario, where we need to be able to accept and read messages. Then we move on to act as the caller, the sender of these messages. I will not cover the third scenario in this post, why I will explain later.

First of all - download Tomcat, ActiveMQ, and Spring, create a web project and place the jars in the lib folder of your web app. Or you can just download the zip file containing the example code at the end of this page

## Implementing the Jms listener

There are several ways of implementing a Jms Listener and I will show you one way. There are four main artifacts needed to make this possible.

- A Jms listener implementation class that receives the call
- A Spring configuration declaring the listener bean, the factory and destinations
- We need to declare resources in the Tomcat context
- We also have to bind the resources in the web.xml

Jms Listener:

~~~ java
public class MyService implements MessageListener {
  public void onMessage(Message msg) {
    if (msg instanceof TextMessage) {
      try {
        String text = ((TextMessage) msg).getText();
        System.out.println(text);
      } catch (JMSException e) {
        e.printStackTrace();
      }
    }
  }
}
~~~

In the spring context we need to create the queue connection factory and a destination that maps to the physical queue:

~~~ markup
<bean id="jmsQueueConnectionFactory" class="org.springframework.jndi.JndiObjectFactoryBean">
  <property name="jndiTemplate"><ref bean="jndiTemplate" /></property>
  <property name="jndiName"><value>jms/cf</value></property>
  <property name="resourceRef"><value>true</value></property>
</bean>
<bean id="myDestination" class="org.springframework.jndi.JndiObjectFactoryBean">
  <property name="jndiTemplate"><ref bean="jndiTemplate" /></property>
  <property name="jndiName"><value>jms/myQueue</value></property>
  <property name="resourceRef"><value>true</value></property>
</bean>
~~~

as well as a listener container in which we inject the listener

~~~ markup
<bean id="myContainer" class="org.springframework.jms.listener.DefaultMessageListenerContainer">
  <property name="connectionFactory" ref="jmsQueueConnectionFactory" />
  <property name="messageListener" ref=" myServiceBean" />
  <property name="concurrentConsumers" value="5" />
  <property name="destination" ref="myDestination" />
</bean>
<bean id="myServiceBean" class="se.callistaenterprise.MyService" />
~~~

Then we need to let Tomcat be aware of the messaging server. It is possible to embed the ActiveMQ instance in the same JVM as Tomcat, but I have chosen to let ActiveMQ startup as a standalone server to make this environment resemble a normal setup as much as possible. If you are running Windows, ActiveMQ comes with a handy possibility to create a Windows service. There is also a practical reason for keeping ActiveMQ separate - it takes about ten seconds for ActiveMQ to start which makes it quite cumbersome when you need to restart yor Tomcat now and then.

In the Tomcat context of your application, make a reference to a connection factory as well as to the specific queue:

~~~ markup
<?xml version="1.0" encoding="UTF-8"?>
<Context>
  <Resource name="jms/cf" auth="Container"
      type="org.apache.activemq.ActiveMQConnectionFactory"
      description="JMS Connection Factory"
      factory="org.apache.activemq.jndi.JNDIReferenceFactory"
      brokerURL="tcp://localhost:61616" brokerName="LocalActiveMQBroker"
      useEmbeddedBroker="false" />

  <Resource name="jms/myService" auth="Container"
      type="org.apache.activemq.command.ActiveMQQueue"
      factory="org.apache.activemq.jndi.JNDIReferenceFactory"
      physicalName="MY.SERVICE" />
</Context>
~~~

One thing that is nice about Tomcat is that you can place this context information in a file named context.xml in the META-INF folder of your web application and Tomcat just reads it from there. No need to fiddle in the config folders.

The last thing we need is to map the resources in web.xml and kickstart the Spring context initialization:


~~~ markup
<context-param>
  <param-name>contextConfigLocation</param-name>
  <param-value>classpath:applicationContext-jms.xml</param-value>
</context-param>
<listener>
  <listener-class>org.springframework.web.context.ContextLoaderListener</listener-class>
</listener>
<resource-env-ref>
  <resource-env-ref-name>jms/cf</resource-env-ref-name>
  <resource-env-ref-type>javax.jms.QueueConnectionFactory</resource-env-ref-type>
</resource-env-ref>
<resource-env-ref>
  <resource-env-ref-name>jms/myService</resource-env-ref-name>
  <resource-env-ref-type>javax.jms.Queue</resource-env-ref-type>
</resource-env-ref>
~~~

This is all to it, just deploy and run ActiveMQ and Tomcat. Since ActiveMQ creates the queue on the fly we don't have to care about doing that by hand. There is an admin gui in ActiveMQ that lets you send simple text messages. Just go to [http://localhost:8161/admin](http://localhost:8161/admin) and try your new service.

## Making an asynchronous call

The second scenario is to call our remote service asynchronously through the messaging platform. I am using the Spring JmsTemplate to send messages so we need to add this to our config file as well as the bean that uses it:

~~~ markup
<bean id="jmsTemplate" class="org.springframework.jms.core.JmsTemplate">
  <property name="connectionFactory"><ref bean="jmsQueueConnectionFactory" />
  <property name="receiveTimeout" value="20" />
</bean>
<bean id="caller" class="se.callistaenterprise.JmsService">
  <property name="jmsTemplate" ref="jmsTemplate" />
  <property name="destination" ref="myDestination" />
</bean>
~~~

The Java code of the caller bean:

~~~ java
public void sendMessage(final String messageText) throws JMSException {
  jmsTemplate.send(destination, new MessageCreator() {
    public Message createMessage(Session session) throws JMSException {
      TextMessage message = session.createTextMessage(messageText);
      message.setJMSExpiration(20000);
      return message;
    }
  });
}
~~~

In order to test this, create a servlet which could contain code like this:

~~~ java
Caller producer = (Caller) WebApplicationContextUtils.
    getWebApplicationContext(this.getServletContext()).getBean("caller");
try {
  String message = "A Callista message";
  producer.sendMessage(message);
} catch (JMSException e) {
  e.printStackTrace();
}
~~~

And there you go!

The third scenario - the Request-Reply pattern - is something I may address in a later post. The Spring JmsTemplate currently lacks (as of version 2.5.4) a proper way of handling the correlation id (used for identifying the reply) that is extracted from the sent message. This pattern, though, is supposed to be addressed in the next version.

## Resources

- [http://activemq.apache.org/](http://activemq.apache.org/)
- [http://www.springframework.org/](http://www.springframework.org/)
- [http://tomcat.apache.org/](http://tomcat.apache.org/)
