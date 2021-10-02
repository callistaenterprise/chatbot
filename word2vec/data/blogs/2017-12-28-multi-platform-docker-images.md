---
categories: blogg teknik 
layout: "details-blog"
published: true
topstory: true
comments: true
authors: 
  - magnuslarsson
tags: Docker Containers Multi Platforms Architecture
heading: Create multi-platform Docker images
---
In this blog post I will describe how to create a Docker image that works on different hardware architectures and operating systems. I will create a Docker image based on a service written in Go and package it for use in both Linux and Windows on 64 bit Intel based hardware.

-[readmore]-	

This blog post is part of the blog series - [Trying out new features in Docker](/blogg/teknik/2017/12/17/blog-series-docker-news/).

# Background

Nowadays, Docker runs on different operating systems (Linux and Windows) and hardware architectures (Intel, Arm, IBM PowerPC and mainframes). 

A drawback with this multi-platform support is that one Docker image has to be built for each specific target platform, i.e. a specific operating system and hardware architecture. So, if you want to be able to run your Docker container on both Linux and Windows using Intel 64-bit hardware you must create two Docker images, one for Linux and one for Windows. You also have to create each Docker image using a Docker engine running on the specific target platform. 

When using the Docker images, you also have to specify what version you want to use, e.g. the Linux or Windows version. This makes it inconvenient to use together with tools like Docker Compose or a container orchestrator, e.g. Kubernetes or Docker in Swarm mode, since the configuration files (Kubernetes yml files or docker-compose.yml) becomes platform specific.

