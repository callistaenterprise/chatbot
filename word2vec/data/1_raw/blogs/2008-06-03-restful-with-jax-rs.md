---
layout: details-blog
published: true
categories: blogg teknik
heading: RESTful with JAX-RS
authors:
  - parwenaker
tags: architecture web
topstory: true
comments: true
---

I recently got the opportunity to do a spike on a RESTful web services interface and decided to use JAX-RS and the reference implementation Jersey to do the prototyping. The term REST was coined by [Roy Fielding](http://www.isr.uci.edu/~fielding/) in his [Ph.D. dissertation](http://www.ics.uci.edu/~fielding/pubs/dissertation/top.htm) back in 2000. There is lot's of material on the web regarding REST and I will not elaborate any further on it in this blog. My focus will instead be on how to implement RESTful services in Java (and JVM compliant languages) using JAX-RS. JAX-RS is described in [JSR 311](https://jsr311.dev.java.net/) that recently went for public review. If you want a good introduction to REST I would recommend the book "[RESTful Web Services](http://www.bokus.com/b/9780596529260.html)". Reading "[HTTP the Definite Guide](http://www.bokus.com/b/9781565925090.html)" will also give you a good insight in a RESTful architecture.

There are currently four implementations of JSR 311 that I am aware of; [Jersey](https://jersey.dev.java.net), the reference implementation, [RESTEasy](http://resteasy.damnhandy.com) by JBoss, [Restlet,](http://www.restlet.org) and [Apache CXF](http://cxf.apache.org/).

JSR-311 defines an API that is a POJO-based and annotation driven like almost all new frameworks and APIs nowadays. The API assumes that the underlaying protocol is HTTP and it provides mappings between HTTP and URI elements and the API classes.

Using JAX-RS, web resources are implemented by resource classes and resource requests are handled by resource methods on the resource classes. A resource class is an ordinary Java class that is annotated with a `@Path` annotation or has one or more methods annotated with a `@Path` annotation. The resource methods are annotated with one of the request method designators; `@GET`, `@POST`, `@PUT`, `@DELETE` or `@HEAD`. A JAX-RS implementation instantiates a resource class instance for each web request to the resource. The resource method that is invoked depends on the HTTP request method (GET, POST etc.) and the request method designator annotations of the method. Using an other set of annotation it is possible to bind properties like HTTP headers, query parameters, matrix parameters, method body etc. to the resource method parameters (or to properties of the request class instance). By default the last parameter in a parameter list of a method is bound to the content of the request body, the entity body. Conversion between a Java objects and an entity body is done by an entity provider.

The rest of this blog will present a very simple example. Like always things like error handling has been left out to make the example clean.

To get started download the Jersey distribution. Initially you will need the `jersey.jar`, `asm-3.1.jar` and `jsr311-api.jar` files. Create a web project in your favorite IDE and put the jar files in the lib catalog of the project. Now you just have to enable Jersey in `web.xml` as follows to get going:

~~~ markup
<servlet>
  <servlet-name>Jersey Web Application</servlet-name>
  <servlet-class>com.sun.jersey.impl.container.servlet.ServletAdaptor</servlet-class>
  <init-param>
    <param-name>com.sun.jersey.config.feature.Redirect</param-name>
    <param-value>true</param-value>
  </init-param>
  <load-on-startup>1</load-on-startup>
</servlet>
<servlet-mapping>
  <servlet-name>Jersey Web Application</servlet-name>
  <url-pattern>/resources/*</url-pattern>
</servlet-mapping>
~~~

Lets assume that we have a Customer class with the attributes id, name and address. Our customer objects are handled by a CustomerRepository object that is accessible from our resource class and we want to expose the Customer objects as web resources. If the resource class is deployed in a Java EE 5 compliant container the repository could be a injected Session Bean. We define a customer resource for our customer collection and sub-resources for the customer objects. The collection url is used to create new customer entities (POST) and list the available customer entities in the collection (GET). On the sub-resources we allow GET to get a representation of the customer entity with a specific id, PUT to update the customer entity and DELETE to delete it. The following methods are allowed on the resources:

[http://host/resources/customer](http://host/resources/customer) (POST, GET)

[http://host/resources/customer/](http://host/resources/customer/)<id> (PUT, GET, DELETE)

Suppose that we have entity providers written that converts a customer object to and from a XML representation. I will not show how that is done, but you can find examples in the attached code. An entity provider does just take an Java object and a bunch of properties as input and spits out a representation on some format like XML, json, Atom, GIF or what ever.

Lets start by defining the resource class, anchor it at the relative URI `/customer` using the `@Path annotation and define the methods needed.

~~~ java
package se.callistaenterprise;

import java.net.URI;

import javax.ws.rs.DELETE;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.PUT;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.ProduceMime;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.UriInfo;

@Path("/customer")
public class CustomerResource {

  private CustomerRepository r =...;

  @GET
  @ProduceMime("text/xml")
  public String list(@Context UriInfo uri) {
  }

  @POST
  public Response post(@Context UriInfo uriInfo, Customer c) {
  }

  @GET
  @ProduceMime("text/xml")
  @Path("{id}")
  public Response get(@PathParam(value="id") long id) {
  }

  @DELETE
  @Path("{id}")
  public Response delete(@PathParam(value="id") long id) {
  }

  @PUT
  @Path("{id}")
  public Response put(@PathParam(value="id") long id, Customer c) {
  }
}
~~~

The first two methods handles the collections resource and the last three handles the sub-resources. The methods that produce an entity body are annotated with the mime type of the entity body produced. The last three methods have a `@Path` template that lets us bind the last part of the URL to the id parameter of the method using the `@PathParam` annotation. All methods but one returns an instance of `javax.ws.rs.core.Response`. This is a special class that lets you build a response in a very nice way using the builder pattern. The first method returns a String and that will be properly converted to the entity body.

The first two methods will return links (URI:s) that points to the sub-resources and we will use the `javax.ws.rs.core.UriInfo` class to build those URI:s. An instance of the UriInfo class is bound by the JAX-RS implementation to the uriInfo parameter of the list and post methods. The UriInfo class also uses the builder pattern and is very easy to work with.

~~~ java
@GET
@ProduceMime("text/xml")
public String list(@Context UriInfo uri) {
  StringBuilder sb = new StringBuilder();
  sb.append(Xml.PRE);
  sb.append("<customers><ul>");
  for(Customer c : r.getCustomers()) {
    sb.append("<li>");
    sb.append("<name>").append(c.getName()).append("</name>");
    sb.append("<uri>");
    sb.append(uri.getAbsolutePathBuilder().path(Long.toString(c.getId())).build());
    sb.append("</uri>");
	sb.append("</li>");
  }
  sb.append("</ul></customers>");
  return sb.toString();
}
~~~

Here is the list method just illustrating a really easy case where we build the XML "by hand" using a StringBuilder. The links to sub-resources are created using the UriInfo instance by just adding the customer id to the current absolute path.

~~~ java
@POST
public Response post(@Context UriInfo uriInfo, Customer c) {
  long id = r.store(c);
  URI uri = uriInfo.getBaseUriBuilder().path(Long.toString(id)).build();
  return Response.status(Response.Status.CREATED).contentLocation(uri).build();
}
~~~

The most complicated part of the post method is done by the entity provider that converts the entity body of the POST request to a customer object. Since the customer object appears last in the parameter list the JAX-RS implementation will try to find a registered entity provider that is able to convert from the entity body mime type to a Customer object. The customer object is stored in our repository and we return a HTTP 201 Created status code and the URL to the newly created resource in the Location header.

The rest of the methods are more or less trivial:

~~~ java
@GET
@ProduceMime("text/xml")
@Path("{id}")
public Response get(@PathParam(value="id") long id) {
  Customer c = r.getCustomer(id);
  return (c != null) ?
      Response.ok(c).build() :
      Response.status(Response.Status.NOT_FOUND).build();
}

@DELETE
@Path("{id}")
public Response delete(@PathParam(value="id") long id) {
  Customer c = r.deleteCustomer(id);
  return (c != null) ?
      Response.ok("Element was deleted").build() :
      Response.status(Response.Status.NOT_FOUND).build();
}

@PUT
@Path("{id}")
public Response put(@PathParam(value="id") long id, Customer c) {
  if (id != c.getId()) return Response.status(Response.Status.BAD_REQUEST).build();
  if (r.getCustomer(id) != null) {
    r.updateCustomer(c);
    return Response.ok().build();
  }
  return Response.status(Response.Status.NOT_FOUND).build();
}
~~~

The common part of the get, put and delete methods is that they bind the last part of the url to the parameter id. The JAX-RS handles the conversion from String to long.

I hope that this simple example has given you some ideas of what the JAX-RS specification is all about. The full example is provided for download at the end of this page. If you want to explore it further you can have a look at the Jersey distribution which have some nice examples.

I think that the JAX-RS makes it really easy to implement RESTful services compared to using the servlet API and URL/URI classes of the JDK.  I have not tried to use [JAX-WS for RESTful webservices](http://java.sun.com/developer/technicalArticles/WebServices/restful/), but I think from the examples that I have seen that JAX-RS provider a much nicer API that is on a higher level than JAX-WS. To test your RESTful services you can use the [Poster firefox plugin](https://addons.mozilla.org/en-US/firefox/addon/2691). It enables you to execute all the HTTP methods.
