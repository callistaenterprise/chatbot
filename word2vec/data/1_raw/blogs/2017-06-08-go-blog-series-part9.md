---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Go Microservices blog series, part 9 - Messaging with RabbitMQ and AMQP
authors: 
  - eriklupander
tags: go microservices docker swarm docker spring cloud netflix oss amqp rabbitmq
topstory: true
comments: true

---

In part 9 of the Go microservices [blog series](/blogg/teknik/2017/02/17/go-blog-series-part1/), we'll examine messaging between Go microservices using RabbitMQ and the AMQP protocol.
 
# Introduction
Microservices is all about separating your application's business domain into bounded contexts with clearly separated domains, running with process separation where any persistent relations across domain boundaries has to rely on eventual consistency rather than ACID-like transactions or foreign key constraints. A lot of these concepts comes from or has been inspired by [Domain-driven design](https://en.wikipedia.org/wiki/Domain-driven_design) (DDD). That's yet another huge topic one could write a blog series about.

In the context of our Go microservice [blog series](/blogg/teknik/2017/02/17/go-blog-series-part1/) and microservice architecture in general, one pattern for accomplishing loose coupling between services is to use messaging for inter-service communication that doesn't need a strict request/response message interchange or similar. That said, using messaging is just one of many strategies one can adopt to facilitate loose coupling between services.

In Spring Cloud, RabbitMQ seems to be the message broker of choice, especially since the Spring Cloud Config server has RabbitMQ as a runtime dependency as we saw in [part 8](/blogg/teknik/2017/05/15/go-blog-series-part8) of the blog series.

For this part of the blog series, we'll make our "accountservice" place a message on a RabbitMQ _Exchange_ whenever a particular account object has been read. This message will be consumed by a brand new microservice we'll write in this blog post. We'll also deal with reusing Go code across multiple microservices by putting them in a "common" library we can import into each service.
 
Remember the system landscape image from Part 1? Here's an image of what it'll look like after this part has been finished:

![part9 overview](/assets/blogg/goblog/part9-overview.png)

There's still a _lot_ of stuff missing until we're done. Don't worry, we'll get there.

# Source code
There will be a lot of new source code for this part and not all of it will be included in the blog text. For the complete source, clone and switch to the branch for part 9:

    git checkout P9
    
