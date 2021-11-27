---
layout: details-blog
published: true
categories: blogg teknik
heading: Five things to avoid in the last sprint
authors:
  - janvasternas
tags: agile craftsmanship
topstory: true
comments: true
---

You are a dedicated team. You have worked hard for a long time building a large complex system. It hasn’t been easy but your reasonably happy with the state your product is in. The system has been running in various staging environments for a long time. You have good test coverage. You use continuous integration.

Now comes the final sprint. The plan is to stabalize the system  in those weeks that are left to enable a smooth production start.

Fix those unresolved bugs that hurts the most. Check the logs for any abnormal situations. Do some user training. Migrate production data. Prepare for the production start.

Are there some things you should avoid in this situation?

-[readmore]-

## Add new major features
There is a great risk that new functionality introduces new bugs. In worst case in may slow down the system in which case you need to optimize your database queries which can possible add some new bugs to the system. If you are really late and the pressure is high it may even be tempting to do the unspeakable - cut down on tests, and we all know what that leads to.

## Start using new frameworks
May have unwanted side-effects. If there already are 100+ jars in the project dependency list, maybe that's enough ?

## Architectural changes
May seem like a good idea, but stay away from it. Generally beware of architects and their ideas.

## Cut the development team in half
May save some short term cost, but is really risky. Unless you are absolutely sure that all the guys that are left can fix bugs in all parts of the system as fast as those not longer there.

## Start large planning work for the next release
Takes the focus from what is most important. Besides, planning is boring.

## All of the above
If you really want to increase the risk delaying the production start, do it all.

If your life feels too slow, feel free to apply any number of the things above in your project. Don’t call me if it doesn’t work out. Been there, done that, survived - sort of.
