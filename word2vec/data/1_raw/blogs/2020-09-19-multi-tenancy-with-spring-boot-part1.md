---
categories: blogg teknik
layout: details-blog
published: true
heading: 'Dynamic Multi Tenancy with Spring Boot, Hibernate and Liquibase Part 1'
authors:
  - bjornbeskow
tags: multi tenancy spring boot data hibernate liquibase postgres
topstory: true
comments: true
---
[Multi Tenancy] usually plays an important role in the business case for [SAAS] solutions. [Spring Boot] and [Hibernate] provide out-of-the-box support for different Multi-tenancy strategies. Configuration however becomes more complicated, and the available code examples are limited. In the first part of this blog series, we'll start by exploring the Multi Tenancy concept and three different architectural patterns for multi tenant data isolation. In the forthcoming episodes, we'll deep dive into the details of implementing the different patterns usign Spring Boot, [Spring Data] and [Liquibase].
 
-[readmore]-

[comment]: # (Links)
[Multi Tenancy]: https://whatis.techtarget.com/definition/multi-tenancy
[SAAS]: https://en.wikipedia.org/wiki/Software_as_a_service
[Spring Framework]: https://spring.io/projects/spring-framework
[Spring Boot]: https://spring.io/projects/spring-boot
[Spring Data]: https://spring.io/projects/spring-data
[Hibernate]: https://hibernate.org/orm/
[Liquibase]: https://www.liquibase.org/

[comment]: # (Images)
[neighbours]: /assets/blogg/multi-tenancy-with-spring-boot/undraw_neighbors_ciwb.png
[SingleDatabaseMultiTenancy]: /assets/blogg/multi-tenancy-with-spring-boot/SingleDatabaseMultiTenancy.png
[SeparateDatabaseMultiTenancy]: /assets/blogg/multi-tenancy-with-spring-boot/SeparateDatabaseMultiTenancy.png
[SeparateSchemaMultiTenancy]: /assets/blogg/multi-tenancy-with-spring-boot/SeparateSchemaMultiTenancy.png

### Blog Series Parts
- Part 1: What is Multi Tenancy (this part)
- [Part 2: Outlining an Implementation Strategy for Multi Tenant Data Access](/blogg/teknik/2020/09/20/multi-tenancy-with-spring-boot-part2/)
- [Part 3: Implementing the Database per Tenant pattern](/blogg/teknik/2020/10/03/multi-tenancy-with-spring-boot-part3/)
- [Part 4: Implementing the Schema per Tenant pattern](/blogg/teknik/2020/10/10/multi-tenancy-with-spring-boot-part4/)
- [Part 5: Implementing the Shared database with Discriminator Column pattern using Hibernate Filters](/blogg/teknik/2020/10/17/multi-tenancy-with-spring-boot-part5/)
- [Part 6: Implementing the Shared database with Discriminator Column pattern using Postgres Row Level Security](/blogg/teknik/2020/10/24/multi-tenancy-with-spring-boot-part6/)
- Part 7: Summing up (forthcoming)

## What is Multi tenancy?

By allowing one single, highly scalable software solution to serve many different customers, a scalable, elastic, agile and cost effective solution can be built. A software architecture in which a (logically) single instance of the software serves multiple tenants is frequently called a *multi-tenancy* architecture. A *tenant* is a group of users who share a common access with specific privileges to the software instance. Everything should be shared, except for the different customers' data, which should be properly separated. Despite the fact that they share resources, tenants aren't aware of each other, and their data is kept totally separate.

![neighbours][neighbours]

### Conflicting requirements

As usual with architectural patterns, a multi-tenant architecture has to balance two partly conflicting needs or forces: On one hand, we would like to share as much as possible, in order to achieve:

 * Better use of resources: One machine reserved for one tenant isn't efficient, as that one tenant is not likely to use all of the machine's computing power. By sharing machines among multiple tenants, use of available resources is maximized.
 * Lower costs: With multiple customers sharing resources, a vendor can offer their services to many customers at a much lower cost than if each customer required their own dedicated infrastructure.
 * Elasticity and Agility: With a shared infrastructure, onboarding new tenants can be much easier, quicker and cost efficient.

