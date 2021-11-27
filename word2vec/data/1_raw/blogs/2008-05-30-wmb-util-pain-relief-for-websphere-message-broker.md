---
layout: details-blog
published: true
categories: blogg teknik
heading: wmb-util - pain relief for WebSphere Message Broker
authors:
  - niklasgustavsson
tags: wmb wmbutil
topstory: true
comments: true
---

WebSphere Message Broker has since version 6 sported a Java API that can be used to perform various actions, primarily message transformations. Users of the API will quickly find that it consists of a low level object model, much like the W3C XML DOM. After some additional use, one will find that the API has some odd inconsistencies, for example will an object model built with the MRM and XML domains differ in how value nodes are created. After a while, most users will grow increasingly frustrated. As programmers we know that adding another level of indirection solves any problem. Thus we'll create a high level abstraction on top of the WMB API. All WMB shops I'm familiar with has done this. All solving their immediate needs.

Enter [wmb-util](http://wmb-util.googlecode.com). It's yet another such API, but this time it's open source and freely available for anyone to use under a commercially friendly license. It sprung out of a project we did for a customer and together with the customer we opted for opening up the project rather than creating another proprietary version. For us this means we can reuse it in other customer projects. For the customer it means they'll get fixes for free, either from our other customer projects or from other users of the library. Hopefully all wins.

So, what does the library contain? The most important part, and the part I'll cover today, is that [very abstraction of the WMB API](http://code.google.com/p/wmb-util/wiki/UsingTheHelperClasses). Basically, it offers high(er)-level classes for a few, typically message types:

- Headers (MQMD, RFH2, Properties, HTTPInput
- XML messages
- SOAP messages
- Simple record based flat files (dubbed TDS in the library)
- Blobs

More messages can be added as need be. Each of the header and payload classes contains a set of static factory methods, used to create, wrap or remove messages. The classes work directly on the underlying WMB object model, meaning you can mix wmb-util code with use of the WMB API directly as you like. For example if you like to perform an XPath query and then use the TdsRecord to perform actions on the resulting elements.

The API aims to make the client code completely portable between the different message domains. More specifically, it should not have any imptact on your code if you use MRM, XML, XMLNS or XMLNSC.

Enough talk, let's look at some examples:

In this case we create a MQ message containing a simple XML payload from scratch

~~~ java
// create an empty output message using the regular WMB API
MbMessage outMessage = new MbMessage();

// create an MQMD header, using the default values
MqmdHeader mqmd = MqmdHeader.create(outMessage);
// this is a text message
mqmd.setFormat(MqmdHeader.FORMAT_MQSTR);

// create a XML payload
XmlPayload payload = XmlPayload.create(outMessage);
payload.declareNamespace("myns", NS);

// now, this code will be exactly the same whether using
// the XML domains or MRM. We'll handle the nodes types,
// value nodes and the missing root element in MRM. Don't worry.
XmlElement root = payload.createRootElement(NS, "root");

// set an attribute
root.setAttribute("my-attribute", "foo");
root.createLastChild(NS, "child");

... // send the message just like you always do
~~~

As seen above, you won't have to worry about things like domains, node types, weird ways of setting up namespace prefixes or that WMB will in some cases use an at-sign in front of attribute names. And you don't have to look up what the minimal attributes needed to create an MQMD header are. You have been copying the input message instead, haven't you?

We invite you all to use and participate in the project. All feedback is welcome, and patches double so.
