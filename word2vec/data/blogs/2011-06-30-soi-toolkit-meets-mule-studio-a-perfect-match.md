---
layout: details-blog
published: true
categories: blogg teknik
heading: Soi-toolkit meets Mule Studio, a perfect match!
authors:
  - magnuslarsson
tags: esb java opensource soa tools mule soi-toolkit
topstory: true
comments: true
---

[Soi-toolkit](http://soi-toolkit.org) and the upcoming [Mule Studio](http://www.mulesoft.org/documentation/display/MULESTUDIO/Home) (currently in beta) are two tools that simplify development of services and integrations based on Mule ESB. This article describes how these two tools complement each other to make the development even more simplified (and fun ☺).

First a short introduction of the two tools and then an illustrated test run...

-[readmore]-

## What is soi-toolkit?
Soi-toolkit is an open source project initiated by Callista together with a number of its customers as a common place to share proven best practices for developing services and integrations based on Mule ESB.

Soi-toolkit can give new Mule ESB users a kick-start by providing answers to a number of classic getting-started questions, i.e. questions that needs to be answered before the actual development of services and integrations in Mule ESB can take place. Typical questions are:

- How to setup a minimalistic but sufficient development environment?
- How to setup projects in a good way, file-structures, naming conventions, dependency management (i.e. use of Maven)?
- How to handle logging, error handling (including automatic recovery and retry logic) and property based configuration?
- How to test, build, release and deploy the services and integrations?

In short soi-toolkit is taking care of all the boring parts and allowing the developer to focus on constructing the services and integrations in Mule ESB.

Soi-toolkit does this by a set of customizable source code generators that given a small set of input parameters can create both an initial setup of the projects and skeleton code for services and integrations following a set of predefined high-level patterns.

Example:

![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/Create-a-jms-service-using-soi-toolkit3.png)

Soi-toolkit not only generates the Mule ESB configuration xml files but also sample transformers, test-classes (jUnit based unit test for the transformer and integration test for the whole service/integration), test-producers/consumers, log-settings and property files with appropriate properties for the generated code.

The generated code is immediately runnable (testable and deployable) once the generator is done but the normal case is of course that the developer takes the generated code as a starting point and refines it (with a test driven approach) to meet the requirements of the specific project.

For more information of soi-toolkit the following links are recommended:

1. [soi-toolkit homepage](http://soi-toolkit.org)
2. [soi-toolkit overview](http://code.google.com/p/soi-toolkit/wiki/Overview)
3. [soi-toolkit tutorials](http://code.google.com/p/soi-toolkit/wiki/Tutorials)
4. [Callista-blog on soi-toolkit](/blogg/teknik/2011/01/23/getting-started-with-soi-toolkit/)

## What is Mule Studio?
According to the [Mule Studio documentation](http://www.mulesoft.org/documentation/display/MULESTUDIO/Home):

> Mule Studio is a user-friendly and powerful Eclipse-based tool that allows you to easily create Mule ESB flows, edit and test them quickly without a deep knowledge of Mule configuration.

Example:

![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/Mule-Studio-graphical-editor1.png)

That’s perfect from a soi-toolkt perspective since Mule Studio can take over exactly from the spot where soi-toolkit leaves the developer, i.e. refining the Mule ESB configuration files. With Mule Studio the developer can do this graphically without touching the underlying XML. If the developer wants he can at any time switch over to the XML and refine it by hand, i.e. the editor is two-way allowing the graphical view to be updated by manual changes in the XML.

For more information of Mule Studio the following links are recommended:

1. [MuleSoft blogs on Mule Studio](http://blogs.mulesoft.org/tag/mule-studio/)
2. [Mule Studio documentation](http://www.mulesoft.org/documentation/display/MULESTUDIO/Home)
3. [Mule Studio beta program](http://www.mulesoft.org/mule-studio-beta-download)

Thit looks very promising, right?

Lets take it out for a spin!

## A test run with soi-toolkit and Mule Studio

**Note:** Mule Studio is currently in beta, i.e. not feature complete, and soi-toolkit’s current release, v0.4.1, is not Mule Studio aware. So the test run below is based on soi-toolkit code from trunk, far from complete when is comes to Mule Studio awareness. But the test run below clearly demonstrates what it will look like once Mule Studio and the new version of soi-toolkit are released.

Let’s start with an empty newly created project. It looks like:

![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/empy-project1.png)

Let’s create an integration that reads messages from one JMS queue, transforms the message and place it on another JMS queue.

We use the soi-toolkit generator for this and launch it using a soi-toolkit Eclipse-plugin from within Mule Studio:

![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/Create-a-jms-service-using-soi-toolkit-in-Mule-Studio1.png)

We specify a one-way pattern as the base and JMS for both incoming and outgoing transport and finally name the integration `jmsToJms` (lacking of a better name).

This results in a number of new source code files:

![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/jmsToJms-integration-files-created1.png)

The most important files are:

- The Mule service configuration:
	- `src/main/app/jmsToJms-config.xml`
	- `src/main/resources/flow/jmsToJms-service.mflow`
- The transformer and its unit-test
	- `src/main/java/.../JmsToJmsTransformer.java`
	- `src/test/java/.../JmsToJmsTransformerTest.java`
- Integration test and test-receiver
	- `src/test/java/.../JmsToJmsIntegrationTest.java`
	- `src/test/java/.../JmsToJmsTestReceiver.java`
	- `src/test/resources/teststub-services/jmsToJms-teststub-service.xml`

Double-clicking on the `jmsToJms-service.mflow` – file (selected in the picture above) opens up Mule Studio’s graphical editor:

![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/Mule-Studio-graphical-editor2.png)

Double-clicking on the elements in the graphical editor opens a property editor where the generated properties can be viewed and if required modified, e.g. for the inbound-jms-endpoint:

![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/jms-endpoint-property-editor1.png)

So we can for example see that the queue-name is generated as a configurable property available in the standard soi-toolkit property file, `labb2-config.properties`:

[![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/jmsToJms-properties2.png)](/assets/blogg/jmsToJms-properties2.png)

Finally clicking on the **Configuration XML** – tab shows the corresponding XML configuration generated by soi-toolkit.

[![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/jmsToJms-config1.png)](/assets/blogg/jmsToJms-config1.png)

Note the generated support for transaction handling, error handling and log-points.

There is more code of interest to go through, e.g. the generated Java transformer, the unit test and integration test classes and so on but to not make this blog endless I stop here for now.

Instead let’s try running the generated code!

First we simply run the unit test on the transformer and the integration tests of the whole integration. The integration test will do the following:

1. Start Mule embedded in the test that in turn start ActiveMQ (as a JMS provider) embedded as well.
2. Sending test messages to the in-jms-queue and wait for the asynchronous delivery of the outgoing message to the receiving teststub-component.
3. Compare the received message with an expected result and check log-queues and deadletter queue for expected results verifying correct error and retry - handling.
4. Both happy days and negative scenarios are covered by the generated integration tests.

The result of running the tests look like:

![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/test-results1.png)

Now let’s start the Mule ESB server so that we can send messages to it manually.

We use the soi-toolkit generated Mule ESB Server, `Labb2MuleServer.java`, it will by default start both the service but also its teststub-service that consumes the outgoing message (i.e. acting as the downstream system).

![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/starting-Mule-ESB1.png)

Next we place a message (`A. Test Message`) on the in-jms-queue using ActiveMQ’s admin-web-gui and we can immeadelty see how our new service consumes the message, transforms it (to `1. Test Message`) and sends it to the out-queue where the teststub consume the message and writes it out to the console.

![](/assets/blogg/soi-toolkit-meets-mule-studio-a-perfect-match/processing-a-message1.png)

Note the standardized (they are customizable!) log-messages that soi-toolkit provides (called `logEvent-info`).

Not bad for a few clicks in a wizard, right?

...and a very good start for test driven development of integrations and services using soi-toolkit and Mule Studio!
