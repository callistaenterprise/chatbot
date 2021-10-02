---
layout: details-blog
published: true
categories: blogg teknik
heading: Another perspective on JAX-WS portability
authors:
  - johaneltes
tags: javaee opensource soa
topstory: true
comments: true
---

JAX-WS is the Java-standard for Web-Service XML to Java POJO binding. It entered the scene in Java EE 5 and Java SE 6. I wrote a [blog entry](/2006/05/31/harmoni-mellan-jaxb-och-jaxrpc-i-javaee-5/) a while back on it's advantages over the predecessor (JAX-RPC). With WSDL-first (contract-first) design, Java POJO:s are generated from WSDL and XSD source files. The resulting Java classes and interfaces are annotated with annotations standardized by [JSR-181](http://jcp.org/en/jsr/detail?id=181). Thanks to the standard, JAX-WS-compliant service consumers and producers can be deployed into any Java EE 5 or Java SE 6 execution environment.

## JAX-WS tooling capabilities

While JAX-WS and the associated JAX-B specifications standardize how WSDL and XSD-defined services are modeled by Java classes with annotations, they do not standardize the tooling for generating Java-classes. Thus, different JAX-WS implementations have different features in terms of how and to what detail the generation process can be controlled. As an example, the [CXF](http://cxf.apache.org/) wsdl-to-java generator allows more fine-grained control of how namespaces are mapped to Java packages than does the [reference implementation ](https://jax-ws.dev.java.net/) (part of Suns Metro).

## CXF to Metro

Recently, I set up a Maven project with CXF, to build a jar of JAXWS/JAXB POJOs from a WSDL with accompanying XML Schemas. The WSDL and the schemas was from different domains (business and technical domains, which I needed to keep apart in different packages. Moreover, the schemas applied different styles of namespaces (urn versus urls). The CXF tooling allowed be to take control of the package naming for each of the involved name spaces.  The generated jar of binding POJOs was referenced/re-used (dependency) by several Java-based web service projects that consumed or produced the WSDL - all using the CXF JAX-WS runtime. When I was developing a Grails application, I had problems integrating CXF due to library clashes (different spring versions and xml parsers in Grails and CXF), so I decided to go for Metro in my Grails application.

## Discovering the obvious

Without giving it much thought, I started to configure Metros wsimport Maven plug-in (which serves the same purpose as wsdl-2-java of CXF) for my Grails application. Intuitively, I thought I would have to use Metro tooling to generate binding classes for the Metro run-time. I turned on my brain at the point when I realized the shortcomings of wsimport, with regards to mapping name-spaces to Java packages. Why should I have to use Metro tooling? Portability of JAX-WS (thanks to JSR-181) does not only allow me to deploy to different JAX-WS run-time libraries / Java EE-containers - it also gives me the option of choing one vendors wsdl-to-java tooling over anothers! Yes, yes - obvious, but it didn't strike me as a value until recently, I must admit. So from now on, CXF is my preferred WSDL-to-java tooling, regardless of JAX-WS implementation to be used at run-ime.

This is how CXF allows me to control name-space-to-package mappings (maven sample):

**CXF**

~~~ markup
<plugins>
  <plugin>
    <groupId>org.apache.cxf</groupId>
    <artifactId>cxf-codegen-plugin</artifactId>
    <version>${cxf.version}</version>
    <executions>
      <execution>
        <id>generate-sources</id>
        <phase>generate-sources</phase>
        <configuration>
          <sourceRoot>
            ${basedir}/target/generated/src/main/java
          </sourceRoot>
          <wsdlOptions>
            <wsdlOption>
              <extraargs>
                <extraarg>-p</extraarg>
                <extraarg>
                  urn:se:namespace1:v1=se.callista.namespace1.v1
                </extraarg>
                <extraarg>-p</extraarg>
                <extraarg>
                  http://namespace2.se/v1=se.callista.namespace2.v1
                </extraarg>
              </extraargs>
              <wsdl>
                ${schema.path}mywsdl.wsdl
              </wsdl>
            </wsdlOption>
          </wsdlOptions>
        </configuration>
        <goals>
          <goal>wsdl2java</goal>
        </goals>
      </execution>
    </executions>
  </plugin>
</plugins>
~~~

In Metro, I can only control the package mapping for the target namespace of the WSDL, not for the schema name-spaces. The others will be mapped to package names by default rules (which is usually in conflict with the package naming standards with a company):

**Metro**

~~~ markup
<plugins>
  <plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>jaxws-maven-plugin</artifactId>
    <executions>
      <execution>
        <goals>
          <goal>wsimport</goal>
        </goals>
      </execution>
    </executions>
    <configuration>
      <packageName>se.callista.namespace1.v1</packageName>
      <wsdlDirectory>${schema.path}</wsdlDirectory>
      <wsdlFiles>
        <wsdlFile>mywsdl.wsdl</wsdlFile>
      </wsdlFiles>
    </configuration>
    <dependencies>
      <dependency>
        <groupId>com.sun.xml.ws</groupId>
        <artifactId>jaxws-tools</artifactId>
        <version>2.1.2</version>
      </dependency>
    </dependencies>
  </plugin>
</plugins>
~~~
