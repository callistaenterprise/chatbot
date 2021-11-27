---
layout: details-blog
published: true
categories: blogg teknik
heading: "From the MuleForge: Working on the SFTP Transport and the Smooks Module"
authors:
  - magnuslarsson
tags: esb opensource largefiles mule sftp smooks
topstory: true
comments: true
---

While Web Services (SOAP or REST based) gets all the attention in the press, there are many companies still struggling with file transfers and transformation of very large files (for the scope of this blog defined as files of size > 1 GB). Typically, these companies, can’t get a file of that size through their integration platform and messaging backbone without having to do all sort of tricks such as [splitting](http://www.enterpriseintegrationpatterns.com/Sequencer.html) files into smaller one and later on both [re-sequence](http://www.enterpriseintegrationpatterns.com/Resequencer.html) and [aggregate](http://www.enterpriseintegrationpatterns.com/Aggregator.html) them back again and/or setting up huge memory heaps on their servers and so on…

On top of that, many companies still use FTP for sending files unencrypted and resulting in a lot of usernames/passwords cluttered all over the system landscape, where instead SFTP can provide a secure transport and more easy managed authentication through its use of SSH and PKI.

In this blog I will describe how I have been working with some of our customers to help them find inexpensive and simple (removing unnecessary complexity) but still robust solutions, using open source products such as [Mule ESB](http://www.mulesoft.org/) and the transformation framework [Smooks](http://www.smooks.org/), to achieve large file transfer and transformation.

-[readmore]-

It turned out during this work that the current status of some of the open source components we decided to use did not meet all our requirements. But since we are talking about open source there is a very good solution to that, add the missing pieces yourself (in the way you want it) and bring it back to the open source project!

The open source projects mentioned below lives in the [MuleForge](http://www.mulesoft.org/muleforge), a hosting site and community for development and sharing of open source extensions to Mule ESB and that is where my contributions ended up.

## SFTP
In late 2009, I was involved in a customer project using Mule ESB. In this project we needed to transfer large files but we didn’t want to use FTP. In fact we strived to replace FTP with SFTP.

We started to evaluate the SFPT transport in Mule ESB (that lived in the MuleForge at that time). We found out that the SFTP transport, thanks to its streaming capabilities, could handle large files very well but there were a number of other features required by the customer that were missing in the transport, such as archive functionality, handling of duplicate file names, file-size checks to determine if a file is completely created before consuming it and so on.

To address these shortcomings I decided to join the SFTP-transport project. A couple months later the project released a new version of the transport that solved the mentioned concerns. Since then, our customer has been using the SFTP-transport in production.

Below is a very basic example of a file transfer from one SFTP-server to another SFTP-server applying a Java based transformation of the content. If you download the source code of the transport and take a look in the integration tests and their [mule-config-files](http://svn.codehaus.org/mule/branches/mule-3.x/transports/sftp/src/test/resources/), you can find many other examples of its use.

![](/assets/blogg/from-the-muleforge-working-on-the-sftp-transport-and-the-smooks-module/Skärmavbild-2011-09-27-kl.-23.47.24.png)

**Note #1:** The example assumes usage of PKI-keys and not old style username/password.

**Note #2:** In a real-world case attributes such as address would not be hardcoded but instead be provided as a configurable property.

Over time the SFTP-transport has been used more and more widely and in early 2011, MuleSoft decided to add the SFTP-transport as a core transport of the Mule ESB product. Since Mule ESB v3.1.2 the SFTP-transport is part of the Mule ESB distribution.

…and my work as a MuleForge committer was over for the time being…

## Smooks
Earlier this year (2011) I started to look at the [Smooks project](http://www.smooks.org/), specifically regarding its capabilities to transform between many different formats using a declarative and template driven approach. Added to that Smooks also have support for stream based transformation opening up for transforming very large files without any hassle (as described above). Very compelling when combined with the streaming capabilities of Mule ESB’s file transports (file, FTP and of course SFTP)!

The way to integrate Smooks in Mule ESB is to use the [Smooks Module for Mule](http://www.mulesoft.org/documentation/display/SMOOKS/Home) at the MuleForge, i.e. Smooks support in Mule is not a core part of the Mule ESB product.

Using the Smooks Module you can for example easily replace the Java based transformer in the SFTP-transport example above with a much more versatile Smooks based transformer by replacing the line:

~~~ markup
<custom-transformer class="...MyTransformer"/>
~~~

with:

~~~ markup
<smooks:transformer configFile="my-smooks-transformer.xml"/>
~~~

A problem I found out working with Smooks and Mule was that the Smooks Module for Mule was not yet released for Mule 3, only for Mule 1.x and Mule 2.x. However, all changes required for Mule 3 was already developed and committed but no one have had time to do the final testing and release management for a Mule 3 compatible release.

…so I decided to join in again, this time with the goal to release a Mule 3 compatible version of the Smooks Module!

Last weekend we released a release candidate for the next version, v1.3-RC1, which brings in compatibility with Mule 3.1.x. See [Smooks for Mule v1.3-RC1 released](http://www.mulesoft.org/documentation/display/SMOOKS/Smooks+for+Mule+1.3-RC1+released) for details!

A very good example of what the Smooks framework is capable of doing for you is the example in the Smooks distribution called **freemarker-huge-transform**. It demonstrates a setup where Smooks transforms very large XML-files containing order heads and order lines. An outer streaming SAX-parser is setup to stream through the order head elements and delegates the processing of the order lines to a DOM-parser. This means that the memory intensive DOM models only exist for one order line at the time resulting in a very small memory footprint even for transforming very large files. Freemarker is used as the templating language to declare what the actual transformation should do with each order head and order line.

Copy of the [smooks-config – file](https://github.com/smooks/smooks/blob/master/smooks-examples/freemarker-huge-transform/smooks-config.xml) from the example, comments removed to keep the size down:

![](/assets/blogg/from-the-muleforge-working-on-the-sftp-transport-and-the-smooks-module/Skärmavbild-2011-09-27-kl.-23.36.36.png)

Going through the example in detail is out of the scope for this blog (see [Smooks v1.4 Examples](http://www.smooks.org/mediawiki/index.php?title=Smooks_v1.4_Examples) for details) but some interesting aspects are worth mentioning:

- The outer sax-parser that read order lines with a streaming approach:

~~~ markup
<core:filterSettings type="SAX" defaultSerialization="false" />
~~~

- The two Freemarker based templates that work together. The outer template handling transformation of order-heads (using the streaming SAX-parser) and the inner template transforming order-lines one-by-one using a traditional DOM-parser.
- The Freemarker templates declare the outline of the transformed outgoing message format and the variables `${...order...}` refers to elements in the incoming message and declares where their corresponding values should be placed in the outgoing transformed message.

## To summarize
By combining a couple of open source products and making some contributions of your own, if required, you can construct very cost-effective, low-complex but still very robust solutions to problems that traditionally are concerned to be very hard, complex and expensive to solve.

**Feel the power of open source!**
