---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: 'Dynamic Multi Tenancy with Spring Boot, Hibernate and Liquibase Part 6: Implementing the Shared Database with Discriminator Column pattern using Postgres Row Level Security'
tags: multi tenancy spring boot data hibernate liquibase postgres database migration aspect
authors:
  - bjornbeskow
---
In the [last part](/blogg/teknik/2020/10/17/multi-tenancy-with-spring-boot-part5/), we implemented the Shared Database with Discriminator Column pattern usign Hibernate Filters. We observed that it will scale well, but the data isolation guarantee is troublesome due to shortcomings in the Hibernate Filter mechanism.

In this part, we will tweak the solution and redo the critical Filtering part using an advanced database mechanism: Row Level Security.

-[readmore]-

[comment]: # (Links)
[Multi Tenancy]: https://whatis.techtarget.com/definition/multi-tenancy
[SAAS]: https://en.wikipedia.org/wiki/Software_as_a_service
[Spring Framework]: https://spring.io/projects/spring-framework
[Spring Boot]: https://spring.io/projects/spring-boot
[Spring Data]: https://spring.io/projects/spring-data
[Hibernate]: https://hibernate.org/orm/
[JPA]: https://en.wikipedia.org/wiki/Jakarta_Persistence
[Cross Cutting Concern]: https://en.wikipedia.org/wiki/Cross-cutting_concern
[Aspect]: https://en.wikipedia.org/wiki/Aspect-oriented_software_development
[AspectJ]: https://www.eclipse.org/aspectj/
[Row Level Security]: https://www.postgresql.org/docs/9.5/ddl-rowsecurity.html
[Github repository]: https://github.com/callistaenterprise/blog-multitenancy
[shared_database_postgres_rls branch]: https://github.com/callistaenterprise/blog-multitenancy/tree/shared_database_postgres_rls

[comment]: # (Images)
[Lock]: /assets/blogg/multi-tenancy-with-spring-boot/Lock.png
[SingleDatabase]: /assets/blogg/multi-tenancy-with-spring-boot/SingleDatabaseMultiTenancy.png

### Blog Series Parts
- [Part 1: What is Multi Tenancy](/blogg/teknik/2020/09/19/multi-tenancy-with-spring-boot-part1/)
- [Part 2: Outlining an Implementation Strategy for Multi Tenant Data Access](/blogg/teknik/2020/09/20/multi-tenancy-with-spring-boot-part2/)
- [Part 3: Implementing the Database per Tenant pattern](/blogg/teknik/2020/10/03/multi-tenancy-with-spring-boot-part3/)
- [Part 4: Implementing the Schema per Tenant pattern](/blogg/teknik/2020/10/10/multi-tenancy-with-spring-boot-part4/)
- [Part 5: Implementing the Shared database with Discriminator Column pattern using Hibernate Filters](/blogg/teknik/2020/10/17/multi-tenancy-with-spring-boot-part5/)
- Part 6: Implementing the Shared database with Discriminator Column pattern using Postgres Row Level Security (this part)
- Part 7: Summing up (forthcoming)

### Data Isolation

In order to achieve proper data isolation between different tenants, we need to include an extra `where` condition on the tenantId for all data access. Doing so in application code can be troublesome and error-prone, as we saw. The burden of proof lies on us that the mechanism is properly implemented and applied. Clearly, it would be better to get that guarantee from the Database instead.

![Lock][Lock]

Modern databases like Postgres or SQLServer provides a [Row Level Security] mechanism, where access to individual rows can be declaratively and transparently restricted to specific users based on various criteria. It can thus be used to implement the data isolation between tenants.

#### Defining Row Level Policies

In Postgres, this means, for each table

1. enabling Row Level Security for the table, and
2. define a Policy for the table, referencing the `tenant_id` discriminator column.

In the Postgres documentaion examples on defining policies, `current_user` is used to define the policies. That won't work in this case, since we don't have separate database users per tenant. Instead, we can utilize a custom *session parameter* e.g. `app.tenant_id` to associate current tenant with a database session (i.e. a database connection). Setting a session parameter is done using a Postgres-specific SQL statement:

~~~sql
"SET app.tenant_id TO '" + tenantId + "'"
~~~

