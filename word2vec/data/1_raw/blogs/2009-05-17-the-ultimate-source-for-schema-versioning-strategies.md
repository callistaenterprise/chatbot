---
layout: details-blog
published: true
categories: blogg teknik
heading: The ultimate source for schema versioning strategies
authors:
  - johaneltes
tags: soa
topstory: true
comments: true
---

We are often asked to define WSDL- and schema design guidelines (contract-first) for clients. We have found a core set of guidelines that seem to work well for clients using XML_binding. The core challenge is to find a portable and reasonably useful approach to controlled evolution, supporting backwards- and forwards compatibility across service consumers and producers bound (via JAX-B or .Net binding technologies). We've seen the chosen approach being used fairly broadly, among others in several oasis specifications (as an example: WS-Topic in [WS-Notification](http://docs.oasis-open.org/wsn/wsn-ws_topics-1.3-spec-os.htm#_Toc122514759)), but never really found a good, authoritative point of reference. Until i found this excellent [document by w3c](http://www.w3.org/2001/tag/doc/versioning-xml). It outlines the problem, defines a number of versioning strategies - each with an identification, and finally lists examples of standards bodies that apply the different strategies. The strategy we are endorsing is [number 2.5](http://www.w3.org/2001/tag/doc/versioning-xml#versionid25).
