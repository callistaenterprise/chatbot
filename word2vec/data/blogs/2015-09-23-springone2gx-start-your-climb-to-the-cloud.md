---
categories: blogg teknik
layout: "details-blog"
published: true
heading: "SpringOne2GX - Start your climb to the cloud"
authors: 
  - matsekhammar
tags: cloud naative twelve-factor
topstory: true
comments: true
---

How do you get your application to the cloud? This is a complex question to answer shortly but in the following text there are some suggestions that can serve as a starting point. 

-[readmore]-

## Starting the climb
At SpringOne2GX a lot of talks were centred around aspects of cloud-centric applications. This also included how to make your applications ”cloud-safe”. One thing that constantly was mentioned was [The Twelve-Factor App](http://12factor.net).

The twelve-factor app is a collection of patterns (best practices) for cloud applications. Not so surprising there are 12 patterns ☺

To give you a quick overview these will be listed shortly below to give you a hint what this is all about:

1. Codebase; One codebase tracked in revision control, many deploys.
2. Dependencies; Explicitly declare and isolate dependencies
3. Config; Store config in the environment
4. Backing Services; Treat backing services as attached resources
5. Build, release, run; Strictly separate build and run stages
6. Processes; Execute the app as one or more stateless processes
7. Port binding; Export services via port binding
8. Concurrency; Scale out via the process model
9. Disposability, maximize robustness with fast startup and graceful shutdown
10. Dev/prod parity; Keep development, staging, and production as similar as possible
11. Logs; Treat logs as event streams
12. Admin processes; Run admin/management tasks as one-off processes

Many of these patterns can also serve as best practices for a **normal application!** Take for example pattern 1; to have one codebase tracked in revision control.

A way to start to cloud-enable your applications is to go through these patterns with your application in mind. Even if you find a pattern that doesn’t make sense right away, it could still be a mind-opening experience.

Also bear in mind that an application in the context of twelve-factor app refers to a single deployable unit. Your application could consist of multiple collaborating deployed components, in the twelve-factor context this is referred to as a distributed system.

Another good source to look into are a book by Matt Stine, [Migration To Cloud-Native Application Architectures](http://pivotal.io/platform/migrating-to-cloud-native-application-architectures-ebook) (free download!).

It is short (50 pages!) and makes a good introduction into why and how to migrate to the cloud. 

I hope these short notes can help you start your way to the cloud if you still are firmly on the ground but would like to try flapping your wings a bit.
