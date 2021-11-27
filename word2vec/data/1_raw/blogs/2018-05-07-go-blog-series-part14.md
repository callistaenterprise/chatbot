---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Go Microservices blog series, part 14 - GraphQL.
authors: 
  - eriklupander
tags: go microservices graphql docker swarm zuul
topstory: true
comments: true

---
In this part of the Go microservices [blog series](https://callistaenterprise.se/blogg/teknik/2017/02/17/go-blog-series-part1/), we'll take a look at using [GraphQL](https://graphql.org/) for serving Account objects to our clients.

# Contents
1. Overview
2. GraphQL
3. Schemas, Fields and Types with graphql-go
4. Resolver function
5. Queries
6. Unit tests
7. Serving over HTTP
8. Summary

### Source code

The finished source can be cloned from github:

    > git clone https://github.com/callistaenterprise/goblog.git
    > git checkout P14

_Note: Most of the Go source code for the blog series was rewritten in July 2019 to better reflect contemporary idiomatic Go coding guidelines and design patterns. However, the corresponding [git branch](https://github.com/callistaenterprise/goblog/tree/P14) for each part of the series remains unchanged in order to stay aligned with the content of each installment. For the latest and greatest code, look at the [master](https://github.com/callistaenterprise/goblog) branch in github._

# 1. Overview

This part of the blog series won't introduce any new services, it will only add a new /graphql POST endpoint to the "accountservice" which will be wired to serve requests as defined by the [graphql schema](https://graphql.org/learn/schema/) we'll define in Go code.

# 2. GraphQL

GraphQL was developed internally by Facebook and was publicly released in 2015. It provides an alternative query language to RESTful and other architectures for serving data from a server to a client. It's perhaps most unique feature is that GraphQL allows clients to define how the data requested shall be structured, rather than letting the server decide. This means that clients can fetch exactly the data required, mitigating the classic problems of fetching either too much or too little data for the use case at hand.

I recommend digging into the [official documentation](https://graphql.org/learn/) for more detailed explanations.

# 3. Schemas with graphql-go

Let's take a quick look at setting up a GraphQL schema using key concepts such as types, field, resolve functions, root queries and the resulting schema.

#### 3.1 Schemas, types and fields
The schema defines what types and fields that can be selected in a GraphQL query. GraphQL isn't tied to any particular DSL or programming language. Since this is a Go blog, I'll use Go GraphQL schemas according to the [graphql-go/graphql](https://github.com/graphql-go/graphql) project on github.

Here's the GraphQL type definition of the "AccountEvent" we introduced in part 13 of the blog series:

    var accountEventType = graphql.NewObject(   // Create new object
        graphql.ObjectConfig{                   // Declare object config
            Name: "AccountEvent",               // Name of the type
            Fields: graphql.Fields{             // Map declaring the fields of this type
                "id": &graphql.Field{           // Field declaration, "id" is its name 
                    Type: graphql.String,       // of type string.
                },
                "eventName": &graphql.Field{
                    Type: graphql.String,
                },
                "created": &graphql.Field{
                    Type: graphql.String,
                },
            },
        }
    )

The type declaration above is about as simple as it gets with GraphQL, not that unlike a Go struct declaration.

However, it gets a bit more hairy when we introduce Resolver functions, arguments and link together several declared types into a composite object.

Here's a somewhat simplified type declaration for our "Account" type that pretty much mirrors the output struct we're currently using:

    // accountType, includes Resolver functions for inner quotes and events.
    var accountType = graphql.NewObject(graphql.ObjectConfig{
        Name: "Account",
        Fields: graphql.Fields{
            "id": &graphql.Field{                // The id, name and servedBy fields should be familiar
                Type: graphql.String,
            },
            "name": &graphql.Field{
                Type: graphql.String,
            },
            "servedBy": &graphql.Field{
                Type: graphql.String,
            },
            
            // continued...
            
This first part is very similar to the "accountEventType" we've already declared, just "primitive" fields on a type, no big deal. 

However, the next part of the "accountType" declaration becomes much more complex when we declare that the "accountType" contains a _list_ of "accountEventType"s and a _Resolve_ function.

We'll see the Resolve function for actual Account objects later when we look at a GraphQL queries. In that context, the Resolve function is the piece of code that actually fetches Account structs (or whatever) from some data source (BoltDB, Hard-coded, CockroachDB ...) and stuffs that data into the GraphQL runtime that makes sure the outputted data conforms with the structure requested by the query.

The Resolve function below operates on already-fetched data (accounts) and performs filtering of each item's "events" using the "eventName" argument if the query has specified such:

            
            "events": &graphql.Field{                      // Here's how we declare that our "account" type can contain  
                Type: graphql.NewList(accountEventType),   // a list field. Declare "events" as type List of the accountEvent
                                                           // type we declared in the last code sample.
                Args: graphql.FieldConfigArgument{         // Args declare _what_ fields we allow queries to use when filtering
                    "eventName": &graphql.ArgumentConfig{  // this sublist in the context of the parent account type.
                        Type: graphql.String,
                    },
                },
                                                           // Resolve functions on types allows us to use declared (and possibly supplied) 
                                                           // args in order to perform filtering of items from a sub-list.
                Resolve: func(p graphql.ResolveParams) (interface{}, error) {
                    account := p.Source.(internalmodel.Account)     // Get the struct we're performing filtering on.

                    events := make([]model.AccountEvent, 0)         // Create a new slice to return the wanted accountEvents in.
                    
                    for _, item := range account.AccountEvents {    // Iterate over all accountEvents on this account.
                        
                        if item.EventName == p.Args["eventName"] {  // Add to new list only if predicate is true
                            events = append(events, item)
                        }
                    }
                    return events, nil                             // Return the new list.
                },    
            },                                                   
            // truncated for brevity...
                
Resolve functions was the hardest part for me to get a grasp on, we'll see a bit more Resolve code in just a little bit when looking at the Resolve function for the actual account query.

### 3.2 Putting the schema together

In order for a client to be able to fetch account objects, we need to create a _schema_ consisting of a _SchemaConfig_ with a _RootQuery_ specifying queryable _Fields_. 

    Schema <- SchemaConfig <- RootQuery <- Field(s)

In Go code this is declared like this:

    rootQuery := graphql.ObjectConfig{Name: "RootQuery", Fields: fields}
    schemaConfig := graphql.SchemaConfig{Query: graphql.NewObject(rootQuery)}
    var err error
    schema, err = graphql.NewSchema(schemaConfig)
    
Deceptively simple. The actual complexity is in the _fields_ argument. We'll declare a single Field called "Account":

    // Schema
    fields := graphql.Fields{
        "Account": &graphql.Field{
            Type: graphql.Type(accountType),               // See accountType above
            Args: graphql.FieldConfigArgument{
                "id": &graphql.ArgumentConfig{
                    Type: graphql.String,
                },
                "name": &graphql.ArgumentConfig{
                    Type: graphql.String,
                },
            },
            Resolve: resolvers.AccountResolverFunc,
        },
    }
    
This looks an awful lot like the stuff we've already declared, which is kind of the point.

My interpretation of what we're actually seeing is that the declared "Account" field is a query on the RootQuery. 

* This "Account" field consists of a single GraphQL type "accountType" - e.g. exactly the type we defined above. 
* The "Account" defines two arguments that can be used for querying an account - id and name.
* The "Account" defines a _Resolve_ func that is provided by a named function reference from another package.

I'd say the final schema with fields and types could be represented like this:

![classdiagram](/assets/blogg/goblog/part14-cd.png)

If we wanted a GraphQL query that returns a list of Accounts, another field could be declared such as:

    "AllAccounts": &graphql.Field{
        Type: graphql.NewList(accountType),          // List of accountType objects
        Args: graphql.FieldConfigArgument{
            "name": &graphql.ArgumentConfig{
                Type: graphql.String,
            },
        },
        Resolve: resolvers.AllAccountsResolverFunc,   // Some function that returns all accounts
    },

That Field on the RootQuery specifies a List of accountType as its type. The single "name" argument could perhaps be implemented as a "like" search or similar in the specified "AllAccountsResolverFunc" function.

# 4. Resolver implementation and testing

So, now that we have put our schema together, how do we actually tie our underlying data model to the Resolver functions declared in that "resolvers" parameter? (It's passed as argument to the function setting up all this stuff)

One of the sweet things about being able to pass Resolve functions that duck-types to the

    functionName(p graphql.ResolveParams) (interface{}, error)
   
signature is that we easily can provide different implementations for unit tests and real implementations. This is done using good ol' go interfaces and implementations:

    // GraphQLResolvers defines an interface with our Resolver function(s)
    type GraphQLResolvers interface {
    	AccountResolverFunc(p graphql.ResolveParams) (interface{}, error)
    }
    
    // LiveGraphQLResolvers - actual implementation used when running outside of unit tests.
    type LiveGraphQLResolvers struct {
    
    }
    
    func (gqlres *LiveGraphQLResolvers) AccountResolverFunc(p graphql.ResolveParams) (interface{}, error) {
    	account, err := fetchAccount(p.Context, p.Args["id"].(string))
    	if err != nil {
    		return nil, err
    	}
    	return account, nil
    }
    
    // TestGraphQLResolvers - implementation used in unit tests.
    type TestGraphQLResolvers struct {
    
    }
    
    func (gqlres *TestGraphQLResolvers) AccountResolverFunc(p graphql.ResolveParams) (interface{}, error) {
    	id, _ := p.Args["id"].(string)
    	name, _ := p.Args["name"].(string)
    	for _, account := range accounts {                     // The accounts slice is declared elsewhere in the same file as test data.
    		if account.ID == id || account.NAME == name {
    			return account, nil
    		}
    	}
    	return nil, fmt.Errorf("No account found matching ID %v or Name %v", id, name)
    }
    
* The "live" implementation uses a "fetchAccount" function that actually talks to the other microservices (dataservice, quotes-service, imageservice) to fetch the requested account object. Nothing new there except some refactoring that makes sure our old _/accounts/{accountId}_ HTTP endpoint uses the same code to get account objects as the new "fetchAccount" function used by our GraphQL resolve function.
* The "test" implementation uses a hard-coded slice of Account objects and returns if matching either argument.

The resolver implementation used is simply whatever the calling code supplies. In unit tests:

    func TestFetchAccount(t *testing.T) {
        initQL(&TestGraphQLResolvers{}) // Test implementation passed.
        ....
        
When started from the main func - i.e. either running standalone or when started within a Docker container), this line is invoked instead:

    initQL(&LiveGraphQLResolvers{})
 
# 5. GraphQL queries

So far, we've only laid the groundwork. The purpose of GraphQL is after all facilitating those dynamic queries mentioned back in section #2 of this blog post.

GraphQL [queries](http://graphql.org/learn/queries/) in their basic form simply asks for specific fields on objects declared in the schema. For example, if we want an Account object only containing the "name" and the events, the query would look like this:

    query FetchSingleAccount {         // Query and an arbitrary name for the query. This is optional!!                          
    	Account(id: "123") {           // We want to query the "Account" field on the RootQuery having id "123"
        	name, events{              // Include the "name" and "events" fields in the response.
            	eventName,created      // On the "events", include only eventName and created timestamp.
            }
        }
    }
    
The response would look like:

    {
        "data":{
            "Account":{
                "name":"Firstname-2483 Lastname-2483",
                "events":[{
                    "created":"2018-02-01T15:26:34.847","eventName":"CREATED"
                }]
            }
        }
    }
    
Note that we **must** specify what fields we want on the events, otherwise the following error would be returned:

    "Field "events" of type "[AccountEvent]" must have a sub selection.",
    
We'll see a  more complex example in the unit tests section below.

There's tons of stuff one can do using GraphQL queries, read up on fragments, parameters, variables etc. [here](http://graphql.org/learn/queries/).


# 6. Unit testing

How do we assert that our schema is actually set up in a valid way and that our queries will work? Unit-tests to the rescue!

All the GraphQL code has gone into the file [/accountservice/service/accountql.go](https://github.com/callistaenterprise/goblog/blob/P14/accountservice/service/accountql.go) and thus it's corresponding unit tests lives in [/accountservice/service/accountql_test.go](https://github.com/callistaenterprise/goblog/blob/P14/accountservice/service/accountql_test.go).

Let's start by specifying a GraphQL query as a multi-line string. The query uses variables, field selection and argument passing to the quote and events sub-fields. 

    var fetchAccountQuery = `query fetchAccount($accid: String!) {
        Account(id:$accid) {
            id,name,events(eventName:"CREATED") {
                eventName
            },quote(language:"en") {
                quote
            },imageData{id,url}
        }
    }`
    
Next, the test function:

    func TestFetchAccount(t *testing.T) {
        initQL(&TestGraphQLResolvers{})                                       // #1 Init GraphQL schema with test resolvers
        Convey("Given a GraphQL request for account 123", t, func() {
            vars := make(map[string]interface{})                              // #2 Variables
            vars["accid"] = "123"
            
            // #3 Create parameters object with schema, variables and the query string
            params := graphql.Params{Schema: schema, VariableValues: vars, RequestString: fetchAccountQuery}
    
            Convey("When the query is executed", func() {
                r := graphql.Do(params)                       // #4 Execute the query   
                rJSON, _ := json.Marshal(r)                   // #5 Transform the response into JSON
    
                Convey("Then the response should be as expected", func() {
                
                    // #6 Assert stuff...
                    So(len(r.Errors), ShouldEqual, 0)         
                    So(string(rJSON), ShouldEqual, `{"data":{"Account":{"events":[{"eventName":"CREATED"}],"id":"123","imageData":{"id":"123","url":"http://fake.path/image.png"},"name":"Test Testsson 3","quote":{"quote":"HEJ"}}}}`)
                })
            })
        })
    }    
    
1. The very first thing we do is to call the _initQL_ func, passning our **test** Resolver implementation. The _initQL_ func is the one that we looked at in section #3, that sets up our schema, fields etc..
2. We declare a String => interface{} map used to pass [variables](http://graphql.org/learn/queries/#variables) into the query execution.
3. The _graphql.Params_ contains the schema, variables and the actual query we want to execute.
4. The query is executed by passing the param object into the _graphql.Do(...)_ func.
5. Transform response into JSON
6. Assert no errors and expected output.

The structure of the test above makes it quite simple to write queries and test them against your schema. The actual output will of course vary depending on what test data your TestResolvers are using and how they are treating arguments passed to them.
    
# 7. Wiring the GraphQL HTTP endpoint

All this GraphQL stuff is rather useless unless we can provide the functionality to consumers of our service. It's time to wire the GraphQL functionality into our HTTP router!

# 7.1 Code setup
Let's take a look at [/accountservice/service/routes.go](https://github.com/callistaenterprise/goblog/blob/P14/accountservice/service/routes.go) where a new _/graphql_ route has been declared:

    Route{
        "GraphQL",  // Name
        "POST",     // HTTP method
        "/graphql", // Route pattern
        gqlhandler.New(&gqlhandler.Config{
            Schema: &schema,
            Pretty: false,
        }).ServeHTTP,
    },
   
Quite simple actually - the endpoint takes the query as POST body and the handler function is provided by a [graphql-go/handler](https://github.com/graphql-go/handler) that accepts _our_ schema (declared in accountql.go within the same package) as argument.

We just need to make sure _initQL(..)_ is invoked someplace with our _live_ resolver functions, for example in our [router.go](https://github.com/callistaenterprise/goblog/blob/P14/accountservice/service/router.go) before initializing the routes:

    func NewRouter() *mux.Router {
    
    	initQL(&LiveGraphQLResolvers{})               // HERE!!
    
    	router := mux.NewRouter().StrictSlash(true)
    	for _, route := range routes {
    	    // rest omitted ...
    	    

### 7.2 Build and run

_(A note on **copyall.sh**: There's just one change to our copyall.sh script this time around, which is that we're back to using standard logging instead of our little "gelftail". While using a Logging-as-a-Service is a must for production environment, it's a bit inconvenient when developing. Since Docker added "docker service logs [servicename]" a while back, it's now much easier seeing the logs without having to look up container id's using **docker ps** . So, for now we'll do our logging old-school.)_
 
To test our GraphQL stuff in a runtime environment, start your Docker Swarm mode server, make sure you have branch P14 checked out from git and run the _./copyall.sh_ script to build and deploy.

As always, deployment take a little while, but once everything is up and running, our brand new http://accountservice:6767/graphql endpoint should be ready for action.

Let's use curl to try it out! 
_(Note that I'm using 192.168.99.100 since that's the IP of my local Docker Swarm mode node)_

    > curl -d '{Account(id: "ffd508b5-5f87-4246-9867-ead4ecb01357") {name, events{eventName, created}}}' -X POST -H "Content-Type: application/graphql" http://192.168.99.100:6767/graphql
    
    {"data":{"Account":{"events":[{"created":"2018-02-01T15:26:34.847","eventName":"CREATED"}],"name":"Firstname-2483 Lastname-2483"}}}
   
Note that we're passing an appropriate Content-Type header. 

I've also exposed the _/graphql_ endpoint in our Zuul EDGE server by adding an entry to the application.yaml. So we can call it through our reverse-proxy too including HTTPS termination:

    > curl -k -d '{Account(id: "ffd508b5-5f87-4246-9867-ead4ecb01357") {name, events{eventName, created}}}' -X POST -H "Content-Type: application/graphql" https://192.168.99.100:8765/api/graphql
        
Note that the ID used in the queries above is for an Account already present in my CockroachDB Accounts database.

To obtain an account id to query with, I've added a two helper GET endpoints to the "dataservice" exposed at port 7070. First, a little _/random_ endpoint you can use to get hold of an Account instance, e.g:

    > curl http://192.168.99.100:7070/random
    {"ID":"10000","name":"Person_0","events":[{"ID":"8f1d0b2f-aa78-4672-85e0-5018870de550","eventName":"CREATED","created":"2018-05-06T09:21:06.747"}
    
If your database is empty (e.g. the above returns a HTTP 500), it should be possible to seed 100 accounts using another little utility endpoint _/seed_
    
    > curl http://192.168.99.100:7070/seed
    (wait a while)
    {'result':'OK'}
    
**Please note that running /seed removes all entries from your CockroachDB!!**
    
### 7.3 Introspecting the schema

A very useful trait of GraphQL is it's capability to describe itself to clients using [introspection](https://graphql.org/learn/introspection/).

By doing queries on __schema and __type, we can obtain info about the schema we declared. This query returns all types in the schema:

    {
      __schema {
        types {
          name
        }
      }
    }
    
Response:

    {
        data": {
            "__schema": {
                "types": [
                    {
                    "name": "Account"
                    },
                      {
                    "name": "__Type"
                    },
                      {
                    "name": "Boolean"
                    },
                      {
                    "name": "__DirectiveLocation"
                    },
                      {
                    "name": "AccountImage"
                    },
                    ... omitted for brevity ...
                ],
            }
        }
    }    
    
We can also take a closer look at the "Account" type, which after all is what we're usually dealing with in this API:

    {
      __type(name: "Account") {
        name
        fields {
          name
          type {
            name
            kind
            ofType {
              name
              kind
            }
          }
        }
      }
    }
    
Response:

    {
    "data": {
        "__type": {
        "fields": [
            {
                "name": "events",
                "type": {
                    "kind": "LIST",
                    "name": null,
                    "ofType": {
                        "kind": "OBJECT",
                        "name": "AccountEvent"
                    }
                }
            },
            {
                "name": "id",
                "type": {
                    "kind": "SCALAR",
                    "name": "String",
                    "ofType": null
                }
            },
            ... Omitted for brevity ...
    },  
    
The query lists available fields and their type on the "Account" type, including the type of list LIST kind, e.g. AccountEvent.

### 7.3 Graphiql

There's 3rd party GUIs that uses the introspection functionality to provide a GUI to explore and prototype queries, most notably [graphiql](https://github.com/graphql/graphiql).

One can install GraphiQL into the cluster or run a local client. I'm using [graphiql-app](https://github.com/skevy/graphiql-app) that's an Electron wrapper around Graphiql. To install on a Mac, use brew:

    > brew cask install graphiql
    
Point the URL at our API running inside the local Docker Swarm mode cluster and enjoy full code-completion etc for writing queries or looking at the schema:

![graphiql](/assets/blogg/goblog/part14-graphiql.png)
    
# 8. Summary

That's about it! In this part, we added support for querying our account objects using GraphQL. While our usage is pretty basic, it should get you started using GraphQL with Go. There's a lot more to explore when it comes to GraphQL, for further studies I recommend the [official introduction](http://graphql.org/learn/) as well as the [wehavefaces.net](https://wehavefaces.net/).

In the [next part](https://callistaenterprise.se/blogg/teknik/2018/09/12/go-blog-series-part15/), we'll finally get to adding support for monitoring using Prometheus endpoints.

Please help spread the word! Feel free to share this blog post using your favorite social media platform, there's some icons below to get you started.

Until next time,

// Erik

