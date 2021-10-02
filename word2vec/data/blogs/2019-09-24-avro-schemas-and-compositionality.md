---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: 'Serialization, Schema Compositionality and Apache Avro'
tags: serialization schema composition apache avro kafka event driven architecture
authors:
  - bjornbeskow
---
Apache Avro, a Serialization framework originating from Hadoop, is rapidly becoming a popular choice for general Java Object Serialization in Apache Kafka based solutions, due to its compact binary payloads and stringent schema support. In its simplest form, it however lacks an important feature of a good Schema formalism: The ability to decompose a schema into smaller, reusable schema components. It can be accomplished, but requires some additional work or using an alternative Schema syntax.
-[readmore]-

[comment]: # (Links)
[Serialization]: https://en.wikipedia.org/wiki/Serialization
[Composition]: https://en.wikipedia.org/wiki/Object_composition
[Data Binding]: https://en.wikipedia.org/wiki/Data_binding
[Apache Avro]: https://avro.apache.org/
[Apache Hadoop]: https://hadoop.apache.org/
[Apache Kafka]: Https://kafka.apache.org/
[Confluent]: https://www.confluent.io/
[Schema Registry]: https://docs.confluent.io/current/schema-registry/docs/index.html
[Event Driven Architectures]: https://martinfowler.com/articles/201701-event-driven.html
[Google Protobuf]: https://developers.google.com/protocol-buffers/
[DRY principle]: https://en.wikipedia.org/wiki/Don%27t_repeat_yourself
[Kafka Benchmark]: https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines

[comment]: # (Images)
[Avro-logo]: http://avro.apache.org/images/avro-logo.png

#### Serialization & Schema Formalisms

Data [Serialization] plays a central role in any distributed computing system, be it message-oriented or RPC-based. Ideally, the involved parties should be able to exchange data in a way that is both efficient and robust, and which can evolve over time. I've seen many data serialization techniques come and go during the last 20 years, shifting with the current technical trends: Fixed-position binary formats, tag-based binary formats, separator-based formats, XML, Json, etc. Early frameworks were usually backed by supporting tools (yes, I'm old enough to remember when Data Dictionaries were state of the art ...), whereas more recent serialization frameworks usually provides a formal Schema language to enforce data correctness and enable contracts to evolve in a controlled way. The Schema formalism usually also provides a [Data Binding] mechanism to allow for easy usage in various programming languages.

In order to support non-trivial domain/information models, the Schema language should provide support for [Composition], where a complex Schema may be composed from smaller, resuable Schemas. This is usually achieved by some kind of *Include* mechanism in the the Schema formalism, and optionally additional build time configuration for any code generation Data Binding support.

#### Apache Kafka and Serialization

[Event Driven Architectures] are becoming increasingly more popular, partly due to the challenges with tightly coupled micro services. When streaming events at scale, a highly scalable messaging backbone is a critical enabler. [Apache Kafka] is widely used, due to its distributed nature and thus extreme scalability. In order for Kafka to really deliver, individual messages needs to be fairly small (see e.g. [Kafka Benchmark]). Hence verbose data serialization formats like XML or JSON might not be appropriate for event sourcing.

![Apache Avro][Avro-logo]

While there are several serialization protocols offering compact binary payloads (among them, [Google Protobuf] stands out a modern and elegant framework), [Apache Avro] is frequently used together with Kafka. While not necessarily the most elegant serialization framework, the [Confluent] Kafka packaging provides a [Schema Registry], which allows a structured way to manage message schemas and schema versions, and the Schema Registry is based on Avro schemas.

Suprisingly, while the formal support for managing Schema versioning (and automatically detecting schema changes which are not backwards compatible) is really powerful, Vanilla Avro lacks a decent *include* mechanism to enable Compositional Schemas that adheres to the [DRY principle]. The standard JSON-based syntax for Avro Schemas allows for a composite type to refer to other fully-qualified types, but the composition is not enforced by the schema itself. Consider the following schema definitions, where the composite UserCarRelation is composed from the simpler User and Car schemas:

