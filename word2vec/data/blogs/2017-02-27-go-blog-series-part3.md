---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Go Microservices, part 3 - embedded database and JSON
authors: 
  - eriklupander
tags: go microservices docker swarm docker spring cloud netflix oss boltdb json
topstory: true
comments: true

---

In part 3, we'll make our Accountservice do something useful.

- Declare an 'Account' struct
- Embed a simple key-value store that we can store Account structs in.
- Serialize a struct to JSON and serve over our /accounts/{accountId} HTTP service.

# Source code
As in all upcoming parts of this blog series, you can get the complete source code of this part by cloning the source (see [part 2](/blogg/teknik/2017/02/21/go-blog-series-part2)) and switching to the P3 branch, i.e:

    git checkout P3

_Note: Most of the Go source code for the blog series was rewritten in July 2019 to better reflect contemporary idiomatic Go coding guidelines and design patterns. However, the corresponding [git branch](https://github.com/callistaenterprise/goblog/tree/P3) for each part of the series remains unchanged in order to stay aligned with the content of each installment. For the latest and greatest code, look at the [master](https://github.com/callistaenterprise/goblog) branch in github._

## Declaring an Account struct
For a more elaborate introduction to Go structs, please check [this guide](https://www.golang-book.com/books/intro/9).

In our project, create a folder named _model_ under the /accountservice folder.

    mkdir model
    
Now, create a file named _account.go_ in the _model_ folder with the following content:

    package model
    
    type Account struct {
            Id string `json:"id"`
            Name string  `json:"name"`
    }
    
This declares our _Account_ abstraction that basically is an id and a name. The case of the first letter denotes scoping (Upper-case == public, lower-case package-scoped). We also use the built-in support for declaring how each field should be serialized by the json.Marshal function in Go.

### Embedding a key-value store
For this, we'll use the [BoltDB](https://github.com/boltdb/bolt) key-value store. It's simple, fast and easy to work with. We can actually preempt _go get_ to retrieve the dependency before we've declared use of it:

    go get github.com/boltdb/bolt

Next, in the _/goblog/accountservice_ folder, create a new folder named "dbclient" and a file named _boltclient.go_. To make mocking easier later on, we'll start by declaring an interface that defines the contract we need implementors to fulfill:

    package dbclient
    
    import (
            "github.com/callistaenterprise/goblog/accountservice/model"
    )
    
    type IBoltClient interface {
            OpenBoltDb()
            QueryAccount(accountId string) (model.Account, error)
            Seed()
    }
    
In the same file, we'll provide an implementation of this interface. Start by declaring a struct that encapsulates a pointer to a bolt.DB instance.

    // Real implementation
    type BoltClient struct {
            boltDB *bolt.DB
    }
    
Here is the implementation of _OpenBoltDb()_. We'll add the two remaining functions a bit further down.
    
    func (bc *BoltClient) OpenBoltDb() {
            var err error
            bc.boltDB, err = bolt.Open("accounts.db", 0600, nil)
            if err != nil {
                    log.Fatal(err)
            }
    }

This part of Go syntax can feel a bit weird at first, where we bind a function to a struct. Our struct now implicitly implements one of the three methods.

We'll need an instance of this "bolt client" somewhere. Let's put it where it's going to be used, in _/goblog/accountservice/service/handlers.go_. Create that file and add the instance of our struct:
    
      package service
      
      import (
              "github.com/callistaenterprise/goblog/accountservice/dbclient"
      )
      
      var DBClient dbclient.IBoltClient
    
Update _main.go_ so it'll open the DB on start:

    func main() {
            fmt.Printf("Starting %v\n", appName)
            initializeBoltClient()                 // NEW
            service.StartWebServer("6767")
    }
    
    // Creates instance and calls the OpenBoltDb and Seed funcs
    func initializeBoltClient() {
            service.DBClient = &dbclient.BoltClient{}
            service.DBClient.OpenBoltDb()
            service.DBClient.Seed()
    }

Our microservice should now create a database on start. However, before running we'll add a piece of code that'll bootstrap some accounts for us on startup.

## Seed some Accounts on startup
Open _boltclient.go_ again and add the following functions:

    // Start seeding accounts
    func (bc *BoltClient) Seed() {
            initializeBucket()
            seedAccounts()
    }
    
    // Creates an "AccountBucket" in our BoltDB. It will overwrite any existing bucket of the same name.
    func (bc *BoltClient) initializeBucket() {
            bc.boltDB.Update(func(tx *bolt.Tx) error {
                    _, err := tx.CreateBucket([]byte("AccountBucket"))
                    if err != nil {
                            return fmt.Errorf("create bucket failed: %s", err)
                    }
                    return nil
            })
    }

    
    // Seed (n) make-believe account objects into the AcountBucket bucket.
    func (bc *BoltClient) seedAccounts() {
    
            total := 100
            for i := 0; i < total; i++ {
    
                    // Generate a key 10000 or larger
                    key := strconv.Itoa(10000 + i)
    
                    // Create an instance of our Account struct
                    acc := model.Account{
                            Id: key,
                            Name: "Person_" + strconv.Itoa(i),
                    }
    
                    // Serialize the struct to JSON
                    jsonBytes, _ := json.Marshal(acc)
    
                    // Write the data to the AccountBucket
                    bc.boltDB.Update(func(tx *bolt.Tx) error {
                            b := tx.Bucket([]byte("AccountBucket"))
                            err := b.Put([]byte(key), jsonBytes)
                            return err
                    })
            }
            fmt.Printf("Seeded %v fake accounts...\n", total)
    }
    
For more details on the Bolt API and how the Update method accepts a func that does the work for us, see the [BoltDB documentation](https://github.com/boltdb/bolt#using-buckets).

We're done with the BoltDB part for now. Let's build and run again:

    > go run *.go
    Starting accountservice
    Seeded 100 fake accounts...
    2017/01/31 16:30:59 Starting HTTP service at 6767
    
Lovely! Stop it using Ctrl+C.

## Adding a Query method
Now we finish our little DB API by adding a Query method to the _boltclient.go_:

    func (bc *BoltClient) QueryAccount(accountId string) (model.Account, error) {
            // Allocate an empty Account instance we'll let json.Unmarhal populate for us in a bit.
            account := model.Account{}
    
            // Read an object from the bucket using boltDB.View
            err := bc.boltDB.View(func(tx *bolt.Tx) error {
                    // Read the bucket from the DB
                    b := tx.Bucket([]byte("AccountBucket"))
    
                    // Read the value identified by our accountId supplied as []byte
                    accountBytes := b.Get([]byte(accountId))
                    if accountBytes == nil {
                            return fmt.Errorf("No account found for " + accountId)
                    }
                    // Unmarshal the returned bytes into the account struct we created at
                    // the top of the function
                    json.Unmarshal(accountBytes, &account)
    
                    // Return nil to indicate nothing went wrong, e.g no error
                    return nil
            })
            // If there were an error, return the error
            if err != nil {
                    return model.Account{}, err
            }
            // Return the Account struct and nil as error.
            return account, nil
    }
    
Follow the comments if the code doesn't make sense. The function will query the BoltDB using a supplied _accountId_ parameter and will return an Account struct _or_ an error.

## Serving the Account over HTTP
Let's fix the _/accounts/{accountId}_ route we declared in _/service/routes.go_ so it actually returns one of the seeded Account structs. Open routes.go and replace the inlined _func(w http.ResponseWriter, r *http.Request) {_ with a reference to a function _GetAccount_ we'll create in a moment:

    Route{
            "GetAccount",             // Name
            "GET",                    // HTTP method
            "/accounts/{accountId}",  // Route pattern
            GetAccount,
    },

Next, update _/service/handlers.go_ with a _GetAccount_ func that fulfills the HTTP handler func signature:
    
    var DBClient dbclient.IBoltClient
    
    func GetAccount(w http.ResponseWriter, r *http.Request) {
    
    	// Read the 'accountId' path parameter from the mux map
    	var accountId = mux.Vars(r)["accountId"]
    
            // Read the account struct BoltDB
    	account, err := DBClient.QueryAccount(accountId)
    
            // If err, return a 404
    	if err != nil {
    		w.WriteHeader(http.StatusNotFound)
    		return
    	}
    
            // If found, marshal into JSON, write headers and content
    	data, _ := json.Marshal(account)
    	w.Header().Set("Content-Type", "application/json")
    	w.Header().Set("Content-Length", strconv.Itoa(len(data)))
    	w.WriteHeader(http.StatusOK)
    	w.Write(data)
    }
    
The GetAccount func fulfills the handler func signature so when Gorilla detects a call to /accounts/{accountId} it will route the request into the GetAccount function. Let's run it!

    > go run *.go
    Starting accountservice
    Seeded 100 fake accounts...
    2017/01/31 16:30:59 Starting HTTP service at 6767

Call the API using curl. Remember, we seeded 100 accounts starting with an Id of 10000.

    > curl http://localhost:6767/accounts/10000
    {"id":"10000","name":"Person_0"}
    
Nice! Our microservice is now actually serving JSON data from an underlying store over HTTP.

# Footprint and performance
Let's check the same memory and CPU usage metrics as in [part 2](/blogg/teknik/2017/02/21/go-blog-series-part2): Before, during and after our simple Gatling-based load test.

## Memory usage after startup
![mem use](/assets/blogg/goblog/part3-memuse.png)

2.1 mb, still not bad! Adding the embedded BoltDB and some more code to handle routing etc. added 300kb to our initial footprint. Let's start the Gatling test running 1K req/s. Now we're actually returning a real Account object fetched from the BoltDB which also is serialized to JSON:

## Memory usage after load test
![mem use2](/assets/blogg/goblog/part3-memuse2.png)
31.2 mb of RAM. The extra overhead of serving 1K req/s using an embedded DB was really small compared to the naive service from Part 2.

## Performance and CPU usage
![cpu use](/assets/blogg/goblog/part3-cpuuse.png)
Serving 1K req/s uses about 10% of a single Core. The overhead of the BoltDB and JSON serialization is not very significant, good! By the way - the _java_ process at the top is our Gatling test which actually uses ~3x the CPU resources as the software it is testing.

![performance](/assets/blogg/goblog/part3-performance.png)
Mean response time is still less than one millisecond. 

Perhaps we should test with a heavier load, shall we say 4K req/s? (Note that one may need to increase the number of available file handles on the OS level):

## Memory use at 4K req/s
![mem use](/assets/blogg/goblog/part3-memuse4k.png)
Approx 120 mb. Almost exactly an increase by 4x. This memory scaling with n/o concurrent requests is almost certainly due to the Golang runtime or possibly Gorilla increasing the number of internal goroutines used to serve requests concurrently as load goes up.

## Performance at 4K req/s
![cpu use](/assets/blogg/goblog/part3-cpuuse4k.png)
CPU use stays just below 30% at 4K req/s. At this point, i.e. running on a 16 GB RAM / Core i7 equipped laptop, I'd say that IO or file handles would bottleneck sooner than available CPU cycles.

![performance](/assets/blogg/goblog/part3-performance4k.png)
Mean latency now finally rises above 1 ms with 95% of requests staying below 3ms. We do see latency starting to take a hit at 4K req/s, though I'd personally say that the little Accountservice with its embedded BoltDB performs really well.

# Comparison to other platforms
One could probably write an interesting blog post about benchmarking this "accountservice" against an functionally equivalent microservice implemented on the JVM, NodeJS, CLR and others. 

I did some _naive_ inconclusive benchmarking (using a Gatling test) on this myself late 2015 comparing a HTTP/JSON service + MongoDB access implemented in Go 1.5 vs Spring Boot@Java 8 and NodeJS. In that particular case the JVM and Go-based solutions scaled equally well with a slight edge to the JVM-based solution regarding latencies. The NodeJS server performed quite similarly to the others up to the point where the CPU utilization reached 100% on a single core and things started going south regarding latencies.
 
_Please don't take the benchmarking mentioned above as some kind of fact as it was just a quick and dirty thing I did for my own pleasure._
 
So while the numbers I've shown regarding performance at 4K req/s using Go 1.7 for the "accountservice" may seem very impressive, they can probably be matched by other platforms as well, though I doubt their memory use will be as pleasant. I guess your milage may vary.

# Final words

In the [next part](/blogg/teknik/2017/03/03/go-blog-series-part4) of this blog series we'll take a look at unit testing our service using GoConvey and mocking the BoltDB client.
