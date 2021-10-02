---
layout: details-blog
published: true
categories: blogg teknik
heading: Using Categories to keep Java domain models uncluttered
authors:
  - johaneltes
tags: synamiclanguages
topstory: true
comments: true
---

Going back to the roots of OOD has been commonly advocated since Eric Evans  presented his book [Domain-Driven Design: Tackling Complexity in the Heart of Software](http://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215/ref=sr_1_1?ie=UTF8&s=books&qid=1238687848&sr=8-1) back in 2003. There are several other sources of the movement, such as the [Naked Objects Framework](http://en.wikipedia.org/wiki/Naked_objects) which we presented at [Cadec 2007](http://www.callistaenterprise.se/download/18.5a1758e1117d436eebd80001364).

In database systems, DDD often takes its representation in a class model of the persistent information to be managed by a service or a system. If Java is used to implement the entity classes describing persistent objects, JPA may be the persistence technology (presented at several Cadecs: [JPA 1.0](http://www.callistaenterprise.se/download/18.5a1758e1117d436eebd80001363/JPA1.0.pdf), [2 years with JPA](http://www.callistaenterprise.se/download/18.6521041711855b35da480001036/JPA.pdf)) used to add data base persistence behavior to the Entity POJOs.

Within DDD, the idea is to allocate all logic (as much as feasible) to the entity POJOs. This often includes logic of the following categories: accessing state (setters, getters, navigation and change of object graph), validating the state, calculation of derived attributes (calculating order sum of an order) and event processing (action-logic triggered by changes to the state of an entity, such as producing a shipment note when the order state is changed to "ready-for-shipment").

## Problem with cluttered POJOs

A challenge with DDD is to know what should go into the object model and what shouldn't. There are many types of behavior that are specific to process or external context that - when pushed into the entity classes - makes them cluttered and potentially fragile. They become fragile, when the the forces that generate change are related to external parties rather than the core business for which the model was initially creates. Change management and dependency management becomes complex.

## Groovy categories to the rescue

The Java language provides little support for dealing with this problem. [qi4j](http://www.qi4j.org/) is an interesting approach to deal with many aspects of POJO cluttering, but not the dependency problem. With qi4j, model objects can only be extended by making changes to the definition of Java interface of a model class. This creates dependencies between change management processes and clutters the dependencies of the entities. I think qi4j carries a lot of promise, but its evolution is bound to the limitations of the Java language, which is sometimes a problem.

In Mid 90's, I worked with Objective-C on the [NextSTEP platform](http://en.wikipedia.org/wiki/Nextstep). It has a construct called Category that allows a "package of behavior" (methods) to be added to an existing class in runtime. It was often used to add methods to the foundation classes (like NSString).

I've missed this ability in Java since I first learned it. It is how ever available in [Groovy](http://groovy.codehaus.org/) - the dynamic language built on the JDK ([a Cadec presentation is available](http://www.callistaenterprise.se/download/18.5a1758e1117d436eebd80001355/Groovy.pdf)). The remaining part of this blog entry illustrates how Groovy categories can be used to extend the use of DDD without cluttering your domain model.

## Our example: adding behavior to JAXB-generated POJO:s

I see Groovy typically being used in the following contexts:

- As the core development language of web application development based on the [Grails framework](http://www.grails.org/) (Callista-presentation [here](http://www.callistaenterprise.se/download/18.4e1bc06811fea7fe4fb80006778/EnterpriseGrails.pdf))
- As integration language complementing Java projects due to it's phenomenal XML processing capabilities (dynamic DSLs through Groovy MarkupBuilder)
- As scripting language

My example for this blog is of the second category. This is the problem:

Create an RSS feed on top of the AccuWeather RESTFul web service (WeatherData).

Prerequisites:

- Use JAXB-generated POJOs available in an existing jar file to parse weather data from the AccuWeather service.

The task:

- Use Groovy to create a web app that transforms the response from the AccuWeather service to an RSS 2.0 feed.
- The result should look like this (in Safari RSS reader)

_Bild saknas_

Design constraints:

- DDD should be applied such that entity logic related to producing RSS output should be added to the domain objects (JAXB-generated model classes)
- All RSS-related logic should be in the same project as the logic that uses/depends on that logic. The logic should be added to the JAXB POJO:s in runtime, when needed by the Groovy RSS servlet.

## The solution

We need to create a Groovy servlet that requests XML weather data from the AccuWeather weather service, parses the response into JAXB-objects produced from the XML Schema of the service and finally writes RSS XML to the servlet response by accessing the JAXB POJOs. Here's the Servlet:

~~~ groovy
package se.callistaenterprise.labs.groovydslblog.accuatomfeed

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.ServletException;
import javax.xml.bind.Unmarshaller;
import javax.xml.bind.JAXBContext;
import com.accuweather.weatherdata.AdcDatabaseType;
import com.accuweather.weatherdata.DayType;
import java.text.SimpleDateFormat

/**
 * Servlet that queries the AccuWeather wetherdata service and re-publishes it as a RSS feed.
 * The query string is passed on to the accuweather service as is, i.e. it is expected to be
 * a wetherdata query string.
 * A typical query string looks like this: ?location=EUR|SE|SW005|KUNGSBACKA&metric=1
 * So that the request to this servlet (as by mapping in web.xml) becomes:
 *
 *  http://localhost:8080/accuatomfeed/AccuFeed.xml?location=EUR|SE|SW005|KUNGSBACKA&metric=1
 *
 * @author Johan Eltes
 */
public class AccuAtomServlet extends HttpServlet {
  protected void doGet(HttpServletRequest req, HttpServletResponse resp)
    throws ServletException, java.io.IOException {

    def queryString = req.queryString // We pass this on to the Accu RESTFul service

    // Get Weather Data from Accu Weather Data Service into JAXB pojos.
    Unmarshaller um = JAXBContext.
      newInstance("com.accuweather.weatherdata").createUnmarshaller()
    URL url = new URL("http://rdona.accu-weather.com/widget/rdona/weather-data.asp?${queryString}")
      AdcDatabaseType accuResponse = um.unmarshal(url).value

    // Produce RSS feed
    resp.contentType = "application/rss+xml"
    resp.writer << '<?xml version="1.0" encoding="UTF-8" ?>'
    def rssBuilder = new groovy.xml.MarkupBuilder(resp.writer)
    use (DayTypeRssSupportCategory, HttpServletRequestRssSupportCategory) {
      rssBuilder.rss (version: '2.0') {
        channel {
          title ("Weather stream for ${queryString?.replace('%7C','|')}")
          description("An RSS feed built with Groovy to transform the accu-wether RESTFul service into an RSS feed.")
          language ('en-us')
          link (req.rssChannelLink) // property rssChannelLink is added to HttpServletRequest by HttpServletRequestRssSupportCategory
          ttl(60)
          pubDate(new SimpleDateFormat("EEE, d MMM yyyy HH:mm:ss Z", Locale.US).format(new Date()))
          accuResponse.forecast.day.each {DayType day ->
            item () {
              title (day.daycode)
              link (day.url.replace('|','%7C'))
              description (day.itemDescription) // Method itemDescription is added to class DayType by DayTypeRssSupportCategory
              pubDate (day.pubDate) // Method itemDescription is added to class DayType by DayTypeRssSupportCategory
            }
          }
        }
      }
    }
  }
}
~~~

The interesting part is the `use`-keyword that in runtime applies a category that adds the method `getItemDescription` that is later invoked as if it was part of the domain class DayType (Groovy allows for property-based access to Java-beans properties as a convenience to calling `get...())`.

What is then exactly a Groovy Category? It is actually just a plan Groovy class that follows a set of conventions, that allows it to be applied as a Category using the use-keyword. Here's the category class that defines the `getItemDescription()` method for the `DatType` class:

~~~ groovy
package se.callistaenterprise.labs.groovydslblog.accuatomfeed

import com.accuweather.weatherdata.DayType
import groovy.xml.MarkupBuilder

/**
 * Adds RSS behavior to DateType
 * @author Johan Eltes
 */
public class DayTypeRssSupportCategory {

  /**
   * Derives a RSS item description from the content of a DayType
   * This is the old-school categories. The AST-transfomration for @Category
   * gives much neater grammar (like Objective-C categories), but it is abit
   * too buggy at the moment.
   *
   * The description is produced as html, so we need to create a local
   * MarkupBuilder rather than passing in the parent MarkupBuilder. Otherwise
   * the html for the description field would not be escaped.
   */
  static String getItemDescription(DayType that) {
    StringWriter writer = new StringWriter()
    MarkupBuilder htmlBuilder = new MarkupBuilder(writer)
    writer << that.daytime.txtlong
    htmlBuilder.table {
      tr {
        td {
          img (src: "http://vortex.accuweather.com/adc2004/common/images/icons/standard/wx/45x45/${that.daytime.weathericon.padLeft(2, '0')}.gif")
        }
        td {
          ul {
            li ("Realfeel High: ${that.daytime.realfeelhigh}")
            li ("Realfeel Low: ${that.daytime.realfeellow}")
            li ("Wind direction: ${that.daytime.winddirection}")
            li ("Wind speed: ${that.windspeed} m/s")
          }
        }
      }
    }
    writer.toString()
  }

  static int getWindspeed(DayType that) {
    that.daytime.windspeed / 3.6
  }
}
~~~

## Conclusions

I do think the type of construct represented by the Groovy Categories is a great way to make DDD scale for real-world-scenarios. In real-world scenarios for DDD require some way of separating concerns so that a core domain object can add value (as a first class object in the spirit of DDD).

Traditionally the solutions would involve various types of advanced patterns or frameworks. The sample used in this blog, would require the Visitor Pattern in order to keep the same level of separation of concerns and dependencies. Using qi4j is a Java-only framework solution that would solve the cluttering-problem, but still make the POJO library depend on the fact that it needs to support the needs of an RSS feed. In this specific case, when we are not in control (or pretend not to be) of the domain classes, qi4j would - to my understanding - not be useful.

With category support in the language (as in Groovy), DDD becomes much more intuitive to implement.

## Try it out

I've attached a [zip](/wp-content/upload/GroovyDslBlog.zip) with the a maven multi project for running the sample. The zip contains one project for the feed web-app and one project that builds the jaxb model classes from the xml schema of the accu weather data response payload.

If you want to use eclipse, then issue...

~~~
$ mvn -Dwtpversion=1.5 eclipse:eclipse
~~~

...which generates an eclipse project for each of the maven projects. Make sure you are located in the `GroovyDslBlog` folder when running the command. To run/debug in Eclipse with WTP you will also need the Groovy plug-in, available here: [http://dist.codehaus.org/groovy/distributions/update/](http://dist.codehaus.org/groovy/distributions/update/) Have fun!

**Improved syntax with AST transformations**

With Groovy 1.6, something called [AST Transformations](http://groovy.codehaus.org/Compile-time+Metaprogramming+-+AST+Transformations) has been added. This allows the programming model to be extended in a modular way without changing the syntax of the language. It has some similarities with what you can achieve with aspectj. Using ast transformations, Groovy 1.6 adds a more object-oriented way of defining categories (yes, exactly the same model as in Objective-C ![](/images/icons/emoticons/smile.gif). Unfortunately, as of Groovy 1.6.3, the ast transformer for "OO" categories is [a bit shaky (fixed for upcoming 1.6.4)](http://jira.codehaus.org/browse/GROOVY-3543). Using this way of defining the category, it would look like:

~~~ groovy
package se.callistaenterprise.labs.groovydslblog.accuatomfeed

import com.accuweather.weatherdata.DayType
import groovy.xml.MarkupBuilder
import java.io.StringWriter

@Category(DayType)
class AstDayTypeRssSupportCategory {

  public String getItemDescription() {
    StringWriter writer = new StringWriter()
    MarkupBuilder htmlBuilder = new MarkupBuilder(writer)
    writer << this.daytime.txtlong
    htmlBuilder.table {
      tr {
        td {
          img (src: "http://vortex.accuweather.com/adc2004/common/images/icons/standard/wx/45x45/${that.daytime.weathericon.padLeft(2, '0')}.gif")
        }
        td {
          ul {
            li ("Realfeel High: ${this.daytime.realfeelhigh}")
            li ("Realfeel Low: ${this.daytime.realfeellow}")
            li ("Wind direction: ${this.daytime.winddirection}")
            li ("Wind speed: ${this.daytime.windspeed} m/s")
          }
        }
      }
    }
    writer.toString()
  }
}
~~~
