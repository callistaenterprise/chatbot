---
categories: blogg teknik
layout: "details-blog"
published: true
topstory: true
comments: true
heading: "SpringOne2GX 2015 - Cloud Native"
authors: 
  - hansthunberg
tags: springone2gx 12factor
---


The [Spring2GX 2015](https://2015.event.springone2gx.com) mantra is Get Cloud Native, but what does it mean?

-[readmore]-

Many of the talks at [Spring2GX 2015](https://2015.event.springone2gx.com) is about building cloud native applications and mention the [twelve-factor](http://12factor.net/). The [twelve-factor](http://12factor.net/) is a collection of characteristics that describes elements of a cloud native application. These characteristics should meet the requirements of a modern application with demands like:

* variable workloads
* servers coming in and out of existence
* zero downtime deploys
* short time to production for new features
* expectations are more dynamic 
* high cohesion and loosely coupling

For **cloud platform providers** these [twelve-factor](http://12factor.net/) characteristics helps to build mechanisms that is needed for cloud native applications, such as

* consistent provisioning
* high visibility of health and logs
* making the system handle well under stress

For [DevOps](https://en.wikipedia.org/wiki/DevOps) these characteristics helps to build, test and run applications in isolation with explicit isolated dependencies. It also enables to build systems that:

* is easy to monitor and trace
* is possible to get to production faster
* makes production the happiest place to be

For **third party providers** It also gives possibilities to build tools like application monitoring and log monitoring to be integrated through the published and versioned API’s.

When it comes to **security** though, the [twelve-factor](http://12factor.net/) comes a little bit short handed. Only in two places can you read some information that can be related to security, in chapter III. Config and IV. Backing Services, but very vague. In a collection of cloud native application patterns describing characteristics for applications in such a heterogeneous environment as the cloud, some more explicit information in security would be expected.