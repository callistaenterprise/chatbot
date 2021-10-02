---
categories: blogg teknik
layout: "details-blog"
published: true
heading: "SpringOne2GX, day one"
authors: 
  - eriklupander
tags: "springxd,springone2gx"
topstory: true
comments: true
---


First impressions from the Spring XD tutorial

-[readmore]-

Some of us from Callista are currently on-site in Washington D.C. to participate in the [SpringOne2GX](http://www.springone2gx.com/) conference. Yesterday some of us participated in the Spring XD (eXtreme Data) tutorial while the others attended the Spring CF (Cloud Foundry) tutorial. In this blog post I'll summarize my personal impressions after the first day with Spring XD.

First off, there little doubt Spring XD is an interesting piece of technology, but I think the tutorial this far is a bit of a mixed experience.

The the basic presentation about core XD concepts was quite good - their so-called “Lambda Architecture” (which has nothing in common with Java 8 lambdas), the XD container, scalability, the core concepts of [Streams]([Streams](http://docs.spring.io/spring-xd/docs/current-SNAPSHOT/reference/html/#streams), [Jobs](http://docs.spring.io/spring-xd/docs/current-SNAPSHOT/reference/html/#batch) and [Taps](http://docs.spring.io/spring-xd/docs/current-SNAPSHOT/reference/html/#_taps) and how Streams (e.g. real-time ingestion of data) are built of Input Sources, Processors and Sinks. I felt some more time could have been spent on the problems it is trying to solve, and especially how it relates to Integration Platforms which also provides composable pipelines made out of EIP components. Another potential topic of interest are those cases where XD may prove to be the wrong tool for the job while first seeming to be so at a first glance. 

Further, the hands-on exercises were on a too basic level in my humble opinion. While there is a day left, I would have liked more focus on potential application of XD from an architect's point of view rather than basics of the [Spring XD DSL](http://docs.spring.io/spring-xd/docs/current-SNAPSHOT/reference/html/#dsl-guide) or the trivial task of how to install the product. I had expected more advanced application of XD concepts on real problems as labs rather than various Hello World scenarios. Perhaps building of an at least semi-complex solution over the two days in increments which would eventually cover the core concepts, DSL use, horizontal scaling, custom processors etc could have been an option.

The most interesting part were actually the coffee-break discussions with my Callista colleagues about Spring XD and what uses we could see in current and past projects. Realization such as _“had we only had this piece of technology when we…”_ can be both uplifting and frustrating. Technologies evolve, making the silver bullets of yesterday seem weathered and spent today.

Today we’ll hook up XD to hadoop, run XD in distributed mode and hopefully cover more complex topics.

More on Spring XD will follow. Stay tuned.
