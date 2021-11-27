---
categories: blogg teknik
layout: "details-blog"
published: true
heading: SpringOne2GX - Eventsourcing and CQRS in a microservice context
authors: 
  - hakandahl
tags: springone2gx microservices cqrs eventsourcing
topstory: true
comments: true
---
At SpringOne2GX I saw [Michael Ploed](https://twitter.com/bitboss) give a good talk on the subject ["Building microservices with event sourcing and CQRS"](http://de.slideshare.net/mploed/building-microservices-with-event-sourcing-and-cqrs). Here I'll do a quick rundown of the two patterns (event sourcing and CQRS) and then some reflections related to microservices.

-[readmore]-

### Event sourcing
The [Event sourcing](http://martinfowler.com/eaaDev/EventSourcing.html) pattern is, like Michael defined it, all about:
"Event sourcing is an architectural pattern in which the state of the application is being determined by a sequence of events".
There are some important implications of that:

* The full history of events are stored and can be inspected or used for playback to restore system state to a given point in time.
	* Events are typically stored in an object/document format, as opposed to being de-composed into a relational model. Note: In a traditional relational model, keeping historical records often takes quite a bit of work and being able to see what the state was at a particular point in time is often not possible, historical records are often kept on a per-table basis (typical for audit-logging).
* Events must be immutable and may never be deleted, or the system state can't be re-built. Delete is to be implemented as an own event, that is appended to the event store.
* Running queries for current state against the stack of events would typically perform bad, since the application would have to rebuild/maintain the current state from all stored events. Mitigating this problem is up to our next pattern.

### CQRS
The [Command Query Responsibility Segregation (CQRS)](http://martinfowler.com/bliki/CQRS.html) is basically a pattern for separating access to datastore in an application into different services for read and write operations.
The major points of this being:

* possibility to scale read-parts separately from write-parts
* possibility to choose an appropriate datastore technique for read vs write and optimize for each case, for example: for a read-heavy database you might want to have the equivalent of a hevily de-normalized database (although it doesn't have to be a classic SQL-databse)

If we let write-operations append to the event store and then let those events propagate asynchronously to a read optimized datastore (propagation via a messaging paradigm) we can have a solution that is scalable and have some nice features as pointed out above.
Notice that the async propagation of data from write-to-read access introduced eventual consistency into the solution, but we can't have it all, remember the [CAP-theorem](https://en.wikipedia.org/wiki/CAP_theorem).

### The Microservices connection
Both event-sourcing and CQRS have been around for some time so that's not really new.
What's interesting in the microservice context is that some event-handling will most likely be needed to synchronize state between different microservices in any reasonably complex landscape and these patterns can be a useful combination. In a more traditional monolithic solution the need for synchronization would often be less, typically due to access to a large data-model all at once, sometimes paired with a codebase with loose internal boundaries for data access.
If we look at the success stories listed in the beginning of the [Microservices presentation](https://callistaenterprise.se/blogg/cadec/2015/05/27/microservices-sto/), both Karma and SoundCloud use event-handling as vital parts in their architecture, although not exactly as above.


Note: the video recorded talk will show up on infoq.com later on, together with all the other talks from SpringOne2GX 2015.
