---
layout: details-blog
published: true
categories: blogg teknik
heading: Groovy as a job control language
authors:
  - johaneltes
tags: dynamiclanguages opensource
topstory: true
comments: true
---

If you need to automate a fairly complex process - like a batch job - Groovy may come in handy. Designing a Java batch job is typically a task that involves the following mechanisms:

- Job control infrastructure that triggers the job as a shell command
- A script that (e.g. ant) that initializes the class path and triggers the main class
- A main class that implements the job control logic
  1. Create POJOs from input XML
  2. Execute the batch business logic by invoking service pojos in multiple components (jar files)
  3. Produce the output XML files

It is generally cumbersome to realize most  of these mechanisms and steps in Java. Ant is nice for very high-level tasks, but doesn't solve the jar distribution problem in a nice way. Batch processing logic typically involve processing that is complex in Java - or at least complex to set-up in Java: Parsing XML into POJOs (Full binding with JAXB complicate the build process and is usually not necessary). We may not even have a schema. Next, batch processing in Java is often about comparing, sorting, merging and filtering of POJOs, an creating new result structures to be serialized in XML. If you once did this kind of processing in Smalltalk or Ruby, you start dreaming of what you could have done in your spare time if you didn't have to work around the clock coding Java iteration logic.

## Groovy and friends to the rescue

Well, Smalltalk or Ruby may not be an option, if you are required to solve your problem without impact on what's deployed on your batch execution environment. Groovy is a language built on the JDK, that shares a lot (but not all) of the expressiveness of Ruby. It is distributed as a jar, so you really don't need to install anything, as long as you have access to a Maven repo with `groovy-all-1.5.jar` (and of cause - have Maven installed).

Groovy is not only a dynamic language for the JVM - it also has the JDK as its object model. Your Java code and Groovy code shares the same object model.

## Ant and Maven with Groovy

To simplify packaging and class-path management of the batch and all its required jars (the logic as well as utility jars), [Maven](http://maven.apache.org) dependency management does a good job. [Ivy](http://ant.apache.org/ivy/) is another option. I've chosen Maven, since it used by most of our customers. We are not concerned with software build and release management - but batch processing. It would be both complex and artificial to use Maven to initialize the process. Using Ant as the shell command script we can benefit from Maven dependency management by using a [Maven ant task](http://maven.apache.org/ant-tasks.html) for resolving the class-path by automatically pulling the required jars from the maven repo (only the first time, of cause - there after, they will be in the local repo of the batch user). This will include a dependency to the Groovy runtime jar. That way, we can bootstrap our scripting language at the same time as we resolve all dependencies of the Groovy batch script. The complete distribution of the batch script will consist of the following artifacts:

- The bootstrapping ant script
- A maven POM that declares the dependencies
- The Groovy script file (which may contain multiple Groovy classes)

The best of all: The ant script `MyBatch.xml` is as simple as this:

~~~ markup
<project basedir="." default="run" xmlns:artifact="antlib:org.apache.maven.artifact.ant" >
  <description>
    Bootstrap Groovy, the Groovy script and its dependent jars.
    Pre-reqs: 1. Ant 1.6 installed
	          2. Maven 2.0.9 (for access of maven properties) installed
              3. Maven ant task jar deployed to the ant lib directory
  </description>

  <artifact:pom id="maven.project" file="pom.xml" />

  <artifact:dependencies pathId="dependency.classpath">
    <pom refid="maven.project"/>
  </artifact:dependencies>

  <taskdef name="groovy"
      classname="org.codehaus.groovy.ant.Groovy"
      classpathref="dependency.classpath"/>

  <target name="run" description="Run the groovy script">
      <!-- Groovy has access to Ant properties, but not Maven properties.
 	       We need to re-bind maven properties (i.e. defined in
	       settings.xml of the batch user) to ant properties,
	       in order to get them into the scope of the Groovy script.
	       In this sample, the script needs access to the svn credentials
	       of the batch user. To avoid redundant specification of
	       credentials within an ant properties file or in the script
	       itself, we pull them from the maven settings file. -->
    <property name="svnuser" value="${maven.project.properties.svnusername}"/>
    <property name="svnpassword" value="${maven.project.properties.svnpassword}"/>
    <groovy src="MyGroovyBatch.groovy" />
  </target>
</project>
~~~

The Maven POM is just as minimalistic. It simply declares the dependencies:

~~~ markup
<project>
<!--
    This pom only serves the ant script with dependency management.
    It is never used to run mvn - only as support for the maven ant task used by build.xml.
-->
  <modelVersion>4.0.0</modelVersion>
  <artifactId>my-batch-dependencies</artifactId>
  <groupId>se.callistaenterprise.groovybatches</groupId>
  <version>1.0</version>
  <dependencies>
    <dependency>
	  <!-- This is the groovy runtime AND the groovy ant task -->
      <groupId>org.codehaus.groovy</groupId>
      <artifactId>groovy-all</artifactId>
      <version>1.5.4</version>
    </dependency>
    <dependency>
      <groupId>my.business.logic-components</groupId>
      <artifactId>business-logic-used-by-batch</artifactId>
      <version>1.0</version>
    </dependency>
    <dependency>
      <groupId>my.utils</groupId>
      <artifactId>my-opensource-util</artifactId>
      <version>1.0</version>
    </dependency>
  </dependencies>
</project>
~~~

And finally, the Groovy script named `MyGroovyBatch.groovy`:

~~~ groovy
println "The groovy batch says hello to ${properties.svnuser}"
ant.echo "I can still use ant from in here, using the Ant DSL"
~~~

The shell command:

~~~
$ ant -f MyBatch.xml
~~~
