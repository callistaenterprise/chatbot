---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Go microservices, part 4 - testing and mocking with GoConvey
authors: 
  - eriklupander
tags: go microservices docker swarm docker spring cloud netflix oss goconvey mocking unit testing
topstory: true
comments: true

---

How should one approach testing of microservices? Are there any unique challenges one needs to take into account when establishing a testing strategy for this particular domain? In part 4 of this blog series, we will take a look at this topic.

- The subject of testing microservices in the unit context
- Write unit tests in the BDD-style of [GoConvey](http://goconvey.co/)
- Introduce a mocking technique

Since this part won't change the core service in any way, no benchmarks this time.

# Introduction to testing microservices

First of all, one should keep the principles of the [testing pyramid](https://martinfowler.com/bliki/TestPyramid.html) in mind. 

![pyramid](/assets/blogg/goblog/part4-pyramid.png)

Unit tests should form the bulk of your tests as integration-, e2e-, system- and acceptance tests are increasingly expensive to develop and maintain.

Secondly - microservices definitely offers some unique testing challenges and part of those is just as much about using sound principles when establishing a software architecture for your service implementations as the actual tests. That said - I think many of the microservice-specifics are beyond the realm of traditional unit tests which is what we're be going to deal with in this part of the blog series. 

Anyway, a few bullets I'd like to stress:

- Unit test as usual - there's nothing magic with your business logic, converters, validators etc. just because they're running in the context of a microservice.
- Integration components such as clients for communicating with other services, sending messages, accessing databases etc. should be designed with dependency injection and mockability taken into account.
- A lot of the microservice specifics - accessing configuration, talking to other services, resilience testing etc. can be quite difficult to unit-test without spending ridiculous amounts of time writing mocks for a rather small value. Save those kind of tests to integration-like tests where you actually boot dependent services as Docker containers in your test code. It'll provide greater value and will probably be easier to get up and running as well.

# Source code
As before, you may checkout the appropriate branch from the cloned repository to get the completed source of this part up front:

    git checkout P4

_Note: Most of the Go source code for the blog series was rewritten in July 2019 to better reflect contemporary idiomatic Go coding guidelines and design patterns. However, the corresponding [git branch](https://github.com/callistaenterprise/goblog/tree/P4) for each part of the series remains unchanged in order to stay aligned with the content of each installment. For the latest and greatest code, look at the [master](https://github.com/callistaenterprise/goblog) branch in github._

## Introduction
Unit testing in Go follows some idiomatic patterns established by the Go authors. Test source files are identified by naming conventions. If we, for example, want to test things in our _handlers.go_ file, we create the file _handlers_test.go_ in the same directory. So let's do that.

We'll start with a sad path test that asserts that we get a HTTP 404 if we request an unknown path:
    
    package service
    
    import (
            . "github.com/smartystreets/goconvey/convey"
            "testing"
            "net/http/httptest"
    )
    
    func TestGetAccountWrongPath(t *testing.T) {
    
            Convey("Given a HTTP request for /invalid/123", t, func() {
                    req := httptest.NewRequest("GET", "/invalid/123", nil)
                    resp := httptest.NewRecorder()
    
                    Convey("When the request is handled by the Router", func() {
                            NewRouter().ServeHTTP(resp, req)
    
                            Convey("Then the response should be a 404", func() {
                                    So(resp.Code, ShouldEqual, 404)
                            })
                    })
            })
    }
    
This test shows the "Given-When-Then" Behaviour-driven structure of GoConvey and also the "So A ShouldEqual B" assertion style. It also introduces usage of the httptest package where we use it to declare a request object as well as a response object we can perform asserts on in a convenient manner.

Run it by moving to the root "accountservice" folder and type:

    > go test ./...
    ?   	github.com/callistaenterprise/goblog/accountservice	[no test files]
    ?   	github.com/callistaenterprise/goblog/accountservice/dbclient	[no test files]
    ?   	github.com/callistaenterprise/goblog/accountservice/model	[no test files]
    ok  	github.com/callistaenterprise/goblog/accountservice/service	0.012s

Wonder about _./..._? It's us telling go test to run all tests in the current folder _and_ all subfolders. We could also go into the _/service_ folder and type _go test_ which then would only execute tests within that folder.

Since the "service" package is the only one with test files in it the other packages report that there are no tests there. That's fine, at least for now!

## Mocking
The test we created above doesn't need to mock anything since the actual call won't reach our _GetAccount_ func that relies on the DBClient we created in [part 3](/blogg/teknik/2017/02/27/go-blog-series-part3). For a happy-path test where we actually want to return something, we somehow need to mock the client we're using to access the BoltDB. There are a number of strategies on how to do mocking in Go. I'll show my favourite using the [stretchr/testify/mock](https://github.com/stretchr/testify#mock-package) package.

In the _/dbclient_ folder, create a new file called _mockclient.go_ that will be an implementation of our [IBoltClient](https://github.com/callistaenterprise/goblog/blob/P4/accountservice/dbclient/boltclient.go#L14) interface.

    package dbclient
    
    import (
            "github.com/stretchr/testify/mock"
            "github.com/callistaenterprise/goblog/accountservice/model"
    )
    
    // MockBoltClient is a mock implementation of a datastore client for testing purposes.
    // Instead of the bolt.DB pointer, we're just putting a generic mock object from
    // strechr/testify
    type MockBoltClient struct {
            mock.Mock
    }
    
    // From here, we'll declare three functions that makes our MockBoltClient fulfill the interface IBoltClient that we declared in part 3.
    func (m *MockBoltClient) QueryAccount(accountId string) (model.Account, error) {
            args := m.Mock.Called(accountId)
            return args.Get(0).(model.Account), args.Error(1)
    }
    
    func (m *MockBoltClient) OpenBoltDb() {
            // Does nothing
    }
    
    func (m *MockBoltClient) Seed() {
            // Does nothing
    }
   
MockBoltClient can now function as our explicitly tailored programmable mock. As stated above, this code implicitly implements the IBoltClient interface since the _MockBoltClient_ struct has functions attached that matches the signature of all functions declared in the IBoltClient interface.

If you dislike writing boilerplate code for your mocks, I recommend taking a look at [Mockery](https://github.com/vektra/mockery) which can generate mocks for any Go interface.

The body of the QueryAccount function may seem a bit weird, but it is simply how strechr/testify provides us with a programmable mock where we have full control of its internal mechanics.

## Programming the mock

Let's create another test function in _handlers_test.go_:

    func TestGetAccount(t *testing.T) {
            // Create a mock instance that implements the IBoltClient interface
            mockRepo := &dbclient.MockBoltClient{}
    
            // Declare two mock behaviours. For "123" as input, return a proper Account struct and nil as error.
            // For "456" as input, return an empty Account object and a real error.
            mockRepo.On("QueryAccount", "123").Return(model.Account{Id:"123", Name:"Person_123"}, nil)
            mockRepo.On("QueryAccount", "456").Return(model.Account{}, fmt.Errorf("Some error"))
            
            // Finally, assign mockRepo to the DBClient field (it's in _handlers.go_, e.g. in the same package)
            DBClient = mockRepo
            ...
    }
    
Next, replace the ... above with another GoConvey test:

    Convey("Given a HTTP request for /accounts/123", t, func() {
            req := httptest.NewRequest("GET", "/accounts/123", nil)
            resp := httptest.NewRecorder()

            Convey("When the request is handled by the Router", func() {
                    NewRouter().ServeHTTP(resp, req)

                    Convey("Then the response should be a 200", func() {
                            So(resp.Code, ShouldEqual, 200)

                            account := model.Account{}
                            json.Unmarshal(resp.Body.Bytes(), &account)
                            So(account.Id, ShouldEqual, "123")
                            So(account.Name, ShouldEqual, "Person_123")
                    })
            })
    })
    
This test performs a request for the known path _/accounts/123_ which our mock knows about. In the "When" block, we assert HTTP status, unmarshal the returned Account struct and asserts that the fields match what we asked the mock to return.

What I like about GoConvey and the Given-When-Then way of writing tests is that they are really easy to read and have great structure.

We might as well add another sad path where we request _/accounts/456_ and assert that we get a HTTP 404 back:

    Convey("Given a HTTP request for /accounts/456", t, func() {
            req := httptest.NewRequest("GET", "/accounts/456", nil)
            resp := httptest.NewRecorder()

            Convey("When the request is handled by the Router", func() {
                    NewRouter().ServeHTTP(resp, req)

                    Convey("Then the response should be a 404", func() {
                            So(resp.Code, ShouldEqual, 404)
                    })
            })
    })
    
Finish by running our tests again:
    
    > go test ./...
    ?   	github.com/callistaenterprise/goblog/accountservice	[no test files]
    ?   	github.com/callistaenterprise/goblog/accountservice/dbclient	[no test files]
    ?   	github.com/callistaenterprise/goblog/accountservice/model	[no test files]
    ok  	github.com/callistaenterprise/goblog/accountservice/service	0.026s

All green! GoConvey actually has an [interactive GUI](http://goconvey.co/) that can execute all tests everytime we save a file. I won't go into detail about it but looks like this and also provides stuff like automatic code coverage reports:

![goconvey-goblog.png](/assets/blogg/goblog/goconvey-goblog.png)
    
# Other types of tests
These GoConvey tests are unit tests though the BDD-style of writing them isn't everyone's cup of tea. There are many other testing frameworks for Golang, a quick search using your favourite search engine will probably yield many interesting options.

If we move up the [testing pyramid](https://martinfowler.com/bliki/TestPyramid.html) we'll want to write [integration tests](https://en.wikipedia.org/wiki/Integration_testing) and finally acceptance-style tests perhaps using something such as cucumber. That's out of scope for now but we can hopefully return to the topic of writing integration tests later on where we'll actually bootstrap a real BoltDB in our test code, perhaps by using the Go Docker Remote API and a pre-baked BoltDB image.

Another approach to integration testing is automating deployment of the dockerized microservice landscape. See for example the [blog post](https://callistaenterprise.se/blogg/teknik/2016/05/05/testing-microservices-with-golang/) I wrote last year where I use a little Go program to boot all microservices given a .yaml specification, including the support services and then performing a few HTTP calls to the services to make sure the deployment is sound.

# Summary

In this part we wrote our first unit tests, using the 3rd party _GoConvey_ and _stretchr/testify/mock_ libraries to help us. We'll do more tests in later parts of the [blog series](https://callistaenterprise.se/blogg/teknik/2017/02/17/go-blog-series-part1/).

In the [next part](/blogg/teknik/2017/03/09/go-blog-series-part5), it's time to finally get Docker Swarm up and running and deploy the microservice we've been working on into the swarm.