On the other hand, we would like to have a fool-proof separation of between tenants, in order to guarantee the privacy, confidentiality and consistency of each tenant's data. We also have to avoid the problem with "noisy neighbors", where a tenant that misbehaves potentially can disturb its neighboring tenants.


## Multi tenancy patterns

As we can see, a challenge lies in separating the **data** for each tenant, while still sharing as much as possible of the other resources. Three principal architectural patterns for Multi Tenancy can be identified, which differs in the degree of (physical) separation of the tenant's data. 

* **Database per tenant**

![SeparateDatabaseMultiTenancy][SeparateDatabaseMultiTenancy]

The most obvious way to separate the data owned by different tenants is to use a separate database per tenant. Using this pattern, the data is physically isolated per tenant, and hence the privacy and confidentiality of the data can easily be guaranteed (including administrative housekeeping such as backups and cleansing). The tradeoff is equally obvious, since the database infrastructure as well as database connection pools cannot be shared between tenants.

* **Schema per tenant**

![SeparateSchemaMultiTenancy][SeparateSchemaMultiTenancy]

A slight variation to is to use a separate *database schema* per tenant, while sharing the database instance. The data for each tenant is logically isolated by the semantics of separate schemas as provided by the database engine. If the schemas is owned by a separate database user per tenant, the database engine's security mechanism further guarantee the privacy and confidentiality of the data (note however that in such a case, the database connection pool cannot be reused by the data access layer).
 
* **Shared database, using a Discriminator Column**

![SingleDatabaseMultiTenancy][SingleDatabaseMultiTenancy]

The final pattern uses a fully shared database, in which data for all tenants are stored in the same table(s). An additional *discriminator* column is added to each table, which needs to be included in an additional `where` clause in each and every query. This pattern provides the least data separation (leaving it to the application to guarantee privacy and confidentiality for the tenant's data) but the maximum sharing of resources. From an infrastructure perspective, it is the conceptually simplest solution, whereas the complexity is pushed into the application. Since data is not separated at the database level, administrative housekeeping such as backups per tenant becomes more difficult.

### Choosing a Multi Tenancy pattern

Hence there are different pro's and con's with the three patterns above. The choice between them will be governed by the requirements of a particular solution. Database-per-tenant provides very strong data isolation between tenants, but requires more infrastructural resources and administrative work in setting up new tenants and performing database migrations. Hence there is an upper limit on the scalability of the Database-per-tenant pattern, both in size and the time required to onboard new tenants. Shared-database-with-Discriminator-column provides maximal sharing of infrastructural resources and hence excellent scalability, but with data isolation between tenants only guaranteed by the application layer.

If you have a smaller number of tenants (< 1000) and require strong guarantees for tenant data isolation, Database-per-tenant and Schema-per-tenant are the most frequent choices. Among them, Schema-per-tenant is usually a good balance between data separation and resource sharing. If you have a large number of tenants, Shared-database-with-Discriminator-column might be the only viable solution.

Sometimes, the most pragmatic approach is a mixed model, supporting different customer segments using different models.

## Summary

In this blog post, we have explored the Multi Tenancy concept and discussed three different architectural patterns for multi tenant data isolation.
In the [next part](/blogg/teknik/2020/09/20/multi-tenancy-with-spring-boot-part2/), we'll dive into an implementation strategy for for Multi Tenant Data Access using Spring Boot, Spring Data, Hibernate and Liquibase, that allows us to implement the different multi tenant patterns transparently and efficiently.

### References

Below are some links to background material and further suggested reading.

[Microservice Architectures — Single Tenant or Multi-Tenant?](https://medium.com/@dale.bingham_30375/microservice-architectures-single-tenant-or-multi-tenant-97f34e807f92)

[Azure Multi-tenant SaaS database tenancy patterns](https://docs.microsoft.com/en-us/azure/azure-sql/database/saas-tenancy-app-design-patterns)

[AWS Tenant Isolation](https://aws.amazon.com/partners/saas-factory/tenant-isolation/)

[Multi-tenancy Design Patterns in SaaS Applications: A Performance Evaluation Case Study](https://www.researchgate.net/publication/338216590_Multi-tenancy_Design_Patterns_in_SaaS_Applications_A_Performance_Evaluation_Case_Study)
