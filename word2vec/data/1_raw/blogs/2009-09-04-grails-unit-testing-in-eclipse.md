---
layout: details-blog
published: true
categories: blogg teknik
heading: Grails Unit Testing in Eclipse
authors:
  - bjornbeskow
tags: dynamiclanguages tdd
topstory: true
comments: true
---

Groovy and Grails support have long been a sad story in Eclipse. Most notable, running and debugging Grails Unit tests in Eclipse has been quite painful, partly due to the fact that the Groovy eclipse plugin didn't recognize the tests as being Unit tests (and hence the **Run as/Unit Test** has not been available), and partly because of classpath clashes between Grails and the Eclipse Groovy plugin (manifested by the dreaded 'Disable Groovy Compiler Generating Class Files' option, which needs to be both set and not set).

With the [alpha release of V2 of the Groovy plugin](http://groovy.codehaus.org/Eclipse+Plugin), things are getting better. Most of the classpath related problems are resolved, and Groovy Unit test classes are now correctly recognized. This means Grails unit tests can now be executed directly in the IDE, without the need to run a grails command.

Some flaws with Grails Unit tests still exist, however: The Eclipse Groovy plugin is not aware of many of the Grails conventions (e.g. that all Groovy classes within the grails-app/domain folder are Domain Entities). This means that the "magic" in terms of meta-programming that Grails performs on e.g. Entities is not done when executed directly in Eclipse, which cause most of the superb Grails mocking support to fail. Consider for instance the simple Employee entity below:

~~~ groovy
class Employee {
  String name
  static constraints = {
    name(blank:false)
  }
}
~~~

In a Unit test for the Employee, the constraint on `name` can be tested by mocking the Entity class:

~~~ groovy
class EmployeeTests extends GrailsUnitTestCase {
  void testNameNotBlank() {
    mockDomain(Employee)
    def e = new Employee(name: "")
    assertFalse "validation should have fail", e.validate()
    assertEquals "blank", e.errors.name
  }
}
~~~

This test runs as expected via the Grails command, but if executed directly within Eclipse, the Employee class is just an ordinary Groovy class that hasn't been meta-programmed by Grails, and the test fails with the following exception:

~~~
org.codehaus.groovy.grails.exceptions.GrailsDomainException:
Identity property not found, but required in domain class [Employee]
~~~

There are ways around these problems. Starting with Groovy 1.6, [**AST Transformations**](http://groovy.codehaus.org/Compile-time+Metaprogramming+-+AST+Transformations) allow meta-programming in compile time. A local AST transformation is triggered by an Annotation on the class to be transformed, and the compiler automatically applies the transformation. Most Grails meta-programming enhancements are also available as AST annotations.

Hence if we mark the Employee entity with the `@Entity` annotation (redundandly, since it lives in the grails-app/domain folder), the compiler will automatically transform it into a Grails entity and hence the mockDomain(Employee) mechanism will work again.

~~~ groovy
@grails.persistence.Entity
class Employee {
  ...
}
~~~

One little caveat, though: The Eclipse Groovy plugin must be configured to use the correct classpath when doing AST transformations. Otherwise, it refuses to compile the annotated class, giving the following error:

~~~
Groovy:Could not find class for Transformation Processor org.codehaus.groovy.grails.compiler.injection.EntityASTTransformation declared by
grails.persistence.Entity
~~~

By adding a file `groovy.properties` with the contents as seen below to the root folder of the eclipse project, the Groovy compiler is configured to use the same classpath as the project (it sure sounds like that should be the default behaviour to me):

~~~
org.eclipse.jdt.core.compiler.groovy.groovyClassLoaderPath=%projclasspath%
~~~
