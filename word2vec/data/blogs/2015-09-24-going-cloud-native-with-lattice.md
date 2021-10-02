---
categories: blogg teknik
layout: "details-blog"
published: true
heading: "SpringOne2GX 2015 - Going Cloud Native (locally) with Lattice"
authors: 
  - oladeibitsch
tags: ""
topstory: true
comments: true
---




During SpringOne2GX I listened to Matt Stine´s presentation about Lattice, a stripped-down version of [Cloud Foundry](https://www.cloudfoundry.org/) which really lowers the barrier to get started to develop and test cloud-native architectures...

-[readmore]-

...literally speaking, Lattice enables a kickstart for developers to install micro-cloud environments on the their local desktops. Lattice reduces the overall footprint from an infrastructure perspective and allows to get started in just minutes.

# Lattice Architecture
Behind the scenes, we recognize the following [components](https://raw.githubusercontent.com/cloudfoundry-incubator/diego-design-notes/master/diego-overview.png) from Cloud Foundry:

- [Router](https://github.com/cloudfoundry/gorouter) is responsible for load balancing traffic across running containers which can be updated dynamically as applications are launched or spun down.
- [Diego](https://github.com/cloudfoundry-incubator/diego) the Cloud Foundry's upcoming elastic runtime for containers. Diego is responsible for scheduling and running containerized workloads.
- [Doppler/Loggregator](https://github.com/cloudfoundry/loggregator) is responsible for streaming logs out of running containers.

Lattice consists of:

* Cluster Scheduling
* Load Balancing (HA Proxy)
* Health Management
* Log Aggregation

# Installation
Lattice is installed easiest by using Vagrant (Mac OS X):

    $ curl https://lattice.s3.amazonaws.com/nightly/lattice-bundle-v0.4.3-osx.zip
    $ unzip lattice-bundle-v0.4.3-osx
    $ cd lattice-bundle-v0.4.3-osx/vagrant
  
    $ vagrant up

Within minutes, a Lattice VM will be reachable at 192.168.11.11.

To be able to interact with Diego, Lattice offers a [CLI](https://en.wikipedia.org/wiki/Command-line_interface), also refered to as `ltc`, that help to manage the [Garden](https://github.com/cloudfoundry-incubator/garden) containers.

The Lattice CLI is a downloaded as a part of the "lattice-bundle" and in order to connect to the Lattice VM, we are using the `ltc`:

    $ cd lattice-bundle-v0.4.3-osx
    $ ltc target 192.168.11.11.xip.io

To lists applications and tasks running on Lattice:

    $ ltc list

# Deployment
Lattice makes deployment of applications very simple and straightforward. The following demo will utilize [Spring Cloud Config](http://cloud.spring.io/spring-cloud-config/spring-cloud-config.html) to provide server and client support for externalized configuration.

In order to show different deployment options with Lattice, I let the server (refered as "config server") to be deployad as a docker container given an existing image from `Docker Hub`. A simple client (refered as "config client") will be deployed as a minimal Spring Boot application into a droplet container. 

The client application also supports updating the properties dynamically. This is by adding a @RefreshScope annotation and a dependency to the Spring Boot Actuator.

## Deployment of a Docker Image
Now, the next step is to install the `config-server` from a Docker Hub:

    $ ltc create config-server springcloud/configserver --run-as-root --memory-mb 256 --env spring.cloud.config.server.git.uri=https://github.com/deibitsch/config-repo

Verify that the `config-server` application is up and running on Lattice:

    $ ltc status config-server

## Deployment of a Droplet
This shows how to clone, build and deploy a minimal Spring Boot application into a `Dropet`.

    $ cd ~/Documents/Development/git-repos
    $ git clone https://github.com/deibitsch/config-client.git
    $ cd config-client
    $ mvn clean install

Build `config-client` into a droplet using a CF buildpack:

    $ ltc build-droplet config-client java -p ~/Documents/Development/git-repos/config-client/target/config-client-0.0.1-SNAPSHOT.jar --env spring.cloud.config.uri=http://config-server.192.168.11.11.xip.io

List existing droplets:

    $ ltc list-droplets

Launch a the droplet as an app running on Lattice by:

    $ ltc launch-droplet config-client config-client

Verify the `config-client` app on Lattice:

    $ ltc status config-client

The client application has two endpoints:

* / returns greeting message ("HELLO LATTICE")
* /refresh enables to refresh properties from central repository (git backend) using "config-server".

You should be able to visit http://config-client.192.168.11.11.xip.io in your browser.

    $ open http://config-client.192.168.11.11.xip.io

The property `greeting.message` can now be dynamically updated by applying a new value to `config-client.properties` in central git-repo. The invocation (HTTP POST) of the `/refresh` endpoint will update property due to `@RefreshScope` annotation in the `config-client` application.

    $ curl -X POST http://config-client.192.168.11.11.xip.io/refresh

The updated property should be updated if you refresh http://config-client.192.168.11.11.xip.io in your browser.

    $ open http://config-client.192.168.11.11.xip.io

# Logging
The Lattice CLI enables to stream logs from a specific application:

    $ ltc logs config-client
  
Simply, invoke the "/refresh" endpoint resulting in log messages to be visible in the terminal:

    $ curl -X POST http://config-client.192.168.11.11.xip.io/refresh

# Scaling
In order to scale up the number of instances of the client application:

    $ ltc scale config-client 2
  
Verify that there are two instances running:  

    $ ltc status config-client
