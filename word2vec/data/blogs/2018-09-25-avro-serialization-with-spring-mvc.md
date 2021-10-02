---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Apache Avro Serialization with Spring MVC
authors: 
  - bjornbeskow
tags: spring mvc rest apache avro kafka event driven architecture
topstory: true
comments: true

---

Apache Avro is becoming a popular choice for Java Object Serialization in EventDriven Architectures using Apache Kafka, due to its compact binary payloads and stringent schema support. If combining Event Notification using Kafka with traditional Request-Response, it is convenient to use the same serialization mechanism for the domain objects, regardless of if they are part of events emitted over Kafka or requested through a REST API. Here's how to do that in a Spring-MVC REST environment.
-[readmore]-

[comment]: # (Links)
[Apache Avro]: https://avro.apache.org/
[Apache Kafka]: Https://kafka.apache.org/
[Confluent]: https://www.confluent.io/
[Schema Registry]: https://docs.confluent.io/current/schema-registry/docs/index.html
[Event Driven Architectures]: https://martinfowler.com/articles/201701-event-driven.html
[Google Protobuf]: https://developers.google.com/protocol-buffers/
[Avro RPC]: https://github.com/phunt/avro-rpc-quickstart
[Spring Boot]: http://projects.spring.io/spring-boot/
[Kafka Benchmark]: https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines
[github.com/callistaenterprise/blog-avro-spring]: https://github.com/callistaenterprise/blog-avro-spring

[Event Driven Architectures] are becoming increasingly more popular, partly due to the challenges with tightly coupled micro services. When streaming events at scale, a highly scalable messaging backbone is a critical enabler. [Apache Kafka] is widely used, due to its distributed nature and thus extreme scalability. In order for Kafka to really deliver, individual messages needs to be fairly small (see e.g. [Kafka Benchmark]). Hence verbose data serialization formats like XML or JSON might not be appropriate for event notifications.

While there are several serialization protocols offering compact binary payloads (among them, [Google Protobuf] stands out a modern and elegant framework), [Apache Avro] is frequently used together with Kafka. While not necessarily the most elegant framework, the [Confluent] Kafka packaging provides a [Schema Registry], which allows a structured way to manage message schemas and schema versions, and the Schema Registry is based on Avro schemas.

#### Avro IDL

Avro schemas can be defined in two ways: In JSON syntax, or in *Avro IDL*, a custom DSL for describing datatypes and RPC operations. While the JSON syntax might seem more appealing, it lacks a decent **include** mechanism, making it hard to decompose and reuse common datatypes between schemas. Hence Avro IDL seems to me to be the syntax most appropriate for serious use. Below is a simple example of an Avro IDL schema, defining a Car type with a mandatory VIN and an optional Plate Number: 

~~~ src/main/resources/avro/Car.avdl
@namespace("se.callista.blog.avro_spring.car.avro")
protocol CarProtocol {

  record Car {
    string VIN;
    union { null, string } plateNumber;
  }

}
~~~

An Avro schema may be used in runtime (useful when working with dynamically typed languages) or compiled into language-specific bindings for e.g. Java. 
The following is an example of a Maven configuration snippet to feed Avro schemas through the Avro IDL compiler:

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
							<sourceDirectory>${project.basedir}/src/main/resources/avro/</sourceDirectory>
							<outputDirectory>${project.build.directory}/generated-sources/avro</outputDirectory>
						</configuration>
					</execution>
				</executions>
			</plugin>
~~~

When feeding it through the IDL compiler, a corresponding Java class is generated:

~~~ Java
package se.callista.blog.avro_spring.car.avro;
...
@org.apache.avro.specific.AvroGenerated
public class Car extends org.apache.avro.specific.SpecificRecordBase implements org.apache.avro.specific.SpecificRecord {
  ...
}
~~~

The resulting Java class can then be used to efficiently serialize and deserialize Java objects to and from byte arrays (using the **org.apache.avro.specific** serialization mechanism, which is the recommended style for statically compiled languages). Using the resulting Java classes when reading from or publishing to Kafka topics is straight forward.

### Request-Reply and REST

But what if you want to use the same Schema definitions in your RESTful API (i.e. using Avro serialization over http)? Avro comes with a proprietary RPC mechanism [Avro RPC], with an http server implementation built on top of Netty. But such a mechanism doesn't easily integrate with other REST frameworks, like e.g. a [Spring Boot] application. I was a little surprised to find that there seems to be no formal support in neither Avro nor Spring to easily integrate Avro serialization with the *HttpMessageConverter* abstraction of Spring MVC.

Luckily, this can fairly easily be done using the existing Avro Serializer/Deserializer framework and the Spring MVC interfaces. Let's see how (a fully working example can be found at [github.com/callistaenterprise/blog-avro-spring]):

#### Generic Interfaces

Lets start by defining two generic interfaces for serialization and deserialization to and from byte arrays:

~~~ Java
public interface Serializer<T> {