The session parameter can be referenced in the policy definition. Wrapped as a Liquibase changeset, it could look like this:  

~~~yaml
- changeSet:
    id: product_row_level_security
    author: bjobes
    changes:
    -  sql:
        dbms: 'postgresql'
        sql: >-
            ALTER TABLE product ENABLE ROW LEVEL SECURITY;
            DROP POLICY IF EXISTS product_tenant_isolation_policy ON product;
            CREATE POLICY product_tenant_isolation_policy ON product
                USING (tenant_id = current_setting('app.tenant_id')::VARCHAR);

~~~

#### Table Owner user and App User

Row Level Security policies are by default **not** applied for the table owner (which makes sense, since the table owner must be able to access all rows for administrative purposes, such as backups). Hence we must make sure that we use a different database user for the application to access the database (which is a best practice to do anyway). Let's add the creation of an application user to our Liquibase migration (where the username, password, schema and database name are passed in as parameters) :

~~~yaml
- changeSet:
    id: app_user
    author: bjobes
    changes:
    -  sql:
        dbms: 'postgresql'
        sql: >-
            CREATE USER ${username} WITH PASSWORD '${password}';
            GRANT CONNECT ON DATABASE ${database} TO app_user;
            ALTER DEFAULT PRIVILEGES IN SCHEMA ${schema} GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES
                ON TABLES TO ${username};
            ALTER DEFAULT PRIVILEGES IN SCHEMA ${schema} GRANT USAGE ON SEQUENCES TO ${username};
            ALTER DEFAULT PRIVILEGES IN SCHEMA ${schema} GRANT EXECUTE ON FUNCTIONS TO ${username};
~~~

#### Associate Tenant with Database Connection

With the Row Level Security policy in place, we now need to set the current tenantId on each database connection before using it, and remove the tenantId once done with the connection. Hence we need a Tenant-Aware DataSource that transparently manages the decoration of tenantId on connections:

~~~java
/**
 * Tenant-Aware Datasource that decorates Connections with
 * current tenant information.
 */
public class TenantAwareDataSource extends DelegatingDataSource {

    public TenantAwareDataSource(DataSource targetDataSource) {
        super(targetDataSource);
    }

    @Override
    public Connection getConnection() throws SQLException {
        final Connection connection = getTargetDataSource().getConnection();
        setTenantId(connection);
        return getTenantAwareConnectionProxy(connection);
    }

    @Override
    public Connection getConnection(String username, String password) throws SQLException {
        final Connection connection = getTargetDataSource().getConnection(username, password);
        setTenantId(connection);
        return getTenantAwareConnectionProxy(connection);
    }

    private void setTenantId(Connection connection) throws SQLException {
        try (Statement sql = connection.createStatement()) {
            String tenantId = TenantContext.getTenantId();
            sql.execute("SET app.tenant_id TO '" + tenantId + "'");
        }
    }

    private void clearTenantId(Connection connection) throws SQLException {
        try (Statement sql = connection.createStatement()) {
            sql.execute("RESET app.tenant_id");
        }
    }

    // Connection Proxy that intercepts close() to reset the tenant_id
    protected Connection getTenantAwareConnectionProxy(Connection connection) {
        return (Connection) Proxy.newProxyInstance(
                ConnectionProxy.class.getClassLoader(),
                new Class[] {ConnectionProxy.class},
                new TenantAwareDataSource.TenantAwareInvocationHandler(connection));
    }

    // Connection Proxy invocation handler that intercepts close() to reset the tenant_id
    private class TenantAwareInvocationHandler implements InvocationHandler {
        private final Connection target;

        public TenantAwareInvocationHandler(Connection target) {
            this.target = target;
        }

        @Nullable
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            switch (method.getName()) {
                case "equals":
                    return proxy == args[0];
                case "hashCode":
                    return System.identityHashCode(proxy);
                case "toString":
                    return "Tenant-aware proxy for target Connection [" + this.target.toString() + "]";
                case "unwrap":
                    if (((Class) args[0]).isInstance(proxy)) {
                        return proxy;
                    } else {
                        return method.invoke(target, args);
                    }
                case "isWrapperFor":
                    if (((Class) args[0]).isInstance(proxy)) {
                        return true;
                    } else {
                        return method.invoke(target, args);
                    }
                case "getTargetConnection":
                    return target;
                default:
                    if (method.getName().equals("close")) {
                        clearTenantId(target);
                    }
                    return method.invoke(target, args);
            }
        }
    }
}
~~~
 
