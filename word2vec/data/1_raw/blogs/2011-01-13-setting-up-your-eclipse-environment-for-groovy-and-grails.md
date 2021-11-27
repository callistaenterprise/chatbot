---
layout: details-blog
published: true
categories: blogg teknik
heading: Setting up your Eclipse environment for Groovy and Grails
authors:
  - christianhilmersson
tags: dynamiclanguages tools eclipse grails groovy springsourcetoolsuite
topstory: true
comments: true
---

This article covers how to setup your standard Eclipse environment with plugins from SpringSource for developing Groovy and Grails applications without using the full SpringSource Tool Suite.

-[readmore]-

## Background
It is more and more common that we see other languages than Java running on the JVM. One such language is Groovy which together with the Ruby on Rails inspired framework Grails forms a good platform for rapid development of simple web applications.

SpringSource Tool Suite is an extended Eclipse with support for a lot of interesting things. There’s is good support for developing Groovy and Grails applications in the SpringSource Tool Suite IDE, easy to setup via the built-in extension mechanism which is available in the Extensions tab on the STS Dashboard.

If however, we are interested in developing Groovy and Grails applications and don’t care so much about all the other stuff that SpringSource Tool Suite is packaging it is possible to pick out only the plug-ins that we need from the SpringSource Tool Suite and apply them to a clean Eclipse version.

This article presents a way of setting up a development environment for Groovy and Grails inside Eclipse.

## Download Java Development Kit
Some of the functionalities in the Grails framework requires you to have a JDK installed.

Make sure that you have a JDK of version J2SE 1.6 installed and that your `JAVA_HOME` environment variable points to the JDK and that Eclipse uses it on the build path of your projects, otherwise follow the instructions below.

- Go to the [JDK Download page](https://cds.sun.com/is-bin/INTERSHOP.enfinity/WFS/CDS-CDS_Developer-Site/en_US/-/USD/ViewProductDetail-Start?ProductRef=jdk-6u23-oth-JPR@CDS-CDS_Developer) at Oracle and download Java SE Development Kit 6u23.
- Follow the instructions in the installer to install the JDK on your computer.
- Make sure that the `JAVA_HOME` environment variable exists and points at your installed JDK `JAVA_HOME="c:\Program Files\Java\jdk1.6.0_23"`
- Start Eclipse and open **Preferences/Java/Installed JREs**
- Click **Add...**, Choose **Standard VM** and click **Next**.
- Click **Directory** and choose the home folder of your JDK (e.g. `c:\Program Files\Java\jdk1.6.0_23`)
- Click **Finish** to get back to the preferences.
- Use the checkbox next to the JDK to activate it.
- Click **OK** to save settings and close preferences.

## Installing the Eclipse plug-ins
We will start with a clean version of Eclipse 3.6.1 from Eclipse’s download page and install the plug-ins we need.

- Open a browser and go to [http://www.eclipse.org/downloads](http://www.eclipse.org/downloads)
- Download the package named:  **Eclipse IDE for Java EE Developers**
- Unpack the downloaded package in the location of your choice and start Eclipse.
- Open up **Install New Software** under the Help menu.
- Add two update sites
	1. SpringSource update site for Eclipse 3.6 Release
	   [http://dist.springsource.com/release/TOOLS/update/e3.6](http://dist.springsource.com/release/TOOLS/update/e3.6)
	2. SpringSource update site for Eclipse 3.6 Release dependencies
	   [http://dist.springsource.com/release/TOOLS/composite/e3.6](http://dist.springsource.com/release/TOOLS/composite/e3.6)
- Back in the **Install New Software** window, choose to work with: **SpringSource update site for Eclipse 3.6 Release**
- Select **SpringSource Tool Suite Grails Support** under the category **Extensions / STS**
- Press the **Next** button and follow the wizard to complete the installation. The installation might seem to be stuck at zero percent for a couple of minutes, just be patient. You will also get a warning that you are trying to install unsigned content which is normal in this case.
- Restart Eclipse
- You might get a question about uploading data to SpringSource with Spring User Agent Analysis, which you can answer in the way you want.

## Adding the Grails framework
To make the plug-ins work we also need to download the Grails framework.

- Open up a browser and go to[ http://www.grails.org/Download](http://www.grails.org/Download)
- Choose to download version 1.3.6 Binary Zip
- Unpack the Grails framework where you like to store your development tools e.g. `c:\tools`
- Add an environment variable `GRAILS_HOME` that points to your Grails installation folder (Not mandatory when running Grails inside Eclipse) `GRAILS_HOME=c:\tools\grails-1.3.6`
- Also update the `PATH` environment variable to point at `${GRAILS_HOME}\bin` (Not mandatory when running Grails inside Eclipse) `PATH=%PATH%;%GRAILS_HOME%\bin`
- In Eclipse, go to **Preferences/Groovy/Grails** and **Add…**
- Enter **Grails** in the **Name** field.
- Press **Browse...** and point out the the root folder of your unzipped your Grails framework e.g. `c:\tools\grails-1.3.6`
- Press **OK**.

Your Eclipse environment is now ready for developing Groovy and Grails applications.

## Simple Groovy script to test your setup
Follow these steps to perform a simple test to see that Groovy now works inside Eclipse. As a side effect you also get a shortcut to a great tool for trying out groovy scripts, the Groovy Console.

### Enter the Grails perspective
You should now have a Grails perspective in Eclipse.

- Choose **Open Perspective/Other...** from the **Window** menu
- Select **Grails** and click **OK**

### Create a Groovy project
- Right click in the **Project Explorer** and open **New/Other...**
- Select **Groovy Project** and click **Next**
- Add a project name e.g. **GroovyConsole** and click **Finish**

## Create a Groovy class
- Right click your project named **GroovyConsole** and open **New/Other...**
- Select **Groovy Class** and click **Next**
- Enter **GroovyConsole** in the name field, check the **Create Script** select box and click **Finish**
- Open the newly created file `GroovyConsole.groovy` and insert the following code:

~~~ groovy
import groovy.ui.Console
def console = new Console()
console.run()
~~~

* Save the file.

### Run the Groovy class
Right click `GroovyConsole.groovy` and click on **Run As/Groovy Script**

- You shall now get a Groovy Console opened which verifies that Groovy is working inside Eclipse. You can also use the Groovy Console for testing groovy scripts.

## Links and references
For more information about the technologies and tools used in this article there is more to read on these locations:

- Groovy – [http://groovy.codehaus.org/](http://groovy.codehaus.org/)
- Grails – [http://www.grails.org/](http://www.grails.org/)
- SpringSource Tool Suite – [http://www.springsource.com/developer/sts](http://www.springsource.com/developer/sts)
- Eclipse – [http://www.eclipse.org/](http://www.eclipse.org/)