  /**
   * Serialize object as byte array.
   * @param T data the object to serialize
   * @return byte[]
   */
  byte[] serialize(T data) throws SerializationException;

}
~~~
~~~ Java
public interface Deserializer<T> {

  /**
   * Deserialize object from a byte array.
   * @param Class<? extends T> clazz the expected class for the deserialized object
   * @param byte[] data the byte array
   * @return T object instance
   */
  T deserialize(Class<? extends T> clazz, byte[] data) throws SerializationException;

}
~~~

#### Avro implementations using org.apache.avro.specific

Now let's use the **org.apache.avro.specific** mechanism to implement serialization and deserialization for all Java classes generated from Avro IDL (supporting serialization using both Avro binary format as well as Avro JSon format):

~~~ Java
public class AvroSerializer<T extends SpecificRecordBase> implements Serializer<T> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AvroSerializer.class);

  private final boolean useBinaryEncoding;
  
  public AvroSerializer(boolean useBinaryEncoding) {
    this.useBinaryEncoding = useBinaryEncoding;
  }

  public boolean isUseBinaryEncoding() {
    return useBinaryEncoding;
  }

  @Override
  public byte[] serialize(T data) throws SerializationException {
    try {
      byte[] result = null;

      if (data != null) {
        if (LOGGER.isDebugEnabled()) {
          LOGGER.debug("data={}:{}", data.getClass().getName(), data);
        }
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        Encoder encoder = useBinaryEncoding ?
            EncoderFactory.get().binaryEncoder(byteArrayOutputStream, null) :
            EncoderFactory.get().jsonEncoder(data.getSchema(), byteArrayOutputStream);;

        DatumWriter<T> datumWriter = new SpecificDatumWriter<>(data.getSchema());
        datumWriter.write(data, encoder);

        encoder.flush();
        byteArrayOutputStream.close();

        result = byteArrayOutputStream.toByteArray();
        if (LOGGER.isDebugEnabled()) {
          LOGGER.debug("serialized data='{}' ({})", DatatypeConverter.printHexBinary(result), new String(result));
        }
      }
      return result;
    } catch (IOException e) {
      throw new SerializationException("Can't serialize data='" + data + "'", e);
    }
  }
}
~~~
~~~ Java
public class AvroDeserializer<T extends SpecificRecordBase> implements Deserializer<T> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AvroDeserializer.class);

  private final boolean useBinaryEncoding;
  
  public AvroDeserializer(boolean useBinaryEncoding) {
    this.useBinaryEncoding = useBinaryEncoding;
  }

  public boolean isUseBinaryEncoding() {
    return useBinaryEncoding;
  }

  @Override
  public T deserialize(Class<? extends T> clazz, byte[] data) throws SerializationException {
    try {
      T result = null;
      if (data != null) {
        if (LOGGER.isDebugEnabled()) {
          LOGGER.debug("data='{}' ({})", DatatypeConverter.printHexBinary(data), new String(data));
        }
        Class<? extends SpecificRecordBase> specificRecordClass =
            (Class<? extends SpecificRecordBase>) clazz;
        Schema schema = specificRecordClass.newInstance().getSchema();
        DatumReader<T> datumReader =
            new SpecificDatumReader<>(schema);
        Decoder decoder = useBinaryEncoding ?
            DecoderFactory.get().binaryDecoder(data, null) :
            DecoderFactory.get().jsonDecoder(schema, new ByteArrayInputStream(data));;

        result = datumReader.read(null, decoder);
        if (LOGGER.isDebugEnabled()) {
          LOGGER.debug("deserialized data={}:{}", clazz.getName(), result);
        }
      }
      return result;
    } catch (InstantiationException | IllegalAccessException | IOException e) {
      throw new SerializationException("Can't deserialize data '" + Arrays.toString(data) + "'", e);
    }
  }
}
~~~

A bit verbose, but nothing fancy in there, just the boiler plate code for using the Avro **org.apache.avro.specific** mechanisms.

#### Spring MVC *HttpMessageConverter* Avro implementation

Next step is to provide an implementation of Spring MVC's *HttpMessageConverter*, using the Avro serializers. The *AbstractHttpMessageConverter* base class provides most the boiler plate code necessary, so we just needs to complement it with what Mime types and Java types the MessageConverter supports, and the actual conversion to and from those types. We'll do it in two different flavors, to support binary or JSON serialization respectively:

~~~ Java
public abstract class AvroHttpMessageConverter<T> extends AbstractHttpMessageConverter<T> {

  protected final Logger logger = LoggerFactory.getLogger(getClass());

  public static final Charset DEFAULT_CHARSET = Charset.forName("UTF-8");

  private Serializer<SpecificRecordBase> serializer;
  private Deserializer<SpecificRecordBase> deserializer;

  public AvroHttpMessageConverter(boolean useBinaryEncoding, MediaType... supportedMediaTypes) {
    super(supportedMediaTypes);
    serializer = new AvroSerializer<>(useBinaryEncoding);
    deserializer = new AvroDeserializer<>(useBinaryEncoding);
  }