_Note: Most of the Go source code for the blog series was rewritten in July 2019 to better reflect contemporary idiomatic Go coding guidelines and design patterns. However, the corresponding [git branch](https://github.com/callistaenterprise/goblog/tree/P9) for each part of the series remains unchanged in order to stay aligned with the content of each installment. For the latest and greatest code, look at the [master](https://github.com/callistaenterprise/goblog) branch in github._
    
# Sending a message
We'll implement a simple make-believe use case: When certain "VIP" accounts are read in the "accountservice", we want to notify an "VIP offer" service that under certain circumstances will generate an "offer" for the account holder. In a properly designed domain model, the accounts objects and VIP offer objects are two independent domains that should have as little knowledge of each other as possible.

![separation](/assets/blogg/goblog/part9-separation.png)

I.e - the accountservice should **never** access the storage of the VIP service (offers) directly. In this case, we're passing a message to the "vipservice" over RabbitMQ fully delegating both business logic and persistence to the "vipservice".

We'll do all communication using the [AMQP](https://en.wikipedia.org/wiki/Advanced_Message_Queuing_Protocol) protocol which is a ISO standardized application layer protocol for messaging geared for interoperability. Our Go library of choice for using AMQP is [streadway/amqp](https://github.com/streadway/amqp), just like in part 8 when we consumed configuration updates.

Let's repeat how _exchanges_ in AMQP relates to _publishers_, _consumers_ and _queues_:

![amqp](/assets/blogg/goblog/part9-rabbitmq-exchange.png)

I.e - a message is published to an _exchange_, which then distributes message copies to _queue(s)_ based on _routing_ rules and bindings which may have registered _consumers_. Check [this thread](https://www.quora.com/Why-does-RabbitMQ-have-both-exchanges-and-queues) on Quora for a good explanation.

## Messaging code
Since we'll want to use our new messaging code as well as our existing code for loading configuration from Spring Cloud config in both our existing _accountservice_ and the new _vipservice_, we'll create our first shared library.

Start by creating new folders under _/goblog/_ called _common_ to keep our new reusable stuff:

    > mkdir -p common/messaging
    > mkdir -p common/config
    
We'll put all AMQP-related code in the _messaging_ folder and the configuration stuff in the _config_ folder. You can copy the contents of _/goblog/accountservice/config_ into _/goblog/common/config_ - remember that this will require us to update the _import_ statements previously importing our config code from within the _accountservice_. Just take a look at the [finished source](https://github.com/callistaenterprise/goblog/tree/P9/common) to see how it's supposed to be.

The messaging code will be encapsulated in a single file that will define both the interface our applications will use to connect, publish and subscribe as well as the actual implementation. In all honesty, there is a lot of boilerplate code required for AMQP-messaging using streadway/amqp so don't get bogged down in the details.

Create a new .go file in _/goblog/common/messaging_: [messagingclient.go](https://github.com/callistaenterprise/goblog/blob/P9/common/messaging/messagingclient.go)

Let's have a look at the important stuff
    
    // Defines our interface for connecting, producing and consuming messages.
    type IMessagingClient interface {
            ConnectToBroker(connectionString string)
            Publish(msg []byte, exchangeName string, exchangeType string) error
            PublishOnQueue(msg []byte, queueName string) error
            Subscribe(exchangeName string, exchangeType string, consumerName string, handlerFunc func(amqp.Delivery)) error
            SubscribeToQueue(queueName string, consumerName string, handlerFunc func(amqp.Delivery)) error
            Close()
    }
    
The snippet above defines our messaging interface. This is what our "accountservice" and "vipservice" will deal with when it comes to messaging, hopefully abstracting away most complexity. Note that I've chosen two variants of "Produce" and "Consume" to use with _topics_ and _direct/queue_ messaging patterns. 

Next, we'll define a struct which will hold a pointer to an amqp.Connection and that we will attach the requisite methods to so it (implicitly, as always with Go) implements the interface we just declared.
    
    // Real implementation, encapsulates a pointer to an amqp.Connection
    type MessagingClient struct {
            conn *amqp.Connection
    }
    
The implementations are quite verbose so let's limit ourselves to two of them - _ConnectToBroker()_ and _PublishToQueue()_:
    
    func (m *MessagingClient) ConnectToBroker(connectionString string) {
            if connectionString == "" {
                    panic("Cannot initialize connection to broker, connectionString not set. Have you initialized?")
            }
    
            var err error
            m.conn, err = amqp.Dial(fmt.Sprintf("%s/", connectionString))
            if err != nil {
                    panic("Failed to connect to AMQP compatible broker at: " + connectionString)
            }
    }
    
This is how we get hold of the connection pointer, e.g. _amqp.Dial_. If we're missing our config or cannot contact our broker, we'll panic our microservice and let the container orchestrator try again with a fresh instance. The passed connection string looks like:

    amqp://guest:guest@rabbitmq:5672/
    
Note that we're using the Docker Swarm mode _service_ name of the rabbitmq broker.

The _PublishOnQueue()_ function is quite long - it's more or less derived from the official [streadway samples](https://www.rabbitmq.com/tutorials/tutorial-one-go.html), though I've simplified it a bit with fewer parameters. To publish a message to a named queue, all we need to pass is:

- body in the form of a byte array. Could be JSON, XML or some binary.
- queueName - name of the queue you want to send your message to.

For more details about exchanges, see the [RabbitMQ docs](https://www.rabbitmq.com/tutorials/amqp-concepts.html).
   
    
    func (m *MessagingClient) PublishOnQueue(body []byte, queueName string) error {
            if m.conn == nil {
                    panic("Tried to send message before connection was initialized. Don't do that.")
            }
            ch, err := m.conn.Channel()      // Get a channel from the connection
            defer ch.Close()
    
            // Declare a queue that will be created if not exists with some args
            queue, err := ch.QueueDeclare(
                    queueName, // our queue name
                    false, // durable
                    false, // delete when unused
                    false, // exclusive
                    false, // no-wait
                    nil, // arguments
            )
    
            // Publishes a message onto the queue.
            err = ch.Publish(
                    "", // use the default exchange
                    queue.Name, // routing key, e.g. our queue name
                    false, // mandatory
                    false, // immediate
                    amqp.Publishing{
                            ContentType: "application/json",
                            Body:        body, // Our JSON body as []byte
                    })
            fmt.Printf("A message was sent to queue %v: %v", queueName, body)
            return err
    }

               
A bit heavy on the boilerplate, but should be easy enough to understand. Declare the queue (so it's created if it does not exist) and then publish our _[]byte_ message to it. The code that publishes a message to a named exchange is more complex as it requires boilerplate to first declare an exchange, a queue and then code to _bind_ them together. See the [complete source](https://github.com/callistaenterprise/goblog/blob/P9/common/messaging/messagingclient.go#L38) for an example.

Moving on, the actual user of our "MessageClient" will be _/goblog/accountservice/service/handlers.go_, so we'll add a field for that and the hard-coded "is VIP" check that will send a message if the requested account was has id "10000":

    var DBClient dbclient.IBoltClient
    var MessagingClient messaging.IMessagingClient     // NEW
    
    func GetAccount(w http.ResponseWriter, r *http.Request) {
         ...
      
a bit further down

        ...
        notifyVIP(account)   // Send VIP notification concurrently.
    
        // If found, marshal into JSON, write headers and content
    	data, _ := json.Marshal(account)
        writeJsonResponse(w, http.StatusOK, data)
    }
    
    // If our hard-coded "VIP" account, spawn a goroutine to send a message.
    func notifyVIP(account model.Account) {
            if account.Id == "10000" {
                    go func(account model.Account) {
                            vipNotification := model.VipNotification{AccountId: account.Id, ReadAt: time.Now().UTC().String()}
                            data, _ := json.Marshal(vipNotification)
                            err := MessagingClient.PublishOnQueue(data, "vipQueue")
                            if err != nil {
                                    fmt.Println(err.Error())
                            }
                    }(account)
            }
    }

Taking the opportunity to showcase an inlined anonymous function that we're calling on a new goroutine, i.e. using the _go_ keyword. Since we have no reason whatsoever to block the "main" goroutine that's executing the HTTP handler while sending a message, this is a perfect time to add a bit of concurrency.

_main.go_ also needs to be updated so it initializes the AMQ connection on startup using configuration loaded and injected into Viper.

    // Call this from the main method.
    func initializeMessaging() {
    	if !viper.IsSet("amqp_server_url") {
    		panic("No 'amqp_server_url' set in configuration, cannot start")
    	}
    
    	service.MessagingClient = &messaging.MessagingClient{}
    	service.MessagingClient.ConnectToBroker(viper.GetString("amqp_server_url"))
    	service.MessagingClient.Subscribe(viper.GetString("config_event_bus"), "topic", appName, config.HandleRefreshEvent)
    }

No big deal - we're assigning the _service.MessagingClient_ instance by creating an empty messaging struct and the calling ConnectToBroker using a property value fetched from Viper. If our configuration doesn't contain a _broker_url_, we panic as we don't want to be running without even the possibility to connect to the broker.

## Updating configuration
We added the _amqp_broker_url_ property to our .yml config files back in part 8, so that's already been taken care of.

    broker_url: amqp://guest:guest@192.168.99.100:5672
_(dev)_   
    
    broker_url: amqp://guest:guest@rabbitmq:5672
_(test)_

Note that for the "test" profile, we're using the Swarm Service name "rabbitmq" instead of the LAN IP address of the Swarm as seen from my dev laptop. (Your actual IP address may vary, 192.168.99.100 seems to be standard when running Docker Toolbox). 

As for having clear-text usernames and passwords in configuration files that's not recommended, in a real-life scenario one could typically use the built-in encryption feature of the Spring Cloud Config server we looked at in Part 8.

## Unit testing
Naturally, we should at least write a unit test that makes sure our _GetAccount_ function in _handlers.go_ does try to send a message whenever someone requests the magical and very very special account identified by "10000".

For this - we need a mock implementation of the IMessagingClient and a new test case in _handlers_test.go_. Let's start with the mock. This time we'll use the 3rd party tool [mockery](https://github.com/vektra/mockery) to generate a mock implementation of our IMessagingClient interface:
_(remember to run these commands in a shell with a proper GOPATH set)_

    > go get github.com/vektra/mockery/.../
    > cd $GOPATH/src/github.com/callistaenterprise/goblog/common/messaging 
    > ./$GOPATH/bin/mockery -all -output .
      Generating mock for: IMessagingClient
 
 Now we have a mock file _IMessagingClient.go_ in our current folder. I don't like the name of the file nor the camelcasing, so we'll rename it to something that makes it evident that it's a mock and follows the conventions for file names used in the blog series:
 
     mv IMessagingClient.go mockmessagingclient.go
     
It's possible you'll need to adjust the imports somewhat in the generated file, removing the import aliases. Other than that, we'll use a black-box approach to this particular mock - just assume it'll work when we start writing tests.
     
Feel free to examine the [source](https://github.com/callistaenterprise/goblog/blob/P9/common/messaging/mockmessagingclient.go) of the generated mock implementation, it's very similar to the stuff we hand-coded back in [part 4](/blogg/teknik/2017/03/03/go-blog-series-part4/) of the blog series.

Moving on to _handlers_test.go_ we're adding a new test case:

    // declare mock types to make test code a bit more readable
    var anyString = mock.AnythingOfType("string")
    var anyByteArray = mock.AnythingOfType("[]uint8")  // == []byte


    func TestNotificationIsSentForVIPAccount(t *testing.T) {
            // Set up the DB client mock
            mockRepo.On("QueryAccount", "10000").Return(model.Account{Id:"10000", Name:"Person_10000"}, nil)
            DBClient = mockRepo
    
            mockMessagingClient.On("PublishOnQueue", anyByteArray, anyString).Return(nil)
            MessagingClient = mockMessagingClient
    
            Convey("Given a HTTP req for a VIP account", t, func() {
                    req := httptest.NewRequest("GET", "/accounts/10000", nil)
                    resp := httptest.NewRecorder()
                    Convey("When the request is handled by the Router", func() {
                            NewRouter().ServeHTTP(resp, req)
                            Convey("Then the response should be a 200 and the MessageClient should have been invoked", func() {
                                    So(resp.Code, ShouldEqual, 200)
                                    time.Sleep(time.Millisecond * 10)    // Sleep since the Assert below occurs in goroutine
                                    So(mockMessagingClient.AssertNumberOfCalls(t, "PublishOnQueue", 1), ShouldBeTrue)
                            })
            })})
    }
    
For details, follow the comments. I don't like that artificial 10 ms sleep just before asserting numberOfCalls, but since the mock is called in a goroutine separate from the "main thread" we need to allow it a tiny bit of time to complete. Hope there's a better idiomatic way of unit-testing when there's goroutines and channels involved. 

I admit - mocking this way is more verbose than using something like Mockito when writing unit-tests for a Java application. Still, I think it's quite readable and easy enough to write.

Make sure that the test passes:

    go test ./...
    
## Running
If you havn't, run the the _springcloud.sh_ script to update the config server. Then, run _copyall.sh_ and wait a few seconds while our "accountservice" is updated. We'll use curl to fetch our "special" account.

    > curl http://$ManagerIP:6767/accounts/10000
    {"id":"10000","name":"Person_0","servedBy":"10.255.0.11"}
    
If things went well, we should be able to open the RabbitMQ admin console and see if we've gotten a message on a queue named _vipQueue_.

    open http://192.168.99.100:15672/#/queues
    
![rabbitmq with 1 message in queue](/assets/blogg/goblog/part9-rabbitmq.png)

At the very bottom of the screenshot above, we see that the "vipQueue" has 1 message. If we use the "Get Message" function within the RabbitMQ admin console, we can look at this message:

![the message](/assets/blogg/goblog/part9-rabbitmq2.png)

# Writing a consumer in Go - the "Vipservice"
Finally, it's time to write a brand new microservice from scratch that we'll use to showcase how to consume a message from RabbitMQ. We'll make sure to apply the patterns we've learned in the blog series up until now, including:

- HTTP server
- Health check
- Centralized configuration
- Reuse of messaging code

If you've checked out the P9 source you can already see the "vipservice" in the root _/goblog_ folder.

I won't go through every single line of code here as some parts are repeated from the "accountservice". Instead we'll focus on the consuming the message we just sent. A few things to note:

- Two new .yml files added to the config-repo, _vipservice-dev.yml_ and _vipservice-test.yml_
- _copyall.sh_ has been updated so it builds and deploys both the "accountservice" and our new "vipservice".

## Consuming a message
We'll use the code from _/goblog/common/messaging_ and the _SubscribeToQueue_ function, e.g:

    SubscribeToQueue(queueName string, consumerName string, handlerFunc func(amqp.Delivery)) error
        
Of most note here is the that we're supposed to provide:
 
- the name of the queue (e.g. "vip_queue")
- a consumer name (who we are) 
- a handler function that will be invoked with a received delivery - very similar to what we did when consuming config updates in part 8. 

The implementation of _SubscribeToQueue_ that actually binds our callback function to a queue isn't that exciting, check the [source](https://github.com/callistaenterprise/goblog/blob/P9/common/messaging/messagingclient.go#L170) if you want the details. 

Moving on, a quick peek at an excerpt of the vipservice's _main.go_ shows how we're setting things up:

    var messagingClient messaging.IMessagingConsumer
    
    func main() {
    	fmt.Println("Starting " + appName + "...")
    
    	config.LoadConfigurationFromBranch(viper.GetString("configServerUrl"), appName, viper.GetString("profile"), viper.GetString("configBranch"))
    	initializeMessaging()
    
    	// Makes sure connection is closed when service exits.
    	handleSigterm(func() {
    		if messagingClient != nil {
    			messagingClient.Close()
    		}
    	})
    	service.StartWebServer(viper.GetString("server_port"))
    }
    
    // The callback function that's invoked whenever we get a message on the "vipQueue"
    func onMessage(delivery amqp.Delivery) {
    	fmt.Printf("Got a message: %v\n", string(delivery.Body))
    }
    
    func initializeMessaging() {
            if !viper.IsSet("amqp_server_url") {
                panic("No 'broker_url' set in configuration, cannot start")
            }
            messagingClient = &messaging.MessagingClient{}
            messagingClient.ConnectToBroker(viper.GetString("amqp_server_url"))
            
            // Call the subscribe method with queue name and callback function
            err := messagingClient.SubscribeToQueue("vip_queue", appName, onMessage)
            failOnError(err, "Could not start subscribe to vip_queue")

            err = messagingClient.Subscribe(viper.GetString("config_event_bus"), "topic", appName, config.HandleRefreshEvent)
            failOnError(err, "Could not start subscribe to " + viper.GetString("config_event_bus") + " topic")
    }
    
Looks familiar, right? We'll probably repeat the basics of how to setup and boot each microservice we add.

The _onMessage_ function just logs the body of whatever "vip" message we receive. If we would implement more of our make-believe use case it would have invoked some fancy logic to determine if the account holder was eligible for the _"super-awesome buy all our stuff (tm)"_ offer and possible write an offer to the "VIP offer database". Feel free to implement and submit a pull request ;)

Not much to add. Except this snippet that allows us to clean up whenever we press Ctrl+C or when Docker Swarm thinks it's time to kill a service instance:

       func handleSigterm(handleExit func()) {
               c := make(chan os.Signal, 1)
               signal.Notify(c, os.Interrupt)
               signal.Notify(c, syscall.SIGTERM)
               go func() {
                       <-c
                       handleExit()
                       os.Exit(1)
               }()
       }
       
Not the most readable piece of code, what is does is that it registers the channel "c" as listener for os.Interrupt and syscall.SIGTERM and a goroutine that will block listening for message on "c" until either of the signals are received. This allows us to be pretty sure that the _handleExit()_ function we supplied will be invoked whenever the microservice is being killed. How sure? Ctrl+C or docker swarm scaling works fine. _kill_ does too. _kill -9_ doesn't. So please don't stop stuff using _kill -9_ unless you have to.

It will call that _Close()_ func we declared on the IMessageConsumer interface, which in the implementation makes sure the AMQP conn is properly closed.

# Deploy and run
The _[copyall.sh](https://github.com/callistaenterprise/goblog/blob/P9/copyall.sh)_ script has been updated, so if you're following along make sure it's up-to date with branch P9 on github and run it. When everything's done, _docker service ls_ should print something like this:

    > docker service ls
    ID            NAME            REPLICAS  IMAGE                        
    kpb1j3mus3tn  accountservice  1/1       someprefix/accountservice                                                                            
    n9xr7wm86do1  configserver    1/1       someprefix/configserver                                                                              
    r6bhneq2u89c  rabbitmq        1/1       someprefix/rabbitmq                                                                                  
    sy4t9cbf4upl  vipservice      1/1       someprefix/vipservice                                                                                
    u1qcvxm2iqlr  viz             1/1       manomarks/visualizer:latest
    
(or using the [dvizz](https://github.com/eriklupander/dvizz) Docker Swarm services renderer):

![dvizz](/assets/blogg/goblog/part9-dvizz.png)

### Checking logs
Since the _docker service logs_ feature is marked as experimental in 1.13.0, we have to look at the "vipservice" logs the old-school way. First, run _docker ps_ to figure out the container id:

    > docker ps
    CONTAINER ID        IMAGE                                                                                       
    a39e6eca83b3        someprefix/vipservice:latest           
    b66584ae73ba        someprefix/accountservice:latest        
    d0074e1553c7        someprefix/configserver:latest       
    
Pick the CONTAINER ID for the vipservice and check its logs using _docker logs -f_:

    > docker logs -f a39e6eca83b3
    Starting vipservice...
    2017/06/06 19:27:22 Declaring Queue ()
    2017/06/06 19:27:22 declared Exchange, declaring Queue ()
    2017/06/06 19:27:22 declared Queue (0 messages, 0 consumers), binding to Exchange (key 'springCloudBus')
    Starting HTTP service at 6868
    
Open another command shell and curl our special Account object.

    > curl http://$ManagerIP:6767/accounts/10000

If everything works, we should see a message being consumed in the log of the original window.

    Got a message: {"accountId":"10000","readAt":"2017-02-15 20:06:27.033757223 +0000 UTC"}
   
# Work queues
A pattern for distributing work across multiple instances of a service is to utilize the concept of [work queues](https://www.rabbitmq.com/tutorials/tutorial-two-go.html). Each "vip message" should be processed by a single "vipservice" instance.

![workqueue](/assets/blogg/goblog/part9-workqueue.png)

So let's see what happens when scale our "vipservice" to two instances using the _docker service scale_ command:

    > docker service scale vipservice=2
    
A new instance of "vipservice" should be available within a few seconds.

Since we're using the _direct/queue_ approach in AMQP we expect round-robin behaviour. Use _curl_ to trigger four VIP account lookups:
 
    > curl http://$ManagerIP:6767/accounts/10000
    > curl http://$ManagerIP:6767/accounts/10000
    > curl http://$ManagerIP:6767/accounts/10000
    > curl http://$ManagerIP:6767/accounts/10000
    
Check the log of our original "vipservice" again:

    > docker logs -f a39e6eca83b3
    Got a message: {"accountId":"10000","readAt":"2017-02-15 20:06:27.033757223 +0000 UTC"}
    Got a message: {"accountId":"10000","readAt":"2017-02-15 20:06:29.073682324 +0000 UTC"}

As expected, we see that the first instance processed two of the four expected messages. If we'd do _docker logs_ for the other "vipservice" instance we'd see two messages there as well. Promise.    
    
## Testing the consumer
Actually - I havn't really come up with an attractive way to unit test the AMQP consumer without spending a ridiculous amount of time mocking the amqp library. There's a test in [messagingclient_test.go](https://github.com/callistaenterprise/goblog/blob/P9/common/messaging/messagingclient_test.go) that tests the subscriber loop that waits indefinitely for incoming messages to process, but that's it.

For more thorough testing of messaging, I'll **probably** return to that topic in a future blog post about _integration testing_ Go microservices using _go test_ with the Docker Remote API or Docker Compose. The test would boot supporting services such as RabbitMQ it can use to send and receive actual messages in test code.

# Footprint and performance
Won't do performance tests this time around, a quick peek at memory use after sending and receiving some messages will have to suffice:

       CONTAINER                                    CPU %               MEM USAGE / LIMIT
       vipservice.1.tt47bgnmhef82ajyd9s5hvzs1       0.00%               1.859MiB / 1.955GiB
       accountservice.1.w3l6okdqbqnqz62tg618szsoj   0.00%               3.434MiB / 1.955GiB
       rabbitmq.1.i2ixydimyleow0yivaw39xbom         0.51%               129.9MiB / 1.955GiB
       
The above is after serving a few requests. The new "vipservice" is not as complex as the "accountservice" so it's expected it uses less RAM after startup.

# Summary

That was probably the longest part of the [series](/blogg/teknik/2017/02/17/go-blog-series-part1/) this far! We've accomplished:

- Examined RabbitMQ and the AMQP mechanics in more depth.
- Added a brand-new "vipservice".
- Extracted messaging (and config) code into a reusable sub-project.
- Publish / Subscribe of messages using the AMQP protocol.
- Mock code generation with mockery.

In [part 10](/blogg/teknik/2017/08/02/go-blog-series-part10), we'll do something more lightweight but just as important for a real-world operations model - structured logging using Logrus, the Docker GELF log driver and publishing logs to a [LaaS](https://en.wikipedia.org/wiki/Logging_as_a_service) provider.

