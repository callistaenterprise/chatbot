---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Go Microservices, part 8 - centralized configuration with Viper and Spring Cloud Config
authors: 
  - eriklupander
tags: go microservices docker swarm docker spring cloud netflix oss config centralized configuration
topstory: true
comments: true

---
In part 8 of the [blog series](https://callistaenterprise.se/blogg/teknik/2017/02/17/go-blog-series-part1/), we'll explore centralized configuration for Go microservices with [Spring Cloud Config](https://cloud.spring.io/spring-cloud-config/).

# Introduction
Centralizing something when dealing with Microservices may seem a bit off given that microservices after all is about decomposing your system into separate independent pieces of software. However, what we're typically after is isolation of processes. Other aspects of microservice operations should be dealt with in a centralized way. For example, logs should end up in your logging solution such as the [elk stack](https://www.elastic.co/webinars/introduction-elk-stack), monitoring goes into a dedicated monitoring - in this part of the [blog series](https://callistaenterprise.se/blogg/teknik/2017/02/17/go-blog-series-part1/), we'll deal with externalized and centralized configuration using Spring Cloud Config and git.

Handling configuration for the various microservices that our application consists of in a centralized manner is actually quite natural as well. Especially when running in a containerized environment on an unknown number of underlying hardware nodes, managing config files built into each microservice image or from mounted volumes can quickly become a real headache. There are a number of proven projects to help deal with this, for example [etcd](https://github.com/coreos/etcd), [consul](https://www.consul.io/) and [zookeeper](https://zookeeper.apache.org/). However, it should be noted that those projects provide a lot more than just serving configuration. Since this blog series focus on integrating Go microservices with the Spring Cloud / Netflix OSS ecosystem of supporting services, we'll be basing our centralized configuration on [Spring Cloud Configuration](https://cloud.spring.io/spring-cloud-config/), a piece of software dedicated to provide exactly that.

_Note: Most of the Go source code for the blog series was rewritten in July 2019 to better reflect contemporary idiomatic Go coding guidelines and design patterns. However, the corresponding [git branch](https://github.com/callistaenterprise/goblog/tree/P8) for each part of the series remains unchanged in order to stay aligned with the content of each installment. For the latest and greatest code, look at the [master](https://github.com/callistaenterprise/goblog) branch in github._

# Spring Cloud Config
The [Spring Cloud](http://projects.spring.io/spring-cloud/) ecosystem provides a solution for centralized configuration not-so-creatively named [Spring Cloud Config](https://cloud.spring.io/spring-cloud-config/). The Spring Cloud Config server can be viewed as a proxy between your services and their actual configuration, providing a number of really neat features such as:
 
* Support for several different configuration backends such as git (default), file systems and plugins for using [etcd](https://github.com/spring-cloud-incubator/spring-cloud-etcd/tree/master/spring-cloud-etcd-config), [consul](https://github.com/spring-cloud/spring-cloud-consul/tree/master/spring-cloud-consul-config) and [zookeeper](https://github.com/spring-cloud/spring-cloud-zookeeper/tree/master/spring-cloud-starter-zookeeper-config) as stores. 
* Transparent decryption of encrypted properties.
* Pluggable security
* Push mechanism using git hooks / REST API and Spring Cloud Bus (e.g. RabbitMQ) to propagate changes in config files to services, making live reload of configuration possible.

For a more in-depth article about Spring Cloud Config in particular, take a look at my colleague Magnus recent [blog post](https://callistaenterprise.se/blogg/teknik/2017/05/12/building-microservices-part-6-configuration-server/).

In this blog post, we will integrate our "accountservice" with a Spring Cloud Config server backed by a public git repository on github, from which we'll fetch configuration, encrypt/decrypt a property and also implement live-reload of config properties. 

Here's a simple overview of the overall solution we're aiming for:

![configserver.png](/assets/blogg/goblog/part8-springcloudconfig.png)


# Overview
Since we're running Docker in Swarm mode, we'll continue using Docker mechanics in various ways. Inside the Swarm, we should run at least one (perferrably more) instances of Spring Cloud Configuration servers. When one of our microservices starts up, all they need to know about are the following:

- The logical service name and port of the config server. I.e - we're deploying our config servers on Docker Swarm as services, let's say we name that service "configserver". That means that is the only thing the microservices needs to know about addressing in order to make a request for its configuration.
- What their name is, e.g. "accountservice"
- What execution profile it is running, e.g. "dev", "test" or "prod". If you're familiar with the concept of _spring.profiles.active_, this is a home-brewn counterpart we can use for Go.
- If we're using git as backend and want to fetch configuration from a particular branch, that needs to be known up front. (Optional)

Given the four criteria above, a sample GET request for configuration could look like this in Go code:

    resp, err := http.Get("http://configserver:8888/accountservice/dev/P8")
    
I.e:
    
    protocol://url:port/applicationName/profile/branch
    
# Setting up a Spring Cloud Configuration server in your Swarm
For part 8, you'll probably want to clone branch P8 since it includes the source for the config server:

    git clone https://github.com/callistaenterprise/goblog.git
    git checkout P8
    
You could probably set up and deploy the config server in other ways. However, for simplicity I've prepared a _/support_ folder in the root _/goblog_ folder of the [source code repository of the blog series](https://github.com/callistaenterprise/goblog/tree/P8/support) which will contain the requisite 3rd party services we'll need further on. 

Typically, each required support component will either be a simple _Dockerfile_ for conveniently building and deploying components which we can use out of the box, or it will be (java) source code and configuration (Spring Cloud applications are usually based on Spring Boot) we'll need to build ourselves using gradle. (No worries, all you need is to have a JDK installed).

_(Most of these Spring Cloud applications were [prepared](https://github.com/callistaenterprise/blog-microservices) by my colleague Magnus for his [microservices blog series](https://callistaenterprise.se/blogg/teknik/2015/05/20/blog-series-building-microservices/)._

Let's get started with the config server, shall we?

## RabbitMQ
What? Weren't we about to install Spring Cloud Configuration server? Well - that piece of software depends on having a message broker to propagate configuration changes using [Spring Cloud Bus](https://cloud.spring.io/spring-cloud-bus/) backed by RabbitMQ. Having RabbitMQ around is a very good thing anyway which we'll be using in a later blog post so we'll start by getting RabbitMQ up and running as a service in our Swarm.

I've prepared a [Dockerfile](https://github.com/callistaenterprise/goblog/blob/P8/support/rabbitmq/Dockerfile) inside _/goblog/support/rabbitmq_ to use a pre-baked image which we'll deploy as a Docker Swarm service.

We'll create a new bash (.sh) script to automate things for us if/when we need to update things.

In the root _/goblog_ folder, create a new file _support.sh_:

    #!/bin/bash
    
    # RabbitMQ
    docker service rm rabbitmq
    docker build -t someprefix/rabbitmq support/rabbitmq/
    docker service create --name=rabbitmq --replicas=1 --network=my_network -p 1883:1883 -p 5672:5672 -p 15672:15672 someprefix/rabbitmq

(You may need to chmod it to make it executable)

Run it and wait while Docker downloads the necessary images and deploys RabbitMQ into your Swarm. When it's done, you should be able to open the RabbitMQ Admin GUI and log in using _guest/guest_ at:

    open http://$ManagerIP:15672/#/

Your web browser should open and display something like this:
![rabbitmq](/assets/blogg/goblog/rabbitmq1.png)

If you see the RabbitMQ admin GUI, we can be fairly sure it works as advertised.

# Spring Cloud Configuration server
In _/support/config-server_ you'll find a Spring Boot application pre-configured to run the config server. We'll be using a [git repository](https://github.com/eriklupander/go-microservice-config/tree/P8) for storing and accessing our configuration using [yaml](https://en.wikipedia.org/wiki/YAML) files.

Feel free to take a look at _/goblog/support/config-server/src/main/resources/application.yml_ which is the config file of the config server:

    ---
    # For deployment in Docker containers
    spring:
      profiles: docker
      cloud:
        config:
          server:
            git:
              uri: https://github.com/eriklupander/go-microservice-config.git
              
    # Home-baked keystore for encryption. Of course, a real environment wouldn't expose passwords in a blog...          
    encrypt:
      key-store:
        location: file:/server.jks
        password: letmein
        alias: goblogkey
        secret: changeme
    
    # Since we're running in Docker Swarm mode, disable Eureka Service Discovery
    eureka:
      client:
        enabled: false
    
    # Spring Cloud Config requires rabbitmq, use the service name.
    spring.rabbitmq.host: rabbitmq
    spring.rabbitmq.port: 5672

We see a few things:

* We're telling the config-server to fetch configuration from our git-repo at the specified URI.
* A keystore for encryption (self-signed) and decryption (we'll get back to that)
* Since we're running in Docker Swarm mode, Eureka Service Discovery is disabled.
* The config server is expecting to find a rabbitmq host at "rabbitmq" which just happens to be the Docker Swarm service name we just gave our RabbitMQ service.
 
The _Dockerfile_ for the config-server is quite simple:

    FROM davidcaste/alpine-java-unlimited-jce
    
    EXPOSE 8888
    
    ADD ./build/libs/*.jar app.jar
    ADD ./server.jks /
    
    ENTRYPOINT ["java","-Dspring.profiles.active=docker","-Djava.security.egd=file:/dev/./urandom","-jar","/app.jar"]

(Never mind that _java.security.egd_ stuff, it's a workaround for a problem we don't care about in this blog series)

A few things of note here:

- We're using a base [docker image](https://hub.docker.com/r/davidcaste/alpine-java-unlimited-jce/) based on Alpine Linux that has the Java unlimited cryptography extension installed, this is a requirement if we want to use the encryption/decryption features of Spring Cloud Config.
- A home-baked keystore is added to the root folder of the container image. 

## Build the keystore

To use encrypted properties later on, we'll configure the config server with a self-signed certificate. (You'll need to have _keytool_ on your PATH). 

In the _/goblog/support/config-server/_ folder, run:

    keytool -genkeypair -alias goblogkey -keyalg RSA \
    -dname "CN=Go Blog,OU=Unit,O=Organization,L=City,S=State,C=SE" \  
    -keypass changeme -keystore server.jks -storepass letmein \
    -validity 730

This should create _server.jks_. Feel free to modify any properties/passwords, just remember to update _application.yml_ accordingly!

## Build and deploy
Time to build and deploy the server. Let's create a shell script to save us time if or when we need to do this again. Remember - you need a Java Runtime Environment to build this! In the _/goblog_ folder, create a file named _springcloud.sh_. We will put all things that actually needs building (and that may take some time) in there:

    #!/bin/bash
    
    cd support/config-server
    ./gradlew build
    cd ../..
    docker build -t someprefix/configserver support/config-server/
    docker service rm configserver
    docker service create --replicas 1 --name configserver -p 8888:8888 --network my_network --update-delay 10s --with-registry-auth  --update-parallelism 1 someprefix/configserver

Run it from the _/goblog_ folder (you may need to chmod +x first):

    > ./springcloud.sh
    
This may take a while, give it a minute or two and then check if you can see it up-and-running using _docker service_:

    > docker service ls
    
    ID                  NAME                MODE                REPLICAS            IMAGE
    39d26cc3zeor        rabbitmq            replicated          1/1                 someprefix/rabbitmq
    eu00ii1zoe76        viz                 replicated          1/1                 manomarks/visualizer:latest
    q36gw6ee6wry        accountservice      replicated          1/1                 someprefix/accountservice
    t105u5bw2cld        quotes-service      replicated          1/1                 eriklupander/quotes-service:latest
    urrfsu262e9i        dvizz               replicated          1/1                 eriklupander/dvizz:latest
    w0jo03yx79mu        configserver        replicated          1/1                 someprefix/configserver

Try to manually load the "accountservice" configuration as JSON using curl:

         > curl http://$ManagerIP:8888/accountservice/dev/master
         {"name":"accountservice","profiles":["dev"],"label":"master","version":"b8cfe2779e9604804e625135b96b4724ea378736",
         "propertySources":[
            {"name":"https://github.com/eriklupander/go-microservice-config.git/accountservice-dev.yml",
            "source":
                {"server_port":6767,"server_name":"Accountservice DEV"}
            }]
         }

_(Formatted for brevity)_

The actual configuration is stored within the "source" property where all values from the .yml file will appear as key-value pairs. Loading and parsing the "source" property into usable configuration in Go is the centerpiece of this blog post.

# The YAML config files
Before moving on to Go code, let's take a look inside the root folder of the P8 branch of the [configuration-repo](https://github.com/eriklupander/go-microservice-config/tree/P8):

    accountservice-dev.yml
    accountservice-test.yml
    
Both these files are currently very sparsely populated:

    server_port: 6767
    server_name: Accountservice TEST
    the_password: (we'll get back to this one)
    
The only thing we're configuring at this point is the HTTP port we want our service to bind to. A real service will probably have a lot more stuff in it.

# Using encryption/decryption
One really neat thing about Spring Cloud Config is its built-in support for transparently decrypting values encrypted directly in the configuration files. For example, take a look at [accountservice-test.yml](https://github.com/eriklupander/go-microservice-config/blob/P8/accountservice-test.yml) where we have a dummy "the_password" property:

    server_port: 6767
    server_name: Accountservice TEST
    the_password: '{cipher}AQB1BMFCu5UsCcTWUwEQt293nPq0ElEFHHp5B2SZY8m4kUzzqxOFsMXHaH7SThNNjOUDGxRVkpPZEkdgo6aJFSPRzVF04SXOVZ6Rjg6hml1SAkLy/k1R/E0wp0RrgySbgh9nNEbhzqJz8OgaDvRdHO5VxzZGx8uj5KN+x6nrQobbIv6xTyVj9CSqJ/Btf/u1T8/OJ54vHwi5h1gSvdox67teta0vdpin2aSKKZ6w5LyQocRJbONUuHyP5roCONw0pklP+2zhrMCy0mXhCJSnjoHvqazmPRUkyGcjcY3LHjd39S2eoyDmyz944TKheI6rWtCfozLcIr/wAZwOTD5sIuA9q8a9nG2GppclGK7X649aYQynL+RUy1q7T7FbW/TzSBg='

By prefixing the encrypted string with _{cipher}_, our Spring Cloud configuration server will know how to automatically decrypt the value for us before passing the result to the service. In a running instance with everything configured correctly, a curl request to the REST API to fetch this config would return:

    ...
          "source": {
            "server_port": 6767,
            "server_name": "Accountservice TEST",
            "the_password": "password"
    ....
    
Pretty neat, right? The "the_password" property can be stored as clear-text encrypted string on a public server (if you trust the encryption algorithm and the integrity of your signing key) and the Spring Cloud Config server (which may not under any circumstance be made available unsecured and/or visible outside of your internal cluster!!) transparently decrypts the property into actual value 'password'.

Of course, you need to encrypt the value using the same key as Spring Cloud Config is using for decryption, something that can be done over the config server's HTTP API:

    curl http://$ManagerIP:8888/encrypt -d 'password'
    AQClKEMzqsGiVpKx+Vx6vz+7ww00n... (rest omitted for brevity)
    
# Viper
Our Go-based configuration framework of choice is [Viper](https://github.com/spf13/viper). Viper has a nice API to work with, is extensible and doesn't get in the way of our normal application code. While Viper doesn't support loading configuration from Spring Cloud Configuration servers natively, we'll write a short snippet of code that does this for us. Viper also handles many file types as config source - for example json, yaml and plain properties files. Viper can also read environment variables from the OS for us which can quite neat. Once initialized and populated, our configuration is always available using the various [viper.Get*](https://godoc.org/github.com/spf13/viper) functions. Very convenient, indeed.
 
Remember the picture at the top of this blog post? Well, if not - here it is again:

![configserver.png](/assets/blogg/goblog/configserver.png)

We'll make our microservices do an HTTP request on start, extract the "source" part of the JSON response and stuff that into Viper so we can get the HTTP port for our web server there. Let's go!

## Loading the configuration
As already demonstrated using curl, we can do a plain HTTP request to the config server where we just need to know our name and our "profile". We'll start by adding some parsing of flags to our "accountservice" _main.go_ so we can specify an environment "profile" when starting as well as an optional URI to the config server:

    var appName = "accountservice"
    
    // Init function, runs before main()
    func init() {
            // Read command line flags
            profile := flag.String("profile", "test", "Environment profile, something similar to spring profiles")
            configServerUrl := flag.String("configServerUrl", "http://configserver:8888", "Address to config server")
            configBranch := flag.String("configBranch", "master", "git branch to fetch configuration from")
            flag.Parse()
            
            // Pass the flag values into viper.
            viper.Set("profile", *profile)
            viper.Set("configServerUrl", *configServerUrl)
            viper.Set("configBranch", *configBranch)
    }
    
    func main() {
            fmt.Printf("Starting %v\n", appName)
    
            // NEW - load the config
            config.LoadConfigurationFromBranch(
                    viper.GetString("configServerUrl"),
                    appName,
                    viper.GetString("profile"),
                    viper.GetString("configBranch"))
            initializeBoltClient()
            service.StartWebServer(viper.GetString("server_port"))    // NEW, use port from loaded config 
    }


The  _config.LoadConfigurationFromBranch(..)_ function goes into a new package we're calling _config_. Create _/goblog/accountservice/config_ and the following file named _loader.go_:
     
    // Loads config from for example http://configserver:8888/accountservice/test/P8
    func LoadConfigurationFromBranch(configServerUrl string, appName string, profile string, branch string) {
            url := fmt.Sprintf("%s/%s/%s/%s", configServerUrl, appName, profile, branch)
            fmt.Printf("Loading config from %s\n", url)
            body, err := fetchConfiguration(url)
            if err != nil {
                    panic("Couldn't load configuration, cannot start. Terminating. Error: " + err.Error())
            }
            parseConfiguration(body)
    }
    
    // Make HTTP request to fetch configuration from config server
    func fetchConfiguration(url string) ([]byte, error) {
            resp, err := http.Get(url)
            if err != nil {
                    panic("Couldn't load configuration, cannot start. Terminating. Error: " + err.Error())
            }
            body, err := ioutil.ReadAll(resp.Body)
            return body, err
    }
    
    // Pass JSON bytes into struct and then into Viper
    func parseConfiguration(body []byte) {
            var cloudConfig springCloudConfig
            err := json.Unmarshal(body, &cloudConfig)
            if err != nil {
                    panic("Cannot parse configuration, message: " + err.Error())
            }
    
            for key, value := range cloudConfig.PropertySources[0].Source {
                    viper.Set(key, value)
                    fmt.Printf("Loading config property %v => %v\n", key, value)
            }
            if viper.IsSet("server_name") {
                    fmt.Printf("Successfully loaded configuration for service %s\n", viper.GetString("server_name"))
            }
    }
   
    // Structs having same structure as response from Spring Cloud Config
    type springCloudConfig struct {
            Name            string           `json:"name"`
            Profiles        []string         `json:"profiles"`
            Label           string           `json:"label"`
            Version         string           `json:"version"`
            PropertySources []propertySource `json:"propertySources"`
    }
    
    type propertySource struct {
            Name   string                 `json:"name"`
            Source map[string]interface{} `json:"source"`
    }

Basically, we're doing that HTTP GET to the config server with our appName, profile and git branch, then unmarshalling the response JSON into the _springCloudConfig_ struct we're declaring in the same file. Finally, we're simply iterating over all the key-value pairs in the _cloudConfig.PropertySources[0]_ and stuffing each pair into viper so we can access them whenever we want using _viper.GetString(key)_ or another of the typed getters the Viper API provides. 

Note that if we have an issue contacting the configuration server or parsing its response, we panic() the entire microservice which will kill it. Docker Swarm will detect this and try to deploy a new instance in a few seconds. The typical reason for a behaviour such as this is when starting your cluster from cold and the Go-based microservice will start much faster than the Spring Boot-based config server does. Let Swarm retry a few times and things should sort themselves out.

We've split the actual work up into one public function and a few package-scoped ones for easier unit testing. The unit test for checking so we can transform JSON into actual viper properties looks like this using the GoConvey style of tests:

    func TestParseConfiguration(t *testing.T) {
    
            Convey("Given a JSON configuration response body", t, func() {
                    var body = `{"name":"accountservice-dev","profiles":["dev"],"label":null,"version":null,"propertySources":[{"name":"file:/config-repo/accountservice-dev.yml","source":{"server_port":6767"}}]}`
    
                    Convey("When parsed", func() {
                            parseConfiguration([]byte(body))
                            
                            Convey("Then Viper should have been populated with values from Source", func() {
                                    So(viper.GetString("server_port"), ShouldEqual, "6767")
                            })
                    })
            })
    }
    
Run from _goblog/accountservice_ if you want to:

    > go test ./...

## Updates to the Dockerfile

Given that we're loading the configuration from an external source, our service needs a hint about where to find it. That's performed by using flags as command-line arguments when starting the container and service:

_goblog/accountservice/Dockerfile_:

    FROM iron/base
    EXPOSE 6767
    
    ADD accountservice-linux-amd64 /
    ADD healthchecker-linux-amd64 /
    
    HEALTHCHECK --interval=3s --timeout=3s CMD ["./healthchecker-linux-amd64", "-port=6767"] || exit 1
    ENTRYPOINT ["./accountservice-linux-amd64", "-configServerUrl=http://configserver:8888", "-profile=test", "-configBranch=P8"]
        
Our ENTRYPOINT now supplies values making it possible to configure from where to load configuration.
 
   
  
# Into the Swarm

You probably noted that we're not using 6767 as a hard-coded port number anymore, i.e:

    service.StartWebServer(viper.GetString("server_port"))
    
Use the _copyall.sh_ script to build and redeploy the updated "accountservice" into Docker Swarm

    > ./copyall.sh
    
After everything's finished, the service should still be running exactly as it did before you started on this part of the blog series, with the exception that it actually picked its HTTP port from an external and centralized configuration server rather than being hard-coded into the compiled binary.

_(Do note that ports exposed in Dockerfiles, Healthcheck CMDs and Docker Swarm "docker service create" statements doesn't know anything about config servers. In a CI/CD pipeline, you'd probably externalize relevant properties so they are injectable by the build server at build time.)_

Let's take a look at the log output of our accountservice:

    > docker logs -f [containerid]
    Starting accountservice
    Loading config from http://configserver:8888/accountservice/test/P8
    Loading config property the_password => password
    Loading config property server_port => 6767
    Loading config property server_name => Accountservice TEST
    Successfully loaded configuration for service Accountservice TEST

_(To actually print config values is a bad practice, the output above is just for educational reasons!)_


# Live configuration updates

    - "Oh, did that external service we're using for [some purpose] change their URL?"     
    - "Darn. None told us!!" 
    
I assume many of us have encountered situations where we need to either rebuild an entire application or at least restart it to update some invalid or changed configuration value. Spring Cloud has the concept of [@RefreshScope](https://github.com/dangdangdotcom/config-toolkit/wiki/Refresh-bean-with-spring-cloud's-@RefreshScope-support)s where beans can be live-updated with changed configuration propagated from a [git commit hook](https://git-scm.com/book/gr/v2/Customizing-Git-Git-Hooks).
 
This figure provides an overview of how a push to a git repo is propagated to our Go-based microservices:

![/assets/blogg/goblog/part8-springcloudpush.png](/assets/blogg/goblog/part8-springcloudpush.png)

In this blog post, we're using a github repo which has absolutely no way of knowing how to perform a post-commit hook operation to my laptop's Spring Cloud server, so we'll emulate a commit hook push using the built-in _/monitor_ endpoint of our Spring Cloud Config server.

    curl -H "X-Github-Event: push" -H "Content-Type: application/json" -X POST -d '{"commits": [{"modified": ["accountservice.yml"]}],"name":"some name..."}' -ki http://$ManagerIP:8888/monitor

The Spring Cloud Config server will know what to do with this POST and send out a _RefreshRemoteApplicationEvent_ on an [exchange](https://www.rabbitmq.com/tutorials/amqp-concepts.html) on RabbitMQ (abstracted by Spring Cloud Bus). If we take a look at the RabbitMQ admin GUI after having booted Spring Cloud Config successfully, that _exchange_ should have been created:
                                                                                                                                                                                                                                        
![Exchange name](/assets/blogg/goblog/part8-springcloudbusexchange.png)

How does an _exchange_ relate to more traditional messaging constructs such as publisher, consumer and queue?

    Publisher -> Exchange -> (Routing) -> Queue -> Consumer

I.e - a message is published to an _exchange_, which then distributes message copies to _queue(s)_ based on _routing_ rules and bindings which may have registered _consumers_.

So in order to consume _RefreshRemoteApplicationEvent_ messages (I prefer to call them _refresh tokens_), all we have to do now is make our Go service listen for such messages on the _springCloudBus_ exchange and if we are the targeted application, perform a configuration reload. Let's do that.

## Using the AMQP protocol to consume messages in Go
The RabbitMQ broker can be accessed using the AMQP protocol. There's a good Go AMQP client we're going to use called [streadway/amqp](https://github.com/streadway/amqp).
Most of the AMQP / RabbitMQ plumbing code should go into some reusable utility, perhaps we'll refactor that later on. The plumbing code is based on [this example](https://github.com/streadway/amqp/blob/master/_examples/simple-consumer/consumer.go) from the streadway/amqp repo.

In _/goblog/accountservice/main.go_, add a new line inside the _main()_ function that will start an AMQP consumer for us:

    func main() {
            fmt.Printf("Starting %v\n", appName)
    
            config.LoadConfigurationFromBranch(
                    viper.GetString("configServerUrl"),
                    appName,
                    viper.GetString("profile"),
                    viper.GetString("configBranch"))
            initializeBoltClient()
            
            // NEW
            go config.StartListener(appName, viper.GetString("amqp_server_url"), viper.GetString("config_event_bus"))   
            service.StartWebServer(viper.GetString("server_port"))
    }

Note the new _amqp_server_url_ and _config_event_bus_ properties, they're loaded from the [_accountservice-test.yml](https://raw.githubusercontent.com/eriklupander/go-microservice-config/P8/accountservice-test.yml) configuration file we're loading.

The _StartListener_ function goes into a new file _/goblog/accountservice/config/events.go_. This file has a _lot_ of AMQP boilerplate which we'll skip so we concentrate on the interesting parts:

    func StartListener(appName string, amqpServer string, exchangeName string) {
            err := NewConsumer(amqpServer, exchangeName, "topic", "config-event-queue", exchangeName, appName)
            if err != nil {
                    log.Fatalf("%s", err)
            }
    
            log.Printf("running forever")
            select {}   // Yet another way to stop a Goroutine from finishing...
    }
    
The NewConsumer function is where all the boilerplate goes. We'll skip down to the code that actually processes an incoming message:

     func handleRefreshEvent(body []byte, consumerTag string) {
             updateToken := &UpdateToken{}
             err := json.Unmarshal(body, updateToken)
             if err != nil {
                     log.Printf("Problem parsing UpdateToken: %v", err.Error())
             } else {
                     if strings.Contains(updateToken.DestinationService, consumerTag) {
                             log.Println("Reloading Viper config from Spring Cloud Config server")
     
                             // Consumertag is same as application name.
                             LoadConfigurationFromBranch(
                                     viper.GetString("configServerUrl"),
                                     consumerTag,
                                     viper.GetString("profile"),
                                     viper.GetString("configBranch"))
                     }
             }
     }
     
     type UpdateToken struct {
             Type string `json:"type"`
             Timestamp int `json:"timestamp"`
             OriginService string `json:"originService"`
             DestinationService string `json:"destinationService"`
             Id string `json:"id"`
     }

This code tries to parse the inbound message into an _UpdateToken_ struct and if the destinationService matches our consumerTag (i.e. the appName "accountservice"), we'll call the same _LoadConfigurationFromBranch_ function initially called when the service started.
    
Please note that in a real-life scenario, the _NewConsumer_ function and general message handling code would need more work with error handling, making sure only the appropriate messages are processed etc.

## Unit testing

Let's write a unit test for the _handleRefreshEvent()_ function. Create a new test file _/goblog/accountservice/config/events_test.go_:

    var SERVICE_NAME = "accountservice"
    
    func TestHandleRefreshEvent(t *testing.T) {
            // Configure initial viper values
            viper.Set("configServerUrl", "http://configserver:8888")
            viper.Set("profile", "test")
            viper.Set("configBranch", "master")
    
            // Mock the expected outgoing request for new config
            defer gock.Off()
            gock.New("http://configserver:8888").
                    Get("/accountservice/test/master").
                    Reply(200).
                    BodyString(`{"name":"accountservice-test","profiles":["test"],"label":null,"version":null,"propertySources":[{"name":"file:/config-repo/accountservice-test.yml","source":{"server_port":6767,"server_name":"Accountservice RELOADED"}}]}`)
    
            Convey("Given a refresh event received, targeting our application", t, func() {
                    var body = `{"type":"RefreshRemoteApplicationEvent","timestamp":1494514362123,"originService":"config-server:docker:8888","destinationService":"accountservice:**","id":"53e61c71-cbae-4b6d-84bb-d0dcc0aeb4dc"}
    `
                    Convey("When handled", func() {
                            handleRefreshEvent([]byte(body), SERVICE_NAME)
    
                            Convey("Then Viper should have been re-populated with values from Source", func() {
                                  So(viper.GetString("server_name"), ShouldEqual, "Accountservice RELOADED")
                            })
                    })
            })
    }
    
I hope the BDD-style of GoConvey conveys (pun intended!) how the test works. Note though how we use _gock_ to intercept the outgoing HTTP request for new configuration and that we pre-populate viper with some initial values.    

## Running it
Time to test this. Redeploy using our trusty _copyall.sh_ script:

    > ./copyall.sh
    
Check the log of the _accountservice_:

    > docker logs -f [containerid]
    Starting accountservice
    ... [truncated for brevity] ...
    Successfully loaded configuration for service Accountservice TEST    <-- LOOK HERE!!!!
    ... [truncated for brevity] ...
    2017/05/12 12:06:36 dialing amqp://guest:guest@rabbitmq:5672/
    2017/05/12 12:06:36 got Connection, getting Channel
    2017/05/12 12:06:36 got Channel, declaring Exchange (springCloudBus)
    2017/05/12 12:06:36 declared Exchange, declaring Queue (config-event-queue)
    2017/05/12 12:06:36 declared Queue (0 messages, 0 consumers), binding to Exchange (key 'springCloudBus')
    2017/05/12 12:06:36 Queue bound to Exchange, starting Consume (consumer tag 'accountservice')
    2017/05/12 12:06:36 running forever
 
Now, we'll make a change to the _accountservice-test.yml_ file on my git repo and then fake a commit hook using the _/monitor_ API POST shown earlier in this blog post:

I'm changing _accountservice-test.yml_ and its _service_name_ property, from _Accountservice TEST_ to _Temporary test string!_ and pushing the change.

Next, use curl to let our Spring Cloud Config server know about the update:

    > curl -H "X-Github-Event: push" -H "Content-Type: application/json" -X POST -d '{"commits": [{"modified": ["accountservice.yml"]}],"name":"what is this?"}' -ki http://192.168.99.100:8888/monitor

If everything works, this should trigger a _refresh token_ from the Config server which our _accountservice_ picks up. Check the log again:

    > docker logs -f [containerid]
    2017/05/12 12:13:22 got 195B consumer: [accountservice] delivery: [1] routingkey: [springCloudBus] {"type":"RefreshRemoteApplicationEvent","timestamp":1494591202057,"originService":"config-server:docker:8888","destinationService":"accountservice:**","id":"1f421f58-cdd6-44c8-b5c4-fbf1e2839baa"}
    2017/05/12 12:13:22 Reloading Viper config from Spring Cloud Config server
    Loading config from http://configserver:8888/accountservice/test/P8
    Loading config property server_port => 6767
    Loading config property server_name => Temporary test string!
    Loading config property amqp_server_url => amqp://guest:guest@rabbitmq:5672/
    Loading config property config_event_bus => springCloudBus
    Loading config property the_password => password
    Successfully loaded configuration for service Temporary test string!      <-- LOOK HERE!!!!
    
As you can see, the final line now prints _"Successfully loaded configuration for service Temporary test string!"_. The source code for that line:

    if viper.IsSet("server_name") {
            fmt.Printf("Successfully loaded configuration for service %s\n", viper.GetString("server_name"))
    }    

I.e - we've dynamically changed a property value previously stored in Viper during runtime without touching our service! This IS really cool!!

**Important note:**
While updating properties dynamically is very cool, that in itself won't update things like the port of our _running_ web server, existing Connection objects in pools or (for example) the active connection to the RabbitMQ broker. Those kinds of "already-running" things takes a lot more care to restart with new config values and is out of scope for this particular blog post.

_(Unless you're set things up with your own git repo, this demo isn't reproducible but I hope you enjoyed it anyway.)_

# Footprint and performance
Adding loading of configuration at startup shouldn't affect runtime performance at all and it doesn't. 1K req/s yields the same latencies, CPU & memory use as before. Just take my word for it or try yourself. We'll just take quick peek at memory use after first startup:

    CONTAINER                                    CPU %               MEM USAGE / LIMIT     MEM %               NET I/O             BLOCK I/O           PIDS
    accountservice.1.pi7wt0wmh2quwm8kcw4e82ay4   0.02%               4.102MiB / 1.955GiB   0.20%               18.8kB / 16.5kB     0B / 1.92MB         6
    configserver.1.3joav3m6we6oimg28879gii79     0.13%               568.7MiB / 1.955GiB   28.41%              171kB / 130kB       72.9MB / 225kB      50
    rabbitmq.1.kfmtsqp5fnw576btraq19qel9         0.19%               125.5MiB / 1.955GiB   6.27%               6.2MB / 5.18MB      31MB / 414kB        75
    quotes-service.1.q81deqxl50n3xmj0gw29mp7jy   0.05%               340.1MiB / 1.955GiB   16.99%              2.97kB / 0B         48.1MB / 0B         30

Even with AMQP integration and Viper as configuration framework, we have an initial footprint of ~4 mb. Our Spring Boot-based _config server_ uses over 500 mb of RAM while RabbitMQ (which I think is written in Erlang?) uses 125 mb.

I'm fairly certain we can starve the config server down to 256 mb initial heap size using some standard JVM -xmx args but it's nevertheless definitely a lot of RAM. However, in a production environment I would expect us running ~2 config server instances, not tens or hundreds. When it comes to the supporting services from the Spring Cloud ecosystem, memory use isn't such a big deal as we usually won't have more than one or a few instances of any such service.

# Summary
In this part of the Go microservices [blog series](https://callistaenterprise.se/blogg/teknik/2017/02/17/go-blog-series-part1/) we deployed a Spring Cloud Config server and its RabbitMQ dependency into our Swarm. Then, we wrote a bit of Go code that using plain HTTP, JSON and the Viper framework loads config from the config server on startup and feeds it into Viper for convenient access throughout our microservice codebase.

In the [next part](/blogg/teknik/2017/06/08/go-blog-series-part9), we'll continue to explore AMQP and RabbitMQ, going into more detail and take a look at sending some messages ourselves.
