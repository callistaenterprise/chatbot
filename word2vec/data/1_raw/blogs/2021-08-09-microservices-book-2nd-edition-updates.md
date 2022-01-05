---
categories: blogg teknik 
layout: details-blog
published: true
topstory: true
comments: true
authors: 
  - magnuslarsson
tags: Java SpringFramework SpringBoot SpringCloud Kubernetes Istio SpringNative GraalVM WSL2
heading: The second edition of my book "Microservices with Spring Boot and Spring Cloud" is now released!
---

The 2nd edition contains many updates using the latest versions of the tools and frameworks covered by the book. It also includes two major additions: support for Windows using WSL 2 and compiling Java-based microservices to native images using Spring Native and GraalVM. In this blog post, I will go through the most significant changes and news.

-[readmore]-

Since the 1st edition was published in September 2019, a lot of exciting new versions have been released by the open source projects used in the book. Last autumn, my publisher asked me if I was interested in producing an updated version of the book. On July 29th, the 2nd edition of my book was published:

<a href="https://www.amazon.com/Microservices-Spring-Boot-Cloud-microservices/dp/1801072973?maas=maas_adg_622CDDFFC9492AD632A6DB9B3E4FC3E0_afap_abs&ref_=aa_maas"><img src="/assets/blogg/microservices-book-2nd-edition-updates/cover.jpg" height="400"></a>

