---
layout: details-blog
published: true
categories: blogg teknik
heading: Lessons learned using DBUnit in a large project
authors:
  - janvasternas
tags: övrigt
topstory: true
comments: true
---

In my current project we have found that test using a slightly larger unit than single classes makes a lot of sense. Typically there is a service class with some methods that calls a number of entity objects to interact with the database. So our unit under test is often the service class, some entity classes and the database + the spring configuration for wiring.

-[readmore]-

The alternative would be to use mock objects extensively. We have tried that to and in some cases it makes a lot of sense but often the setup of the mock objects need a lot of code and to a certain extent is a copy of the implementation. When the implementation changes the mock setup has to change.

In test where the database is included you need a smooth way to setup data before the test. We have used DbUnit for that. Typically a test method has a String constant containing an xml representation of all the rows we want to be inserted before the test. It is reasonably compact using properties for columns rather than new tags which would have been to verbose. Typically a test case will

- set up data in the database (often 20-60 rows in different tables)
- get an initialized spring bean from the context,
- call a method on that bean
- either examines the returned value or the changed state in the database.

## Problem
There are two problems with this approach when your doing a large system and have a couple of hundred test classes with 20-30 test methods each.

1. To create new test data you need to specify all `NOT NULL` attributes with correct values even if only some of them are important for the specific test your designing.
2. To change all affected test when your domain models evolves over time may create a lot of work. Attribute come and go or move between entities and then you need to change all test that uses that table. This has turned out to be a major refactoring activity for us. It it sometimes tempting to design your changes in a way that minimizes the test refactoring work and then you really are "bicycling on this ice". You may leave out constraint that really should have been in the database, not good.

## Some of the things we have found can minimize the negative effects

### Break up the data into smaller fragment
In the beginning each test method had its own chunk of test data defined in one variable. Often this was copied to the next test method and minor changes was made to create a new scenario. Not only does this increase the refactoring burden, it also makes it very difficult to understand what the difference between two setups are.

By breaking up the data in 5-6 smaller pieces you can replace only one of the pieces with another version and reuse the rest. Choosing good names of the variables helps to understand the intent of the test and its data.

### Reuse same data for dbunit between test methods
Many times all you want to do is change the value of one or very few columns in one row between two test methods. Using the same data, insert with DbUnit and then write 2-5 lines of java code to read, manipulate some attributes and save the changes makes a lot of sense for the same reasons as above, less data to refactor and easier to understand what a test really does.

### Encapsulate the task of creating a dbunit dataset and inserting it into the database
Add a method to your test classes superclass that does this and in that method you can
analyze table metadata, if a value is not supplied in the xml and the column is `NOT NULL` you may supply a default value based on the type like 0, " ", current time etc. or even get a default value specified in a properties file on a table/column basis.

If you do that you only have to specify the columns that really matter to a specific test and leave the rest out. So the test is not affected by changes in the columns that are not specified.

### Always run tests against empty databases
If there are some readonly data that can never change, populate it with a script that is separated from your tests.

## Things that we have tried but found not so good

### Common data for all tests
Prepopulated minimal set of data that could be used by all tests, it simply doesn't work. After some time it is impossible to change that data because it is used by so many tests and the new test you want write needs the data setup differently.

### Clever method calls
Mixing java snippets to include variable data in a dbunit xml string and dbunit definitions, makes the code very hard to understand.

~~~ java
String data = "<ORDER ID='1' CUSTOMER_ID='578' />" +
    getXmlForOrderRow(1, "bike", 500) +
    "<CUSTOMER ID='578' NAME='B Streisand' />";
~~~

In the method call is the first parameter the id of the order ? Is the third parameter the quantity or the price ? Is there a value for the OPTION attribute specified in the order row or not ? You need to examine the method to find out, potentially having to jump between method definitions and the data setup.

## Conclusion
DbUnit makes a lot of sense but you need to try to minimize the refactoring effort when the entity model changes.
