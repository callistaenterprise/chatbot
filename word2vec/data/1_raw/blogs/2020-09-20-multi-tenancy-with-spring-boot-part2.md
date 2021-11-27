---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: 'Dynamic Multi Tenancy with Spring Boot, Hibernate and Liquibase Part 2: Outlining an Implementation Strategy for Multi Tenant Data Access'
tags: multi tenancy spring boot data hibernate liquibase postgres database migration aspect
authors:
  - bjornbeskow
---
In this part, we will outline an implementation strategy to encapsulate a Multi Tenant Data Access mechanism as a transparent, isolated [Cross Cutting Concern] with little or no impact on the application code. We will also introduce the notion of [Database Schema Migration] and explain why it is a critical part of a Multi Tenancy mechanism.

-[readmore]-

[comment]: # (Links)
[Multi Tenancy]: https://whatis.techtarget.com/definition/multi-tenancy
[SAAS]: https://en.wikipedia.org/wiki/Software_as_a_service
[Spring Framework]: https://spring.io/projects/spring-framework
[Spring Boot]: https://spring.io/projects/spring-boot
[Spring Data]: https://spring.io/projects/spring-data
[Hibernate]: https://hibernate.org/orm/
[JPA]: https://en.wikipedia.org/wiki/Jakarta_Persistence
[experimental support for the shared-database-using-discriminator-column pattern]: https://hibernate.atlassian.net/browse/HHH-6054
[Liquibase]: https://www.liquibase.org/
[Database Schema Migration]: https://en.wikipedia.org/wiki/Schema_migration
[Flyway]: https://flywaydb.org/
[Cross Cutting Concern]: https://en.wikipedia.org/wiki/Cross-cutting_concern
[Aspect]: https://en.wikipedia.org/wiki/Aspect-oriented_software_development
[Reversibility]: https://martinfowler.com/articles/designDead.html#Reversibility
[Github repository]: https://github.com/callistaenterprise/blog-multitenancy

[comment]: # (Images)
[neighbours]: /assets/blogg/multi-tenancy-with-spring-boot/undraw_neighbors_ciwb.png
[Database Plan]: /assets/blogg/multi-tenancy-with-spring-boot/database-plan.jpg

### Blog Series Parts
- [Part 1: What is Multi Tenancy](/blogg/teknik/2020/09/19/multi-tenancy-with-spring-boot-part1/)
- Part 2: Outlining an Implementation Strategy for Multi Tenant Data Access (this part)
- [Part 3: Implementing the Database per Tenant pattern](/blogg/teknik/2020/10/03/multi-tenancy-with-spring-boot-part3/)
- [Part 4: Implementing the Schema per Tenant pattern](/blogg/teknik/2020/10/10/multi-tenancy-with-spring-boot-part4/)
- [Part 5: Implementing the Shared database with Discriminator Column pattern using Hibernate Filters](/blogg/teknik/2020/10/17/multi-tenancy-with-spring-boot-part5/)
- [Part 6: Implementing the Shared database with Discriminator Column pattern using Postgres Row Level Security](/blogg/teknik/2020/10/24/multi-tenancy-with-spring-boot-part6/)
- Part 7: Summing up (forthcoming)

## Encapsulating Multi Tenant Data Access 

Implementing database access to multi tenant data according to one of the patterns described in the previous part will require multi-tenant specific code to be developed. Depending on which pattern is chosen, the amount and characteristicts of the code will differ (where the database-per-tenant pattern will mostly affect details related to database connection management, whereas a shared-database-with-discriminator-column will mostly affect query generation).

![neighbours][neighbours]

In all cases, the code will most likely be used in all different parts of an application that access data. Hence the multi tenancy logic clearly constitutes a [Cross Cutting Concern], which can be tricky to cleanly decompose without *scattering* or *tangling* code as a result. Hence the multi tenancy pattern is best implemented using some sort of architectural capability or [Aspect], so that most parts of the application logic can be unaffected and totally unaware of the multi tenancy support. This is important to keep the technical complexity out of the application logic (allowing the developers to focus on the business complexities instead). It is also an important prerequisite for adopting an agile, evolutionary approach to multi tenancy, providing the necessary but tricky [Reversibility] of architechtural decisions that may allow us to start simple and evolve into more complex patterns in the future, if necessary.

### Object-relational Mappers, Spring Data and Spring Boot

An Object-relational mapper such as [Hibernate] or more generally [JPA] already provides an isolated, modular mechanism for general relational database access that hides many technical, low-level details. The [Spring Data] further raises the abstraction level, expanding it into non-relational databases such as MongoDB as well. At the heart of JPA, an aspect-oriented mechanism is used to inject a suitable implementation of the `EntityManager` interface into application code, with all the details about the underlying database connection kept fully separated in configuration. The [Spring Framework] provides excellent support for working with externalized configuration, wheres [Spring Boot] removes the need for explicit configuration by applying default configuration based on common conventions. The implementation strategy that we will define in this blog series will hence be to leverage the mechanisms of Spring Data and Spring Boot, but add the Multi Tenancy dimension. Our goal is to encapsulate the required code an configuration needed for the different Multi Tenancy patterns in such a way that they can be plugged in seamlessly.

## Database Migrations

Before diving into outlining the implementation strategy, let us introduce an important supporting mechanism: Database Migrations.