  @Override
  protected boolean supports(Class<?> clazz) {
    return SpecificRecordBase.class.isAssignableFrom(clazz);
  }

  @SuppressWarnings("unchecked")
  @Override
  protected T readInternal(Class<? extends T> clazz, HttpInputMessage inputMessage)
      throws IOException, HttpMessageNotReadableException {
    T result = null;
    byte[] data = IOUtils.toByteArray(inputMessage.getBody());
    if (data.length > 0) {
      result = (T) deserializer.deserialize((Class<? extends SpecificRecordBase>) clazz, data);
    }
    return result;
  }

  @Override
  protected void writeInternal(T t, HttpOutputMessage outputMessage)
      throws IOException, HttpMessageNotWritableException {
    byte[] data = serializer.serialize((SpecificRecordBase) t);
    outputMessage.getBody().write(data);
  }

}
~~~
~~~ Java
public class AvroBinaryHttpMessageConverter<T> extends AvroHttpMessageConverter<T> {

  public AvroBinaryHttpMessageConverter() {
    super(true, new MediaType("application", "avro", DEFAULT_CHARSET),
        new MediaType("application", "*+avro", DEFAULT_CHARSET));
  }

}
~~~
~~~ Java
public class AvroJsonHttpMessageConverter<T> extends AvroHttpMessageConverter<T> {

  public AvroJsonHttpMessageConverter() {
    super(false, new MediaType("application", "avro+json", DEFAULT_CHARSET),
        new MediaType("application", "*+avro+json", DEFAULT_CHARSET));
  }

}
~~~

Simple enough. Now we need to configure Spring MVC to use the new MessageConverter in Controllers and in REST clients using RestTemplate:

~~~ Java
@Configuration
public class ConverterConfig extends WebMvcConfigurerAdapter {

  @Override
  public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
    super.configureMessageConverters(converters);
    converters.add(new AvroJsonHttpMessageConverter<SpecificRecordBase>());
  }

  @Bean
  public RestTemplate restTemplate(RestTemplateBuilder builder) {
    RestTemplate restTemplate = builder.build();
    restTemplate.getMessageConverters().add(0, new AvroJsonHttpMessageConverter<SpecificRecordBase>());
    return restTemplate;
  }

}
~~~

#### Using the MessageConverter in a REST endpoint

Once we have the MessageConverter configured, we can use the Avro generated classes as parameter and return types in our Controller implementation, relying on the MessageConverter doing the correct Serialization/Deserialization based on content type negotiation:

~~~ Java
import se.callista.blog.avro_spring.car.avro.Car;

@RestController
public class CarController {

  @RequestMapping(value = "/car/{VIN}", method = RequestMethod.GET, produces = "application/avro+json")
  public Car getCar(@PathVariable("VIN") String VIN) {
    ...
  }

  @RequestMapping(value = "/car/{VIN}", method = RequestMethod.PUT, consumes = "application/avro+json",
      produces = "application/avro+json")
  public Car updateCar(@PathVariable("VIN") String VIN, @RequestBody Car car) {
    ...
  }
}
~~~

Similar for consuming a REST endpoint using RestTemplate:

~~~ Java
import se.callista.blog.avro_spring.car.avro.Car;

public class CarClient {

  private static final MediaType APPLICATION_AVRO_JSON =
      new MediaType("application", "avro+json", Charset.forName("UTF-8"));

  @Autowired
  private RestTemplate restTemplate;

  public Car getCar(String VIN) {
    HttpHeaders headers = new HttpHeaders();
    headers.setAccept(Collections.singletonList(APPLICATION_AVRO_JSON));
    HttpEntity<Void> entity = new HttpEntity<>(headers);

    ResponseEntity<Car> result =
        restTemplate.exchange("/car/" + VIN, HttpMethod.GET, entity, Car.class);
    return result.getBody();
  }

  public Car updateCar(String VIN, Car car) {
    HttpHeaders headers = new HttpHeaders();
    headers.setAccept(Collections.singletonList(APPLICATION_AVRO_JSON));
    headers.setContentType(APPLICATION_AVRO);
    HttpEntity<Car> entity = new HttpEntity<>(car, headers);

    ResponseEntity<Car> result =
        restTemplate.exchange("/car/" + VIN, HttpMethod.PUT, entity, Car.class);
    return result.getBody();
  }

}
~~~

As usual with most of the Spring APIs, the end result is reasonably elegant and non-intrusive, isn't it?

#### Why Avro over REST anyway?

So why would you like to use Avro serialization in a REST API anyway? If you are investing in an Event-Driven Architecture and are using Kafka as event distribution platform, Avro is the recommended choice due to its compact binary message format and good Schema versioning support from the Schema Registry. But then there may be a small area within your solution where a Synchronous Query API is needed, maybe to support a subsystem or client that is not yet ready to go all-in event driven. In such a situation, it makes perfect sense to reuse the same Avro-based Domain Object types from the existing Event streams to define your REST-based API.

Your mileage may vary ...

Enjoy!