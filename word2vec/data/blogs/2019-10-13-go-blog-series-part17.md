---
categories: blogg teknik
layout: "details-blog"
published: false
heading: Go Microservices blog series, part 17 - Integration testing with docker-compose.
authors: 
  - eriklupander
tags: go microservices testing integration docker docker-compose
topstory: true
comments: true

---
In this part of the Go microservices [blog series](https://callistaenterprise.se/blogg/teknik/2017/02/17/go-blog-series-part1/), we'll take a look at building with [Makefiles](https://ftp.gnu.org/old-gnu/Manuals/make-3.79.1/html_chapter/make_2.html) AND how to automate integration-testing of one of our microservices using [docker-compose](https://docs.docker.com/compose/overview/).

# Contents
1. Building with Makefiles
2. Deploying with Docker Stack
3. Integration testing
4. Summary

### Source code

The finished source can be cloned from github:

    > git clone https://github.com/callistaenterprise/goblog.git
    > git checkout P17

# 1. Building with Makefiles
While most compiled languages provides a compiler, developers usually rely on some kind of framework or library to streamline their build process, manage dependencies, run tests and so on. For example, in the Java world, we've been using ant, maven and more recently gradle for our building needs. 

In Go we have a rich set of built-in tools for compiling, dependency management, linting, formatting and testing our code etc, but as far as I know, the most popular choice for build automation among Go developers is plain old [Make](https://en.wikipedia.org/wiki/Make_(software) originating from 1976!

## 1.1 Makefiles
I won't go into details about the inner workings of Make (on Linux and OS X it's we're typically running [GNU Make](https://www.gnu.org/software/make/)), this will just be a quick intro on how I use [Makefiles](https://ftp.gnu.org/old-gnu/Manuals/make-3.79.1/html_chapter/make_2.html) to automate my most common Go build-related tasks.

A Makefile in it's simplest forms allows us to define a number of variables and a number of _tasks_ such as "test" for running your unit tests, "build" for building or "lint" for running your linter.

I typically start each of my Makefiles by defining a variable name of my executable:

    executable := dataservice

This variable can then be used in my tasks. 

As an example of a really simple task, this one runs all my Go unit tests:

    test:
        go test ./...
        
I.e - it will just execute "go test ./...". For the "dataservice" it looks like:

    $ make test
    go test ./...
    ?   	github.com/callistaenterprise/goblog/dataservice/cmd	[no test files]
    ?   	github.com/callistaenterprise/goblog/dataservice/cmd/dataservice	[no test files]
    ?   	github.com/callistaenterprise/goblog/dataservice/internal/app/dbclient	[no test files]
    ?   	github.com/callistaenterprise/goblog/dataservice/internal/app/dbclient/mock_dbclient	[no test files]
    ok  	github.com/callistaenterprise/goblog/dataservice/internal/app/service	0.030s

A more advanced example is my "build" task that first builds a linux/AMD64 executable into the _bin/_ folder and then executes a _docker build_ command to build a local Docker images (which includes the built binary). 

    build:
    	@echo Building $(executable)
    	GOOS=linux GO111MODULE=on go build -o bin/$(executable) cmd/$(executable)/main.go
    	docker build -t someprefix/$(executable) -f Dockerfile .

One can also combine several tasks together:

    all: clean fmt test $(executable)
    
    clean:
    	@rm -rf bin/*
    
    $(executable):
    	@echo Building $(executable)
    	GO111MODULE=on go build -o bin/$@ cmd/$@/main.go

As you may notice, we're using the _$(executable)_ variable and a task named after the variable in order to build a binary for the current OS/Arch.

Ultimately, Makefiles provides a really simple way to group one or several commands into tasks, who then also can be grouped together as prerequisites for running other tasks etc.

## 1.2 Parent makefiles
The source code for this blog series currently consists of 4 discrete Go-based microservices: accountservice, imageservice, dataservice and vipservice. Naturally, we want to build them as uniformly as possible and we would also like to build them all from a parent Makefile.

I've placed this "parent" Makefile in the _/goblog_ root folder. For example, the task for building all microservices looks like this:

    build:
    	$(MAKE) -C accountservice/ build
    	$(MAKE) -C dataservice/ build
    	$(MAKE) -C imageservice/ build
    	$(MAKE) -C vipservice/ build 

This will execute the _build_ task in each of the specified (-C) subfolders, where the [$(MAKE)](https://www.gnu.org/software/make/manual/html_node/MAKE-Variable.html) variable makes sure all "sub-tasks" are executed using the same make binary as the top-level invocation.

Make is quite powerful, but arguably some of the more advanced features are not that easy to grasp. So for more advanced tasks or scripting needs, I usually resort to using bash shell scripts invoked from make tasks rather than trying to unleash the full power of Make.

# 2. Deploying with Docker Stack
Most projects - if not all - tests their code and services in some manner before going into production. Unit-tests running as part of local builds has been around for a really long time, a topic visited in [part 4](https://callistaenterprise.se/blogg/teknik/2017/03/03/go-blog-series-part4/) of this blog series. However, as we move up the [testing pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), the system under test becomes more reliant on _real_ (e.g. not mocked) supporting services being available during the test. With the automation and Continuous Integration aspect of integration testing, you end up in a situation where you need to both run your actual microservice under test, but also need to run whatever services your microservice depends upon. For example, the dataservice in this blog series rely on CockroachDB to be available, and it will also need a configuration server in order to fetch it's configuration on startup.

Managing all of this was quite challenging before the advent of (docker) containers. Maybe you had a "testing DB" running somewhere on your (testing) network, where your test would seed/cleanup data for every test suite executed for a given application.

However, with docker containers, it has become relatively straightforward to provision a full isolated "stack" of services for a given test suite by declaring and running everything in docker containers, orchestrated by some container orchestration mechanism.

In this blog post, we'll use docker-compose in order to integration-test the HTTP endpoints of our "dataservice" component. We will also use go's built-in test functionality to write the actual tests, including seeding of test data and asserting results. We'll also use [mmock](https://github.com/jmartin82/mmock) for creating an HTTP mock that can be programmed to response with a pre-baked HTTP response for a given HTTP request such as the HTTP request for getting its configuration.

![test landscape]()

// Erik
