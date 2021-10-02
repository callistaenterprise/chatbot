---
layout: details-blog
published: true
categories: blogg teknik
heading: Debugging Groovy in Eclipse
authors:
  - johaneltes
tags: dynamiclanguages
topstory: true
comments: true
---

As [Groovy ](http://groovy.codehaus.org) becomes integrated in more and more environments, the IDE support is slowly improving. There are many options for editing Groovy, but well-integrated debugging has so far been the privilege of [IntelliJ Idea](http://www.jetbrains.com/idea/) users.

In terms of refactoring, IntelliJ is still outstanding for Groovy developers. But there is a solution to the basic needs for Eclipse developers. IBMs mash-up platform WebSphere sMash hosted by the open source [Project Zero ](http://www.projectzero.org/) bundles an Eclipse editor and debugger for Groovy. Although developed under the umbrella of Project Zero, the Groovy plug-in is generally applicable to any Java project using Eclipse that needs to integrate Groovy development.

Using this plug-in, you can add Groovy coding to any project. It even supports WTP, with full dynamic compilation. As with Java classes, you don't need to rebuild / redeploy / restart Tomcat while debugging web applications in WTP. Just edit, save and refresh in browser.

Project Zero does not provide documentation on how to set it up for general use (outside of sMash development), so I thought I share my experience of doing so. It is fairly straight forward. The checklist assumes that you have a Java/Java EE project in your Eclipse workspace. I've used the Ganymede Enterprise Development distribution of Eclipse 3.4.

Here we go:

1. Use the update manager in eclipse to install the sMash plug-in for Eclipse: [http://www.projectzero.org/zero/silverstone/latest/update/zero.eclipse/](http://www.projectzero.org/zero/silverstone/latest/update/zero.eclipse/)
2. Add the Groovy nature to your Java project using the context menu (right-click on the project / **Groovy/Add Groovy Nature**
3. In the project properties dialog:
   * Select **Java Build Path** and add your Groovy source folders (main + test folders)
   * Select **Groovy Project Properties** and update the **Groovy compiler output location** if needed. In case you build with maven, change it to `target/classes`.
4. In case you changed the **Groovy compiler output location** in the project properties dialog, you need to clean the project, to make it "hit". Use menu **Project/Clean..**.

Happy Groovy debugging in Eclipse!
