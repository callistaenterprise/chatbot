---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: >-
  WebFlux - Reactive Programming with Spring,
  Part 3.
authors:
  - annaeriksson
tags: webflux spring
---

This is the third part of my [blog series on reactive programming](https://callistaenterprise.se/blogg/teknik/2020/05/24/blog-series-reactive-programming/), which will give an introduction to WebFlux - Spring's reactive web framework.

-[readmore]-


## 1. An introduction to Spring WebFlux
 
The original web framework for Spring - Spring Web MVC - was built for the Servlet API and Servlet containers. 

WebFlux was introduced as part of Spring Framework 5.0. Unlike Spring MVC, it does not require the Servlet API. It is fully asynchronous and non-blocking, implementing the Reactive Streams specification through the Reactor project (see my [previous blog post](https://callistaenterprise.se/blogg/teknik/2020/09/12/blog-series-reactive-programming-part-2/)).


WebFlux requires Reactor as a core dependency but it is also interoperable with other reactive libraries via Reactive Streams.
 

### 1.1 Programming models

Spring WebFlux supports two different programming models: annotation-based and functional. 

#### 1.1.1 Annotated controllers

If you have worked with Spring MVC, the annotation-based model will look quite familiar since it is using the same 
 annotations from the Spring Web module as are being used with Spring MVC. The major difference being that the methods
 now return the reactive types Mono and Flux. See the following example of a RestController using the annotation-based model:

```java
@RestController
@RequestMapping("/students")
public class StudentController {

    @Autowired
    private StudentService studentService;


    public StudentController() {
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<Student>> getStudent(@PathVariable long id) {
        return studentService.findStudentById(id)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    @GetMapping
    public Flux<Student> listStudents(@RequestParam(name = "name", required = false) String name) {
        return studentService.findStudentsByName(name);
    }

    @PostMapping
    public Mono<Student> addNewStudent(@RequestBody Student student) {
        return studentService.addNewStudent(student);
    }

    @PutMapping("/{id}")
    public Mono<ResponseEntity<Student>> updateStudent(@PathVariable long id, @RequestBody Student student) {
        return studentService.updateStudent(id, student)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public Mono<ResponseEntity<Void>> deleteStudent(@PathVariable long id) {
        return studentService.findStudentById(id)
                .flatMap(s ->
                        studentService.deleteStudent(s)
                                .then(Mono.just(new ResponseEntity<Void>(HttpStatus.OK)))
                )
                .defaultIfEmpty(new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }
}
```

Some explanations about the functions used in the example:
- The `map` function is used to transform the item emitted by a Mono by applying a synchronous function to it.
- The `flatMap` function is used to transform the item emitted by the Mono asynchronously,
returning the value emitted by another Mono.
- The `defaultIfEmpty` function provides a default value if a Mono is completed without any data.
 
#### 1.1.2 Functional endpoints 
 
The functional programming model is lambda-based and leaves the application in charge of the full request handling.
It is based on the concepts of `HandlerFunctions` and `RouterFunctions`.

HandlerFunctions are used to generate a response for a given request:

```java
@FunctionalInterface
public interface HandlerFunction<T extends ServerResponse> {
    Mono<T> handle(ServerRequest request);
}
```

The RouterFunction is used to route the requests to the HandlerFunctions:

```java
@FunctionalInterface
public interface RouterFunction<T extends ServerResponse> {
    Mono<HandlerFunction<T>> route(ServerRequest request);
    ...
}
```

Continuing with the same student example we would get something like the following using the functional style.

A StudentRouter:

```java
@Configuration
public class StudentRouter {

    @Bean
    public RouterFunction<ServerResponse> route(StudentHandler studentHandler){
        return RouterFunctions
            .route(
                GET("/students/{id:[0-9]+}")
                    .and(accept(APPLICATION_JSON)), studentHandler::getStudent)
            .andRoute(
                GET("/students")
                    .and(accept(APPLICATION_JSON)), studentHandler::listStudents)
            .andRoute(
                POST("/students")
                    .and(accept(APPLICATION_JSON)),studentHandler::addNewStudent)
            .andRoute(
                PUT("students/{id:[0-9]+}")
                    .and(accept(APPLICATION_JSON)), studentHandler::updateStudent)
            .andRoute(
                DELETE("/students/{id:[0-9]+}")
                    .and(accept(APPLICATION_JSON)), studentHandler::deleteStudent);
    }
}

```  
  
And a StudentHandler:
```java
@Component
public class StudentHandler {

    private StudentService studentService;

    public StudentHandler(StudentService studentService) {
        this.studentService = studentService;
    }

    public Mono<ServerResponse> getStudent(ServerRequest serverRequest) {
        Mono<Student> studentMono = studentService.findStudentById(
                Long.parseLong(serverRequest.pathVariable("id")));
        return studentMono.flatMap(student -> ServerResponse.ok()
                .body(fromValue(student)))
                .switchIfEmpty(ServerResponse.notFound().build());
    }

    public Mono<ServerResponse> listStudents(ServerRequest serverRequest) {
        String name = serverRequest.queryParam("name").orElse(null);
        return ServerResponse.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body(studentService.findStudentsByName(name), Student.class);
    }

    public Mono<ServerResponse> addNewStudent(ServerRequest serverRequest) {
        Mono<Student> studentMono = serverRequest.bodyToMono(Student.class);
        return studentMono.flatMap(student ->
                ServerResponse.status(HttpStatus.OK)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body(studentService.addNewStudent(student), Student.class));

    }

    public Mono<ServerResponse> updateStudent(ServerRequest serverRequest) {
        final long studentId = Long.parseLong(serverRequest.pathVariable("id"));
        Mono<Student> studentMono = serverRequest.bodyToMono(Student.class);

        return studentMono.flatMap(student ->
                ServerResponse.status(HttpStatus.OK)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body(studentService.updateStudent(studentId, student), Student.class));
    }

    public Mono<ServerResponse> deleteStudent(ServerRequest serverRequest) {
        final long studentId = Long.parseLong(serverRequest.pathVariable("id"));
        return studentService
                .findStudentById(studentId)
                .flatMap(s -> ServerResponse.noContent().build(studentService.deleteStudent(s)))
                .switchIfEmpty(ServerResponse.notFound().build());
    }
}

```
Some explanations about the functions used in the example:
- The `switchIfEmpty` function has the same purpose as `defaultIfEmpty`, but instead of providing
a default value, it is used for providing an alternative Mono.


Comparing the two models we can see that:
- Using the functional variant requires some more code for things such as
  retrieving input parameters and parsing to the expected type.
- Not relying on annotations, but writing explicit code does offer some more flexibility
  and could be a better choice if we for example need to implement more complex routing.

### 1.2 Server support

WebFlux runs on non-Servlet runtimes such as Netty and Undertow (non-blocking mode) as well as Servlet 3.1+ runtimes such as Tomcat and Jetty.

The Spring Boot WebFlux starter defaults to use Netty, but it is easy to switch by changing your Maven or Gradle dependencies.

For example, to switch to Tomcat, just exclude spring-boot-starter-netty from the spring-boot-starter-webflux
dependency and add spring-boot-starter-tomcat:

```xml
<dependency>
	<groupId>org.springframework.boot</groupId>
	<artifactId>spring-boot-starter-webflux</artifactId>
	<exclusions>
		<exclusion>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-netty</artifactId>
		</exclusion>
	</exclusions>
</dependency>

<dependency>
	<groupId>org.springframework.boot</groupId>
	<artifactId>spring-boot-starter-tomcat</artifactId>
</dependency>
```


### 1.3 Configuration

Spring Boot provides auto-configuration for Spring WebFlux that works well for the common cases.
If you want full control of the WebFlux configuration, the `@EnableWebFlux` annotation can be used 
(this annotation would also be needed in a plain Spring application to import the Spring WebFlux configuration).

If you want to keep the Spring Boot WebFlux config and just add some additional WebFlux configuration, 
you can add your own @Configuration class of type WebFluxConfigurer (but without @EnableWebFlux).

For details and examples, read the [WebFlux config](https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html#webflux-config) documentation.

## 2.  Securing your endpoints
To get Spring Security WebFlux support, first add the spring-boot-starter-security dependency to your project.
Now you can enable it by adding the `@EnableWebFluxSecurity` annotation to your Configuration class (available since Spring Security 5.0)

The following simplified example would add support
for two users, one with a USER role and one with an ADMIN role, 
enforce HTTP basic authentication and require the ADMIN role for any access to the path /students/admin:

```java
@EnableWebFluxSecurity
public class SecurityConfig {

    @Bean
    public MapReactiveUserDetailsService userDetailsService() {

        UserDetails user = User
                .withUsername("user")
                .password(passwordEncoder().encode("userpwd"))
                .roles("USER")
                .build();

        UserDetails admin = User
                .withUsername("admin")
                .password(passwordEncoder().encode("adminpwd"))
                .roles("ADMIN")
                .build();

        return new MapReactiveUserDetailsService(user, admin);
    }

    @Bean
    public SecurityWebFilterChain securityWebFilterChain(ServerHttpSecurity http) {
        return http.authorizeExchange()
                .pathMatchers("/students/admin")
                .hasAuthority("ROLE_ADMIN")
                .anyExchange()
                .authenticated()
                .and().httpBasic()
                .and().build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

}
```

It is also possible to secure a method rather than a path, by first adding the annotation `@EnableReactiveMethodSecurity`
to your config:

```java
@EnableWebFluxSecurity
@EnableReactiveMethodSecurity
public class SecurityConfig {
    ...
}
```

And then adding the `@PreAuthorize` annotation to the methods to be secured.
We might for example want our POST, PUT and DELETE methods only to be accessible by the
ADMIN role. Then the PreAuthorize annotation could be applied to those methods, like:

```java
@DeleteMapping("/{id}")
@PreAuthorize("hasRole('ADMIN')")
public Mono<ResponseEntity<Void>> deleteStudent(@PathVariable long id) {
    ...
}
```

Spring Security offers more support related to WebFlux applications, such as CSRF protection, 
OAuth2 integration and reactive X.509 authentication. For more details, read the followig section
in the Spring Security documentation: [Reactive Applications](https://docs.spring.io/spring-security/site/docs/current/reference/html5/#reactive-applications)


## 3. WebClient

Spring WebFlux also includes a reactive, fully non-blocking web client. 
It has a functional, fluent API based on Reactor.

Let's take a look at a (once again) simplified example, 
how the WebClient can be used to query our StudentController:


```java
public class StudentWebClient {

    WebClient client = WebClient.create("http://localhost:8080");

        public Mono<Student> get(long id) {
            return client
                    .get()
                    .uri("/students/" + id)
                    .headers(headers -> headers.setBasicAuth("user", "userpwd"))
                    .retrieve()
                    .bodyToMono(Student.class);
        }
    
        public Flux<Student> getAll() {
            return client.get()
                    .uri("/students")
                    .headers(headers -> headers.setBasicAuth("user", "userpwd"))
                    .retrieve()
                    .bodyToFlux(Student.class);
        }
    
        public Flux<Student> findByName(String name) {
            return client.get()
                    .uri(uriBuilder -> uriBuilder.path("/students")
                    .queryParam("name", name)
                    .build())
                    .headers(headers -> headers.setBasicAuth("user", "userpwd"))
                    .retrieve()
                    .bodyToFlux(Student.class);
        }
    
        public Mono<Student> create(Student s)  {
            return client.post()
                    .uri("/students")
                    .headers(headers -> headers.setBasicAuth("admin", "adminpwd"))
                    .body(Mono.just(s), Student.class)
                    .retrieve()
                    .bodyToMono(Student.class);
        }
    
        public Mono<Student> update(Student student)  {
            return client
                    .put()
                    .uri("/students/" + student.getId())
                    .headers(headers -> headers.setBasicAuth("admin", "adminpwd"))
                    .body(Mono.just(student), Student.class)
                    .retrieve()
                    .bodyToMono(Student.class);
        }
    
        public Mono<Void> delete(long id) {
            return client
                    .delete()
                    .uri("/students/" + id)
                    .headers(headers -> headers.setBasicAuth("admin", "adminpwd"))
                    .retrieve()
                    .bodyToMono(Void.class);
        }
}
```


## 4. Testing 
For testing your reactive web application, WebFlux offers the WebTestClient, that comes with
a similar API as the WebClient.

Let's have a look at how we can test our StudentController using the WebTestClient:

```java
@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class StudentControllerTest {
    @Autowired
    WebTestClient webClient;

    @Test
    @WithMockUser(roles = "USER")
    void test_getStudents() {
        webClient.get().uri("/students")
                .header(HttpHeaders.ACCEPT, "application/json")
                .exchange()
                .expectStatus().isOk()
                .expectHeader().contentType(MediaType.APPLICATION_JSON)
                .expectBodyList(Student.class);

    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void testAddNewStudent() {
        Student newStudent = new Student();
        newStudent.setName("some name");
        newStudent.setAddress("an address");

        webClient.post().uri("/students")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.APPLICATION_JSON)
                .body(Mono.just(newStudent), Student.class)
                .exchange()
                .expectStatus().isOk()
                .expectHeader().contentType(MediaType.APPLICATION_JSON)
                .expectBody()
                .jsonPath("$.id").isNotEmpty()
                .jsonPath("$.name").isEqualTo(newStudent.getName())
                .jsonPath("$.address").isEqualTo(newStudent.getAddress());
    }

    ...
}
```

## 5. WebSockets and RSocket

### 5.1 WebSockets
With Spring 5, WebSockets also gets added reactive capabilities.
To create a WebSocket server, you can create an implementation of the `WebSocketHandler` interface,
which holds the following method:

```java
Mono<Void> handle(WebSocketSession session)
```

This method is invoked when a new WebSocket connection is established,
and allows handling of the session. 
It take a `WebSocketSession` as input and returns Mono&lt;Void> to signal when application handling of the session is complete.

The WebSocketSession has methods defined for handling the inbound and outbound streams:
```java
Flux<WebSocketMessage> receive()
Mono<Void> send(Publisher<WebSocketMessage> messages)
```
Spring WebFlux also provides a `WebSocketClient` with implementations for Reactor Netty, Tomcat, Jetty, Undertow, and standard Java.

For more details, read the following chapter in Spring's Web on Reactive Stack documentation:
[WebSockets](https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html#webflux-websocket)
 

### 5.2 RSocket
RSocket is a protocol that models Reactive Streams semantics over a network. 
It is a binary protocol for use on byte stream transports such as TCP, WebSockets, and Aeron.
For an introduction to this topic, I recommend the following blog post that my 
colleague Pär has written: 
[An introduction to RSocket](https://callistaenterprise.se/blogg/teknik/2020/06/05/rsocket-part-1/)

And for more details on Spring Framework's support for the RSocket protocol:
[RSocket](https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html#rsocket)

## 6. To summarize...
This blog post demonstrated how WebFlux can be used to build a reactive web application.
The next and final blog post in this series will show how we can make our 
entire application stack fully non-blocking by also implementing non-blocking 
database communication - using R2DBC (Reactive Relational Database Connectivity)!

## References

[Spring Framework documentation - Web on Reactive Stack](https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html)

[Spring Boot Features - The Spring WebFlux framework](https://docs.spring.io/spring-boot/docs/current/reference/html/spring-boot-features.html#boot-features-webflux)

[Spring Security - Reactive Applications](https://docs.spring.io/spring-security/site/docs/current/reference/html5/#reactive-applications)