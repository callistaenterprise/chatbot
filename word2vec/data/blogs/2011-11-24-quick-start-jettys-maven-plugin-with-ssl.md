---
layout: details-blog
published: true
categories: blogg teknik
heading: Quick Start - Jetty's maven plugin with SSL
authors:
  - marcuskrantz
tags: build tools
topstory: true
comments: true
---

Speed is the key. I often need a web server in order to run a web application I developed to try things out. Setting up this infrastructure can often be quite tedious but if the only thing you need is a servlet container I often use the approach described in this article. We start out with nothing except Maven and Java installed.

-[readmore]-

Create a web application project:

~~~
$ mvn archetype:generate -DgroupId=org.example -DartifactId=example-server -DarchetypeArtifactId=maven-archetype-webapp -Dversion=1.0
~~~

This gives us a new directory (`example-server`) which is a Maven web application project. To run the web application, we configure the maven-jetty-plugin. Add the following configuration to project's `pom.xml`.

~~~ markup
<build>
  <finalName>example-server</finalName>
  <plugins>
    <plugin>
      <groupId>org.mortbay.jetty</groupId>
      <artifactId>maven-jetty-plugin</artifactId>
      <version>6.1.26</version>
    </plugin>
  </plugins>
</build>
~~~

Enter the `example-server` directory and do:

~~~
$ mvn jetty:run
~~~

As soon as the server is started you can enter the following url in your browser.

~~~
http://localhost:8080/example-server
~~~

As you can see, the server is started and listens on port 8080 by default. If you want to change this, it can easily be configured. Just extend the plugin with a configuration element and add a connector.

~~~ markup
<plugin>
  <groupId>org.mortbay.jetty</groupId>
  <artifactId>maven-jetty-plugin</artifactId>
  <version>6.1.26</version>
  <configuration>
    <connectors>
      <connector implementation="org.mortbay.jetty.nio.SelectChannelConnector">
        <port>9090</port>
      </connector>
    </connectors>
  </configuration>
</plugin>
~~~

## Adding TLS/SSL support
Assume you want to communicate in a secure way. The only thing you need to do is to add another connector element and specify a keystore containing the server's certificate. If you don't know how to create a certificate for your server, you can read my other blog post [Creating self-signed certificates for use on Android](/blogg/teknik/2011/11/24/creating-self-signed-certificates-for-use-on-android/). Simply add the following connector element and make sure the `server.jks` is located in your `example-server` directory:

~~~ markup
<connector implementation="org.mortbay.jetty.security.SslSocketConnector">
  <port>9443</port>
  <keystore>${basedir}/server.jks</keystore>
  <password>password</password>
  <keyPassword>password</keyPassword>
</connector>
~~~

You can test this in a nice way using openssl to see what the server returns when you try to access it on port 9443.

~~~
$ openssl s_client -connect localhost:9443
~~~

Finally, if you for some reason want mutual authentication, you also need to specify a trust store in which the server keeps certificates of trusted clients. Extend the previous connector with the following information:

~~~ markup
<connector implementation="org.mortbay.jetty.security.SslSocketConnector">
  <port>9443</port>
  <keystore>${basedir}/server.jks</keystore>
  <password>password</password>
  <keyPassword>password</keyPassword>
  <truststore>${basedir}/serverTruststore.jks</truststore>
  <trustPassword>password</trustPassword>
  <needClientAuth>true</needClientAuth>
</connector>
~~~

Now you have a web server up and running your web application with mutual authentication. The clients must provide a valid certificate in order to communicate with the server. At last I just want to add a final element to our configuration. Since TLS/SSL can be quite horrible to troubleshoot, I add the following configuration which gives a lot of nice output :)

~~~ markup
<systemProperties>
  <systemProperty>
    <name>javax.net.debug</name>
    <value>ssl</value>
  </systemProperty>
<systemProperties>
~~~

Have fun!

## References
* [Maven Jetty Plugin](http://docs.codehaus.org/display/JETTY/Maven+Jetty+Plugin)
* [Maven Webapp Archetype](http://maven.apache.org/guides/mini/guide-webapp.html)
