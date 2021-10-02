---
layout: details-blog
published: true
categories: blogg teknik
heading: Yet another Mock framework
authors:
  - bjornbeskow
tags: opensource tdd
topstory: true
comments: true
---

I have used [EasyMock](http://www.easymock.org/) for Mock Object creation since version 1.0 in 2001. It has never been perfect, but good enough. The need to explicitly work with a separate Control object for every Mock object created was a pain, but that was changed in version 2.0. EasyMock is a decent Mock Object framework.

Still, in lectures and tutorials we do on Mock Object usage, I have always had a bit of a problem explaining how tests using EasyMock fits into the generic _Arrange-Act-Assert_ form of most unit tests. The "recording" part of an EasyMock test tends to fall into both the Arrange and the Assert category: it governs the behavior of the mock object **and** it records an expectation:

~~~ java
import static org.easymock.EasyMock.*;

//mock creation
List mockedList = createMock(List.class);

//Arrange for mock object usage - program behaviour and register expectation
expect(mockedList.get(1)).andReturn("one");
replay(mockedList);

//Act
mockedList.get(1);

//Assert: verify all expectations
verify(mockedList);
~~~

So what, one might ask? Isn't that just of interest for a purist? Well, not only. Besides the fact that the assertions on correct usage of the mock object becomes hidden in the Arrange part, the assertions are **always** implicit there, regardless of whether they make sense or not. Over and over again, I find that I only need the Arrange part: program the mock object with how it should behave. The implicit assertions then just gets in the way, often leading to false negatives.

I have learned to live with this, but last week when struggling with some refactoring work in an area with tons of mock-based tests, I had enough. There must be a better way!

Of course there is. Half an hour surfing, and I discovered [Mockito](http://code.google.com/p/mockito/). It is an EasyMock clone that does exactly what I was looking for: Allowing Mock Object expectations to be specified separately from Mock Object behaviour:

~~~ java
import static org.mockito.Mockito.*;

//mock creation
List mockedList = mock(List.class);

//Arrange for mock object usage - program behaviour
stub(mockedList.get(1)).toReturn("one");

//Act using mock object - will never throw any unexpected exception!
mockedList.get(1);

//explicit verification, if relevant - if it fails it will throw an assertion error here:
verify(mockedList).get(1);
~~~

No big deal, one might think. But having worked with it for a couple of days, it sure made my refactorings **a whole lot** easier. It was well worth the effort switching framework.
