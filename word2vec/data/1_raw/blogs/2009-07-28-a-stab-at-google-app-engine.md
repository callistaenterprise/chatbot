---
layout: details-blog
published: true
categories: blogg teknik
heading: A stab at Google App Engine
authors:
  - johaneltes
tags: dynamiclanguages javaee
topstory: true
comments: true
---

I decided to see what it would take to deploy the weather feed of my previous post to Google App Engine - a cloud platform for Java servlets. I went the maven path, so that I could simply deploy to GAE via a maven build command. In order to keep the original project independent of GAE, I set up a second web-app project as a war overlay. A war overlay project is a maven war project that that declares a dependency to another war project. Maven then merges the web artifacts of both projects into the web war produced by the depending project. An additional advantage is that I could keep the maven default layout for the original web project. GAE needs a slightly different structure, which is then used in the overlay project only.

This was useful, since GAE-specific stuff goes into a GAE-specific deployment descriptor (`appengine-web.xml`).

## The traps

Of cause I went into a number of traps, before it all worked.

### 1. Script files not processed
My app uses Groovy Templates for dynamic html output. Although web.xml had a servlet mapping that matched the extension used for the templates, they were served unprocessed by GAE servlet engine. The solution was to specifically exclude them from static resources in `appengine-web.xml`:

~~~ markup
<static-files>
  <exclude path="/WEB-INF/**.groovy" />
  <exclude path="**.gtpl" />
</static-files>
~~~

(The app doesn't use uncompiled groovy, but just to prepare for the future...)

### 2. JAXB doesn't work in GAE, what so ever
Although I found JAXWS on the list of Java EE specs not supported by GAE, I still had a hope that plain JAXB without JAXWS network access would work. It didn't. So I had to skip JAXB and use Groovy:s Markup builder. As a result, the DDD achieved by Groovy Categories is gone... **(2010-05-15: JAXB is now a supported Java EE component)**

## The result
Point an RSS-reader to [http://rss2weather.appspot.com](http://rss2weather.appspot.com) and try the advertised feeds (weather for a list of places currently of interest to me).
