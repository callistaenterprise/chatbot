---
layout: details-blog
published: true
categories: blogg teknik
heading: Is REST the future for SOA?
authors:
  - johaneltes
tags: architecture soa
topstory: true
comments: true
---

I just read Boris Lublinsky's article on [Is REST the future for SOA?](http://www.infoq.com/articles/RESTSOAFuture).

I think it makes a good job in clarifying that REST and SOA are different architecture styles, rather than merely a choice of protocol. I also like that he discusses the common case where people talk about REST when they actually mean http services without SOAP and WSDL. Lublinsky names this no mans land "REST Web Services". I think it is unfurtunate to include "REST" in the name. It kind of preserves the fuzziness. I would prefer "HTTP services". I was tempted to say "HTTP XML Services" but I guess JSON would be the typical payload representation.

-[readmore]-

Beyond that, I don't agree with his conclusions on how "REST Web Services" compare to WS-* web services. In contrast, I think it is more lightweight to utilize the HTTP protocol. Today, WS-* is WS-I Basic Profile with transport layer security. So there is no "feature" of WS-* that is not available in the http protocol, while there are actually several examples of the opposite (compression, redirect, caching etc) that are lost by layering SOAP on top of http.

Moreover, http as a protocol is simpler because developers today are born with http.

So what about contracts? I agree with Lublinsky's take on contracts. With "REST Web Services" we still need contracts. And the XML schemas could be used regardless whether WS-* or "REST Web Services" are used. Generally, the payload of well-designed contract first WS-* web services can be used out of the box as contracts for "REST Web Services" as well. But since XML schemas used for services based on canonical business models rarely express a majority of the constraints of the service, we still depend on a document to be interpreted by developers in design time (and by automated functional tests that verify the complete set of constraints). Lublinsky's believe in the importance of XML Schema as a contract language does not at all match my experience of service contract design and evolution. The major driver for still using XML Schemas (formal service contracts): There are standard tools for generating stubs and scheletons in Java and .Net languages that help developers process the payload (request and response messages) as if java- or .net objects were actually marshaled between service consumer and producer. As a contract language, XML schema isn't close to the importance expressed by Lublinsky.

For the service consumer of a contract-first service, an http XML service is likely the most straight-forward protocol to consume in case the consumer is a "system" rather than a web browser. Trough content negotiation it is also easy to provide multiple representations from the same endpoint. Web browser applications need for JSON payload could then be supported in parallell, through mechanisms architected into the http protocol itself (content negotiation etc).

But most importantly – as stated by the article – this is not REST.
