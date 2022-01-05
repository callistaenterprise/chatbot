---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: >-
  R2DBC - Reactive Programming with Spring,
  Part 4.
authors:
  - annaeriksson
tags: r2dbc spring
---

This is part four of my [blog series on reactive programming](https://callistaenterprise.se/blogg/teknik/2020/05/24/blog-series-reactive-programming/), which will give an introduction to R2DBC and describe how we can use
Spring Data R2DBC to create a fully reactive application.

-[readmore]-


## 1. What is R2DBC?
If you are not already familiar with reactive programming and Reactive Streams, I recommend you to first
read my [introduction on reactive programming](https://callistaenterprise.se/blogg/teknik/2020/05/24/blog-series-reactive-programming-part-1/)
which describes the motivation behind this programming paradigm.

When developing a reactive application that should include access to a relational database, 
JDBC is not a good fit, since it is a blocking API.

R2DBC stands for `Reactive Relational Database Connectivity` and is intended to provide a way to work with
 SQL databases using a fully reactive, non-blocking API.
It is based on the Reactive Streams specification and is primarily an SPI (Service Provider Interface) for database driver implementors 
and client library authors - meaning it is not intended to be used directly in application code.

At this moment, driver implementations exist for Oracle, Microsoft SQL Server, MySQL, PostgreSQL, H2, MariaDB and 
Google Cloud Spanner. 

## 2. Spring Data R2DBC
Spring Data offers an R2DBC client - Spring Data R2DBC.

This is not a full ORM like JPA - it does not offer features such as caching or lazy loading.
But it does provide object mapping functionality and a Repository abstraction.

To demonstrate how it can be used, let's revisit the StudentController example from my 
[previous blog on WebFlux](https://callistaenterprise.se/blogg/teknik/2021/03/28/blog-series-reactive-programming-part-3/): 

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

This controller holds some different methods for performing actions on students.
We can see that it is using a StudentService to perform these actions.
Now we will look into this functionality behind the REST controller and how
we can implement database access using R2DBC.

### 2.1 Implementation example


#### 2.1.1 Dependencies
First, we need to add a couple of new dependencies to our project:

```xml
<dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-r2dbc</artifactId>
        </dependency>

        <dependency>
            <groupId>io.r2dbc</groupId>
            <artifactId>r2dbc-postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        ...
</dependencies>
```
We need to include the spring-boot-starter-data-r2dbc to enable spring-data-r2dbc.
For this example we will use a postgresql database, and so we need to add the 
r2dbc-postgresql to get the r2dbc driver implementation needed.


#### 2.1.2 Database config

We can either add our database connection details in application.properties:
```xml
spring.r2dbc.url=r2dbc:postgresql://localhost/studentdb
spring.r2dbc.username=user
spring.r2dbc.password=secret
```
or use a Java-based configuration:

```java
import io.r2dbc.spi.ConnectionFactories;
import io.r2dbc.spi.ConnectionFactory;
import io.r2dbc.spi.ConnectionFactoryOptions;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import static io.r2dbc.spi.ConnectionFactoryOptions.*;

@Configuration
public class R2DBCConfig {

    @Bean
    public ConnectionFactory connectionFactory() {
        return ConnectionFactories.get(
                ConnectionFactoryOptions.builder()
                        .option(DRIVER, "postgresql")
                        .option(HOST, "localhost")
                        .option(USER, "user")
                        .option(PASSWORD, "secret")
                        .option(DATABASE, "studentdb")
                        .build());
    }

}
```


#### 2.1.3 StudentService
Now let's take a look at the StudentService that the StudentController is using:

```java
@Service
public class StudentService {

    @Autowired
    private StudentRepository studentRepository;

    public StudentService() {
    }

    public Flux<Student> findStudentsByName(String name) {
        return (name != null) ? studentRepository.findByName(name) : studentRepository.findAll();
    }

    public Mono<Student> findStudentById(long id) {
        return studentRepository.findById(id);
    }

    public Mono<Student> addNewStudent(Student student) {
        return studentRepository.save(student);
    }

    public Mono<Student> updateStudent(long id, Student student) {
        return studentRepository.findById(id)
                .flatMap(s -> {
                    student.setId(s.getId());
                    return studentRepository.save(student);
                });

    }

    public Mono<Void> deleteStudent(Student student) {
        return studentRepository.delete(student);
    }

}
```

As you can see, it uses a StudentRepository to perform the different database operations on students.
So now let's take a look at this repository.


#### 2.1.4 StudentRepository
The StudentRepository is an implementation of [ReactiveCrudRepository](https://docs.spring.io/spring-data/commons/docs/current/api/org/springframework/data/repository/reactive/ReactiveCrudRepository.html).
This is an interface from Spring Data R2DBC for generic CRUD operations using Project Reactor types.
Since ReactiveCrudRepository already holds definitions for most of the repository methods we use in the StudentService
(findAll, findById, save and delete) all we need to declare is the following:

```java
public interface StudentRepository extends ReactiveCrudRepository<Student, Long> {

    public Flux<Student> findByName(String name);

}
```
More complex queries could be defined as well by adding a @Query annotation to a method and specifying the actual sql.

Besides the ReactiveCrudRepository, there is also an extension called [ReactiveSortingRepository](https://docs.spring.io/spring-data/commons/docs/current/api/org/springframework/data/repository/reactive/ReactiveSortingRepository.html)
which provides additional methods to retrieve entities sorted.


#### 2.1.5 Student
Finally, let's look at the implementation of Student:

```java
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Table;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Table
public class Student {

    @Id
    private Long id;
    private String name;
    private String address;

}
```
A few things to note:

- The id of an entity should be annotated with Spring Data's @Id annotation.

- The @Table annotation is not necessary but adding it lets the classpath scanner find and pre-process the entities
 to extract the related metadata. If you don't add it this will instead happen the first time you store an entity
 which could have a slightly negative impact on performance.

- Lombok is recommended to be used to avoid boilerplate code.

- There are also some other recommendations to ensure you get optimal performance, you can find the 
details in the [reference documentation](https://docs.spring.io/spring-data/r2dbc/docs/current/reference/html/#mapping.general-recommendations).
 

#### 2.1.6 Other options for queries
Instead of using a repository, you could execute an SQL statement directly using a [DatabaseClient](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/r2dbc/core/DatabaseClient.html).

For example, to retrieve all students:
```java
 public Flux<Student> findAll() {
        DatabaseClient client = DatabaseClient.create(connectionFactory);
        return client.sql("select * from student")
                .map(row -> new Student(row.get("id", Long.class),
                        row.get("name", String.class),
                        row.get("address", String.class))).all();
 }

```

It is also possible to use the [R2dbcEntityTemplate](https://docs.spring.io/spring-data/r2dbc/docs/current/api/org/springframework/data/r2dbc/core/R2dbcEntityTemplate.html)
to perform operations on entities. For example:

```java
@Autowired
private R2dbcEntityTemplate template;

public Flux<Student> findAll() {
    return template.select(Student.class).all();
}

public Mono<Void> delete(Student student) {
    return template.delete(student).then();
}

```

### 2.2 Other features

#### 2.2.1 Optimistic locking
Quite similar to JPA, it is possible to apply a `@Version` annotation at field level, to ensure that updates are only
 applied to rows with a matching version - if the version is not matching an OptimisticLockingFailureException is thrown. 

 
#### 2.2.2 Transactions
Spring supports reactive transaction management through the [ReactiveTransactionManager](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/transaction/ReactiveTransactionManager.html) SPI.
The `@Transactional` annotation can be applied on reactive methods returning Publisher types and
 programmatic transaction management can be applied using the [TransactionalOperator](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/transaction/reactive/TransactionalOperator.html).

#### 2.2.3 Reactive libraries
Just like WebFlux, Spring Data R2DBC requires Project Reactor as a core dependency but is
interoperable with other reactive libraries that implement the Reactive Streams specification.
Repositories exist for RxJava2 and RxJava3 as well (view [package summary](https://docs.spring.io/spring-data/commons/docs/current/api/org/springframework/data/repository/reactive/package-summary.html)).

#### 2.2.4 Connection pooling
For connection pooling, there is a library called r2dbc-pool available.
For details on how to use it, take a look [here](https://github.com/r2dbc/r2dbc-pool).


## 3. Production readiness
R2DBC is still a fairly new technology. The latest release versions as of now:
- R2DBC specification: 0.8.5
- Spring Data R2DBC: 1.3.1
- r2dbc-postgresql: 0.8.8
- r2dbc-pool: 0.8.7

Before deciding to go to production with this for your application, it is of course recommended to take a closer look
 at the current state of the database driver and pooling implementations compared to your requirements. There are some 
 open issues that might prevent you from taking this step as of now, but improvements are ongoing.


## 4. To summarize...
This blog post demonstrated how Spring Data R2DBC can be used in a WebFlux application.
And by that, we have created a fully reactive application and also come to an end of this series on reactive programming.

Another very interesting initiative worth mentioning is [Project Loom](https://wiki.openjdk.java.net/display/loom/Main).
This is an OpenJDK project that started already in 2017 aiming to deliver lightweight concurrency, 
including a new type of Java threads that do not directly
correspond to dedicated OS threads. This type of virtual threads would be much cheaper
to create and block. 

As you might recall from my [first blog post](https://callistaenterprise.se/blogg/teknik/2020/05/24/blog-series-reactive-programming-part-1/) the key drivers behind the reactive programming model is that we:
- move away from the thread per request model and can handle more requests with a low number of threads
- prevent threads from blocking while waiting for I/O operations to complete
- make it easy to do parallel calls
- support “back pressure”, giving the client a possibility to inform the server on how much load it can handle

Project Loom seems very promising when it comes to helping out with the first two items in this list - this
would then be taken care of by the JVM itself without any additional framework needed.

 It is not yet decided when the changes will be introduced in an official 
 Java release, but early access binaries are [available for download](https://jdk.java.net/loom/).
 

## References

[R2DBC](https://r2dbc.io)

[Spring Data R2DBC Reference Documentation](https://docs.spring.io/spring-data/r2dbc/docs/current/reference/html/#reference)

[r2dbc-postgresql](https://github.com/pgjdbc/r2dbc-postgresql)

[r2dbc-pool](https://github.com/r2dbc/r2dbc-pool)

[Project Loom](https://wiki.openjdk.java.net/display/loom/Main)

[Going inside Java’s Project Loom and virtual threads](https://blogs.oracle.com/javamagazine/going-inside-javas-project-loom-and-virtual-threads)