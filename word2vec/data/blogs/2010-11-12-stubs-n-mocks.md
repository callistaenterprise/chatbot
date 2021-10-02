---
layout: details-blog
published: true
categories: blogg teknik
heading: Difference between Stubs 'n' Mocks
authors:
  - magnusekstrand
tags: java tdd
topstory: true
comments: true
---

As Martin Fowler states in his article [Mocks Aren't Stubs](http://martinfowler.com/articles/mocksArentStubs.html#TheDifferenceBetweenMocksAndStubs), mocks are often confused with stubs (or vice versa). It is understandable but there are some distinctions. A common interpretation is that stubs are static classes and mocks are dynamically generated classes by using some mocking framework. But the real difference between them is in the style of how you use them, i.e. state-based versus interaction-based unit testing.

## Stubs

A stub is a class supposed to return data from its methods and functions. The return value is hard-coded. Stubs are used inside unit tests when we are testing that a class or method delivers expected output for a known input. They are easy to use in testing, and involve no extra dependencies for unit testing. The basic idea is to implement the dependencies as concrete classes, which reveal only a small part of the overall behavior of the dependent class, which is needed by the class under test.

First, the interface...

~~~ java
public interface Service {
  // Get real data from database for example.
  List findLanguages();
}
~~~

Class with a dependency to the interface...

~~~ java
public CallService(Service service) {
  this.service = service;
}

public List findLanguagesWithA() {
  List languages = new ArrayList();
  for (String s : service.findLanguages()) {
    if (s.contains("a"))
      languages.add(s);
  }
  return languages;
}
~~~

Testing the implementation...

~~~ java
@Test
public void whenCallServiceIsStubbed() {
  CallService service = new CallService(new StubCallService());
  assertTrue(service.findLanguagesWithA().size() == 1);
  assertTrue(service.findLanguagesWithA().get(0).equals("Java"));
}

class StubCallService implements Service {
  public List findLanguages() {
    return Arrays.asList(
        new String[] { "Groovy", "Clojure", "Java"});
  }
}
~~~

The stub does nothing more or less than returning the value that we need for the test. It is common to see such stubs implemented as an anonymous inner classes in Java...

~~~ java
@Test
public void whenCallServiceIsInlined() {
  CallService service = new CallService(new Service() {
    public List findLanguages() {
      return Arrays.asList(
          new String[] { "Groovy", "Clojure", "Java"});
    }
  });
  assertTrue(service.findLanguagesWithA().size() == 1);
  assertTrue(service.findLanguagesWithA().get(0).equals("Java"));
}
~~~

This saves a lot of time maintaining stub classes as separate declarations, and also helps avoiding the common pitfalls of stub implementations, i.e. reusing stubs across unit tests.

Implementing stubs in this way (mostly) requires dozens of lines of empty declarations of methods that are not used in the service. Also, if the dependent interface changes, we have to manually change all the closure stub implementations in all the test cases. Which can be a hard and tedious work. The example here is simple. In real world there would be a lot more interface methods declared.

A solutions to this problem is to use a base class, and instead of implementing the interface afresh for each test case, we extend that base class. If the interface change, we only need to change the base class. Usually the base class would be stored in the unit test directory of the project, not in the production or main source directory.

A base class implementing the interface...

~~~ java
public class StubCallServiceAdapter implements Service {
  @Override
  public List findLanguages() {
    return Arrays.asList(
        new String[] { "Groovy", "Clojure", "Java"});
  }
}
~~~

And the new test case will look like this...

~~~ java
@Test
public void whenCallServiceIsBaseClassed() {
  CallService service = new CallService(
      new StubCallServiceAdapter());
  assertTrue(service.findLanguagesWithA().size() == 1);
  assertTrue(service.findLanguagesWithA().get(0).equals("Java"));
}
~~~

## Mocks

Mocks are used to record and verify the interaction between two classes. Using mock objects gives a high level control over testing the internals  of the implementation of the unit under test. Mocks are beneficial to use at the I/O boundaries - database, networks, XML-RPC servers etc - of the application, so that the interactions of these external resources can be implemented when they are not in the application's control.

~~~ java
@Test
public void whenCallServiceIsMocked() {
  Service mock = createControl().createMock(Service.class);
  CallService service = new CallService(mock);

  expect(mock.findLanguages()).andReturn(Arrays.asList(
      new String[] { "Groovy", "Clojure", "Java"}));
  replay(mock);

  List languages = service.findLanguagesWithA();
  assertTrue(languages.size() == 1);
  assertTrue(languages.get(0).equals("Java"));
  verify(mock);
}
~~~

_(example uses EasyMock)_

Another advantage to the mocking approach is that it gives a more development process when working within a team. If one person is responsible for writing one chunk of code and another person within the team is responsible for some other piece of dependent code, it may not be feasible for this person to write a stubby implementation of the dependency, when the first person is still working on it. However, by using mock objects anyone can test this piece of code independent of the dependencies that may be outside that persons responsibility.

Advantages with mock objects:

- Allow testing a specific unit of code with few line of code
- Isolated and autonomous tests
- Fairly easy to set up
- Fast test executions

## Summary

Stubs and mocks may seem the same but the flow of information from each is very different:

- Stubs provide input for the application under test so that the test can be performed on something else.
- Mocks provide input to the test to decide on pass or fail.

A stub is application facing, and a mock is test facing. It's important to know and distinguish the two since many frameworks for mocking use these terms for different kinds of objects.

The biggest distinction is that a stub you've already written with predetermined behavior. So you would have a class that implements the dependency (abstract class or interface most likely) you are faking for testing purposes and the methods would just be stubbed out with set responses. They wouldn't do anything fancy and you would have already written the stubbed code for it outside of your test.

A mock is something that as part of your test you have to setup with your expectations. A mock is not setup in a predetermined way so you have code that does it in your test. Mocks in a way are determined at runtime since the code that sets the expectations has to run before they do anything.

Tests written with mocks usually follow:

~~~
initialize -> set expectations -> exercise -> verify
~~~

While the pre-written stub would follow

~~~
initialize -> exercise -> verify
~~~

However, the purpose of both is to eliminate testing all the dependencies of a class or function so your tests are more focused and simpler in what they are trying to prove.
