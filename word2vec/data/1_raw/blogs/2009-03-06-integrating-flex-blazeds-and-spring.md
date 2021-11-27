---
layout: details-blog
published: true
categories: blogg teknik
heading: Integrating Flex, BlazeDS and Spring
authors:
  - janvasternas
tags: övrigt
topstory: true
comments: true
---

Suppose you have an web application with a service layer implemented by spring beans and want to get a richer user interface ? One way to do it to use Flex.

Parts of the Flex development platform has become Open Source. What you absolutely need is addition to that is the Flex Builder. It enables debugging of the Flex application and without that you are completely lost. The license is 150 Euro so it is no big deal.

So the User Interface is produced using Flex and to take care of the remoting we can use BlazeDS which is Open Source from Adobe. BlazeDS is deployed as an web appication.

My Helloworld sample version 1 uses a simple java class on the server side. Version 2 will use spring.

The class has a method

~~~ java
public List<Topic> getAllTopics()
~~~

Topic contains two attributes speaker and name.

In Flex I define a RemoteObject to describe the communication with the server

~~~ markup
<mx:RemoteObject id="server" destination="cadec-service">
  <mx:method name="getAllTopics" result="getAllTopicsResult(event)" />
</mx:RemoteObject>
~~~

The method tag tells Flex that whenever the `getAllTopics` Method is called the return value will be handled by the `getAllTopicsResult` method which is defined like this

~~~ java
private function getAllTopicsResult(event:ResultEvent):void	{
    topics = event.result as ArrayCollection;
}
~~~

It simply saves the result to a variable topics. Finally a DataGrid is defined to display the result

~~~ markup
<mx:DataGrid dataProvider="(topics)">
  <mx:columns>
    <mx:DataGridColumn dataField="speaker" width="150"/>
    <mx:DataGridColumn dataField="name" width="350"/>
  </mx:columns>
</mx:DataGrid>
~~~

When the page is loaded a call to `getAllTopics` is made

~~~ markup
<mx:Application . . . creationComplete="server.getAllTopics()">
~~~

and when the reply arrives the grid is populated and looks like this

_Bild saknas_

BlazeDS need to know what the destination="cadec-server" means. The information is supplied in file named `remoting-config.xml`

~~~ markup
<destination id="cadec-service">
  <properties>
    <source>se.callista.CadecService</source>
  </properties>
</destination>
~~~

This will create an instance of the CadecService (each time). The classes are put in WEB-INF classes.

HelloWorld sample version 2 uses spring on the server side.

To enable that I followed the instructions outlined by [http://coenraets.org/flex-spring/](http://coenraets.org/flex-spring/)

2 classes `SpringFactory.class` and `SpringFactory$SpringFactoryInstance.class` needs to be present att `WEB-INF/classes`.

To enable the spring integration these classes needs to be configured in the services-config file

~~~ markup
<factories>
  <factory id="spring" class="flex.samples.factories.SpringFactory"/>
</factories>
~~~

Now the `remoting-config.xml` destination can be changed to use the SpringFactory to get the bean from spring instead of initializing it. Obviously this means that the `CadedService` class will only be instatiated once.

~~~ markup
<destination id="cadec-service">
  <properties>
    <factory>spring</factory>
    <source>cadecService</source>
  </properties>
</destination>
~~~

Now everything works again.

If this wasn't simple enough we just have to wait for the new spring/flex integration project to deliver

[http://www.infoq.com/news/2009/01/spring-adobe-blazeds;jsessionid=8F49E7F3F0F00D6880768A222111D793](http://www.infoq.com/news/2009/01/spring-adobe-blazeds;jsessionid=8F49E7F3F0F00D6880768A222111D793)
