---
layout: details-blog
published: true
categories: blogg teknik
heading: Getting started with Sonar to manage your technical debt
authors:
  - christianhilmersson
tags: buildautomation javaee tools sonar technicaldept
topstory: true
comments: true
---

In fast evolving projects you are most certain to find some kind of technical debt. As architects and developers we are always looking for the best mix of flexibiltiy, clarity and maintainability in our code base. To maintain the quality of the code most project have a set of coding standards and architectural guidelines which the team should be aware of and follow. Nevertheless I've noticed that, and I'm sure most of you have seen or experienced this, when projects are working under hard time pressure these things tend to be put aside in favor of making the delivery on time.

In the best case this leads to post delivery activities in terms of cleaning up and documenting the code but my observations tell me that most often the code is left as it is, making it harder to maintain. In my opinion it is desirable to be able to coop with such problems at a much earlier stage.

Wouldn’t it be great to have a tool for helping you find and pinpoint potential problems early on, even integrated as a part of your continuous builds and also directly from inside your IDE?

## Sonar
Sonar is a software that analyzes your code base and displays parameters related to technical debt. Primarily it is built for Java projects but through the use of plugins it is also possible to analyze other languages as well. The software is very well suited for projects built with Maven but there are also ways of analyzing other types of projects.

If you are familiar with tools like Checkstyle you should rather quickly grasp the value of the tools that Sonar brings in terms of managing your code base and keeping it neat and clean.

### The fundamentals
The concept is that Sonar runs as a server application that collects data from your code through a Maven plugin. The analyzed data can then easily be viewed in the web GUI included with the server application or through other tools such as the Eclipse plugin. The Eclipse plugin integrates great with the IDE and lets the developer jump between the analysis and the code instantly which eases the work of correcting problems pointed out in the analysis.

The default setup covers the most common metrics of technical debt, such as coding standard alignment, code coverage of tests and a lot more. It is also  possible to add plugins that measures additional parameters of the code. The Sonar site reports that there currently are more than 30 plugins available in addition to the default behavior.

### Continuous code analysis
Sonar currently integrates with the following continuous integration engines, which makes it easy to keep your analysis up to date down to each code change:

- Bamboo
- Hudson
- Continuum 1.2
- Cruise Control
- TeamCity

For more information on setting up Sonar with your continuous integration engine read here: [http://docs.codehaus.org/display/SONAR/Collect+data#Collectdata-Continuousintegrationengines](http://docs.codehaus.org/display/SONAR/Collect+data#Collectdata-Continuousintegrationengines)

### The Eclipse plugin
The Eclipse plugin is available at the following update site: http://dist.sonar-ide.codehaus.org/eclipse/

In Eclipse:


- Open the **Help** Menu and click on **Install New Software...**
- In the field **Work with**, enter: `http://dist.sonar-ide.codehaus.org/eclipse/`
- Check the **Sonar integration for Eclipse** and follow the installation wizard.

After the installation, Eclipse is restarted and a new Sonar perspective is added to the Eclipse and you can associate projects with Sonar.

More information about the Eclipse plugin is available here: [http://docs.codehaus.org/display/SONAR/Sonar+Eclipse](http://docs.codehaus.org/display/SONAR/Sonar+Eclipse)

## Getting started
In this section I will explain a really quick way to get going with the Maven project of your own choice.

### Prerequisites
Download the latest version from [http://www.sonarsource.org/downloads/](http://www.sonarsource.org/downloads/)

For this tutorial I use Sonar version 2.4.1

Make sure you are using the following:

- JDK version 1.5 or higher (check by running `javac –version`in a console)
- Maven of version 2.0.9 or higher (check by running `mvn –version` in a console)

Sonar persists the collected analysis data to a database and there are built in support for most of the major db vendors. Fortunately we don’t have to bother about that choice for now since Sonar ships with a default configuration which uses an embedded Derby server which will work just perfect for the needs in this article.

### Start the server

1. Unpack the sonar zip to a folder of your choice (make sure the user that run Sonar has write permissions to the unpacked folder)
2. Enter the newly unpacked folder and run:

On windows

~~~
$ cd bin\windows-x86-32
$ StartSonar.bat`
~~~

On other systems

~~~
$ cd bin/[OS]
$ ./sonar.sh console
~~~

### Analyze your project
Sonar requires the project to be built at least once before it can do the analysis with the plugin. So before starting the plugin that is performing the actual analysis we do a clean build. Since the plugin (sonar:sonar) runs all tests during the analysis we first run the clean build with tests disabled and then the tests will run when the plugin is activated.

Enter the folder of the Maven project you want to analyze and run the following:

~~~
$ mvn clean install –Dmaven.test.skip=true
~~~

Followed by the actual analysis, which also will run the tests:

~~~
mvn sonar:sonar
~~~

### Watch the result
Open a web browser and enter [http://localhost:9000](http://localhost:9000/) in the URL field, click on your project and enjoy your metrics.

## References
Information in this article were found on [http://www.sonarsource.org/](http://www.sonarsource.org/) where you also can find more information about Sonar.
