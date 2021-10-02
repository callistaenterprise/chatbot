---
layout: details-blog
published: true
categories: blogg teknik
heading: Working with collections in scala rocks
authors:
  - janvasternas
tags: scala
topstory: true
comments: true
---

This is not new for you guys that already know Scala. I attended a Scala tutorial last week and having worked exclusively with java 13 years it was a really good experience. My current project has a lot of code that deals with collections. Filtering, sorting, matching, manipulating and creating lookup caches is done en masse. Feels like this would have been much easier to accomplish if we could have used Scala. I think it is the combination of a richer api and the support for closures that make the difference.

It is not a problem to do any of these thing is Java but I think that the way you can do it in Scala is much more compact, readable and less likely to create errors.

-[readmore]-

Some very simple samples.

~~~ scala
// Define a class with two fields, name and year of birth (like 1982)
class Person(val firstName: String, val born: Int)

// assume list is a List containing Person instances

// Get the last entry of a list
val lastPerson = list.last

// Sort a list, e1 and e2 are placeholders for 2 Person instances to compare
// The result is a new list. The original list is immutable
val sortedAscending = list.sortWith((e1, e2) => (e1.firstName < e2.firstName))

// Reverse the order, resulting in yet another list
val sortedDescending = sortedAscending.reverse

// Filter out some elements of a list, returning a new list
val grownups = list.filter(e1 => e1.born < 1990)

// Create a Map, key is year of birth and value is a list of all
// persons born that year
val personsByYear = list.groupBy(e1 => e1.born)

// Create a new List containing only the firstName strings
val stringList = list.map(e1 => e1.firstName)

val person = new Person("Lance Armstrong", 1971)
// Create a tuple, a container for two objects, another Scala beauty
val personAndAge = (person, 2011 - person.born)

// Apply this to a whole list, return a new list of tuples
val personAndAgeList = list.map(e1 => (e1, 2011 - e1.born))

// All of the code above could be made even more compact like
val sortedAscending = list.sortWith(_.firstName < _.firstName)
val stringList = list.map(_.firstName)
~~~
