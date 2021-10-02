---
categories: blogg teknik 
layout: "details-blog"
published: true
topstory: true
comments: true
heading: Blog Series - Trying out new features in Docker
authors: 
  - magnuslarsson
tags: Docker
---

This is a blog series about new features in Docker that I learned from visiting the DockerCon EU conference in Copenhagen, 16-19 October 2017, and in my daily work.

-[readmore]-

In this blog series, I will focus on news in the Docker Engine and surrounding tools, i.e. not go into details on the inner workings of container orchestrators, such as [Docker in Swarm mode](https://docs.docker.com/engine/swarm/) or [Kubernetes](https://kubernetes.io). They are worth a blog series on their own :-)

However, I will use container orchestrators to demonstrate other features in Docker. For example, demonstrate how we can use [Docker in Docker](https://store.docker.com/images/docker) to quickly and easily setup a local container cluster on our development machines without blowing away the memory...

1. [Setting up a Docker Swarm cluster using Docker in Docker](/blogg/teknik/2017/12/18/docker-in-swarm-mode-on-docker-in-docker/)

1. [Setting up a Kubernetes cluster using Docker in Docker](/blogg/teknik/2017/12/20/kubernetes-on-docker-in-docker/)

1. [Create multi-platform Docker images](/blogg/teknik/2017/12/28/multi-platform-docker-images/)

If you want to learn about how to develop microservices in Java or Go that can be deployed as Docker containers, take a look at the [blog series - Building Microservices](/blogg/teknik/2015/05/20/blog-series-building-microservices).