A bit bulky, but a well proven mechanism to decorate a datasource with additional functionality.

#### Configuring the DataSources

We need to configure two DataSources: One master DataSource for Liquibase Database migrations, and one tenant-aware datasource for the application to use.

~~~java
@Configuration
public class DataSourceConfiguration {

    @Bean
    @ConfigurationProperties("multitenancy.master.datasource")
    public DataSourceProperties masterDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @LiquibaseDataSource
    @ConfigurationProperties("multitenancy.master.datasource.hikari")
    public DataSource masterDataSource() {
        HikariDataSource dataSource = masterDataSourceProperties()
                .initializeDataSourceBuilder()
                .type(HikariDataSource.class)
                .build();
        dataSource.setPoolName("masterDataSource");
        return dataSource;
    }

    @Bean
    @Primary
    @ConfigurationProperties("multitenancy.tenant.datasource")
    public DataSourceProperties tenantDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @Primary
    @ConfigurationProperties("multitenancy.tenant.datasource.hikari")
    public DataSource tenantDataSource() {
        HikariDataSource dataSource = tenantDataSourceProperties()
                .initializeDataSourceBuilder()
                .type(HikariDataSource.class)
                .build();
        dataSource.setPoolName("tenantDataSource");
        return new TenantAwareDataSource(dataSource);
    }
}
~~~

Just as before, since we mark the tenantDataSource as @Primary, it will be used by default in any component that autowires a DataSource.

#### Discriminator column and EntityListener

The EntityListener mechanism for setting the tenantId when creating new entities remains the same:

~~~java
public interface TenantAware {

    void setTenantId(String tenantId);
    
}

public class TenantListener {

    @PreUpdate
    @PreRemove
    @PrePersist
    public void setTenant(TenantAware entity) {
        final String tenantId = TenantContext.getTenantId();
        entity.setTenantId(tenantId);
    }
}

@MappedSuperclass
@Getter
@Setter
@NoArgsConstructor
@EntityListeners(TenantListener.class)
public abstract class AbstractBaseEntity implements TenantAware, Serializable {
    private static final long serialVersionUID = 1L;

    @Size(max = 30)
    @Column(name = "tenant_id")
    private String tenantId;

    public AbstractBaseEntity(String tenantId) {
        this.tenantId = tenantId;
    }

}
~~~

And just as before, all entities will need to extend `AbstractBaseEntity`:

~~~java
@Entity
public class Product extends AbstractBaseEntity {
...
}
~~~

And finally the externalized configuration in application.yml:

~~~yaml
spring:
...
  liquibase:
    changeLog: classpath:db/changelog/db.changelog-tenant.yaml
    parameters:
      database: blog
      schema: public
      username: app_user
      password: secret
multitenancy:
  master:
    datasource:
      url: jdbc:postgresql://localhost:5432/blog
      username: postgres
      password: secret
      hikari:
        maximum-pool-size: 1
  tenant:
    datasource:
      url: ${multitenancy.master.datasource.url}
      username: app_user
      password: secret
~~~

### What have we achieved?

We now have a much simplified implementation of the Shared Database with Discriminator Column pattern. The data isolation guarantee between tenants is provided by the Row Level Security mechanism in Postgres (provided we never allow an application to access the database using the database owner user). This solution should be both robust and highly scalable.

A fully working, minimalistic example can be found in the [Github repository] for this blog series, in the [shared_database_postgres_rls branch].

## What's next?

In the next and final part, we'll recapitulate the pros and cons of the different patterns, and discuss some migration strategies and practices to be able to start with one and but be prepared to migrate to another pattern if necessary.

### References

The following links have been very useful inspiration when preparing this material:

[aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/)

[www.bytefish.de/blog/spring_boot_multitenancy_using_rls.html](https://www.bytefish.de/blog/spring_boot_multitenancy_using_rls.html)