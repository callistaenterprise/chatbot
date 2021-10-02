---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Go microservices, part 6 - health checks.
authors: 
  - eriklupander
tags: go microservices docker swarm docker spring cloud netflix oss healthcheck health check golang
topstory: true
comments: true

---

As our microservices and the landscape they operate in grows more complex, it also becomes increasingly important for our services to provide a mechanism for Docker Swarm to know if they're feeling healthy or not. Therefore, we'll take a look at how to add health checks in this sixth part of the [blog series](/blogg/teknik/2017/02/17/go-blog-series-part1).

For example, our "accountservice" microservice isn't very useful if it cannot:
- Serve HTTP
- Connect to its database

The idiomatic way to handle this in a microservice is to provide an [healthcheck endpoint](https://docs.microsoft.com/en-us/azure/architecture/patterns/health-endpoint-monitoring) (good article from Azure Docs) that in our case - since we're HTTP based - should map to _/health_ and respond with a HTTP 200 if things are OK, possibly together with some machine-parsable message explaining what's OK. If there is a problem, a non HTTP 200 should be returned, possibly stating what's not OK. Do note that some argue that failed checks should return 200 OK with errors specified in the response payload. I can agree with that too, but for the case of simplicity we'll stick with non-200 for this blog post. So let's add such an endpoint to our "account" microservice.

# Source code
As always, feel free to checkout the appropriate branch from git to get all changes of this part up front:

    git checkout P6

_Note: Most of the Go source code for the blog series was rewritten in July 2019 to better reflect contemporary idiomatic Go coding guidelines and design patterns. However, the corresponding [git branch](https://github.com/callistaenterprise/goblog/tree/P6) for each part of the series remains unchanged in order to stay aligned with the content of each installment. For the latest and greatest code, look at the [master](https://github.com/callistaenterprise/goblog) branch in github._

## Add check for accessing the BoltDB
Our service won't be of much use if it cannot access its underlying database. Therefore, we'll add a new function to the [IBoltClient](https://github.com/callistaenterprise/goblog/blob/P6/accountservice/dbclient/boltclient.go#L14) interface, _Check()_:

    type IBoltClient interface {
            OpenBoltDb()
            QueryAccount(accountId string) (model.Account, error)
            Seed()
            Check() bool              // NEW!
    }          

The Check method is perhaps a bit naive, but will serve its purpose for the sake of this blog. It specifies that either _true_ or _false_ will be returned depending on whether the BoltDB was accessible or not.

Our implementation of _Check()_ in [boltclient.go](https://github.com/callistaenterprise/goblog/blob/P6/accountservice/dbclient/boltclient.go#L70) is not very realistic either, but it should explain the concept well enough:
 
    // Naive healthcheck, just makes sure the DB connection has been initialized.
    func (bc *BoltClient) Check() bool {
            return bc.boltDB != nil
    }
    
The mocked implementation in [mockclient.go](https://github.com/callistaenterprise/goblog/blob/P6/accountservice/dbclient/mockclient.go#L26) follows our standard stretchr/testify pattern:

    func (m *MockBoltClient) Check() bool {
            args := m.Mock.Called()
            return args.Get(0).(bool)
    }
    

## Adding the /health endpoint

This is very straightforward. We'll start by adding a new _/health_ route to our _/accountservice/service/routes.go_ file below the existing route to _/accounts/{accountId}_:

    Route{
            "HealthCheck",
            "GET",
            "/health",
            HealthCheck,
    },
    
We declared that the route shall be handled by a function named HealthCheck that we now will add to the _/accountservice/service/handlers.go_ file:

    func HealthCheck(w http.ResponseWriter, r *http.Request) {
            // Since we're here, we already know that HTTP service is up. Let's just check the state of the boltdb connection
            dbUp := DBClient.Check()
            if dbUp {
                    data, _ := json.Marshal(healthCheckResponse{Status: "UP"})
                    writeJsonResponse(w, http.StatusOK, data)
            } else {
                    data, _ := json.Marshal(healthCheckResponse{Status: "Database unaccessible"})
                    writeJsonResponse(w, http.StatusServiceUnavailable, data)
            }
    }
    
    func writeJsonResponse(w http.ResponseWriter, status int, data []byte) {
            w.Header().Set("Content-Type", "application/json")
            w.Header().Set("Content-Length", strconv.Itoa(len(data)))
            w.WriteHeader(status)
            w.Write(data)
    }
    
    type healthCheckResponse struct {
            Status string `json:"status"`
    }

The _HealthCheck_ function delegates the check of the DB state to the _Check()_ function we added to the DBClient. If OK, we create an instance of the _healthCheckResponse_ struct. Note the lower-case first character? That's how we [scope](https://golang.org/ref/spec#Exported_identifiers) this struct to only be accessible within the _service_ package. We also extracted the "write a http response" code into a utility method to keep ourselves [DRY](https://en.wikipedia.org/wiki/Don't_repeat_yourself).

# Running
    
From the _/goblog/accountservice_ folder, build and run:

    > go run *.go
    Starting accountservice
    Seeded 100 fake accounts...
    2017/03/03 21:00:31 Starting HTTP service at 6767
    
Open a new console window and _curl_ the _/health_ endpoint:

    > curl localhost:6767/health
    {"status":"UP"}
    
It works! 

# The Docker Healthcheck

![docker healthcheck](/assets/blogg/goblog/part6-healthcheck.png)

Next, we'll use the Docker [HEALTHCHECK](https://docs.docker.com/engine/reference/builder/#healthcheck) mechanism to let Docker Swarm check our service for liveness. This is done by adding a line in the Dockerfile:

    HEALTHCHECK --interval=5s --timeout=5s CMD ["./healthchecker-linux-amd64", "-port=6767"] || exit 1

What's this _"healthchecker-linux-amd64"_ thing? We need to help Docker a bit with these health checks as Docker itself doesn't provide us with an HTTP client or similar to actually execute the health checks. Instead, the HEALTHCHECK directive in a Dockerfile specifies a command (CMD) that should perform the call to _/health_ endpoint. Depending on the [exit code](https://golang.org/pkg/os/#Exit) of the program that was run, Docker will determine whether the service is healthy or not. If too many subsequent health checks fail, Docker Swarm will kill the container and start a new instance.

The most common way to do the actual healthcheck seems to be [curl](https://curl.haxx.se/). However, this requires our base docker image to actually have curl (and any underlying dependencies) installed and at this moment we don't really want to deal with that. Instead, we'll use Go to brew our own little healthchecker program.

# Creating the healthchecker program

Time to create a new sub-project under the _/src/github.com/callistaenterprise/goblog_ path:

    mkdir healthchecker
    
Then, create _main.go_ inside the _/healthchecker_ folder:

    package main
    
    import (
    	"flag"
    	"net/http"
    	"os"
    )
    
    func main() {
    	port := flag.String("port", "80", "port on localhost to check") 
    	flag.Parse()
    
    	resp, err := http.Get("http://127.0.0.1:" + *port + "/health")    // Note pointer dereference using *
    	
    	// If there is an error or non-200 status, exit with 1 signaling unsuccessful check.
    	if err != nil || resp.StatusCode != 200 {
    		os.Exit(1)
    	}
    	os.Exit(0)
    }
    
Not an overwhelming amount of code. What it does:

- Uses the [flags](https://golang.org/pkg/flag/) support in golang to read a _-port=NNNN_ command line argument. If not specified, fall back to port 80 as default.
- Perform a HTTP GET to 127.0.0.1:[port]/health
- If an error occurred or the HTTP status returned wasn't 200 OK, exit with a non-zero exit code. 0 == Success, > 0 == fail.

Let's try this. If you've stopped the "accountservice", start it again either by _go run *.go_ or by building it in a new console tab by going into the _"/goblog/accountservice"_ directory and build/start it:

    go build
    ./accountservice

**Reminder: If you're getting strange compile errors, check so the GOPATH still is set to the root folder of your Go workspace, e.g. the parent folder of _/src/github.com/callistaenterprise/goblog_**

Then switch back to your normal console window (where you have GOPATH set as well) and run the healthchecker:

    > cd $GOPATH/src/github.com/callistaenterprise/goblog/healtchecker
    > go run *.go
    exit status 1
    
Ooops! We forgot to specify the port number so it defaulted to port 80. Let's try it again:

    > go run *.go -port=6767
    >
    
No output at all means we were successful. Good. Now, let's build a linux/amd64 binary and add it to the "accountservice" by including the healthchecker binary in the Dockerfile. We'll continue using the _copyall.sh_ script to automate things a bit:

    #!/bin/bash
    export GOOS=linux
    export CGO_ENABLED=0
    
    cd accountservice;go get;go build -o accountservice-linux-amd64;echo built `pwd`;cd ..
    
    // NEW, builds the healthchecker binary
    cd healthchecker;go get;go build -o healthchecker-linux-amd64;echo built `pwd`;cd ..
    
    export GOOS=darwin
   
    // NEW, copies the healthchecker binary into the accountservice/ folder
    cp healthchecker/healthchecker-linux-amd64 accountservice/
    
    docker build -t someprefix/accountservice accountservice/
    
One last thing, we need to update the "accountservice" _Dockerfile_. It's full content looks like this now:

    FROM iron/base
    EXPOSE 6767
    
    ADD accountservice-linux-amd64 /
    
    # NEW!! 
    ADD healthchecker-linux-amd64 /
    HEALTHCHECK --interval=3s --timeout=3s CMD ["./healthchecker-linux-amd64", "-port=6767"] || exit 1
    
    ENTRYPOINT ["./accountservice-linux-amd64"]

Additions:

- We added an ADD statement which makes sure the healthchecker binary is included in the image. 
- The HEALTHCHECK statement specifies our binary as well as some parameters that tells Docker to execute the healthcheck every 3 seconds and to accept a timeout of 3 seconds.

# Deploying with healthcheck
Now we're ready to deploy our updated "accountservice" with healthchecking. To automate things even further, add these two lines to the bottom of the _copyall.sh_ script that will remove and re-create the accountservice inside Docker Swarm every time we run it:

    docker service rm accountservice
    docker service create --name=accountservice --replicas=1 --network=my_network -p=6767:6767 someprefix/accountservice

Now, run _./copyall.sh_ and wait a few seconds while everything builds and updates. Let's check the state of our containers using _docker ps_ that lists all running containers:

    > docker ps
    CONTAINER ID        IMAGE                             COMMAND                 CREATED        STATUS                
    1d9ec8122961        someprefix/accountservice:latest  "./accountservice-lin"  8 seconds ago  Up 6 seconds (healthy)
    107dc2f5e3fc        manomarks/visualizer              "npm start"             7 days ago     Up 7 days

The thing we're looking for here is the _"(healthy)"_ text under the STATUS header. Services without a healthcheck configured doesn't have a health indication at all.

## Making things fail on purpose

To make things a bit more interesting, let's add a testability API that lets us make the endpoint act unhealthy on purpose. In _routes.go_, declare a new endpoint:

    Route{
            "Testability",
            "GET",
            "/testability/healthy/{state}",
            SetHealthyState,
    },    
    
This route (which you never should have in a production service!) provides us with a REST-ish endpoint for failing healthchecks on purpose. The _SetHealthyState_ function goes into _goblog/accountservice/handlers.go_ and looks like this:

    var isHealthy = true // NEW

    func SetHealthyState(w http.ResponseWriter, r *http.Request) {
    
            // Read the 'state' path parameter from the mux map and convert to a bool
            var state, err = strconv.ParseBool(mux.Vars(r)["state"])
            
            // If we couldn't parse the state param, return a HTTP 400
            if err != nil {
                    fmt.Println("Invalid request to SetHealthyState, allowed values are true or false")
                    w.WriteHeader(http.StatusBadRequest)
                    return
            }
            
            // Otherwise, mutate the package scoped "isHealthy" variable.
            isHealthy = state
            w.WriteHeader(http.StatusOK)
    }
    
Finally, add the _isHealthy_ bool as a condition to the HealthCheck function:

    func HealthCheck(w http.ResponseWriter, r *http.Request) {
            // Since we're here, we already know that HTTP service is up. Let's just check the state of the boltdb connection
            dbUp := DBClient.Check()
            
            if dbUp && isHealthy {              // NEW condition here!
                    data, _ := json.Marshal(
                    ...
            ...        
    }
    
Restart the accountservice:
    
    > cd $GOPATH/src/github.com/callistaenterprise/goblog/accountservice
    > go run *.go
    Starting accountservice
    Seeded 100 fake accounts...
    2017/03/03 21:19:24 Starting HTTP service at 6767

Make a new healthcheck call from the other window:

     > cd $GOPATH/src/github.com/callistaenterprise/goblog/healthchecker
     > go run *.go -port=6767
     >
     
First attempt successful. Now change the state of the accountservice using a curl request to the testability endpoint:

    > curl localhost:6767/testability/healthy/false
    > go run *.go -port=6767
    exit status 1
    
It's working! Let's try this running inside Docker Swarm. Rebuild and redeploy the "accountservice" using _copyall.sh_:

    > cd $GOPATH/src/github.com/callistaenterprise/goblog
    > ./copyall.sh
    
As always, wait a bit while Docker Swarm redeploys the "accountservice" service using the latest build of the "accountservice" container image. Then, run _docker ps_ to see if we're up and running with a healthy service:
    
    > docker ps
    CONTAINER ID    IMAGE                            COMMAND                CREATED         STATUS 
    8640f41f9939    someprefix/accountservice:latest "./accountservice-lin" 19 seconds ago  Up 18 seconds (healthy)
    
Note CONTAINER ID and the CREATED. Call the testability API on your docker swarm IP (mine is 192.168.99.100):

    > curl $ManagerIP:6767/testability/healthy/false
    >
    
Now, run _docker ps_ again within a few seconds. 
 
    > docker ps
    CONTAINER ID        IMAGE                            COMMAND                CREATED         STATUS                                                             NAMES
    0a6dc695fc2d        someprefix/accountservice:latest "./accountservice-lin" 3 seconds ago  Up 2 seconds (healthy)

See - a brand new CONTAINER ID and new timestamps on CREATED and STATUS. What actually happened was that Docker Swarm detected three (default values for --retries) consecutive failed healthchecks and immediately decided the service had become unhealthy and need to be replaced with a fresh instance which is exactly what happened without any administrator intervention.

# Summary
In this part we added health checks using a simple _/health_ endpoint and a little healthchecker go program in conjunction with the Docker HEALTHCHECK mechanism, showing how that mechanism allows Docker Swarm to handle unhealthy services automatically for us.

In the [next part](/blogg/teknik/2017/04/24/go-blog-series-part7), we'll dive deeper into Docker Swarm mechanics as we'll be focusing on two key areas of microservice architecture - Service Discovery and Load-balancing.
