---
layout: details-blog
published: true
categories: blogg teknik
heading: Use Eclipse plugins to find bugs and check test coverage
authors:
  - annicasunnman
tags: opensource quality
topstory: true
comments: true
---

A really useful plugin to Eclipse is [FindBugs](http://findbugs.sourceforge.net/manual/eclipse.html), install the plugin and you can actually find bugs in your code.

It's a good tool to use during projects, but also when performing code reviews. You can get a feeling quite quick on areas that are containing more problems than others. You can use the plugin and run it on a whole project on or a separate java file. It's quite fast running it on a whole project, so just go ahead and install it.

The Find Bug plugin comes with a bug explorer:

_Bild saknas_

Here you can see the severity of the bugs and select the ones you think will cause problems. The code is also marked with a bug:

_Bild saknas_

Another good plugin to be used during development is the [EclEmma](http://www.eclemma.org/), Java Code Coverage for Eclipse. With the plugin you get a really colorful Eclipse environment, read rows are not tested and green are tested.

_Bild saknas_

It's a really easy way of getting coverage on module or on a specific class. If you have goals that some percentage should be reached on your code, it's quite easy to get the coverage.

Just keep in mind that there is no use to add a lot of "unnecessary" testing just to get the coverage percentage up.
