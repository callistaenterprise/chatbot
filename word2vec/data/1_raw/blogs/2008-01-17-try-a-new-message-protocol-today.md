Do you want interoperability in the middleware arena without vendor lock-in?

Then AMQP can be something for you!

AMQP stands for Advanced Message Queuing Protocol and is a emerging protocol specification that intends to enable implementations from many sources and address the most common business requirements.

To enable complete interoperability for the messaging middleware, both the networking protocol and the semantics of the broker services are specified in AMQP. The AMQP protocol is a binary protocol (multi-channel, negotiated, asynchronous, secure, portable, neutral). The services are of three main types, which are connected into processing chains in the server

- The _exchange_ receives messages from publisher applications and routes these to message queues.
- The _message queue_ stores messages until they can be processed by a consuming client application.
- The _binding_ defines the relationship between a message queue and an exchange.

Among the supporters you will find Cisco, IONA, Red Hat and JPMorganChase.

Qpid is the Apache project (in incubator) on AMQP and delivers implementations in Java, C++, Python, C# and Ruby.

Try it out when you want to get out of the shadow from the big middleware market holders!