~~~ src/main/resources/avro/user/User.avsc
{"namespace": "se.callista.blog.avro.user",
 "type": "record",
 "name": "User",
 "fields": [
     {"name": "userId", "type": "string"},
 ]
}
~~~

~~~ src/main/resources/avro/car/Car.avsc
{"namespace": "se.callista.blog.avro.car",
 "type": "record",
 "name": "Car",
 "fields": [
     {"name": "vehicleIdentificationNumber", "type": "string"},
 ]
}
~~~

~~~ src/main/resources/avro/userCarRelation/UserCarRelation.avsc
{"namespace": "se.callista.blog.avro.userCarRelation",
 "type": "record",
 "name": "UserCarRelation",
 "fields": [
     {"name": "user", "type": "se.callista.blog.avro.user.User"},
     {"name": "car", "type": "se.callista.blog.avro.car.Car"},
 ]
}
~~~

In order for the Avro Compiler to interpret and properly generate code for the UserCarRelation schema, it needs to be aware of the inclusions (in the correct order). The Avro maven plugin provides explicit support for this missing inlusion mechanism:

~~~
  <plugin>
    <groupId>org.apache.avro</groupId>
    <artifactId>avro-maven-plugin</artifactId>
    <version>${avro.version}</version>
    <executions>
      <execution>
        <phase>generate-sources</phase>
        <goals>
          <goal>schema</goal>
        </goals>
        <configuration>
          <sourceDirectory>${project.basedir}/src/main/resources/avro/userCarRelation</sourceDirectory>
          <imports>
            <import>${project.basedir}/src/main/resources/avro/user/User.avsc</import>
            <import>${project.basedir}/src/main/resources/avro/car/Car.avsc</import>
          </imports>
        </configuration>
      </execution>
    </executions>
  </plugin>
~~~

As seen, this inclusion is only handled by the Data Binding toolchain and not explicitly present in the Schema itself.
Hence it won't work with e.g. the Kafka Schema Registry.

#### Avro IDL

In more recent versions of Avro, there is however an alternative syntax for describing Schemas.
*Avro IDL* is a custom DSL for describing datatypes and RPC operations. The toplevel concept in an Avro IDL definition file is a *Protocol*,
a collection of operations and their associated datatypes. While the syntax at first look seems to be geared toward RPC, the RPC operations can
be omitted, and hence a Protocol may be used to only define datatypes. Interestingly enough, Avro IDL do contain a standard *include* mechanism,
where other IDL files as well as JSON-defined Avro Schemas may be properly included. Avro IDL originated as an experimental feature in Avro,
but is now a supported alternative syntax.

Below is the same example as above, in Avro IDL:

~~~ src/main/resources/avro/user/User.avdl
@namespace("se.callista.blog.avro.user")
protocol UserProtocol {

  record User {
    string userId;
  }

}
~~~

~~~ src/main/resources/avro/car/Car.avdl
@namespace("se.callista.blog.avro.car")
protocol CarProtocol {

  record Car {
    string vehicleIdentificationNumber;
  }

}
~~~

~~~ src/main/resources/avro/userCarRelation/UserCarRelation.avdl
@namespace("se.callista.blog.avro.userCarRelation")
protocol UserCarRelationProtocol {

  import idl "../user/User.avdl";
  import idl "../car/Car.avdl";

  record UserCarRelation {
    se.callista.blog.avro.user.User user;
    se.callista.blog.avro.car.Car car;
  }

}
~~~

Now the build system configuration can be correspondingly simplified:

~~~
  <plugin>
    <groupId>org.apache.avro</groupId>
    <artifactId>avro-maven-plugin</artifactId>
    <version>${avro.version}</version>
    <executions>
      <execution>
        <phase>generate-sources</phase>
        <goals>
          <goal>idl-protocol</goal>
        </goals>
        <configuration>
          <sourceDirectory>${project.basedir}/src/main/resources/avro/userCarRelation</sourceDirectory>
        </configuration>
      </execution>
    </executions>
  </plugin>
~~~

#### Summing Up

Compositionality is an important aspect of a well-designed information or message model, in order to highlight
important structural relationships and to eliminate redundancy. If Apache Avro is used as your Serialization framework,
I believe Avro IDL should be the preferred way to express the Schema contracts.
