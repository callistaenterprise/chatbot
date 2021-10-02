---
layout: details-blog
published: true
categories: blogg teknik
heading: Metamorphosis - The screwdriver turns into a nuclear plant
authors:
  - bjornbeskow
tags: tdd
topstory: true
comments: true
---

Continuous Integration servers have been around for quite a number of years. Mostly out of slentrian, I have stuck to CruiseControl since the alternatives (AntHill, Continuum, Hudsun, ...) just haven't been that much better to motivate me to switch.

I just attended Kuhsuke Kawaguchi's [Hudson](https://hudson.dev.java.net/) presentation at [JavaZone](http://jz09.java.no/), and got quite a surprise. When I looked at Hudson last time (yes, it was a time ago), it was just another CI server with a nice web GUI. The presentation today showed a completely different creature. Build distribution and scalability has obviously been the focus in the Hudson team, and the latest Hudson version comes with an extremely ambitious Clustering mechanism:

- Several nodes collaborate in a Master-Slave setup, with support for at least up to 100 slaves.
- Master and slaves may run on heterogeneous hardware, with support for Solaris, most Linux dialects as well as windows.
- Slaves can be automatically configured from the Master: when a new Slave node is added, it can have a specified version of the JVM, Ant and Maven libraries downloaded and installed automatically. Using the Hudson PXE protocol, a new slave node can even boot over the network, have the operating system installed from the Master before continuing the bootstrap!
- Slave node system resources (disk space, wap space, memory etc) can be automatically monitored by the Master, and slave nodes are automatically put offline if they degenerate
- The cluster utilization itself is constantly monitored: How many nodes are busy? How long is the job queue? Using the Hudson [EC2](http://aws.amazon.com/ec2/) plugin, new Slave nodes can even be allocated dynamically in the Cloud, on demand!
- You can even run other clustered applications like [Hadoop](http://hadoop.apache.org/) or [Selenium Grid](http://selenium-grid.seleniumhq.org/) on a Hudson cluster!

Wow! Not what I was looking for, but really cool stuff.
