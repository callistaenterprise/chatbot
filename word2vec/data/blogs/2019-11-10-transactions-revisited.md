---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: 'Transactions Revisited'
tags: distributed transactions XA domain driven design architecture ACID BASE CAP
authors:
  - bjornbeskow
---
[Transactions] play an important role in most software systems, as well as in many everyday situations. In recent days however, and especially in the context of highly distributed, internet scale solutions, transactions have gained quite a bad reputation (it's not uncommon to hear collegues in the profession say "Transaction? Bah, we don't need that!"). So what's the deal? 
-[readmore]-

[comment]: # (Links)
[TCC Pattern]: https://www.atomikos.com/Blog/TransactionsForTheRESTOfUs
[ACID]: https://en.wikipedia.org/wiki/ACID
[BASE]: https://www.dataversity.net/acid-vs-base-the-shifting-ph-of-database-transaction-processing/
[CAP Theorem]: https://en.wikipedia.org/wiki/CAP_theorem
[Atomicity]: https://en.wikipedia.org/wiki/Atomicity_(database_systems)
[Transactions]: https://en.wikipedia.org/wiki/Transaction
[Database Transaction]: https://en.wikipedia.org/wiki/Database_transaction
[Two Phase Commit]: https://en.wikipedia.org/wiki/Two-phase_commit_protocol
[XA]: https://en.wikipedia.org/wiki/X/Open_XA
[Bounded Context]: https://martinfowler.com/bliki/BoundedContext.html
[Compensating Transaction]: https://en.wikipedia.org/wiki/Compensating_transaction

[comment]: # (Images)
[Transaction-Sign]: https://www.picpedia.org/highway-signs/images/transaction.jpg
[2pc]: /assets/blogg/transactions-revisited/2-phase-commit.png

## What is a Transaction anyway?

There is clearly an ambiguity in place here, which may be fooling us. "Transaction" as in [Database Transaction] seems tho have a highly specialized meaning, which contains elements that may not be so important from the business domain perspective. Let's try to clarify things:

![Transaction-Sign][Transaction-Sign]
*Image from www.picpedia.org/highway-signs/images/transaction.jpg, courtacy of Nick Youngson, www.nyphotographic.com*

### Database Transactions

Within the area of Databases, the notion of a Transaction has traditionally been defined in terms of a set of properties intended to guarantee validity even in the event of errors, refered to as the *ACID* properties:

* **Atomicity** guarantees that all operations within a "unit of work" succeeds completely, or fails completely.
* **Consistency** ensures that a transaction can only bring the database from one valid state to another, maintaining all invariants at all times.
* **Isolation** determines how the changes done in one transaction is visible to other concurrent transations.
* **Durability** guarantees that a transaction which has committed will survive permanently.

Within a single database instance, the ACID properties provides no challenge for most databases. Such transactions are often called *local* transactions. But when a single database isn't sufficient (for instance when we need to scale it horizontally to cope with high volumes of data and clients, or when the transaction affects data that lives in different databases or resources), things get trickier. Such transactions are often called *global* transactions. We now need a more sophisticated mechanism to synchronize the transaction between the multiple resources involved, a mechanism which is usually referred to as [Two Phase Commit] and standardised by the [XA] protocol. During the early JavaEE days, support for global transactions was a key selling point for high-end application servers, databases and message queue providers. 

![Two Phase Commit][2pc]

What makes things tricky is the asynchronous and unreliable nature of the networks that plague all distributed solutions. As noted by Eric Brewer in 1999, it is theoretically impossible to achieve both high availability, consistence and data partitioning as the same time. His [CAP Theorem] states that Web Services cannot ensure all three of the following properties at once:

* **Consistency**: The client perceives that a set of operations has occurred all at once.
* **Availability**: Every operation must terminate in an intended response.
* **Partition tolerance**: Operations will complete, even if individual components are unavailable.

Since we started out with a need for data partitioning, we are left with two options to choose between: consistency **or** availability.
In the Internet era, not many people are willing to sacrifice availability. Hence we give up consistency.

### Eventual Consistency

So we give up the Consistency guarantee, and must accept the fact that data will inevitably be inconsistent at times (i.e. some invariants are not guaranteed at all times). In the best of worlds, the inconsistencies are short-lived, and the data will self-heal over time and become consistent again. This alternative to ACID is sometimes referered to as [BASE]:

* **B**asically **A**vailable
* **S**oft state
* **E**ventually consistent

### Atomicity

So we are forced to give up ACID in order to have high availabilty. Hence transactions suck, and should be avoided, right?

Well, not really. The *Consistency* and *Isolation* aspects of ACID came from the specialized Database Transaction notion. But the most important aspect of a transaction in most Business scenarios as well as in everyday life is *Atomicity*. If two or more operations or steps in a business process forms a logical atomic *Unit of Work*, we must make sure that all those operations are successfully applied, or else that none of them are. If we cannot guarantee this atomicity, there is no hope for any eventual consistency either: If some of the operations are applied and some aren't, the resulting inconsistency will remain forever (or at least until we explicitly do something about it).

### Transactional Boundaries

So it seems we still need to care about the transactional needs and boundaries of our business domain. Ideally, the transactional boundaries are kept within a [Bounded Context] of the domain (i.e. within one Microservice). If so, a wise choice of database technology might be sufficient to fulfil the needs for atomicity. If however the logical Unit of Work spans multiple Microservices, Database Transactions will not be of much help. In such cases, we need dedicated mechanisms or patterns to achieve the transactional needs of the domain. In a forthcoming blog, I'll discuss two such patterns; Compensating Transactions and Reservations. Stay tuned!
