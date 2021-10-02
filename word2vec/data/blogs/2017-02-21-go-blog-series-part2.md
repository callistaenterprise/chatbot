---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Go microservices, part 2 - building our first service
authors: 
  - eriklupander
tags: go microservices docker swarm docker spring cloud netflix oss gorilla
topstory: true
comments: true

---

In part 2 of this blog series, we will:
- Set up our Go workspace
- Build our first microservice
- Serve some JSON over HTTP using Gorilla Web Toolkit.

To stay focused on the Go fundamentals, we'll wait a bit with deploying it on Docker Swarm.

_Note: Most of the Go source code for the blog series was rewritten in July 2019 to better reflect contemporary idiomatic Go coding guidelines and design patterns. However, the corresponding [git branch](https://github.com/callistaenterprise/goblog/tree/P2) for each part of the series remains unchanged in order to stay aligned with the content of each installment. For the latest and greatest code, look at the [master](https://github.com/callistaenterprise/goblog) branch in github._

# Introduction
While serving JSON over HTTP isn't the only option for inter-service or external communication, we'll focus on HTTP and JSON in this blog series. Using RPC mechanisms and binary messaging formats such as [Protocol Buffers](https://developers.google.com/protocol-buffers/) can be a very interesting option for inter-service communication or for external communication when the external consumer of your service(s) is another system. Go has built-in RPC support and gRPC is absolutely worth looking at as well. However, for now we'll focus on HTTP provided by the built-in [http package](https://golang.org/pkg/net/http/) and [Gorilla Web Toolkit](http://www.gorillatoolkit.org/).

Another aspect to take into account is that many useful frameworks (security, tracing, ...) relies on HTTP headers to transfer state about the ongoing request between participants. Examples we'll see in later blog posts is how we'll pass correlation ID's and OAuth bearers in HTTP headers. While other protocols certainly supports similar mechanisms, many frameworks are built with HTTP in mind and I'd rather try to keep our integrations as straightforward as possible. 

# Setting up a Go Workspace
Feel free to skip the section if you're already a seasoned Go dev. In my humble opinion, the structure of a Go workspace took some time getting used to. Where I'm used to typically having the root of a project as workspace root, Go conventions about how to properly structure a workspace so the go compiler can find source codes and dependencies is somewhat unorthodox, placing your source code under the _/src_ folder in a subtree named after its source control path. I strongly recommend reading the [official guide](https://golang.org/doc/code.html) and [this article](https://astaxie.gitbooks.io/build-web-application-with-golang/content/en/01.2.html) before getting started. I wish I had.

## Installing the SDK
Before writing our first lines of code (or checking out the complete source), we'll need to install the Go SDK. I suggest following [the official guide](https://golang.org/doc/install), it should be straightforward enough.
 
## Setting up a development environment.
In this blog series, we'll be using the built-in Go SDK tools we just installed for building and running, as well as following the idiomatic way of setting up a Go workspace.
 
### 1. Create a root folder for your workspace
All commands are based on a OS X or Linux dev environment. If you're running Windows, please adapt the instructions as necessary.
     
    mkdir ~/goworkspace
    cd goworkspace
    export GOPATH=`pwd`

Here we created a root folder and then assigned the environment variable [GOPATH](https://github.com/golang/go/wiki/GOPATH) to that folder. This is the root of our workspace under which all Go source we write or 3rd party libraries we'll use will end up. I recommend adding this GOPATH to your _.bash_profile_ or similar so you don't have to reset it each time you open up a new console window.

### 2. Create folders and files for our first project
Given that we're in the root of the workspace (e.g. the same folder as specified in the GOPATH env var), execute the following statements:
    
    mkdir -p src/github.com/callistaenterprise
    
If you want to follow along and code stuff yourself, execute these commands: 
    
    cd src/github.com/callistaenterprise
    mkdir -p goblog/accountservice
    cd goblog/accountservice
    touch main.go
    mkdir service

OR - you can clone the git repository containing the sample code and switch to branch P2. From the _src/github.com/callistaenterprise_ folder you created above, execute:

    git clone https://github.com/callistaenterprise/goblog.git
    cd goblog
    git checkout P2

Remember - _$GOPATH/src/github.com/callistaenterprise/goblog_ is the root folder of _our project_ and what's actually stored on github. 

Now we should have enough structure to easily get us started. Open up _main.go_ in your Go IDE of choice. I'm using IntelliJ IDEA with their excellent Golang plugin when writing the code for this blog series. Other popular choices seems to be [Eclipse (with Go plugin)](https://marketplace.eclipse.org/category/free-tagging/golang), [Atom](https://atom.io/packages/go-plus), [Sublime](https://github.com/DisposaBoy/GoSublime), [vim](https://github.com/fatih/vim-go) or JetBrains new dedicated commercial [Gogland](https://www.jetbrains.com/go/) IDE.
 
# Creating the service - main.go
The _main_ function in Go is exactly what you expect it to be - the entry point of our Go programs. Let's create just enough code to get something we can actually build and run:

    package main
    
    import (
            "fmt"
            )
            
    var appName = "accountservice"
    
    func main() {
        fmt.Printf("Starting %v\n", appName)
    }
    
Now, let's run it. Make sure you're in the folder corresponding to your _$GOPATH/src/github.com/callistaenterprise/goblog/accountservice_

    > go run *.go
    Starting accountservice
    >
    
That's it! This program will just print and then exit. Time to add our very first HTTP endpoint!
 
# Building an HTTP web server

*Note: The basics of these HTTP examples were derived from an excellent [blog post](http://thenewstack.io/make-a-restful-json-api-go/)*

To keep things neat, we'll put all HTTP service related files into the _service_ folder.

### Bootstrap the HTTP server

Create the file _webserver.go_ inside the _/services_ folder:

    package service
    
    import (
            "net/http"
            "log"
    )
    
    func StartWebServer(port string) {
    
            log.Println("Starting HTTP service at " + port)
            err := http.ListenAndServe(":" + port, nil)    // Goroutine will block here
    
            if err != nil {
                    log.Println("An error occured starting HTTP listener at port " + port)
                    log.Println("Error: " + err.Error())
            }
    }

We're using the built-in _net/http_ package to execute _ListenAndServe_ which starts a HTTP server on the specified port.

Update _main.go_ so we call the _StartWebServer_ function with a (for now) hard-coded port:

    package main
    
    import (
            "fmt"
            "github.com/callistaenterprise/goblog/accountservice/service"  // NEW
    )
    
    var appName = "accountservice"
    
    func main() {
            fmt.Printf("Starting %v\n", appName)
            service.StartWebServer("6767")           // NEW
    }

Run the program again:

    > go run *.go
    Starting accountservice
    2017/01/30 19:36:00 Starting HTTP service at 6767
    
We now have a simple HTTP server listening to port 6767 on localhost. [Curl](https://curl.haxx.se/) it:

    > curl http://localhost:6767
    404 page not found
    
A 404 is exactly what we're expecting as we havn't declared any routes yet.

Stop the Web server by pressing Ctrl+C.

## Adding our first route
It's time to actually serve something from our server. We'll start by declaring our very first [route](http://www.gorillatoolkit.org/pkg/mux#Route) using a Go [struct](https://gobyexample.com/structs) that we'll use to populate the Gorilla router. In the _service_ folder, create _routes.go_:
 
    package service
    
    import "net/http"
    
    // Defines a single route, e.g. a human readable name, HTTP method and the
    // pattern the function that will execute when the route is called.
    type Route struct {
    	Name        string
    	Method      string
    	Pattern     string
    	HandlerFunc http.HandlerFunc
    }
    
    // Defines the type Routes which is just an array (slice) of Route structs.
    type Routes []Route
    
    // Initialize our routes
    var routes = Routes{
    
    	Route{
    		"GetAccount",                                     // Name
    		"GET",                                            // HTTP method
    		"/accounts/{accountId}",                          // Route pattern
    		func(w http.ResponseWriter, r *http.Request) {
                w.Header().Set("Content-Type", "application/json; charset=UTF-8")
                w.Write([]byte("{\"result\":\"OK\"}"))
            },
    	},
    }
    
In the snippet above, we declared the path _/accounts/{accountId}_ which we later can curl. Gorilla also supports complex routing with regexp pattern matching, schemes, methods, queries, headers values etc. so one is certainly not limited to just paths and path parameters.
 
For now, we will just return a tiny JSON message we've hard-coded as response:

       {"result":"OK"}

We'll also need some boilerplate code that hooks up the actual [Gorilla Router](http://www.gorillatoolkit.org/pkg/mux#overview) to the routes we declared. In _service_ folder, create _router.go_:

    package service
    
    import (
    	"github.com/gorilla/mux"
    )
    
    // Function that returns a pointer to a mux.Router we can use as a handler.
    func NewRouter() *mux.Router {
    
        // Create an instance of the Gorilla router
    	router := mux.NewRouter().StrictSlash(true)
    	
    	// Iterate over the routes we declared in routes.go and attach them to the router instance
    	for _, route := range routes {
    	    
    	    // Attach each route, uses a Builder-like pattern to set each route up.
    		router.Methods(route.Method).
                    Path(route.Pattern).
                    Name(route.Name).
                    Handler(route.HandlerFunc)
    	}
    	return router
    }
    
#### Importing dependencies
In the import section for _router.go_ we see that we have declared a dependency on the _github.com/gorilla/mux_ package. See [here](https://github.com/golang/go/wiki/GOPATH#repository-integration-and-creating-go-gettable-projects) for a good explanation on how go dependencies are fetched using _go get_.

In order for the above file to compile and run, we'll need to use _go get_ to fetch the declared package(s) into our workspace:

    > go get
    
This may take a little while since the Go tool is actually downloading all the source code required by the gorilla/mux package from https://github.com/gorilla/mux. This source code will end up in _$GOPATH/src/github.com/gorilla/mux_ on your local file system and it will be built into your statically linked binary.

#### Wrapping up
Now, revisit _webserver.go_ and add the two following lines at the start of the StartWebServer function:

    func StartWebServer(port string) {
    
            r := NewRouter()             // NEW
            http.Handle("/", r)          // NEW

This attaches the Router we just created to the http.Handle for the root path _/_. Let's compile and run the server again.

    > go run *.go
    Starting accountservice
    2017/01/31 15:15:57 Starting HTTP service at 6767
    
Try to curl:

    > curl http://localhost:6767/accounts/10000
      {"result":"OK"}
      
Nice! We've just created our first HTTP service!

# Footprint and performance
Given that we're exploring Go-based microservices due to alleged awesome memory footprint and good performance, we'd better do a quick benchmark to see how this performs. I've developed a simple [Gatling](http://gatling.io/) test that hammers _/accounts/{accountId}_ with GET requests. If you've checked out the source for this part, you can find the load test in the _/goblog/loadtest_ folder. Or you can look at it on [github](https://github.com/callistaenterprise/goblog/tree/master/loadtest).

### Running the load test yourself
If you want to run the load-test yourself, make sure the "accountservice" is up and running on localhost and that you have cloned the source and checked out branch P2. You'll also need to have a Java Runtime Environment and [Apache Maven](https://maven.apache.org/) installed.

Change directory to the _/goblog/loadtest_ folder and execute the following command from the command-line:

    > mvn gatling:execute -Dusers=1000 -Dduration=30 -DbaseUrl=http://localhost:6767
    
This should start and run the test. The arguments are:

- users: Number of concurrent users the test will simulate
- duration: For how many seconds the test will run
- baseUrl: Base path to the host providing the service we're testing. When we move over to Docker Swarm, the baseUrl will need to be changed to the public IP of the Swarm. More on that in [part 5](/blogg/teknik/2017/03/09/go-blog-series-part5).

After the test has finished, it writes results to the console windows as well as a fancy HTML report into _target/gatling/results/_.

### Results

_Note: Later on, when the services we're building are running inside Docker containers on Docker Swarm, we'll do all benchmarks and metrics capturing there. Until then, my mid-2014 MacBook Pro will have to suffice._

_Before_ starting the load test, the memory consumption of the Go-based "accountservice" is as follows according to the OS X task manager:

![mem use](/assets/blogg/goblog/part2-memuse.png)

1.8 mb, not bad! Let's start the Gatling test running 1K req/s. Remember that this is a _very_ naive implementation that just responds with a hard-coded string.

### Memory use
![mem use2](/assets/blogg/goblog/part2-memuse2.png)
Ok, serving 1K req/s makes the "accountservice" consume about 28 mb of RAM. That's still perhaps 1/10th of what a Spring Boot application uses at startup. It will be very interesting to see how this figures changes once we start to add some real functionality to it.

### Performance and CPU usage
![cpu use](/assets/blogg/goblog/part2-cpuuse.png)
Serving 1K req/s uses about 8% of a single Core.

![performance](/assets/blogg/goblog/part2-performance.png)
Note sure how Gatling rounds sub-millisecond latencies, but mean latency is reported as 0 ms with _one_ request taking a whopping 11 millisecond. At this point, our "Accountservice" is performing admirably, serving on average 745~req/s in the sub-millisecond range.
      
## What's next?
In the [next part](/blogg/teknik/2017/02/27/go-blog-series-part3), we'll actually make our _accountservice_ do something useful. We'll add a simple embedded database with Account objects that we'll serve over HTTP. We'll also take a look at JSON serialization and check how these additions to the service affects its footprint and performance.
