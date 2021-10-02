---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Spring Framework 5 announced
authors: 
  - bjornbeskow
tags: spring framework
topstory: true
comments: true
---



The future of [Spring Framework](http://projects.spring.io/spring-framework/): Java 8 and Reactive.

-[readmore]-

Jürgen Höller gave a short presentation on the opening evening at [Spring2GX](https://2015.event.springone2gx.com), where he revealed the roadmap for Spring Framework 5 (scheduled for Q3-Q4 2016).
A little bit in the shadow of all the rapid innovation and hype with the [Spring Cloud](http://projects.spring.io/spring-cloud/) and associated projects, it's easy to think that the Spring Framework has stagnated and have become almost legacy. Jürgen's presentation  proved that to be very wrong indeed. Two major themes are planned for the next major release of Spring Framework:
* **Full adoption of Java 8**. Spring Framework 5 will no longer use JDK6 as the minimum Java version, but will require Java 8. It will be interesting to see how much impact that will have on the existing Spring Framework APIs. Just requiring Java 8 as the target runtime will not make much difference. The introduction of [Streams](https://docs.oracle.com/javase/8/docs/api/java/util/stream/package-summary.html) and [Lambdas](https://docs.oracle.com/javase/tutorial/java/javaOO/lambdaexpressions.html) in Java 8 will be a very welcome additions to many of the Spring APIs, but possibly at the expense of backwards compatibility?
* **Fully supporting a reactive programming model**. Exactly how that is going to be achieved was not clear in Jürgen's talk. Judging from the rest of the talks at the conference, [RxJava](https://github.com/ReactiveX/RxJava) seems to be the most likely model, whereas the [Spring Reactor](https://spring.io/blog/2013/05/13/reactor-a-foundation-for-asynchronous-applications-on-the-jvm) seems to have lost momentum.

Interesting news, indeed.
