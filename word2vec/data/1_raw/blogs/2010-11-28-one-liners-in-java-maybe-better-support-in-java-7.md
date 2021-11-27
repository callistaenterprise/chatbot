---
layout: details-blog
published: true
categories: blogg teknik
heading: One-liners in Java – maybe better support in Java 7
authors:
  - magnusekstrand
tags: java java7
topstory: true
comments: true
---

For sure, Java is a great language. I wrote my first Java app 1996 and have had lots of fun with it ever since. But for the past 4-5 years my interest in dynamic programming languages as Python, Groovy and Clojure has increased more and more. When working with other languages you discover a bunch of nice programming features you don't want to be without.

Already said, Java is a great language, but it is verbose. For example, when creating maps and lists with values/objects in Java, you need to write horribly many lines of code to achieve a very simple task. In Groovy for example, you can do it with a clear and simple syntax.

~~~ groovy
def emptyList = [];
def numbers = [1, 2, 3];
def numbers = [1..100];
~~~

In Java, there is no good way doing this. The standard procedure is:

~~~ java
List<Integer> numbers = new ArrayList<Integer>();
numbers.add(1);
numbers.add(2);
numbers.add(3);
~~~

There are alternatives, such as making an anonymous inner class with an instance initializer (a.k.a "double brace initialization"):

~~~ java
List<Integer> numbers = new ArrayList<Integer>() { { add(1); add(2); add(3); } };
~~~

Which probably should be written like this if you follow the Java stylish way (in other words, not really a one-liner):

~~~ java
List<Integer> numbers = new ArrayList<Integer>() { {
  add(1);
  add(2);
  add(3);
} };
~~~

However, I'm not too fond of the previous approach because what you end up with is a subclass of ArrayList which has an instance initializer, and that class is created just to create one object. And further on, the instance of the anonymous class that you have created contain a synthetic reference to the enclosing object. If you serialize the collection you will also serialize everything in the outer class. The approach is also incompatible with one popular way to implement the `equals(Object o)` method. Assume the class Example having this method:

~~~ java
public boolean equals(final Object o) {
  if (o == null) {
    return false;
  } else if (!getClass().equals(o.getClass())) {
    return false;
  } else {
    Example other = (Example) o; // Compare this to other.
  }
}
~~~

Then, objects created by "double brace initialization" will never be equal to objects created without it. So this approach should never be uses for any class that needs a non trivial `equals(Object)` method. Collection classes should be fine though.

To achieve a one-liner initialization of a list there is an idiomatic alternative that doesn't require such heavy handed use of anonymous inner classes.

~~~ java
List<Integer> numbers = new ArrayList<Integer>(Arrays.asList(1, 2, 3));
~~~

This approach is especially useful when setting up mocks and stubs in your unit tests. It 's fairly clean and understandable, and it helps you keeping down the number of lines of code:

~~~ java
MutableRepositoryItem prod1 = mock(MutableRepositoryItem.class);
MutableRepositoryItem prod2 = mock(MutableRepositoryItem.class);
MutableRepositoryItem prod3 = mock(MutableRepositoryItem.class);
List<RepositoryItem> children = new ArrayList<RepositoryItem>();
children.add(prod1);
children.add(prod2);
children.add(prod3);
~~~

Can be written like this:

~~~ java
MutableRepositoryItem prod1 = mock(MutableRepositoryItem.class);
MutableRepositoryItem prod2 = mock(MutableRepositoryItem.class);
MutableRepositoryItem prod3 = mock(MutableRepositoryItem.class);
List<RepositoryItem> children =
    new ArrayList<RepositoryItem>(
        Arrays.asList(prod1, prod2, prod3));
~~~

Which is three lines of code less

What would be nice is if the Collection Literals proposal for [Project Coin](http://wikis.sun.com/display/ProjectCoin/Home) is accepted, so we can have list literals in Java 7. Imagine writing lists and maps in this way:

~~~ java
List<Integer> emptyList = [];
List<Integer> numbers = [1, 2, 3];
List<Integer> numbers = [1..100];

Map<String, Integer> emptyMap = {:};
Map<String, Integer> mycars =
    {"Saab" : 1994, "Volvo" : 1998, "Hyundai" : 2003};
~~~

Alternatively a slightly more verbose syntax:

~~~ java
List<Integer> numbers = new ArrayList<Integer>() [1, 2, 3];
List<Integer> numbers = new ArrayList<Integer>() [1..100];

Map<String, Integer> mycars =
    new HashMap<String, Integer>()
        {"Saab" : 1994, "Volvo" : 1998, "Hyundai" : 2003};
~~~

Both these syntaxes is far better than what you can do today. If I'm going to vote for an alternative I would pick the shorter syntax. Why? It's cleaner, simpler and shorter.

But there are certainly some difficulties to solve such as:

~~~ java
[1, 2, 3].add(new Date()); // compile error?
[].add(new Date()); // compile error?
~~~

It should be a really simple thing adding list and map literals to Java. But the devil is in the details. When looking into these details you will discover that Java's static types and generics combine will cause some difficulty. It will be interesting to see how it will be resolved in the future. If it will not be solved, there is a risk that Java will lose some of its attractiveness as a first choice language for many developers. Young developers are considering Java the new Cobol - a dying old-fashioned language that is no fun to work in.

Finally, wouldn't be nice to have a simpler syntax for generics where you don't have to write the generics type twice in a generics declaration. Today you need to write this:

~~~ java
Map<String, Collection<Integer>> map =
    new HashMap<String, Collection<Integer>>();
~~~

When Java 7 is out you can, hopefully, write something like this:

~~~ java
Map<String, Collection<Integer>> map = new HashMap();
~~~
