---
layout: details-blog
published: true
categories: blogg teknik
heading: Increased productivity with JavaRebel
authors:
  - parwenaker
tags: tools
topstory: true
comments: true
---

In my current project we are using the [JBoss Application Server](http://www.jboss.org/). Since the project in based on EJB3 and is rather extensive we have been experiencing problems with long "deployment to test"-cycles during development. We write lots of unit tests and use a test driven approach, but we also need to do lots of integration testing in the target environment since the application is heavily AJAX based. Sitting and waiting for application deployment and application server restarts is really not only wasting valuable time, but also interruptive for the creative flow that you build up during software development. But worst of all, it takes the joy out of programming.

What we have done to minimize this problem is to introduce [JavaRebel](http://www.zeroturnaround.com/javarebel) ([being renamed to JRebel](http://www.zeroturnaround.com/blog/renaming-javarebel)) together with the [FileSync Eclipse plugin](http://andrei.gmxhome.de/filesync/index.html) and exploded deployment of war archives into the development cycle. JavaRebel is a commercial tool, but I think it is very reasonable priced for what you get. What it does is that it enables reloading of Java classes on the fly. You just edit and recompile your classes in [Eclipse](http://www.eclipse.org) and the changes are picked up by the target JVM (running the app-server) without a restart or application redeploy.

JavaRebel is enabled using a [Maven plugin](http://www.zeroturnaround.com/javarebel/configuration/maven) that places a rebel.xml file into all jar and war files in our application. The rebel.xml file specifies where JavaRebel should go and look for the actual class files. In our case it is in the target directories that Eclipse uses as it's output folders. The second thing that is required is to enable a JavaRebel agent when starting the application server JVM. When the JVM is started the JavaRebel agent will start monitoring changes to classes and reload them when they are needed. It will even through plugins reload and reconfigure Spring application contexts when the xml configuration files are edited.

We use [Maven](http://maven.apache.org) as our build system, so the development cycle used to look something like this:

1. Build with maven
2. Deploy to application server
3. (wait...)
4. Test
5. Edit - and back to 1...

Now it looks like this:

1. Build ONCE with Maven
2. Deploy ONCE to application server
3. Edit/Compile/Test

The [FileSync plugin](http://andrei.gmxhome.de/filesync/index.html) is used to keep files in the exploded war archives in synch with the files in the Eclipse source folders. This enables editing in Eclipse and testing in the browser of JSP and Javascript files just by refreshing.

Keep in mind that JavaRebel does not handle all kind of file changes. If you change something that has to do with application configuration, e.g. annotations it is not picked up, but that would require a hook into the application server. You do not have to rebuild from Maven though. The only thing needed is a restart of the application server.

I definitely think that JavaRebel is a valuable, easy to setup tool that bring joy back to programming!
