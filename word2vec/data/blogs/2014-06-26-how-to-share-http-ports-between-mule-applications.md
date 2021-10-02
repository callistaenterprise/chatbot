---
layout: details-blog
published: true
categories: blogg teknik
authors:
  - magnuslarsson
heading: How to share HTTP ports between Mule applications
topstory: true
comments: true
---

Mule 3 introduced an [application-level component model](http://www.mulesoft.org/documentation/display/current/Mule+Deployment+Model) allowing for fine grained deployment of Mule applications. One disadvantage with this model is it that HTTP services packaged in different applications can't share HTTP ports. This leads in many cases to Mule instances that use several HTTP ports. This is not preferable, for example, from a network security point of view since it force firewalls to accept traffic through a number of HTTP ports.

In Mule 3.5.0 this problem can be resolved using [shared resources](http://www.mulesoft.org/documentation/display/current/Shared+Resources). In this blog we will show you how to develop two Mule applications each exposing HTTP services that share a common HTTP port.

-[readmore]-

##Pre-requirements
We will use Anypoint Studio (the May 2014 release) to develop the Mule applications and Mule ESB 3.5.0 Community Edition standalone runtime to execute the applications. They can both be downloaded from [here](http://www.mulesoft.org/download-mule-esb-community-edition). For the scope of this blog we assume that Mule ESB 3.5.0 CE standalone runtime is installed in the folder `${MULE_HOME}`.

##Create a shared HTTP connector
To be able to use the same HTTP port from the two applications we need a shared HTTP connector. This can be setup by creating a file named `mule-domain-config.xml` under `${MULE_HOME}/domains/default` with a content like:

~~~ xml
<?xml version="1.0" encoding="UTF-8"?>
<mule-domain
  xmlns="http://www.mulesoft.org/schema/mule/domain"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:http="http://www.mulesoft.org/schema/mule/http"
  xsi:schemaLocation="
    http://www.mulesoft.org/schema/mule/domain http://www.mulesoft.org/schema/mule/domain/current/mule-domain.xsd
    http://www.mulesoft.org/schema/mule/http   http://www.mulesoft.org/schema/mule/http/current/mule-http.xsd">

    <http:connector name="my-shared-http-connector" />

</mule-domain>
~~~

Note that we named the HTTP connector `my-shared-http-connector`, we will refer to the connector in the applications below using this name.

Also note that you can create you own domain for more fine grained control over shared resources, see [shared resources](http://www.mulesoft.org/documentation/display/current/Shared+Resources) for more information.

##Develop the Mule applications
In Anypoint Studio create a new project using `File --> New --> Mule Project`, set the project name to `http-one`, ensure that the runtime named `Mule server 3.5.0 CE` is selected and hit the `Finish` button, e.g.:

![Create Mule Project](/assets/blogg/how-to-share-http-ports-between-mule-applications/create-project.png)

The project will be created and a graphical flow editor will be opened.
Create a simple HTTP service by dragging in a HTTP connector and an Echo component. Set the HTTP port and path to values of your choice, `8081` and `one` in my case:

![Create Mule FLow](/assets/blogg/how-to-share-http-ports-between-mule-applications/create-flow.png)

You can now try to run the Mule flow inside Anypoint Studio by right-clicking on the flow file (`http-one.mflow` and select `Run As --> Mule Application`. Then within a Web Browser try out the application. A request sent to `http://Localhost:8081/one/hello` should respond `/hello` like:

![Run Flow inside Studio ](/assets/blogg/how-to-share-http-ports-between-mule-applications/run-flow-in-studio.png)

After trying it out stop the application to allow Mule standalone later on to use the port.

Anypoint Studio does not yet support the concept of shared resources so we have to edit the underlying XML configuration file. Switch to the `Configuration XML` tab in the flow editor and add `connector-ref="my-shared-http-connector"` to the http-inbound-endpoint, see:

![Edit Flow XML file ](/assets/blogg/how-to-share-http-ports-between-mule-applications/edit-flow.png)

*Note:* We can no longer run the flow in Anypoint Studio since it doesn't (yet) understand the concept of shared resources!

Now we can create the deployable file for our application by right-clicking on the project folder `http-one` and select `Export... --> Mule --> Anypoint Studio Project to Mule Deployable Archive` and specify a proper name of the zip-file, e.g. `http-one.zip`.

To create the other application repeat the steps above, but name the application `http-two` instead. Ensure that you use the same HTTP port, but another path as in the first application. I used `8081` and `two` for my second application.

##Deploy the Mule applications
This can be done simply by copying `http-one.zip` and `http-two.zip` to `${MULE_HOME}/apps`. If Mule already is running they will be automatically deployed.

##Start Mule ESB
We should now be able to start Mule ESB with the shared HTTP connector and the two applications that expose HTTP services using one and the same HTTP port. The startup should result in an output like:

~~~ bash
$ cd ${MULE_HOME}/bin
$ mule
.
.
.
**********************************************************************
* Mule ESB and Integration Platform                                  *
* Version: 3.5.0 Build: ff1df1f3                                     *
* MuleSoft, Inc.                                                     *
* For more information go to http://www.mulesoft.org                 *
*                                                                    *
* Server started: 6/20/14 10:18 AM                                   *
* JDK: 1.7.0_45 (mixed mode)                                         *
* OS: Mac OS X (10.9.3, x86_64)                                      *
* Host: Magnus-MacBook-Pro.local (192.168.1.114)                     *
**********************************************************************
.
.
.
INFO  2014-06-20 10:18:32,417 [WrapperListener_start_runner] org.mule.module.launcher.DeploymentDirectoryWatcher:
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ Mule is up and kicking (every 5000ms)                    +
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
INFO  2014-06-20 10:18:32,431 [WrapperListener_start_runner] org.mule.module.launcher.StartupSummaryDeploymentListener:
**********************************************************************
*              - - + DOMAIN + - -               * - - + STATUS + - - *
**********************************************************************
* default                                       * DEPLOYED           *
**********************************************************************

*******************************************************************************************************
*            - - + APPLICATION + - -            *       - - + DOMAIN + - -       * - - + STATUS + - - *
*******************************************************************************************************
* http-one                                      * default                        * DEPLOYED           *
* http-two                                      * default                        * DEPLOYED           *
*******************************************************************************************************
~~~

##Try it out!
Use curl to try out if the two applications actually can share one and the same HTTP port:

~~~ bash
$ curl http://localhost:8081/one/hello-one
/one/hello-one

$ curl http://localhost:8081/two/hello-two
/two/hello-two
~~~

..and if you look into the log files of each application you will see that that each application got its request as expected:

~~~ text
$ more ${MULE_HOME}/logs/mule-app-http-one.log
...
INFO  2014-06-20 10:21:28,178 [my-shared-http-connector.receiver.02] org.mule.component.simple.LogComponent:
********************************************************************************
* Message received in service: http-oneFlow1. Content is: '/one/hello-one'     *
********************************************************************************
~~~

~~~ text
$ more ${MULE_HOME}/logs/mule-app-http-two.log
...
INFO  2014-06-20 10:21:34,226 [my-shared-http-connector.receiver.02] org.mule.component.simple.LogComponent:
********************************************************************************
* Message received in service: http-twoFlow1. Content is: '/two/hello-two'     *
********************************************************************************
~~~

##Summary
You have seen how one of the most problematic disadvantages of the deployment model in Mule 3 now is resolved. Using shared resources in Mule 3.5.0 we can enable applications to share one and the same HTTP port. Actually shared resources can be used in other areas such as sharing the same VM-, JMS- and JDBC-endpoints resulting in new interesting opportunities, but we leave that for a later blog to delve into. As of today the development environment, Anypoint Studio, is lagging a bit not supporting the concept of shared resources. Hopefully it won't take long until that issue also is resolved.
