---
layout: details-blog
published: true
categories: blogg teknik
heading: Remote deploy to Tomcat 7 using Cargo
authors:
  - marcuskrantz
tags: agile build buildautomation tools
topstory: true
comments: true
---

One of the last days in my current project I was about to freeze the codebase and finish things up. Luckily, I had a couple of hours left to play around with something that I have been thinking about throughout the project but never had time to implement. My mission was to deploy the application to a remote tomcat container. The requirements I made up was:

- Maven-based (no custom schell scripting :)
- Minimal configuration
- Multiple servers (test, qa, production)
- Application server independent

After some research, I found Cargo that seemed to meet my requirements and I decided to try it out. I used the following setup to test Cargo:

- Apache Tomcat 7.0.26
- Maven 3.0.3
- example.war deployed in my local maven repository

## 1. Create maven deployer project
First of all I created a new empty project called `example-deployer`, the idea was to use this project to deploy my `example.war` to various servers:

~~~
$ mvn archetype:generate -Dversion=1.0-SNAPSHOT -DgroupId=org.example -DartifactId=example-deployer -Dpackaging=pom
~~~

## 2. Create maven profiles
Next, I wanted to be able to deploy to two different servers: `qa` and `production`. Since I used different ports, different protocols and different context paths for these two environment I created two Maven profiles that can be activated using the `env-property`. In these two profiles I set property values for each environment.

~~~ markup
<profiles>
  <profile>
    <id>prod</id>
    <activation>
      <property>
        <name>env</name>
        <value>prod</value>
      </property>
    </activation>
    <properties>
      <remote.protocol>https</remote.protocol>
      <remote.port>443</remote.port>
      <remote.hostname>prod.example.org</remote.hostname>
      <remote.context>/</remote.context>
    </properties>
  </profile>
  <profile>
    <id>qa</id>
    <activation>
      <property>
        <name>env</name>
        <value>qa</value>
      </property>
    </activation>
    <properties>
      <remote.protocol>http</remote.protocol>
      <remote.hostname>qa.example.org</remote.hostname>
      <remote.port>8080</remote.port>
      <remote.context>/qa</remote.context>
    </properties>
  </profile>
</profiles>
~~~

It is now possible to activate the qa or prod profile by adding `-Denv=prod` or `-Denv=qa`

## 3. Configure Cargo
I was surprised how easy it was to configure Cargo's maven plugin. There are basically three blocks of configuration 1) The container to use, 2) Configuration how to access the container and 3) the war-artifact to deploy to the remote container.

Since I do not want to exploit the username and password to the application server, I enter these manually during deploy time. Here is the configuration used:

~~~ markup
<build>
  <plugins>
    <plugin>
      <groupId>org.codehaus.cargo</groupId>
      <artifactId>cargo-maven2-plugin</artifactId>
      <version>1.2.0</version>
      <configuration>
        <container>
          <containerId>tomcat7x</containerId>
          <type>remote</type>
        </container>
        <configuration>
          <type>runtime</type>
          <properties>
            <cargo.hostname>${remote.hostname}</cargo.hostname>
            <cargo.protocol>${remote.protocol}</cargo.protocol>
            <cargo.servlet.port>${remote.port}</cargo.servlet.port>
            <cargo.remote.username>${remote.user}</cargo.remote.username>
            <cargo.remote.password>${remote.pass}</cargo.remote.password>
          </properties>
        </configuration>
        <deployer>
          <type>remote</type>
          <deployables>
            <deployable>
              <groupId>${project.groupId}</groupId>
              <artifactId>example-web</artifactId>
              <type>war</type>
              <properties>
                <context>${remote.context}</context>
              </properties>
            </deployable>
          </deployables>
        </deployer>
      </configuration>
    </plugin>
  </plugins>
</build>
~~~

The last thing we need to add to the configuration is to include a dependency to the war-artifcact that we want to deploy.

~~~ markup
<dependencies>
  <dependency>
    <groupId>org.example</groupId>
    <artifactId>example-web</artifactId>
    <version>${project.version}</version>
    <type>war</type>
  </dependency>
</dependencies>
~~~

It is now possible to deploy to out qa or prod server. Note that if we don't want to expose the username and password in the script (that probably is in our source code repo) we can force the user to specify them on the command line. We are now ready to deploy, execute the following command:

~~~
mvn cargo:deploy -Denv=qa -Dremote.user= -Dremote.pass=
~~~

The example above does not work out of the box without some configuration of the application server. For example, in the Apache Tomcat case, you will need the manager web application to be deployed and configured to allow username/password access of a certain user. You can find all the details in the reference documentation as well as in the Apache Tomcat container documentation:

- [Cargo Reference Documentation](http://cargo.codehaus.org/Maven2+Plugin+Reference+Guide)
- [Cargo Tomcat Reference](http://cargo.codehaus.org/Tomcat+7.x)
