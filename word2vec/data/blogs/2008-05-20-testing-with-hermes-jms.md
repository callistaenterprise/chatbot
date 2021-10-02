---
layout: details-blog
published: true
categories: blogg teknik
heading: Testing with Hermes JMS
authors:
  - annicasunnman
tags: opensource
topstory: true
comments: true
---

I have been implementing new JMS services in my project. The services are defined by XML schemas. During development I implemented basic unit tests to make sure JAXB validation worked as expected. The test was catching some of the validation errors that caused by missing data or wrong occurrences of some elements. I was quite satisfied when I finalized the implementation with my unit test, though I knew that I hadn't tested all variants of possible data in the database that could possibly exist.

Next step before deliver to test was to deploy in a test environment and then trigger the MDB to create the message and send it to my destination queue. The project was already using the tool [Hermes JMS](http://www.hermesjms.com/confluence/display/HJMS/Home) for browsing the queues.

I was a bit surprised over how easy it was to start up with Hermes. The project had already configured all queues and necessary setup for the JMS/MQ part of course in a xml file. What I needed to do was only to download the Hermes and then install it on my PC on the expected path (default). The [installation ](http://www.hermesjms.com/confluence/display/HJMS/Installing) of Hermes is then using the existing configuration called hermes-config.xml created by the project and I was able to reach all queues immediate.

Using the tool was easy. You get the sessions (all the environment setups) on the left hand; on the right hand you have the messages for the selected queues and below you can check out the content of the messages when selecting one.

During the development of new services it is hard to do functional tests on the integration. By using the tool I could easily browse and check the messages and exceptions that occurred with a database with some real data. Of course it is time consuming to test this way - but still to write all kind of variants that the database can hold for you would probably take even longer. So I think this was the best way to combine some unit testing on basic level and the do some more hands on test to see what happens when you really trigger off the messages. Functional test on this level is hard to test by unit test or integration test that is automated. By doing this functional testing before delivering to the test team I can at least be sure that they will be able to test the new integration.

By the way on the homepage for Hermes there is a great header called "Donating" with the wonderful text: It would be nice if I could cover these (referring to changes) with donations from happy users so if you feel inclined then please donate". This type of licence is called "commercially friendly way". Ironic and humoristic? I think so. But still it is a good and easy tool to be used when interacting with JMS providers and I can really recommend it.