Database Schema Migrations refers to the management of incremental, reversible changes and version control to relational database schemas.
A schema migration is performed on a database whenever it is necessary to update or revert that database's schema to some newer or older version.
While migrations can be applied manually, in order to support agility in both development and operations, the migrations are typically performed programmatically by using a schema migration tool, such as [Liquibase] or [Flyway]. When invoked with a specified desired schema version, the tool automates the successive application or reversal of an appropriate sequence of schema changes until it is brought to the desired state.

!["database plan" by tec_estromberg is licensed with CC BY 2.0.][Database Plan]

Since both the Database-per-tenant and Schema-per-tenant patterns means all database tables are duplicated across tenants, a solid mechanism for automating Database Migrations will be critical. Hence we will have to include the setup and configuration of Liquibase in our implementation strategy from the start.

## Outlining the Implementation Strategy

Time to start outlining the implementation strategy for encapsulating Multi Tenant Data Access. We'll start with the very basics, which is common to the different patterns: A mechanism for resolving the Current Tenant for each request, and make it available whenever needed.

A fully working, minimalistic example for this preliminary work as well as the forthcoming parts can be found in our [Github repository].

### Resolving the Current Tenant

So let's start with resolving the tenant id to use for a request. The tenant id needs to be captured from some information associated with the current request (such as the requestor's domain name, an explicit http header etc) and be passed along to whoever needs it downstream. The idiomatic way to achieve this in Spring is to use a Web Interceptor to capture the information, and a ThreadLocal variable to invisibly pass it along to whoever needs it. Let's define a TenantContext class, to pass the tenant id along:

~~~java
package se.callista.blog.service.multi_tenancy.util;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public final class TenantContext {

    private TenantContext() {}

    private static InheritableThreadLocal<String> currentTenant = new InheritableThreadLocal<>();

    public static void setTenantId(String tenantId) {
        log.debug("Setting tenantId to " + tenantId);
        currentTenant.set(tenantId);
    }

    public static String getTenantId() {
        return currentTenant.get();
    }

    public static void clear(){
        currentTenant.remove();
    }
}
~~~

The exact mechanism for how to determine the Current Tenant will likely differ from case to case. Frequent options are to use an explicit http header, or to use a part of the domain's name to deternite the tenant id.

So let's continue and add an interceptor that capture the tenant id either from an http header `X-TENANT_ID` or from the sub-domain part of the request's server name:

~~~java
@Component
public class TenantInterceptor implements WebRequestInterceptor {

    @Override
    public void preHandle(WebRequest request) throws Exception {
        String tenantId = null;
        if (request.getHeader("X-TENANT-ID") != null) {
            tenantId = request.getHeader("X-TENANT-ID");
        } else {
            tenantId = ((ServletWebRequest)request).getRequest().getServerName().split("\\.")[0];
        }
        TenantContext.setTenantId(tenantId);
    }

    @Override
    public void postHandle(WebRequest request, ModelMap model) throws Exception {
        TenantContext.clear();
    }

    @Override
    public void afterCompletion(WebRequest request, Exception ex) throws Exception {
    }

}
~~~

Finally we add the configuration required for the interceptor:

~~~java
@Configuration
public class WebConfiguration implements WebMvcConfigurer {

    private final TenantInterceptor tenantInterceptor;

    @Autowired
    public WebConfiguration(TenantInterceptor tenantInterceptor) {
        this.tenantInterceptor = tenantInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addWebRequestInterceptor(tenantInterceptor);
    }

}
~~~

We now have a transparent mechanism for capturing and communicating the Current Tenant to a downstream component.

### Current Tenant in Asynchronous methods

The ThreadLocal mechanism only works out of the box for synchronous flows. If using asynchronous executions, we must also be able to pass along the Current Tenant to the asynchronous execution context. In Spring, asynchronous execution is encapsulated via the `TaskExecutor` abstraction. The `TackDecorator` interface provides a mechanism to attach additional information to an asynchronous execution. Let's define a `TenantAwareTaskDecorator` class, to pass the tenant id along:

~~~java
package se.callista.blog.service.multi_tenancy.async;

import org.springframework.core.task.TaskDecorator;
import org.springframework.lang.NonNull;
import se.callista.blog.service.multi_tenancy.util.TenantContext;

public class TenantAwareTaskDecorator implements TaskDecorator {

    @Override
    @NonNull
    public Runnable decorate(@NonNull Runnable runnable) {
        String tenantId = TenantContext.getTenantId();
        return () -> {
            try {
                TenantContext.setTenantId(tenantId);
                runnable.run();
            } finally {
                TenantContext.setTenantId(null);
            }
        };
    }
}
~~~

And the corresponding configuration to enable it:

~~~java
package se.callista.blog.service.multi_tenancy.async;

import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.AsyncConfigurerSupport;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

@Configuration
public class AsyncConfig extends AsyncConfigurerSupport {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();

        executor.setCorePoolSize(7);
        executor.setMaxPoolSize(42);
        executor.setQueueCapacity(11);
        executor.setThreadNamePrefix("TenantAwareTaskExecutor-");
        executor.setTaskDecorator(new TenantAwareTaskDecorator());
        executor.initialize();

        return executor;
    }

}
~~~

## What's next?

We have taken the first preliminary steps in implementing an encapsuled mechanism for Dynamic Multi Tenant Data Access using Spring Boot. In the [next part](/blogg/teknik/2020/10/03/multi-tenancy-with-spring-boot-part3/), we'll implement the Database-per-tenant pattern using Hibernate, with Database Migrations using Liquibase and support for dynamically adding new tenants.

