---
layout: details-blog
published: true
categories: blogg teknik
heading: Maven Eclipse integration revisited
authors:
  - bjornbeskow
tags: övrigt
topstory: true
comments: true
---

Integrating the Eclipse environment with Maven has always been a challenge, as we have reported upon [before](/pages/viewpage.action?pageId=884867). I want the productivity of the Eclipse IDE **and** the expressive power, consistency and repeatability of Maven. But a fundamental difference in the underlying paradigms of Eclipse versus Maven have made that coexistence awkward and ugly:

- Eclipse assumes all dependent jar files for a project are explicitly listed within the project (in the `.classpath` file), whereas Maven relies on dependencies being defined in `pom.xml` files and resolved at build time using an underlying repository model

Furthermore, there is a difference in expressiveness, where several fundamental capabilities in Maven have no Eclipse counterparts:

- Eclipse assumes all projects lives within a flat structure, with no hierarchical dependencies between projects, whereas Maven allows hierarchical composition of projects and builds
- Eclipse assumes projects are always built the same way, whereas Maven provides a sophisticated Build Lifecycle model
- Eclipse assumes a project have one classpath, whereas Maven provides different classpath scopes (i.e. runtime vs. test scope)
- etc.

There are two principal ways to try to bridge the gap and allow the different paradigms to coexist:

- Either plug in Maven knowledge into Eclipse, to allow for Eclipse projects to access dependencies via Maven pom.xml files and execute Maven build lifecycle stages inside Eclipse, or
- Plug in Eclipse knowledge into Maven, to allow Maven to generate the necessary Eclipse project files to reflect the information in the `pom.xml`

The first approach is the most appealing, but the Maven plugins to Eclipse have for several years been too immature, unstable and error-prone to be of any use. Instead we have resorted to the second approach, where the eclipse plugin to Maven have been capable of generating rudimentary Eclipse project files. Together with the use of Eclipse external build tool definitions, it has been possible to define a semi-automated process that is a bit awkward but good enough.

I was therefore delighted to read that [Sonatype](http://www.sonatype.com), a new commercial company started by the Maven engineers and specializing in Maven support, has finally brought the m2eclipse plugin to a near-stable state as an Eclipse Technology project. The inconsistencies and flaws from past years are removed. The plugin is The Maven Dependencies Classpath Container efficiently adds dependencies specified in the Maven pom.xml file, and reliably and immedialtely reflects changes done to the `pom.xml` file both from within and outside Eclipse.

The plugin also a dedicated Maven `pom.xml` file editor and wizards/dialogs for easy Maven dependency management. Having tested the plugin for a week now in a project, I think it is really delivers what Sonatype promises: The "lynchpin" between Eclipse and Maven.