Work is, however, ongoing to support building multi-platform Docker images that are composed by platform specific Docker images. A new Docker tool, `docker manifest`, is under development. For the time being, a [standalone manifest tool](https://github.com/estesp/manifest-tool) maintained by Phil Estes from IBM can be used to create multi-platform Docker images. For more details, see the following blog post from IBM: [Create and use multi-architecture docker images](https://developer.ibm.com/linuxonpower/2017/07/27/create-multi-architecture-docker-image/)

In September 2017, Docker announced that their official Docker images were updated to make them multi-platform aware, see the blog post [Docker official images are now multi-platform](https://blog.docker.com/2017/09/docker-official-images-now-multi-platform/).

To inspect multi-platform support in a Docker image a containerized tool, `mplatform/mquery`, can be used. E.g. run the following command to inspect multi-platform support in the official Docker image for Go: 

	docker run --rm mplatform/mquery golang

Expected result:

	Image: golang
	 * Manifest List: Yes
	 * Supported platforms:
	   - linux/amd64
	   - linux/arm/v7
	   - linux/arm64/v8
	   - linux/386
	   - linux/ppc64le
	   - linux/s390x
	   - windows/amd64:10.0.14393.1884
	   - windows/amd64:10.0.16299.64	

For more background information, see the DockerCon EU 2017 video: [Docker Multi-arch All the Things](https://dockercon.docker.com/watch/Q2LpoYRL3drmxzWc8yDmn9) and the blog post from Docker [Multi-arch All the Things](https://blog.docker.com/2017/11/multi-arch-all-the-things/).

# Overview

To create a multi-platform Docker image we need to:

1. Create deployment artifacts (e.g. executable files) for each target platform
2. Create a Dockerfile per target platform
3. Build a Docker image for each target platform
4. Push the target platform specific Docker image to a Docker registry, e.g. DockerHub
5. Create a multi-platform Docker image in the Docker registry based on the individual target platform Docker images

This process is summarized in the following picture:

![overview](/assets/blogg/docker/multi-arch-docker-images/overview.png)

# Test Case

I have developed a simple service, written in Go, that creates some random quotes about successful programming languages. See [go-quotes](https://github.com/callistaenterprise/cadec-2017-service-discovery/tree/master/go-quotes).

I want to run my service both as a Linux and a Windows container (on 64-bit Intel hardware).

Implementation notes:

1. Go supports cross compilation, so I can create the executable files on the same developer machine.

2. To be able to create the Linux and Windows based Docker images I need access to Docker engines that runs on Linux and Windows.

3. To minimize the scope of the blog post, I don't want to involve the use of a CI environment or virtual machines for building my Docker images. 

4. "Docker for Mac" only supports Linux containers, while "Docker for Windows" support both Linux and Windows containers.

5. So, for the scope of this blog post, I will use Windows instead of macOS as my development environment.   

> **Note:** Currently you can only run either Linux or Windows containers at the time on a Windows PC but soon we will be able to run Linux and Windows containers concurrently on a Windows PC, see [Docker for Windows 17.11 with Windows 10 Fall Creators Update](https://blog.docker.com/2017/11/docker-for-windows-17-11/): 
>
> "*it will soon be possible to run Windows and Linux Docker containers side-by-side*"


I'm using:

1. Windows 10 Pro, Windows 10 Fall Creators Update (1709)
2. Docker for Windows v17.09.1-ce-win42  
3. Go v1.9.2

# Build

Below follow instructions for how to build the platform specific Docker images and how to assemble a composed multi-platform Docker image.

Use a "*Windows PowerShell*" terminal window to execute the commands below. 

## Get the code

	git clone https://github.com/callistaenterprise/cadec-2017-service-discovery
	cd cadec-2017-service-discovery\go-quotes\

## Build a Docker image for Windows

Compile the Go source code to an executable for Windows:

	set GOOS=windows
	go build -o quotes-windows-amd64.exe

Try out the Windows executable without using Docker:

	./quotes-windows-amd64.exe

It should startup and say something like:

	Starting ML Go version of quote-service on port 8080
	2017/12/19 16:23:17 Starting ML HTTP service at 8080

Open another "*Windows PowerShell*" terminal window and try out the service using `curl`:

	curl http://localhost:8080/api/quote -UseBasicParsing

Expected response:

	StatusCode        : 200
	StatusDescription : OK
	Content           : {"hardwareArchitecture":"amd64","operatingSystem":"windows","ipAddress":"4d131b511ab9/fe80::9846:5b
	                    e3:c0bb:2d91%Ethernet172.24.224.172","quote":"In Go, the code does exactly what it says on the page
	                    ."...

> **Note**: Pay special attention to the value of the fields `hardwareArchitecture` and `operatingSystem` in the response (`amd64` and `windows` in the response above). They will be used later on when we want to verify that we are communicating with a container on the expected platform.

Stop the program with `CTRL/C`.

Ensure that your "Docker for Windows" runs Windows containers. enter the command:

	docker info

Look for the field `OSType`, it should say `windows`.

If not, switch to Windows containers using the Docker menu:

![windows](/assets/blogg/docker/multi-arch-docker-images/switch-to-windows.png)

The Dockerfile for building the Windows Docker image, `Dockerfile-windows-amd64`, looks like:

	FROM microsoft/nanoserver
	EXPOSE 8080
	
	ADD quotes-windows-amd64.exe /
	
	ENTRYPOINT ["./quotes-windows-amd64.exe"] 

Build the Docker image and push it to DockerHub:

	docker build -f Dockerfile-windows-amd64 -t magnuslarsson/quotes:24-go-windows-amd64 .
	docker push magnuslarsson/quotes:24-go-windows-amd64

> **Note #1:** Obviously you can't use my username, `magnuslarsson`, when pushing images to DockerHub, you have to replace it with your own :-)
>
> **Note #2:** You might need to login to DockerHub first, using `docker login`.

You can start the Windows specific Docker image with:

	docker run -d -p 8080:8080 --name quotes magnuslarsson/quotes:24-go-windows-amd64

The current version of "Docker for Windows" has a limitation that prevents access ports published by containers using `localhost`, e.g. `curl http://localhost:8080/api/quote` does not work. For details, see [https://blog.sixeyed.com/published-ports-on-windows-containers-dont-do-loopback/](https://blog.sixeyed.com/published-ports-on-windows-containers-dont-do-loopback/).

Instead, we can use the PC's IP address. You can use `ipconfig` to get the IP address.

E.g.: 

	curl http://192.168.1.224:8080/api/quote -UseBasicParsing

Expect a similar response as from the `curl` command above. Verify that `operatingSystem` field has the value `windows`!

Stop the Windows container with the command:

	docker rm -f quotes

## Build a Docker image for Linux

Compile the Go source to an executable for Linux:

	set GOOS=linux
	go build -o quotes-linux-amd64

Switch to Linux containers using the Docker menu:

![linux](/assets/blogg/docker/multi-arch-docker-images/switch-to-linux.png)

The Dockerfile for building the Linux Docker image, `Dockerfile-linux-amd64`, looks like:

	FROM scratch
	EXPOSE 8080
	
	ADD quotes-linux-amd64 /
	
	ENTRYPOINT ["./quotes-linux-amd64"] 

Build the Docker image and push it to DockerHub:

	docker build -f Dockerfile-linux-amd64 -t magnuslarsson/quotes:24-go-linux-amd64 .
	docker push magnuslarsson/quotes:24-go-linux-amd64

You can start the Linux specific Docker image with:

	docker run -d -p 8080:8080 --name quotes magnuslarsson/quotes:24-go-linux-amd64

Now, try out the service using curl:

	curl http://localhost:8080/api/quote -UseBasicParsing

Expected response:

	StatusCode        : 200
	StatusDescription : OK
	Content           : {"hardwareArchitecture":"amd64","operatingSystem":"linux","ipAddress":"0c4e0824f479/172.17.0.2","qu
	                    ote":"I like a lot of the design decisions they made in the [Go] language. Basically, I like all of
	                     t...

Verify that `operatingSystem` field now has the value `linux`!

Stop the Linux container with the command:

	docker rm -f quotes

## Build a multi-platform Docker image

Now, it's time to combine the two platform specific Docker images into one common Docker image.

We will us the standalone tool `manifest-tool`. Executables can be downloaded from: [https://github.com/estesp/manifest-tool/releases](https://github.com/estesp/manifest-tool/releases).

I used version v0.7.0 of the tool compiled for macOS (I got stuck on some strange authentication problem when trying out the Windows version).

The manifest file, `manifest-quotes-multi-platform.yml`, looks like:

	image: magnuslarsson/quotes:24-go
	manifests:
	  -
	    image: magnuslarsson/quotes:24-go-linux-amd64
	    platform:
	      architecture: amd64
	      os: linux
	  -
	    image: magnuslarsson/quotes:24-go-windows-amd64
	    platform:
	      architecture: amd64
	      os: windows

The multi-platform Docker image is create with the command:

	./manifest-tool-darwin-amd64 --username=magnuslarsson --password=xxx push from-spec manifest-quotes-multi-platform.yml
> **Note:** `./manifest-tool-darwin-amd64` requires macOS, you can however try out the Windows version (or a Linux version) on your own.

Verify that we now have a Docker image for our Go service that supports both Linux and Windows:

	docker run --rm mplatform/mquery magnuslarsson/quotes:24-go

Expected response:

	Image: magnuslarsson/quotes:24-go
	 * Manifest List: Yes
	 * Supported platforms:
	   - linux/amd64
	   - windows/amd64:10.0.14393.1944

You can also take a look into DockerHub to see the resulting three Docker images, e.g. in my case: [https://hub.docker.com/r/magnuslarsson/quotes/tags/](https://hub.docker.com/r/magnuslarsson/quotes/tags/)

Expected result:

![dockerhub](/assets/blogg/docker/multi-arch-docker-images/dockerhub.png)

## Try out the multi-platform Docker image

Now we should be able to run our Go service in both Windows and Linux containers using one and the same Docker image: `magnuslarsson/quotes:24-go`!

Since we currently have "Docker for Windows" configured to run Linux containers, let's start with trying it out on Linux:

	docker run -d -p 8080:8080 --name quotes magnuslarsson/quotes:24-go

Test it using curl:

	curl http://localhost:8080/api/quote -UseBasicParsing

Verify that `operatingSystem` field in the response has the value `linux`!

Kill the Linux container:

	docker rm -f quotes

Switch "Docker for Windows" to use Windows containers:

![windows](/assets/blogg/docker/multi-arch-docker-images/switch-to-windows.png)

Start a Windows container:

	docker run -d -p 8080:8080 --name quotes magnuslarsson/quotes:24-go

> **Note:** We are using exaclty the same command as when starting a Linux container!

Test it using curl:

	curl http://192.168.1.224:8080/api/quote -UseBasicParsing

> **Note:** Remember to replace my IP Address with yours!

Verify that the `operatingSystem` field in the response now has the value `windows`!

Wrap up with killing the Windows container:

	docker rm -f quotes

# Next up...

For more blog posts on new features in Docker, see the blog series - [Trying out new features in Docker](/blogg/teknik/2017/12/17/blog-series-docker-news/).