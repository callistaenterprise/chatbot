Spring Source recently announced a new member of the Spring family: Spring integration. It is an attempt to provide an abstraction for messaging, in the domain of business integration (i.e. it is not Telecom Messaging). Due to the lack of frameworks in this area, we have designed messaging abstractions for several large Java EE projects. One such effort was presented in a speech I held at Expertzone Developer Summit (slide 42 and onwards)  and also at Cadec 2006 (page 28 - 37). It is indeed a very welcome addition to the Spring family!

## What is Spring Integration?ƒ

"Integration" without a namespace, overlaps with the core of Spring itself. Spring is a framework for none-intrusive integration of platform mechanisms into application logic - sometimes by defining a unifying abstraction (api) for each class of mechanisms (Transaction Management, Batch Processing, Servlet Requests etc), and always (even when the Java platform has a sufficient abstraction - like JDBC) by providing a configuration mechanism to integrate various implementations in a loosely coupled fashion (dependency injection). So - when Spring itself is about integration - what is then Spring Integration? Meta integration? No, the name Integration stems from the ambition to provide a framework that helps developers apply the Enterprise Integration Patterns (EIP).  When an application architect approaches integration, her concern is to abstract messaging. There are several reasons for doing so:

- Messaging API:s and communication mechanisms has a much shorter life expectancy than a typical enterprise application. Three years back, it was JMS, three years a head it may be JAX WS and so on.
- Although JMS as well as JAX WS provides abstraction for message based middleware, a layer of message handling on top of these API:s will have to be repeated for every message consumer or producer, unless abstracted for re-use (exception handling strategies, Java bean marshaling, delegating processing of an inbound message to the appropriate business bean...)
- A higher-level API than JMS with support for dependency injection is more or less required for unit testing of business logic that depends on message exchange.

Spring Integration defines such an abstraction.

## Is EIP a valid scope for a Spring framework?

I'm not quite sure it is.

EIP includes Web Service integration. Web Services have not yet been incorporated, but communicated as a target. Although Web Services are often used for integration (integration of services) and are also by definition an abstraction for message based communication, there will be a substantial loss of semantics, when hiding it as a Channel Adapter type.  I've had a common messaging abstraction across asynchronous messaging technologies and web services in mind when designing similar abstractions (also Spring-based) for customers. According to my experience to much of service semantics are lost when pushing Web Services (WSDL-defined services) down under the cover of a messaging abstraction. Today, I would say that the opposite is a better approach. The Spring-based service integration framework Apache CXF is a good example.  I think Spring Integration should have been named Spring Messaging and solely be focused on the application developers perspective of message-based communication.

Spring is a framework for application architects. When an integration architect approaches integration, applications are considered "frozen commodity". A substantial part of EIP is targeting the needs of an Integration Architect. Aspects like routing, scatter/gather, pub/sub and other types of advanced mediation is better externalized to ESB-type of subsystems than integrated into the application build/release cycle. Mediation sub systems may of cause be based on Spring (maybe Spring Enterprise Integration to support realization of such subsystems).

## The core - what is missing in the current feature set?

- Inbound JMS processing has no means to configure the type of sophisticated retry / error queue policies often required in real life. On the other hand - as all DI-based frameworks, the user could override any default ChannelAdapter implementation that is not fit for purpose.
- Java EE Message Driven Beans are not supported. Inbound JMS processing must be implemented via Spring MessageListener container. This is not an option for enterprise integration at most customers I've been working for. Java EE message driven beans are typically the only remaining EJB-type in use today, due to the value they contribute in terms of monitoring, threading, advanced built-in retry/backout policies, failover awareness etc.
- File-based messaging is supported, but with limited functionality. Several critical areas are missing, most of which could be contributed by integration (yes, again!) of Spring Batch (message splitting, re-start etc). Spring Batch is not tied to a particular data source, the features it provides are typically needed when the source of the "message" is a legacy system that is not event based. Or better - let an ESB subsystem do the splitting / aggregation...

## We need Spring integration, but...

As the framework is scoped, it may inspire to bad habits rather than common integration best-practice . Even if a application framework supports multi-channel access to other systems (like files, sockets, and of-cause - JMS), it is typically not the path an application architect should take. Chose a single, robust endpoint technology, like JMS and then delegate semantic and technical adaption to an ESB subsystem that connects to the JMS source.

If you chose a message-based approach, like JMS, Spring Integration is an excellent abstraction that should be used (please provide support for Java EE Message Driven Beans!). If you chose a service-oriented approach, chose a service-oriented abstraction like JAX WS with Apache CXF (if you need Spring), rather than Spring integration. Don't use Spring Integration (or Apache CXF) for point-to-point / multi-channel integration - delegate to your enterprise ESB or to an application-bound light-weight ESB like Mule.
