---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Microservice landscape testing with Golang
authors: 
  - eriklupander
topstory: true
comments: true
---

In this blog post, we'll use [Golang](https://golang.org/) to boot and test a microservice environment.

-[readmore]-

Sometimes testing a microservice environment presents challenges not typically encountered when developing more traditional applications of the monolith kind. For example, our modern microservice environment may consist of a number of containers (we're using [Docker](https://www.docker.com/)) each providing a service or a support function for managing the microservice landscape. In this blog post, I'll be using the [tutorial series](https://callistaenterprise.se/blogg/teknik/2015/06/08/building-microservices-part-4-dockerize-your-microservices/) my colleague [Magnus](https://callistaenterprise.se/om/medarbetare/magnuslarsson/) has published on this blog and on github as our sample Microservice landscape. It consists of one public-facing service backed by several internal microservices and no less than six supporting services:

- Edge server [Zuul](https://github.com/Netflix/zuul)
- OAuth server [Spring](http://projects.spring.io/spring-security-oauth/docs/oauth2.html)
- Discovery server [Eureka](https://github.com/Netflix/eureka)
- Config server [Spring](http://cloud.spring.io/spring-cloud-static/docs/1.0.x/spring-cloud.html#_spring_cloud_config)
- Monitoring [Hystrix](https://github.com/Netflix/Hystrix)
- Messaging [RabbitMQ](https://www.rabbitmq.com/)

Want to try/run this yourself? Clone the [source code](https://github.com/callistaenterprise/blog-microservices/tree/B6) and follow instructions in the [blog post](https://callistaenterprise.se/blogg/teknik/2015/06/08/building-microservices-part-4-dockerize-your-microservices/)!

Part of the challenge here is to make all these components work together, something that requires a non-trivial amount of configuration. Also, making sure things stays that way over time is equally important. Typically, you have a CI/CD pipeline to detect regressions, but with container technology it is quite easy to bootstrap all components on your developer laptop (given enough RAM). This blog post won’t go into details about the inner workings of the sample project, what I intend to show is how we can use a simple golang program to efficiently bootstrap the entire landscape using [Docker compose](https://docs.docker.com/compose/), wait for service availability, run a number of endpoint tests and finally shut it all down again. In other words - a very simplistic testing framework for early detection of configuration or service regressions. To accomplish this we'll use my new favorite general-purpose non--JVM language - [Golang](https://golang.org)!

## Why golang?

This program was actually inspired by a bash shell script and it is certainly just as easy to do this using whatever console-friendly language you prefer. I like Go due to its relative simplicity, [quick compile time](http://stackoverflow.com/questions/2976630/why-does-go-compile-so-quickly), [goroutines](https://gobyexample.com/goroutines), portability and rich set of libraries.

## How?

It’s actually a rather trivial task, divided into a number of distinct steps:

1. Define how to test your landscape, we'll use a [YAML](http://yaml.org/) file.
2. Build and launch the Go program, specifying the YAML file you just filled in.
3. Await the outcome.
4. Live long and prosper.

### The YAML config file
Let’s start by having a look at a sample [YAML](http://yaml.org/) file for specifying the environment we want to boot and test:

    ---
    title: Microservices sample test file                                                #(1)
    docker_compose_root: /Users/myuser/projects/microservices-workshop/solution-7        #(2)
    docker_compose_file: docker-compose.yml                                              #(3)
    services:                                                                            #(4)
      - http://192.168.99.100:8761
      - http://192.168.99.100:8761/eureka/apps/edgeserver
      - http://192.168.99.100:8761/eureka/apps/product
      - http://192.168.99.100:8761/eureka/apps/productapi
      - http://192.168.99.100:8761/eureka/apps/productcomposite
      - http://192.168.99.100:8761/eureka/apps/recommendation
      - http://192.168.99.100:8761/eureka/apps/review
    oauth:                                                                               #(5)
      url: https://192.168.99.100:9999/uaa/oauth/token
      client_id: acme
      client_password: acmesecret
      scope: webshop
      grant_type: password
      username: user
      password: password
      token_key: access_token
    endpoints:                                                                           #(6) 
    - url: https://192.168.99.100/api/product/1046
      auth_method: TOKEN
    - url: https://192.168.99.100/api/product/1337
      auth_method: TOKEN
    - url: https://192.168.99.100/api/product/7331
      auth_method: TOKEN
              
The YAML files defines some environment specifics such as title, docker project root directory and file, what microservices to query Eureka for _before_ fetching OAuth token and testing services.

1. Title. Used used in some console output.
2. Absolute path to where the docker-compose.yml files lives.
3. Name of the docker-compose yml file. Usually we stick with the default 'docker-compose.yml'
4. List of microservice status endpoints provided by our discovery server, in this case Eureka. All URLs must respond with a HTTP status code indicating success for a GET request before retrieving the OAuth token and commencing service testing.
5. OAuth settings. client_id and client_password are used as HTTP Basic auth for retrieving an OAuth token for username/password. scope, grant_type and token_key are OAuth parameters.
6. List of (micro)service endpoints to actually test. Currently only GET is supported, should add support for POST/PUT/REMOVE, request bodies, parsing etc. Note that auth_method TOKEN and NONE are the currently supported ones.

## Go code

So, how does our little golang program tie this together? I would recommend starting by taking a look directly at the main.go source file main() method:

    func main() {
            CallClear() 
    
            // 1. Check required command-line tools are present
            // docker-compose etc.
            CheckDocker()
    
            // 2. Load service specification from yaml
            t := LoadSpecification()
    
            // 3. Start using docker-compose up -d, then use defer to make sure it's torn down afterwards.
            DockerComposeUp(t)
            defer DockerComposeDown(t)
            
            // 4. Then wait for specified microservices
            awaitServicesHasStarted(t)
    
            // 5. When all are started, get and store OAuth token                     
            StoreOAuthToken(t)
    
            // 6. execute list of endpoint HTTP calls.  (blocks until finished)
            runEndpoints(t)
    }


_CallClear()_ performs a "clear" or "cls" on the executing console depending on the host OS. For the sake of clarity, I've omitted some console output using fancy [VT100 console cursor control](http://www.termsys.demon.co.uk/vtansi.htm), will return to that later.

#### (1) Check if prerequisites are met

_exec.LookPath_ is a convenience method for checking if a certain executable is present on the PATH, in this case 'docker-compose'. If not present, we use the log.Fatal() to log and exit.

    func CheckDocker() {
            _, err := exec.LookPath("docker-compose")
            if err != nil {
                    log.Fatal("docker-compose not installed, fix!")
            }
            fmt.Printf("docker-compose installed OK\n")
    }
    
#### (2) Is where we use gopkg.in/yaml.v2 to load the spec .yaml file.

    func LoadSpecification() (TestDef) {
            spec := parseSpecFile()
            dir, _ := os.Getwd()
            dat, _ := ioutil.ReadFile(dir + "/" + spec)
            var t TestDef
            yaml.Unmarshal([]byte(dat), &t)
    
            fmt.Println("Loaded specification '" + t.Title + "'")
    
            return t
    }
    
Not too verbose - get the .yaml file cmd-line arg, current directory, read the file and pass a reference to an uninitialized TestDef struct into the yaml.Unmarshal method. The yaml library does all the parsing for us, allowing us to return the populated struct to the main() method.

#### (3) Use exec to run OS commands for bootstrapping our environment.

    func DockerComposeUp(t TestDef) {
            cmd := exec.Command("docker-compose", "-f", t.DockerComposeFile, "up", "-d")
            cmd.Dir = t.DockerComposeRoot
            env := os.Environ()
            env = append(env, fmt.Sprintf("PROJECT_ROOT=%s", t.DockerComposeRoot))
            cmd.Env = env
            cmd.Run()
            fmt.Println("Docker starting up using " + t.DockerComposeRoot + "/" + t.DockerComposeFile + " ...")
    }
    
The _exec.Command_ prepares a Cmd using varargs separated arguments to the docker-compose executable. '-f' specifies the file name and '-d' tells it to run in a daemon mode. Eventually, we'll call Run() on the _cmd_ instance. 

Note how we specify the docker-compose file using a value from our testDef and how we append a PROJECT_ROOT environment variable to the env of the Cmd. Each Cmd is only active for a given Cmd so it's _not_ possible in go to first do this:
         
         // WON'T WORK
         cmd1 := exec.Command("export", "PROJECT_ROOT=" + t.DockerComposeRoot)
         cmd1.Run()
         cmd2 := exec.Command("docker-compose", "-f", t.DockerComposeFile, "up", "-d")
         cmd2.Run()
         // WON'T WORK!!
         
In the faulty snippet above, the 'export' won't carry over to cmd2, making use of such a environment variable in the docker-compose.yml yield nil, hence the use of the environment trick in the correct example further up.

#### (4) Awaiting service startup

How do we know when all infrastructure and services have started and is ready for testing? Our best bet is to utilize Eureka - remember these?

    services:                                                                            #(4)
          - http://192.168.99.100:8761
          - http://192.168.99.100:8761/eureka/apps/config-server
          ...
          - http://192.168.99.100:8761/eureka/apps/product
          
The first URL is simply the root of the Eureka service - if Eureka isn't up we can't check the state of services that has registered with the discover service. Under _http://192.168.99.100:8761/eureka/apps/[service name]_ Eureka publishes status pages (XML) for each registered service. For our purpose, we're OK as long as a "OK" HTTP status code is returned. 

    func awaitServicesHasStarted(t TestDef) {
            wg := sync.WaitGroup{}
    
            fmt.Println("Waiting for all microservices to start...")
            consoleRow++
            fmt.Println("")
            consoleRow++
    
            for _, service := range t.Services {
                    wg.Add(1)
                    consoleRow++
                    go PollService(service, &wg, len(t.Services), consoleRow)
            }
            wg.Wait()         // Blocks here until all wg.Done() has been called within PollService.
    
            // Fix cursor position after all services have started
            consoleRow+=3
            fmt.Printf("\033[%d;0H", consoleRow)   // Move cursor to row
    }
    
Here we see some fun golang features in action, namely the [WaitGroup](https://golang.org/pkg/sync/#WaitGroup) and the [go](https://golang.org/ref/spec#Go_statements) keyword. What this snippet does is that it will spawn t.Services number of goroutines executing the PollService method. For each "go" wg.Add(1) tells the waitgroup to increment the number of future wg.Done() it needs to receive until continuing processing after wg.Wait().

    func PollService(service string, wg *sync.WaitGroup, total int, consoleRow int) {
    
            Cprint(consoleRow, 0, service)
            Cprint(consoleRow, 60, "... waiting ")
    
            req, _ := http.NewRequest("GET", service, nil)
            var DefaultTransport http.RoundTripper = &http.Transport{
                    TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
            }
    
            for {
                    resp, err := DefaultTransport.RoundTrip(req)
                    if err != nil || resp.StatusCode > 299 {
                            Cprint(consoleRow, 0, service)
                            Cprint(consoleRow, 60, "... waiting ")
                    }  else {
                            Cprint(consoleRow, 0, service)
                            Cprint(consoleRow, 60, "done                   ")
                            wg.Done()
                            return
                    }
                    time.Sleep(time.Second * 1)
            }
    }
    
Ignore all the Cprint calls for now, they're just for the VT100-style console output. The important part is the HTTP GET requests performed using net/http's DefaultTransport. DefaultTransport? Why not use the standard net/http client golang provides? Well - the easiest way of having golang's net/http client to accept servers with self-signed certificates is by setting the TLSClientConfig seen in the code.

Apart from the cert fix (and the ugly Cprint statements), the program will keep looping issuing one request per second to whatever Url that was specified in the _service_ parameter until a < 299 HTTP status is returned.

For example, _http://192.168.99.100:8761_ - which in our microservice landscape is the Eureka start page - won't return 200 OK until the Eureka service is up and running. Somewhat later, the "Product service" status can be queried by asking Eureka it's state at the _http://192.168.99.100:8761/eureka/apps/product_. So remember, it is not the actual service endpoint we are checking, we are just making sure it has booted and registered itself with its discovery service.

#### (5) Testing services
Actual endpoint testing is probably much more complex in a real-world scenario than here - you'd want full support for other HTTP methods, POST bodies, headers, response parsing etc. - which is out of scope for this little exercise. The service testing code (e.g. runEndpoints) is actually very similar to the PollService one, with the difference that we're adding a HTTP header with whatever OAuth token our request to [StoreOAuthToken](https://github.com/eriklupander/microservicetester/blob/master/src/github.com/eriklupander/mstest/oauthtoken.go) function yielded:

    req := BuildHttpRequest(endpoint.Url, endpoint.Method)
    var DefaultTransport http.RoundTripper = &http.Transport{
            TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
    }
    if endpoint.Auth_method == "TOKEN" {
        req.Header.Add("Authorization", "Bearer " + TOKEN)
    }
    
We then try each service up to 10 times before giving up:
    
    retries := 10
    for i := 0; i < retries; i++ {
            
            resp, err := DefaultTransport.RoundTrip(req)

            if err != nil || resp.StatusCode > 299 {
                    Cprint(consoleRow, 0, endpoint.Url)
                    Cprint(consoleRow, 70, "... failed. Retrying " + strconv.Itoa(i) + "/" + strconv.Itoa(retries) + " ...            ")
            } else {
                    Cprint(consoleRow, 0, endpoint.Url)
                    Cprint(consoleRow, 70, "... OK                                          ")
                    wg2.Done()
                    break
            }
            time.Sleep(time.Second * 3)

            if (i == retries - 1) {
                    wg2.Done()
                    Cprint(consoleRow, 0, endpoint.Url)
                    Cprint(consoleRow, 70, "... All attempts failed, something is broken.                                 ")
            }
    }
    
Again, we use a WaitGroup to make sure each goroutine can finish before the program exits.

#### Console printing with cursor control
Finally, the little CPrint method used to output program state to the console window:

    var l sync.Mutex
    
    func Cprint(row int, col int, text string) {
            l.Lock()
            fmt.Printf("\033[%d;%dH", row, col)
            fmt.Print(text)
            l.Unlock()
    }
    
We're simply using Printf with the VT100 escape sequence for positioning the cursor and row/col and then printing text. Since each goroutine may call this code to update console output at any time we need to use a lock mechanism or the output will become really garbled. Alternatively, we could have used a sync go channel instead, see bottom of this blog post for an example.

## Running it
Below, we have a sample output from a run. 

    > go run src/github.com/eriklupander/mstest/*.go spec.yml
    
    Starting up...
    docker-compose installed OK
    Loaded specification 'Microservices sample test file'
    Docker starting up using /Users/eriklupander/privat/blog-microservices/docker-compose.yml ...
    Waiting for all microservices to start...
    
    
    http://192.168.99.100:8761                                 done                   
    http://192.168.99.100:8761/eureka/apps/edgeserver          done                   
    http://192.168.99.100:8761/eureka/apps/product             done                   
    http://192.168.99.100:8761/eureka/apps/productapi          done                   
    http://192.168.99.100:8761/eureka/apps/productcomposite    done                   
    http://192.168.99.100:8761/eureka/apps/recommendation      done                   
    http://192.168.99.100:8761/eureka/apps/review              done                   
    
    Getting OAuth token ... OK
    
    https://192.168.99.100/api/product/1046                              ... OK                                          
    https://192.168.99.100/api/product/1337                              ... OK                                          
    https://192.168.99.100/api/product/7331                              ... OK                                          
    
    All done.
    Docker shutting down...





## Bonus content: Concurrent console output using channel
Bonus snippet of code using Go channels for handling (synchronized) console printing without explicit use of mutexes and/or locks.

    var consoleChannel chan CText                   // Declare privately scoped channel that we can pass console print
                                                    // statements to
    func init() {
        // Maybe some other stuff
        
        go pollConsoleChannel()                     // Start a goroutine that will handle receives on the channel
    }
    
    func pollConsoleChannel() {
            consoleChannel = make(chan CText)       // Instantiate unbuffered (e.g. sync) channel
            
            // Will iterate until main program exits, blocks at <-.
            for {
                    msg := <- consoleChannel                          // Blocks here until a message is received.
                    fmt.Printf("\033[%d;%dH", msg.Row, msg.Col)       // Position cursor
                    fmt.Print(msg.Text)                               // Prints text at cursor position
            }
    }
    
    /* Application invokes this func to print to console */
    func ChPrint(row int, col int, text string) {
            
            msg := CText{                // Build a simple instance of the CText struct
                    row,
                    col,
                    text,
            }
            consoleChannel <- msg        // Submit message on channel
    }
    
    /* Simple struct for encapsulating row, col and text to log */
    type CText struct {
            Row int
            Col int
            Text string
    }