> If you are interested in a complete overview of the content in the book, I will cover that in a few blog posts as well, [here is part 1](https://callistaenterprise.se/blogg/teknik/2021/10/11/microservices-book-2nd-edition-part1/) for now. 

Let's start looking at the new support for Windows using WSL 2 and native compile: 

1. **Support for Windows 10 and WSL 2**   

   The 1st edition only describes how to run the examples in the book on a Mac. One of the main goals of the 2nd edition was to add support for running the examples on a Windows PC. To run the same commands as used on a Mac, Windows Subsystem for Linux v2 (WSL 2) is used to run a Linux server on the Windows PC. All commands for building, running, and testing the microservices are executed on the Linux server using Windows Terminal. Tools that require a user interface, like an IDE (Visual Studio Code) and a Web Browser, run in Windows. Docker runs in a separate WSL 2 instance, reachable from both Windows and the Linux server.

   The following screenshot demonstrates how the microservices are deployed in Kubernetes using Minikube in WSL 2. Windows Terminal is used to run a load test and check the status of the Pods in Kubernetes. The source code is edited in Visual Studio Code using its Remote WSL extension, and the traffic that flows through the microservices is monitored in a Web Browser using Istio and Kiali also deployed in Kubernetes:
       
    ![Win10/WSL2 screenshot](/assets/blogg/microservices-book-2nd-edition-updates/Win10WSL2.png)

2. **Compiling Java-based microservices to native images**  

    The second main goal of the 2nd edition was to describe how we can use the emerging technology for compiling Java-based microservices to native images. Thus, the book's last chapter explains how to use the current beta version of Spring Native and the underlying GraalVM to compile a microservice into a Docker image containing a native executable. One of the main benefits of a native image is a dramatically reduced startup time compared to using the Java VM. However, it comes at the price of a long compile-time. Furthermore, since Spring Native is still in beta, not all tools and frameworks in the Spring ecosystem are fully supported. But this is an exciting technology to keep an eye on for the future.  

    Below is an example where a microservice from the book compiled to a native image starts in 0.644 seconds. To compare, starting up the microservice using the Java VM takes around 13 seconds in the same environment, 20 times slower!

    ![Spring Native demo](/assets/blogg/microservices-book-2nd-edition-updates/SpringNative.gif)

Besides these two additions, the most important news and changes are:

1. **Upgraded to Spring Boot v2.5.2 and Spring Cloud 2020.0.3**  
   The 2nd edition is updated to use new features introduced in Spring Boot v2.3 - v2.5, for example:
          
    1. Updated the source code to use the new Configuration File Processing. Specifically, the `spring.profiles` property has been replaced with the new `spring.config.activate.on-profile` property.
    2. Updated the source code to use the new generic way of importing additional configuration files. The new property `spring.config.import` is used to import files from the Spring Cloud Config Server.
    3. Creating optimized Docker images based on `layered jars` instead of the traditional `fat-jar` using Spring Boot's **layer extraction tool**.
    4. Using **Graceful Shutdown** and the support for **Liveness** and **Readiness probes** to run the microservices smoothly on Kubernetes. 
    5. Using **Cloud Native Buildpacks** to build Docker images when building native compiled Docker images.
    6. Using the support for Java 16 and Gradle v7.

    Finally, regarding Spring Boot, the reactive parts of the source code have been both simplified and more robust. For Spring Cloud Stream, the functional and reactive programming model introduced in v3.0.0 has been applied when interacting with message brokers, i.e. RabbitMQ and Kafka. This means, for example, that Java's functional interface `Consumer` is used to declare consumers of the events published through a message broker. 
  
2. **Upgraded to Java 16 and Gradle 7**.  
   Since many Java developers still use Java 8 (including most of the customers I work with), all source code is written using Java 8 syntax. But in runtime, a Java 16 JRE is used.

3. **Using Testcontainers instead of embedded databases for integration tests**  
With Testcontainers, the same database engines used in production can be used when running integration tests with JUnit.

4. **Upgraded to JUnit 5**

5. **Replaced SpringFox with springdoc-openapi for producing OpenAPI documentation on the fly**  
The SpringFox project is no longer actively maintained, and the migration to the springdoc-openapi project is a no-brainer.

6. **Replaced the authorization server from the deprecated Spring Security OAuth project with Spring Authorization Server**

7. **Updated usage of OAuth to be compliant with the upcoming OAuth 2.1 specification**  
No more usage of Implicit and Resource Owner Password Credentials grant flows.

8. **Simplified setup of the OIDC provider in Auth0**  
The central part of the configuration required for the Auth0 account is automated.

9.  **Upgraded to Resilience4j 1.7.0**  
Older versions of Resilience4j do not work with Spring Boot using version 2.4 or newer.

10. **Upgraded to Minikube 1.18.1**  
The driver for VirtualBox is replaced with the driver for HyperKit on macOS and the Docker-driver on Windows/WSL2. This results in faster startup times for the Kubernetes clusters and overall lower resource usage.

11. **Upgraded to Kubernetes to 1.20.5**  
Simplified use of the `cert-manager` for automated issuing and provisioning of certificates. Using self-signed certificates instead of the cumbersome setup of `ngrok` and `Let's Encrypt` in a development environment (with no fixed and public IP address).

12. **Replaced Kustomize with Helm 3 to configure the deployments in Kubernetes**  
Common boilerplate definitions in the Kubernetes `yaml` files have been extracted using Helm `library` charts. The microservices have their own chart definition. Each runtime environment is defined in a `parent chart`, where the microservices' charts are used as `subcharts` to describe the runtime components in each environment's system landscape.

13. **Upgraded to Istio 1.9.3**  
    - Simplified the setup of Istio and automated injection of Istio proxies.
    - Using the `cert-manager` to issue and provision certificates.
    - Replaced the `v1apltha1` security policy APIs, removed in Istio v1.6, with the corresponding new APIs.

14. **Upgraded to Elastic and Kibana 7.12.1**

15. **Upgraded to Prometheus 2.21.0 and Grafana 7.2.1**  
Automated setup of Grafana dashboards.

# The power of Open Source

Writing a book based on the latest versions of open source projects is asking for trouble. It is inevitable to be exposed to regressions in existing functionality and new features that don't fully work as intended. During the development of this book, I reported several issues on GitHub and participated in several discussions on Stack Overflow to get various problems resolved. I want to thank the open-source community for helping me resolving, among others, the following issues:

1. https://github.com/spring-cloud/spring-cloud-sleuth/issues/1770
2. https://github.com/spring-cloud/spring-cloud-config/issues/1780
3. https://github.com/spring-projects-experimental/spring-native/issues/393
4. https://github.com/spring-projects-experimental/spring-native/issues/396
5. https://github.com/spring-projects-experimental/spring-native/issues/823
6. https://github.com/resilience4j/resilience4j/issues/1233
7. https://github.com/kubernetes/minikube/issues/9482
8. https://github.com/kubernetes/minikube/issues/10495