---
layout: details-blog
published: true
categories: blogg teknik
heading: Using soi-toolkit to create secure HTTPS services (SOAP or REST style) in Mule ESB
authors:
  - magnuslarsson
tags: esb https mule mutalauthentication soap soitoolkit studio
topstory: true
comments: true
---

Have you ever tried to setup a secure communication using HTTPS?

With mutual authentication, a service consumer, an ESB in the middle, a service producer and a number of certificates and truststores this can be quite challenging and time consuming. This is however a very typical integration scenario that we help our customers to implement over and over again. Getting all the security configuration in place at the same time always seem to be a challenge...

Based on experiences from a number of projects we have added support in the latest version of [soi-toolkit](http://code.google.com/p/soi-toolkit), v0.6.0, to automate the initial setup of secure communication in Mule ESB using HTTPS with mutual authentication.

-[readmore]-

Soi-toolkit is integrated with Mule Studio as a Eclipse plugin and can after a few clicks create a proper setup for you including mule flow, unit and integration tests, test consumer, teststub for the service producer, sample certificates and truststore and a property file that you can use to simply replace the sample certificates to your own once you are ready for that.

A sample secure mule flow created by soi-toolkit looks like:

![Mule Flow](/assets/blogg/using-soi-toolkit-to-create-secure-https-services-soap-or-rest-style-in-mule-esb/3_service.png)

...and execution of the generated unit and integration tests looks like:

![jUnit tests](/assets/blogg/using-soi-toolkit-to-create-secure-https-services-soap-or-rest-style-in-mule-esb/5_jUnitTestResults.png)

A [tutorial](http://code.google.com/p/soi-toolkit/wiki/TutorialCreateSecureRequestResponseService) on the subject is available at [create a secure request/response service using HTTPS with mutual authentication](http://code.google.com/p/soi-toolkit/wiki/TutorialCreateSecureRequestResponseService).

In this tutorial you can as well get help on testing the secure service using soapUI:

![soapUI](/assets/blogg/using-soi-toolkit-to-create-secure-https-services-soap-or-rest-style-in-mule-esb/7.4_soapui_receiveResponse.png)

...and see a proof on that the secure setup actually works:

![tcpmon](/assets/blogg/using-soi-toolkit-to-create-secure-https-services-soap-or-rest-style-in-mule-esb/7.5_tcpmon.png)

Give it a try and run through the [tutorial](http://code.google.com/p/soi-toolkit/wiki/TutorialCreateSecureRequestResponseService)!
