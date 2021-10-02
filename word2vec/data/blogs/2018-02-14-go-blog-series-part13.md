---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Go Microservices blog series, part 13 - data consistency, gorm and CockroachDB.
authors: 
  - eriklupander
tags: go microservices cockroachdb gorm docker swarm database sql acid 
topstory: true
comments: true

---
In this part of the Go microservices [blog series](https://callistaenterprise.se/blogg/teknik/2017/02/17/go-blog-series-part1/), we'll take a look at distributed data storage using [CockroachDB](https://www.cockroachlabs.com) and the [GORM](http://gorm.io/) O/R-mapper.

# Contents
1. Overview
2. The CAP theorem
3. CockroachDB
4. Installing CockroachDB
5. The new "Dataservice" with GORM
6. Running and testing an endpoint
7. Load test and resilience
8. Summary

### Source code

The finished source can be cloned from github:

    > git clone https://github.com/callistaenterprise/goblog.git
    > git checkout P13

_Note: Most of the Go source code for the blog series was rewritten in July 2019 to better reflect contemporary idiomatic Go coding guidelines and design patterns. However, the corresponding [git branch](https://github.com/callistaenterprise/goblog/tree/P13) for each part of the series remains unchanged in order to stay aligned with the content of each installment. For the latest and greatest code, look at the [master](https://github.com/callistaenterprise/goblog) branch in github._

# 1. Overview
Data consistency vs availability in distributed systems is a very interesting topic. These days, traditional [ACID](https://en.wikipedia.org/wiki/ACID) relational databases are often replaced by NoSQL databases operating on the principles of eventual consistency from the [BASE](https://en.wikipedia.org/wiki/Eventual_consistency) model. BASE combined with [bounded contexts](https://martinfowler.com/bliki/BoundedContext.html) often forms the basis of persistence in distributed microservice architectures.
 
Bounded contexts and eventual consistency can somewhat simplified be explained as:
 
- Bounded contexts are a central pattern in Domain-driven design, which is a very useful pattern when designing microservice architectures. For example - if you have an "Accounts" microservice and an "Orders" microservice, they should own their own data (e.g. "accounts" and "orders") in separate databases _without_ old-school foreign key constraints between them. Each microservice is solely responsible for writing and reading data from its own domain. If the "orders" microservice needs to know about the owning "account" for a given "order", the "orders" microservice must ask the "account" microservice for account data - the "orders" microservice may _not_ under any circumstance query or write directly to the tables or document stores of the "account" microservice.
- Eventual consistency can be several things. It's primarily the concept of a data replication mechanism where a given data write will _eventually_ be replicated across the distributed storage system so any given read will yield the latest version of the data. One can also consider it a requisite of the bounded context pattern, e.g. for a "business transaction" write that appears atomic to an outside viewer, many microservices may be involved in writing data across several bounded contexts without any distributed mechanisms guaranteeing a global ACID transaction. Instead, _eventually_ all involved microservices will have performed their writes, resulting in a consistent state across the distributed system from the perspective of the business transaction. See a good comparison of ACID and BASE [here](https://www.thoughtco.com/abandoning-acid-in-favor-of-base-1019674).

These days, many people turn to the NoSQL database [Apache Cassandra](http://cassandra.apache.org/) when they require horizontally scalable data storage with automatic replication and eventual consistency. However, I'm a bit curious how a cutting edge "SQL" database such as CockroachDB works in our microservice context, so that'll be the focus of this blog post. 

First, a few words about the [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem).  

# 2. The CAP theorem
CAP is a three-letter acronymn for database systems that claims that no distributed database may ever fulfill all these three criterias at any one time:

- Consistent: A read is guaranteed to return the _most recent_ write.
- Available: The choice is always between serving the data you have even though you can't guarantee that is the most recent version of it (a write may have occured 10 microseconds ago on another cluster member) OR you must deny serving data if you're not absolutely sure there's no inconsistent state of the requested data anywhere in the cluster.
- Partition tolerant: If a database server goes down, the remaining nodes must continue to function and when the failed node recovers, consistent data must still be served.

A distributed database may only choose two of above, making them either "CAP-Available" (AP) or "CAP-Consistent" (CP). The main advantage of an AP database is better latencies since CP databases must coordinate writes and reads across nodes, while an AP system is allowed to possibly return inconsistent or missing data which is faster. In other words - AP databases favor speed while CP databases favors robustness.  

Do note that it's fully possible to run a CAP-capable distributed database as long as there are no network or other problems. The problem is that there's always going to be network problems at some point, see [the fallacies of distributed computing](http://en.wikipedia.org/wiki/Fallacies_of_Distributed_Computing). This is especially relevant for microservices given that we're typically leaving the monolithic database of your enterprise behind, instead letting each microservice "own" their own domain of data - sometimes split over many databases, possibly even across multiple data centers.

CockroachDB is a CAP Consistent (CP) database. For a more in-depth explanation, check out this awesome [article](https://www.cockroachlabs.com/blog/limits-of-the-cap-theorem/) from cockroachlabs.

# 3. CockroachDB
CockroachDB was created by ex-Google employees that used to work on Google's [Cloud Spanner](https://cloud.google.com/spanner/). CockroachDB do - as prevoiusly stated - not claim to be a CAP-database, but claims full C and P, and a significant number of 9's for availability.

At it's core, CockroachDB is a distributed key-value store written in Go, but differs from its peers by having an ANSI-compliant SQL interface, behaving like a relational database in most, if not all, aspects. The authors are very transparent about CockroachDB still having some issues making it unsuitable for OLAP-like workloads. Essentially, JOIN operations are continuously being optimized but they still have quite a way to go until the JOIN performance is on par with old-school databases.

![cockroachdb overview](/assets/blogg/goblog/part13-cockroachdb-1.png)
_Source: Cockroachlabs_

A CockroachDB cluster _always_ consists of at least three database nodes, where the database will stay 100% operational if one node goes down. The underlying replication engine always makes sure any entry exists on at least two nodes with auto-replication if a node goes down. We'll get back to this claimed resilience a bit later where we'll stress test things while taking down a DB node, should be a fun exercise!

# 4. Install and run
Time to get this database installed and up and running in our cluster. We're going to pull v1.1.3 directly from Docker Hub and start three nodes, each running one instance of CockroachDB on separate ports. Since each node needs it's own mounted storage we cannot (AFAIK) run three _instances_ of a CockroachDB _docker swarm mode service_, we need three separate services.

For development purposes, this is actually very easy. I've prepared a bash-script to set this up:

    #!/bin/bash
    
    # CoachroachDB master, will publish admin GUI at 3030, mapped from 8080
    docker service rm cockroachdb1
    docker service create --name=cockroachdb1 --network=my_network -p 26257:26257 -p 3030:8080 --mount type=volume,source=cockroach-data1,target=/cockroach/cockroach-data cockroachdb/cockroach:v1.1.3 start --insecure
    
    # CoachroachDB
    docker service rm cockroachdb2
    docker service create --name=cockroachdb2 --network=my_network --mount type=volume,source=cockroach-data2,target=/cockroach/cockroach-data cockroachdb/cockroach:v1.1.3 start --insecure --join=cockroachdb1
    
    # CoachroachDB
    docker service rm cockroachdb3
    docker service create --name=cockroachdb3 --network=my_network --mount type=volume,source=cockroach-data3,target=/cockroach/cockroach-data cockroachdb/cockroach:v1.1.3 start --insecure --join=cockroachdb1

Let's dissect the first _docker service create_ a bit:

- Ports: We're publishing port 26257 which actually isn't necessary unless we want to try to connect to the cluster from the outside. We're also mapping the admin GUI locally at port 8080 to port 3030.
- Volume mounts. CockroachDB requires some persistent storage, so we're mounting a local folder as persistent storage using the _--mount_ flag. 
- Start command: _start --insecure_. We're supplying a _start_ command and the _--insecure_ argument (it's a CockroachDB argument, has nothing to do with Docker!) in order to run a local cluster without setting up certificates. Also note the _--join=cockroachdb1_ argument passed to the two "workers" telling them to form a cluster with their leader. 

Startup may take a few minutes, after which the green and pleasant admin GUI should be available in your favorite browser at http://192.168.99.100:3030:

![Overview](/assets/blogg/goblog/part13-cockroach-gui2.png)
_The overview_

![Nodes list](/assets/blogg/goblog/part13-cockroach-gui3.png)
_List of server nodes_

Nice! Now we're ready to create some databases and users. For more details, please check the rich [documentation](https://www.cockroachlabs.com/docs/stable/learn-cockroachdb-sql.html).

We're going to use the [built-in](https://www.cockroachlabs.com/docs/stable/use-the-built-in-sql-client.html) SQL client to create two databases and a two users - one for each of our bounded contexts. Since our CockroachDB instances are running in Docker Containers, we can't use _cockroach sql_ directly. We must do it by connecting to a running container using a bit of docker wizardry:

    > docker ps
    
    CONTAINER ID        IMAGE                                COMMAND         
    10f4b6c727f8        cockroachdb/cockroach:v1.1.3         "/cockroach/cockro..." 
 
Find a container running the _cockroachdb/cockroach_ container and note the container ID. Then we'll use _docker exec_ to launch the SQL CLI:  
   
    > docker exec -it 10f4b6c727f8 ./cockroach sql --insecure
    
    # Welcome to the cockroach SQL interface.
    # All statements must be terminated by a semicolon.
    # To exit: CTRL + D.
    #
    # Server version: CockroachDB CCL v1.1.3 (linux amd64, built 2017/11/27 13:59:10, go1.8.3) (same version as client)
    # Cluster ID: 5c317c3e-5784-4d8f-8478-ec629d8a920d
    #
    # Enter \? for a brief introduction.
    #
    root@:26257/>  
    
We're in!

I've prepared a .sql file whose contents we easily can copy-paste directly into the console. This is a one-time job for the purpose of this particular blog post. In a real-life scenario you'd obviously script this using some build automation tool.

    CREATE DATABASE account;
    CREATE DATABASE image;
    
    CREATE USER account_user WITH PASSWORD 'account_password';
    CREATE USER image_user WITH PASSWORD 'image_password';
    
    GRANT ALL ON DATABASE account TO account_user;
    GRANT ALL ON DATABASE image TO image_user;
    
Done! Now on to the wonderful world of Go and O/R-mapping!
    
# 5. Using CockroachDB from Go using GORM

### 5.1 Landscape overview
First let's start with a brand new overview of what the microservice landscape will look like once this part is done:

![New landscape overview](/assets/blogg/goblog/part13-overview.png)

Key stuff:

- The BoltDB is gone from the _accountservice_.
- The new "dataservice" will access _accounts_ and _account events_ stored in a CockroachDB database named "account".
- The existing "imageservice" will now store _image urls_ in another CockroachDB database named "image". (Remember, bounded-contexts and the share-nothing principle of microservices)
- The two databases above are both hosted in the three-node CockroachDB cluster. Data may exist on any two of three server nodes.
- The _accountservice_ used to both act as a service aggregator AND account storage. It's purpose is now strictly orchestrating the fetching of account objects by talking to the Go-based "imageservice" and "dataservice" as well as the Java-based "quotes-service" and then aggregating them to a unified response.
- The communication from our microservices to the CockroachDB cluster uses the [postgresql wire protocol](https://www.cockroachlabs.com/docs/stable/frequently-asked-questions.html#why-does-cockroachdb-use-the-postgresql-wire-protocol-instead-of-the-mysql-protocol).

### 5.2 GORM
GORM is an "[object-relational mapper](https://en.wikipedia.org/wiki/Object-relational_mapping)" (ORM) for Go - think of it as a rough equivalent of [Hibernate](http://hibernate.org/) or similar, although perhaps not as mature or fully-featured. Still - > 7000 stars on github and over 120 contributors gives an indication of a well-liked and commonly used library. 

CockroachDB uses the [postgresql wire protocol](https://www.cockroachlabs.com/docs/stable/frequently-asked-questions.html#why-does-cockroachdb-use-the-postgresql-wire-protocol-instead-of-the-mysql-protocol) which works very nicely with GORM - GORM has support for several major SQL vendors [out of the box](http://jinzhu.me/gorm/database.html#connecting-to-a-database).

What about tables where we'll store and retrieve actual data? In this particular blog, we'll utilize the [AutoMigrate](http://jinzhu.me/gorm/database.html#migration) feature of [GORM](http://jinzhu.me/gorm/) to create our tables. 

##### 5.2.1 Structs and gorm tags
The AutoMigrate feature introspects Go structs with 'gorm'-tags and automatically creates tables and columns given these structs. Let's take a closer look how we declare primary keys, foreign keys and an index directly on the structs by using gorm [tags](https://github.com/golang/go/wiki/Well-known-struct-tags).

    type AccountData struct {
        ID               string         `json:"" gorm:"primary_key"`
        Name             string         `json:"name"`
        AccountEvents    []AccountEvent `json:"events" gorm:"ForeignKey:AccountID"`
    }
    
    type AccountEvent struct {
        ID        string `json:"" gorm:"primary_key"`
        AccountID string `json:"-" gorm:"index"`
        EventName string `json:"eventName"`
        Created   string `json:"created"`
    }    

Most of the GORM tags should be self-explanatory for people vaguely familiar with relational databases - e.g. "primary_key", "index" etc.

The _AccountData_ struct has a [has-many](http://jinzhu.me/gorm/associations.html#has-many) relationship with _AccountEvents_, mapped using the "ForeignKey:AccountID" tag. This will result in AutoMigrate creating two tables with columns appropriate for each of the struct fields, including foreign key constraints and the specified index. The two tables will be created within the _same_ database with full referential integrity, i.e. they belong to the same "account data" [bounded context](https://martinfowler.com/bliki/BoundedContext.html) that'll be served by our new _dataservice_. The "image data" - consisting of a single _AccountImage_ struct, will belong to its own bounded context and be served from the _imageservice_ microservice.

The generated tables looks like this from the CockroachDB GUI:

![tables tables](/assets/blogg/goblog/part13-tables.png)

_(I've rearranged the codebase somewhat so "model" structs used by more than one service resides in _/goblog/common/model_ now.)_

##### 5.2.2 Working with Gorm
Dealing with Gorm requires surprisingly little boilerplate on the structs, but working with its DSL for querying and mutating data may take a little while getting used to. Let's take a look at a few basic use cases:

###### 5.2.2.1 Basics, Connection and AutoMigrate
All interactions with the GORM API in these examples happen through "gc.crDB" which is my wrapping of a pointer to [gorm.DB](https://godoc.org/github.com/jinzhu/gorm#DB), i.e:

    type GormClient struct {
        crDB *gorm.DB
    }
    
    var gc &GormClient{}

Below, we're opening the connection using _postgres_ SQL dialect and then calling the _AutoMigrate_ function to create tables.

     var err error
     gc.crDB, err = gorm.Open("postgres", addr)    // Addr is supplied from config server, of course
     if err != nil {
         panic("failed to connect database: " + err.Error())
     }
 
     // Migrate the schema
     gc.crDB.AutoMigrate(&model.AccountData{}, &model.AccountEvent{})  // Note that we pass the structs we want tables for.

######  5.2.2.2 Persisting data

    // Create an instance of our Account struct
    acc := model.AccountData{
        ID:     key,                      // A pre-generated string id
        Name:   randomPersonName(),       // Some person name
        Events: accountEvents,            // slice of AccountEvents
    }

    gc.crDB.Create(&acc)                  // Persist!
    
The code above will write both a row to the ACCOUNT_DATA table as well as any ACCOUNT_EVENT rows present in the Events slice, including foreign keys. Using the SQL client, we can try a standard JOIN:

    root@:26257> use account;
    root@:26257/account> SELECT * FROM account_data AS ad INNER JOIN account_events AS ae ON ae.account_id = ad.id WHERE ad.id='10000';
    +-------+----------+--------------------+------------+------------+---------------------+
    |  id   |   name   |         id         | account_id | event_name |       created       |
    +-------+----------+--------------------+------------+------------+---------------------+
    | 10000 | Person_0 | accountEvent-10000 |      10000 | CREATED    | 2017-12-22T21:38:21 |
    +-------+----------+--------------------+------------+------------+---------------------+
    (1 row)
    
We're seeding one AccountEvent per AccountData so the result is absolutely right!

######  5.2.2.3 Querying data
It's of course possible to use the postgres driver and do standard SQL queries like the one above. However, to leverage GORM appropriately, we'll use the [query DSL](http://jinzhu.me/gorm/crud.html#query) of GORM.

Here's an example where we load an AccountData instance by ID, [eagerly loading](http://jinzhu.me/gorm/crud.html#preloading-eager-loading) any AccountEvents related to it.

    func (gc *GormClient) QueryAccount(ctx context.Context, accountId string) (model.AccountData, error) {
        acc := model.AccountData{}                                 // Create empty struct to store result in
        gc.crDB.Preload("Events").First(&acc, "ID = ?", accountId) // Use the Preload to eagerly fetch events for 
                                                                   // the account. Note use of ID = ?
        if acc.ID == "" {                                          // Not found handling...
            return acc, fmt.Errorf("Not Found")
        }
        return acc, nil                                            // Return populated struct.
    }    
    
A more complex example - find all AccountData instances having a person whose name starts with 'Person_8' and count the number of AccountEvents for each entry.

    func (gc *GormClient) QueryAccountByNameWithCount(ctx context.Context, name string) ([]Pair, error) {
    
        rows, err := gc.crDB.Table("account_data as ad").             // Specify table including alias
        Select("name, count(ae.ID)").                                 // Select columns including count, see Group by
        Joins("join account_events as ae on ae.account_id = ad.id").  // Do a JOIN
        Where("name like ?", name + "%").                             // Add a where clause
        Group("name")                                                 // Group by name
        .Rows()                                                       // Call Rows() to execute the query
    
        result := make([]Pair, 0)                                     // Create slice for result
        for rows.Next() {                                             // Iterate over returned rows
            pair := Pair{}                                            // Pair is just a simple local struct
            rows.Scan(&pair.Name, &pair.Count)                        // Pass result into struct fields
            result = append(result, pair)                             // Add resulting pair into slice
        }
        return result, err                                            // Return slice with pairs.
    }    
    
Note the fluent DSL with Select..Joins..Where..Group which is surprisingly pleasant to work with once you get used to it. Should be familiar if you've worked with similar APIs in the past such as [JOOQ](https://en.wikipedia.org/wiki/Java_Object_Oriented_Querying) 
       
Calling an endpoint exposing the query above yields:

    [{
        "Name": "Person_80",
        "Count": 3
      }, 
      {
        "Name": "Person_81",
        "Count": 6
    }]
 
_Tidied up the response JSON for the sake of readability_

### 5.3 Unit Testing with GORM
Regrettably, there doesn't seem to be an idiomatic and super-simple way to unit-test GORM interactions with the database. Some strategies do however exist, such as:

- Using [go-sqlite3](https://github.com/mattn/go-sqlite3) to boot a real light-weight database in unit tests.
- Using [go-sqlmock](https://github.com/DATA-DOG/go-sqlmock), see some examples [here](https://github.com/jirfag/go-queryset/blob/master/queryset/queryset_test.go). 
- Using [go-testdb](https://github.com/erikstmartin/go-testdb).

In all honesty, I havn't really examined any of the options above closely. Instead, I've wrapped the GORM db struct in a struct of my own, which implicitly implements this interface:

     type IGormClient interface {
         QueryAccount(ctx context.Context, accountId string) (model.AccountData, error)
         QueryAccountByNameWithCount(ctx context.Context, name string) ([]Pair, error)
         SetupDB(addr string)
         SeedAccounts() error
         Check() bool
         Close()
     }        
  
Having an interface makes it very straightforward to use [testify/mock](github.com/stretchr/testify/mock) to mock any interaction with methods on the struct wrapping the GORM db object.  
    
# 6. Running and testing an endpoint
If you've cloned the source and have installed CockroachDB, you can execute the _./copyall.sh_ script to build and deploy the updated microservices:

- accountservice
- imageservice
- dataservice (NEW)
- vipservice

The configuration has been updated, including [.yaml-files](https://github.com/eriklupander/go-microservice-config/blob/P13/dataservice-test.yml) for the new "dataservice".

Once we're up and running, let's do a curl request to the "accountservice" _/accounts/{accountId}_ endpoint:

    > curl http://192.168.99.100:6767/accounts/10002 -k | json_pp
    {
       "imageData" : {
          "id" : "10002",
          "servedBy" : "10.0.0.26",
          "url" : "http://path.to.some.image/10002.png"
       },
       "id" : "10002",
       "servedBy" : "10.0.0.3",
       "name" : "Person_2",
       "accountEvents" : [
          {
             "ID" : "accountEvent-10002",
             "created" : "2017-12-22T22:31:06",
             "eventName" : "CREATED"
          }
       ],
       "quote" : {
          "ipAddress" : "eecd94253fcc/10.0.0.18:8080",
          "quote" : "To be or not to be",
          "language" : "en"
       }
    }

Looks good to me!

# 7. Load test and resilience
Let's get down to the business of testing whether our setup with CockroachDB is Consistent and Partition Tolerant, while providing acceptable levels of Availability.

Load- and resilience testing a microservice landscape with a distributed data store such as CockroachDB on a laptop running everything in virtualbox isn't that realistic perhaps, but should at least provide some insights.

For this purpose, I'm going to set up a landscape with the following characteristics:

- We'll bypass our EDGE server. We'll call the accountservice directly to remove TLS overhead for this particular test case.
- 1 instance of the _accountservice_, _imageservice_, _dataservice_ respectively.
- 2 instances of the _quotes-service_.
- 3 CockroachDB instances each running as a Docker Swarm mode service.

### 7.1 Results - Gatling

I've pre-seeded the "account" database with about 15000 records, including at least one "account_event" per "account". First test runs a [gatling](https://gatling.io) [test](https://github.com) that bombs away at the _/accounts/{accountId}_ microservice to fetch our account objects with a peak rate of 50 req/s.

##### 7.1.1 First run
The test runs for 75 seconds with a 5 second ramp-up time. 

![gatling report 1](/assets/blogg/goblog/part13-gatling2.png)
_Figure 7.1.1: Latencies (ms)_

Overall latencies are just fine, our microservices and the CockroachDB have no issue whatsoever handling ~50 req/s.
 
_(Why not more traffic? I ran into [this bug](https://github.com/moby/moby/issues/31746) which introduced 1 or 2 seconds of extra latency per "hop" inside the cluster when running the test for a longer time _or_ with more traffic - effectively making the results worthless for this test case)_ 

##### 7.1.2 Second run
During the second run at approx. 20:10:00 in the test, I'm deliberately killing the "cockroachdb3" service. At 20:10:30, I restart the "cockroachdb3" service.
 
![gatling report 2](/assets/blogg/goblog/part13-gatling1.png)
_Figure 7.1.2.1: Service response time (ms)_

Killing one of the three cockroachdb nodes and restarting it ~30 seconds later has the following effects:

- No requests fail. This is probably a combination of the CockroachDB master quickly stopping handing over queries to the unavailable node as well as the retrier logic in our microservice which makes sure a failed call from the _accountservice_ to the _dataservice_ is retried 100 ms later.
- Taking down the node just before 20:10:00 _probably_ causes the small latency spike at ~20:09:57_, though I'd say it is a very manageable little spike end-users probably wouldn't notice unless this was some kind of near-realtime trading platform or similar.
- The larger much more noticable spike actually happens when the "cockroachdb3" node comes back up again. My best guess here is that the cockroachdb cluster spends some CPU time and possibly blocks operations when the node re-joins the cluster making sure it's put into a synchronized state or similar.
- The mean service latency increased from 33 in run #1 to 39 in run #2, which indicates that while the "spike" at 20:10:30 is noticable, it affects relatively few requests as a whole causing just a slight adverse effect on the overall latencies of the test run.

##### 7.1.3 Both scenarios from the CockroachDB GUI
We can look at the same scenarios from the perspective of the CockroachDB GUI where we can examine a plethora of different metrics.

In the graphs below, we see both scenarios in each graph - i.e. we first run the Gatling test _without_ taking down a CockroachDB instance, while we do the same "kill and revive"-scenario a minute later.

![cockroachdb1](/assets/blogg/goblog/part13-cockroachdb-qps.png)
_Figure 7.1.3.1: CockroachDB queries per second over the last 10 seconds_

![cockroachdb2](/assets/blogg/goblog/part13-cockroachdb-99th.png)
_Figure 7.1.3.2: CockroachDB 99th percentile latency over the last minute_
                                                                          
![cockroachdb3](/assets/blogg/goblog/part13-cockroachdb-lnc.png)
_Figure 7.1.3.3: CockroachDB live node count_

The graphs from CockroachDB are pretty consistent with what we saw in the Gatling tests - _taking down_ a CockroachDB node has hardly any noticable effect on latencies or availabilty, while _taking up_ a node actually has a rather severe - though short-lived - effect on the system. 

##### 7.1.3 Resource utilization
A typical snapshot of Docker Swarm mode manager node CPU and memory utilization for a number of running containers during the first test:

    CONTAINER                                    CPU %               MEM USAGE / LIMIT    
    cockroachdb1.1.jerstedhcv8pc7a3ec3ck9th5     33.46%              207.9MiB / 7.789GiB  
    cockroachdb2.1.pkhk6dn93fyr14dp8mpqwkpcx     1.30%               148.3MiB / 7.789GiB 
    cockroachdb3.1.2ek4eunib4horzte5l1utacc0     10.94%              193.1MiB / 7.789GiB 
    dataservice.1.p342v6rp7vn79qsn3dyzx0mq6      8.41%               10.52MiB / 7.789GiB
    imageservice.1.o7odce6gaxet5zxrpme8oo8pr     9.81%               11.5MiB / 7.789GiB   
    accountservice.1.isajx2vrkgyn6qm50ntd2adja   17.44%              15.98MiB / 7.789GiB  
    quotes-service.2.yi0n6088226dafum8djz6u3rf   7.03%               264.5MiB / 7.789GiB 
    quotes-service.1.5zrjagriq6hfwom6uydlofkx1   10.16%              250.7MiB / 7.789GiB 

We see that the master CockroachDB instance (#1) takes most of the load, while #2 seems to be almost unused while #3 uses ~10% CPU. Not entirely sure what's going on under the hood among the CockroachDB nodes, probably the master node is handing off some work to the other node(s) (perhaps those requests whose data it doesn't store itself?).

Another note is that our Go microservices - especially the "accountservice" - is using a substantial amount of CPU serving the load - in a more real-life scenario we would almost certainly have scaled the accountservice to several worker nodes as well. On a positive note - our Go-based microservices are still using very little RAM.
 
### 7.2 Concurrent read/writes
This test case will _write_ random account objects through a new POST API in the _accountservice_ to the databases while simultaneously performing a lot of reads. We'll observe behaviour as we put the system under moderate (total ~140 DB interactions per second) load and finally see what happens when we pull the plug from one, then another, of the CockroachDB instances just like in 7.1.2 above.

This load-test that writes/reads things concurrently and acts upon newly created data is written in a simple Go [program](https://github.com/callistaenterprise/goblog/blob/P13/dbloadtest/main.go). We'll observe the behaviour by looking at the graphs in the CockroachDB admin GUI.

![concurrent 1](/assets/blogg/goblog/part13-cockroachdb-qps2.png)
_Figure 7.2.1: Queries per second and 99th percentile_
                                                      
![concurrent 2](/assets/blogg/goblog/part13-cockroachdb-lnc2.png)
_Figure 7.2.2: Node count_

![concurrent 3](/assets/blogg/goblog/part13-cockroachdb-replicas.png)
_Figure 7.2.3: Replicas_

What can we make of the above?

- CoachroachDB and our microservices seems to handle taking down and then up nodes during a read/write load quite well.
- The main noticable latency spike we see happens at 10:18:30 in the timeline when we bring "cockroachdb3" back up.
- Again - taking _down_ nodes are handled really well.
- Taking _up_ "cockroachdb2" at 10:15:30 was hardly noticable, while taking up "cockroachdb3" at 10:18:30 affected latencies much more. This is - as previously stated - probably related to how CockroachDB distributes data and queries amongst cluster members. For example - perhaps the ~500 records written per minute while a node were down is automatically replicated to the node that was unavailable when it comes back up.  
 
### 7.3 The issue of addressing
As you just saw, our cluster can handle when a CockroachDB worker node goes down, providing seamless balancing and failover mechanisms. The problem is that if we kill "cockroachdb1", things comes abruptly to a halt. This stems from the fact that our CoackroachDB cluster is running as three _separate_ Docker Swarm mode services - each having their own unique "cockroachdb1", "cockroachdb2" and "cockroachdb3" service name. Our _dataservice_ only knows about this connection URL:
 
     postgresql://account_user:account_password@cockroachdb1:26257/account 
                                                ^  HERE!  ^
 
so if the service named "cockroachdb1" goes down, we're in deep s--t. The setup with three separate Docker Swarm mode services is by the way the [official](https://www.cockroachlabs.com/docs/stable/orchestrate-cockroachdb-with-docker-swarm.html) way to run CockroachDB on Docker Swarm mode. 

Ideally, our "dataservice" should only need to know about a single "cockroachdb" service, but at this point I havn't figured out how to run three _replicas_ of a CockroachDB service which would make them a single adressable entity. The main issue seems to be mounting _separate_ persistent storage volumes for _each_ replica, but there may be other issues.

Anyway - my interrim **hacky** solution would probably be based around the concept of client-side load balancing (see [part 7](https://callistaenterprise.se/blogg/teknik/2017/04/24/go-blog-series-part7/) of the blog series), where our _dataservice_ would have to become Docker API-aware and use the Docker Remote API to get and maintain a list of IP-addresses for containers having a given label.

If we add _--label cockroachdb_ to our _docker service create_ commands, we could then apply a filter predicate for that label to a "list services" Docker API call in order to get all running CockroachDB instances. Then, it'll be straightforward to implement a simple round-robin client-side load balancing mechanism rotating connection instance(s) to the CockroachDB nodes including circuit-breaking and housekeeping.

![part13 - client side load balancer](/assets/blogg/goblog/part13-clb.png) 
_Figure 7.3_

I'd consider the above solution a hack, I'd much rather figure out how to run CockroachDB instances using replicas. Also - do note that running production databases inside containers with mounted storage is kind of [frowned upon](https://myopsblog.wordpress.com/2017/02/06/why-databases-is-not-for-containers/) anyway, so in a production scenario you'd probably want to use a dedicated DB cluster anyway. 

# 8. Summary
In this part of the blog series, we've added a "dataservice" that works with the CockroachDB database well suited to distributed operation, also using the Gorm O/R-mapper for Go for mapping our Go structs to SQL and back. While we've only scratched the surface of the capabilities of CockroachDB, our simple tests seems to indicate an open-source database that might be a really interesting candidate for systems that needs a SQL/ACID-capable relational database with horizontal scalability, consistency and high availability.

The [next part](https://callistaenterprise.se/blogg/teknik/2018/05/07/go-blog-series-part14/) ~~should deal with an issue that actually should be one of the first things to incorporate in a sound software architecture - security~~~ adds support for querying accounts using GraphQL. We'll get to security - promise!

Please help spread the word! Feel free to share this blog post using your favorite social media platform, there's some icons below to get you started.

Until next time,

// Erik

