---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: 'Dynamic Multi Tenancy with Spring Boot, Hibernate and Liquibase Part 4: Implement the Schema-per-tenant pattern using Hibernate'
tags: multi tenancy spring boot data hibernate liquibase postgres database migration aspect
authors:
  - bjornbeskow
---
In the [last part](/blogg/teknik/2020/10/03/multi-tenancy-with-spring-boot-part3/), we implemented the Database-per-tenant pattern, and observed that it has limited scalability. In this part, we will tweak the solution and  implement the Schema-per-tenant pattern in much the same way.

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
[schema branch]: https://github.com/callistaenterprise/blog-multitenancy/tree/schema

[comment]: # (Images)
[neighbours]: /assets/blogg/multi-tenancy-with-spring-boot/undraw_neighbors_ciwb.png
[Schema]: /assets/blogg/multi-tenancy-with-spring-boot/SeparateSchemaMultiTenancy.png

### Blog Series Parts
- [Part 1: What is Multi Tenancy](/blogg/teknik/2020/09/19/multi-tenancy-with-spring-boot-part1/)
- [Part 2: Outlining an Implementation Strategy for Multi Tenant Data Access](/blogg/teknik/2020/09/20/multi-tenancy-with-spring-boot-part2/)
- [Part 3: Implementing the Database per Tenant pattern](/blogg/teknik/2020/10/03/multi-tenancy-with-spring-boot-part3/)
- Part 4: Implementing the Schema per Tenant pattern (this part)
- [Part 5: Implementing the Shared database with Discriminator Column pattern using Hibernate Filters](/blogg/teknik/2020/10/17/multi-tenancy-with-spring-boot-part5/)
- [Part 6: Implementing the Shared database with Discriminator Column pattern using Postgres Row Level Security](/blogg/teknik/2020/10/24/multi-tenancy-with-spring-boot-part6/)
- Part 7: Summing up (forthcoming)

A fully working, minimalistic example for this part can be found in the [Github repository] in the [schema branch].

## DataSource Management

The major scalability problem with the Database-per-tenant implementation from last week is the fact that it forces us to use a separare DataSource per tenant. A Schema-per-tenant implementation can overcome this limitation by using one single DataSource and instead decorate each connection borrowed from the pool with the correct Schema for the specific tenant.

![Schema][Schema]

So let's tweak the implementation from last episode into Schema-per-tenant! 

### Implementing CurrentTenantIdentifierResolver

The `CurrentTenantIdentifierResolver` implementation remains unchanged: 


~~~java
@Component
public class CurrentTenantIdentifierResolverImpl implements CurrentTenantIdentifierResolver {

    @Override
    public String resolveCurrentTenantIdentifier() {
        String tenantId = TenantContext.getTenantId();
        if (!StringUtils.isEmpty(tenantId)) {
            return tenantId;
        } else {
            // Allow bootstrapping the EntityManagerFactory, in which case no tenant is needed
            return "BOOTSTRAP";
        }
    }

    @Override
    public boolean validateExistingCurrentSessions() {
        return true;
    }
}
~~~

### Implementing MultiTenantConnectionProvider

We will now only need a single dataSource, we no longer have to override the Spring Boot default DataSource. We will use a 'master' schema for the *master repository* with information about each tenant and its corresponding schema.

The JPA entity to represent meta data about a Tenant will just map a tenantId to a database schema:

~~~java
@Entity
public class Tenant {

    @Id
    @Size(max = 30)
    @Column(name = "tenant_id")
    private String tenantId;

    @Size(max = 30)
    @Column(name = "schema")
    private String schema;

}
~~~

The Spring Data Repository remains unchanged:

~~~java
public interface TenantRepository extends JpaRepository<Tenant, String> {
    @Query("select t from Tenant t where t.tenantId = :tenantId")
    Optional<Tenant> findByTenantId(@Param("tenantId") String tenantId);
}
~~~

We can now simplify the implementation of the `MultiTenantConnectionProvider` interface (we keep the LoadingCache to just keep the mapping between tenantId and schema). We use the single datasource to provide the connections, but decorate them with the correct schema to use before handling the connection to Hibernate. Likewise, we remove the schema information when the connection is returned.

~~~java
@Slf4j
@Component
public class SchemaBasedMultiTenantConnectionProvider implements MultiTenantConnectionProvider {

    private final transient DataSource datasource;
    private final transient TenantRepository tenantRepository;
    private final Long maximumSize;
    private final Integer expireAfterAccess;

    private transient LoadingCache<String, String> tenantSchemas;

    @PostConstruct
    private void createCache() {
        tenantSchemas = CacheBuilder.newBuilder()
                .maximumSize(maximumSize)
                .expireAfterAccess(expireAfterAccess, TimeUnit.MINUTES)
                .build(new CacheLoader<String, String>() {
                    public String load(String key) {
                        Tenant tenant = tenantRepository.findByTenantId(key)
                                .orElseThrow(() -> new RuntimeException("No such tenant: " + key));
                        return tenant.getSchema();
                    }
                });
    }

    @Autowired
    public SchemaBasedMultiTenantConnectionProvider(
            DataSource datasource,
            TenantRepository tenantRepository,
            @Value("${multitenancy.schema-cache.maximumSize:1000}")
            Long maximumSize,
            @Value("${multitenancy.schema-cache.expireAfterAccess:10}")
            Integer expireAfterAccess) {
        this.datasource = datasource;
        this.tenantRepository = tenantRepository;
        this.maximumSize = maximumSize;
        this.expireAfterAccess = expireAfterAccess;
    }

    @Override
    public Connection getAnyConnection() throws SQLException {
        return datasource.getConnection();
    }

    @Override
    public void releaseAnyConnection(Connection connection) throws SQLException {
        connection.close();
    }

    @Override
    public Connection getConnection(String tenantIdentifier) throws SQLException {
        log.info("Get connection for tenant {}", tenantIdentifier);
        String tenantSchema;
        try {
            tenantSchema = tenantSchemas.get(tenantIdentifier);
        } catch (ExecutionException e) {
            throw new RuntimeException("No such tenant: " + tenantIdentifier);
        }
        final Connection connection = getAnyConnection();
        connection.setSchema(tenantSchema);
        return connection;
    }

    @Override
    public void releaseConnection(String tenantIdentifier, Connection connection) throws SQLException {
        log.info("Release connection for tenant {}", tenantIdentifier);
        connection.setSchema(null);
        releaseAnyConnection(connection);
    }

    @Override
    public boolean supportsAggressiveRelease() {
        return false;
    }

    @Override
    public boolean isUnwrappableAs(Class unwrapType) {
        return MultiTenantConnectionProvider.class.isAssignableFrom(unwrapType);
    }

    @Override
    public <T> T unwrap(Class<T> unwrapType) {
        if ( MultiTenantConnectionProvider.class.isAssignableFrom(unwrapType) ) {
            return (T) this;
        } else {
            throw new UnknownUnwrapTypeException( unwrapType );
        }
    }
}
~~~

### Configuring Hibernate EntityManagers

We still need to configure two entityManagers: One master entityManager to host the tenant repository, and a separate entityManager to serve the tenant-specific databases. The entityManagers need their own transaction managers as well.

The configuration for the master entityManager remains almost the same as in the previous part:

~~~java
@Configuration
@EnableJpaRepositories(
        basePackages = { "${multitenancy.master.repository.packages}" },
        entityManagerFactoryRef = "masterEntityManagerFactory",
        transactionManagerRef = "masterTransactionManager"
)
public class MasterPersistenceConfig {
    private final ConfigurableListableBeanFactory beanFactory;
    private final JpaProperties jpaProperties;
    private final String entityPackages;

    @Autowired
    public MasterPersistenceConfig(ConfigurableListableBeanFactory beanFactory,
                                   JpaProperties jpaProperties,
                                   @Value("${multitenancy.master.entityManager.packages}")
                                   String entityPackages) {
        this.beanFactory = beanFactory;
        this.jpaProperties = jpaProperties;
        this.entityPackages = entityPackages;
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean masterEntityManagerFactory(DataSource dataSource) {
        LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();

        em.setPersistenceUnitName("master-persistence-unit");
        em.setPackagesToScan(entityPackages);
        em.setDataSource(dataSource);

        JpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
        em.setJpaVendorAdapter(vendorAdapter);

        Map<String, Object> properties = new HashMap<>(this.jpaProperties.getProperties());
        properties.put(AvailableSettings.PHYSICAL_NAMING_STRATEGY, "org.springframework.boot.orm.jpa.hibernate.SpringPhysicalNamingStrategy");
        properties.put(AvailableSettings.IMPLICIT_NAMING_STRATEGY, "org.springframework.boot.orm.jpa.hibernate.SpringImplicitNamingStrategy");
        properties.put(AvailableSettings.BEAN_CONTAINER, new SpringBeanContainer(this.beanFactory));
        em.setJpaPropertyMap(properties);

        return em;
    }

    @Bean
    public JpaTransactionManager masterTransactionManager(
            @Qualifier("masterEntityManagerFactory") EntityManagerFactory emf) {
        JpaTransactionManager transactionManager = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(emf);
        return transactionManager;
    }
}
~~~

Again, this configuration is very similar to the Spring Boot auto-configuration, but since we need dual entityManagers, we still have to configure them explicitly.    

We do the same for the tenant entityManager, but this time we set the `MultiTenancyStrategy` to `SCHEMA`. We also explicitly remove any `DEFAULT_SCHEMA`configuration, since it will always be set explictly.

~~~java
@Configuration
@EnableJpaRepositories(
        basePackages = { "${multitenancy.tenant.repository.packages}" },
        entityManagerFactoryRef = "tenantEntityManagerFactory", 
        transactionManagerRef = "tenantTransactionManager"
)
public class TenantPersistenceConfig {

    private final ConfigurableListableBeanFactory beanFactory;
    private final JpaProperties jpaProperties;
    private final String entityPackages;

    @Autowired
    public TenantPersistenceConfig(
            ConfigurableListableBeanFactory beanFactory,
            JpaProperties jpaProperties,
            @Value("${multitenancy.tenant.entityManager.packages}")
                    String entityPackages) {
        this.beanFactory = beanFactory;
        this.jpaProperties = jpaProperties;
        this.entityPackages = entityPackages;
    }

    @Primary
    @Bean
    public LocalContainerEntityManagerFactoryBean tenantEntityManagerFactory(
            @Qualifier("schemaBasedMultiTenantConnectionProvider") MultiTenantConnectionProvider connectionProvider,
            @Qualifier("currentTenantIdentifierResolver") CurrentTenantIdentifierResolver tenantResolver) {
        LocalContainerEntityManagerFactoryBean emfBean = new LocalContainerEntityManagerFactoryBean();
        emfBean.setPersistenceUnitName("tenant-persistence-unit");
        emfBean.setPackagesToScan(entityPackages);

        JpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
        emfBean.setJpaVendorAdapter(vendorAdapter);

        Map<String, Object> properties = new HashMap<>(this.jpaProperties.getProperties());
        properties.put(AvailableSettings.PHYSICAL_NAMING_STRATEGY, "org.springframework.boot.orm.jpa.hibernate.SpringPhysicalNamingStrategy");
        properties.put(AvailableSettings.IMPLICIT_NAMING_STRATEGY, "org.springframework.boot.orm.jpa.hibernate.SpringImplicitNamingStrategy");
        properties.put(AvailableSettings.BEAN_CONTAINER, new SpringBeanContainer(this.beanFactory));
        properties.remove(AvailableSettings.DEFAULT_SCHEMA);
        properties.put(AvailableSettings.MULTI_TENANT, MultiTenancyStrategy.SCHEMA);
        properties.put(AvailableSettings.MULTI_TENANT_CONNECTION_PROVIDER, connectionProvider);
        properties.put(AvailableSettings.MULTI_TENANT_IDENTIFIER_RESOLVER, tenantResolver);
        emfBean.setJpaPropertyMap(properties);

        return emfBean;
    }

    @Primary
    @Bean
    public JpaTransactionManager tenantTransactionManager(
            @Qualifier("tenantEntityManagerFactory") EntityManagerFactory emf) {
        JpaTransactionManager tenantTransactionManager = new JpaTransactionManager();
        tenantTransactionManager.setEntityManagerFactory(emf);
        return tenantTransactionManager;
    }
}
~~~

As last time, since we mark the tenantEntityManagerFactory and tenantTransactionManager as `@Primary`, they will be used by default in any component that autowires a PersistentContext or EntityManager.

The externalized properties in application.yml are similar to the previous part. Most notably, we can now use the default configuration for DataSources:

~~~yaml
...
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/blog
    username: postgres
    password: secret
...
multitenancy:
  schema-cache:
    maximumSize: 100
    expireAfterAccess: 10
  master:
    repository:
      packages: se.callista.blog.service.multi_tenancy.repository
    entityManager:
      packages: se.callista.blog.service.multi_tenancy.domain
...
  tenant:
    repository:
      packages: se.callista.blog.service.repository
    entityManager:
      packages: se.callista.blog.service.domain
...
~~~

### Onboarding new Tenants

The `TenantManagementService` which we use to onboard new Tenants becomes sligthly simplified. It still uses raw SQL to create the schema. Since the SQL is potentially vendor specific (we use PostgreSQL in the example), you may need to tweek it to work with another database:

~~~java
@Slf4j
@Service
public class TenantManagementServiceImpl implements TenantManagementService {

    private final DataSource dataSource;
    private final JdbcTemplate jdbcTemplate;
    private final LiquibaseProperties liquibaseProperties;
    private final ResourceLoader resourceLoader;
    private final TenantRepository tenantRepository;

    @Autowired
    public TenantManagementServiceImpl(DataSource dataSource,
                                       JdbcTemplate jdbcTemplate,
                                       @Qualifier("tenantLiquibaseProperties")
                                       LiquibaseProperties liquibaseProperties,
                                       ResourceLoader resourceLoader,
                                       TenantRepository tenantRepository) {
        this.dataSource = dataSource;
        this.jdbcTemplate = jdbcTemplate;
        this.liquibaseProperties = liquibaseProperties;
        this.resourceLoader = resourceLoader;
        this.tenantRepository = tenantRepository;
    }

    private static final String VALID_SCHEMA_NAME_REGEXP = "[A-Za-z0-9_]*";

    @Override
    public void createTenant(String tenantId, String schema) {

        // Verify schema string to prevent SQL injection
        if (!schema.matches(VALID_SCHEMA_NAME_REGEXP)) {
            throw new TenantCreationException("Invalid schema name: " + schema);
        }

        try {
            createSchema(schema);
            runLiquibase(dataSource, schema);
        } catch (DataAccessException e) {
            throw new TenantCreationException("Error when creating schema: " + schema, e);
        } catch (LiquibaseException e) {
            throw new TenantCreationException("Error when populating schema: ", e);
        }
        Tenant tenant = Tenant.builder()
                .tenantId(tenantId)
                .schema(schema)
                .build();
        tenantRepository.save(tenant);
    }

    private void createSchema(String schema) {
        jdbcTemplate.execute((StatementCallback<Boolean>) stmt -> stmt.execute("CREATE SCHEMA " + schema));
    }

    private void runLiquibase(DataSource dataSource, String schema) throws LiquibaseException {
        SpringLiquibase liquibase = getSpringLiquibase(dataSource, schema);
        liquibase.afterPropertiesSet();
    }

    protected SpringLiquibase getSpringLiquibase(DataSource dataSource, String schema) {
        SpringLiquibase liquibase = new SpringLiquibase();
        liquibase.setResourceLoader(resourceLoader);
        liquibase.setDataSource(dataSource);
        liquibase.setDefaultSchema(schema);
        liquibase.setChangeLog(liquibaseProperties.getChangeLog());
        liquibase.setContexts(liquibaseProperties.getContexts());
...        
        return liquibase;
    }
}
~~~

The simple, administrative REST endpoint to create new tenants is almost similar:

~~~java
@Controller
@RequestMapping("/")
public class TenantsApiController {

    @Autowired
    private TenantManagementService tenantManagementService;

    @PostMapping("/tenants")
    public ResponseEntity<Void> createTenant(@RequestParam String tenantId, @RequestParam String schema) {
        this.tenantManagementService.createTenant(tenantId, schema);
        return new ResponseEntity<>(HttpStatus.OK);
    }
}
~~~

### Database Migrations

The Liquibase config also remains almost similar. We still need to run Liqubase all liquibase migrations on the Master repository as well as for all tenants.
We'll start with the master liquibase configuration:

~~~java
@Configuration
@ConditionalOnProperty(name = "multitenancy.master.liquibase.enabled", havingValue = "true", matchIfMissing = true)
public class LiquibaseConfig {

    @Bean
    @ConfigurationProperties("multitenancy.master.liquibase")
    public LiquibaseProperties masterLiquibaseProperties() {
        return new LiquibaseProperties();
    }

    @Bean
    @ConfigurationProperties("multitenancy.tenant.liquibase")
    public LiquibaseProperties tenantLiquibaseProperties() {
        return new LiquibaseProperties();
    }

    @Bean
    public SpringLiquibase liquibase(ObjectProvider<DataSource> liquibaseDataSource) {
        LiquibaseProperties liquibaseProperties = masterLiquibaseProperties();
        SpringLiquibase liquibase = new SpringLiquibase();
        liquibase.setDataSource(liquibaseDataSource.getIfAvailable());
        liquibase.setChangeLog(liquibaseProperties.getChangeLog());
        liquibase.setContexts(liquibaseProperties.getContexts());
...        
        return liquibase;
    }

}
~~~

This is again more or less identical to to the Spring Boot auto-configuration, but since we need one config for the master database and a separate config for the tenant databases, we need to configure it explicitly.

Let's continue with the tenant database migrations. Just as before, ee'll need to query the TenantRepository for all tenants, and run a migration on each of them, using the correct schema.

~~~java
@Slf4j
public class DynamicSchemaBasedMultiTenantSpringLiquibase implements InitializingBean, ResourceLoaderAware {

    @Autowired
    private TenantRepository masterTenantRepository;

    @Autowired
    private DataSource dataSource;

    @Autowired
    @Qualifier("tenantLiquibaseProperties")
    private LiquibaseProperties liquibaseProperties;

    private ResourceLoader resourceLoader;

    @Override
    public void afterPropertiesSet() throws Exception {
        log.info("Schema based multitenancy enabled");
        this.runOnAllSchemas(dataSource, masterTenantRepository.findAll());
    }

    protected void runOnAllSchemas(DataSource dataSource, Collection<Tenant> tenants) throws LiquibaseException {
        for(Tenant tenant : tenants) {
            log.info("Initializing Liquibase for tenant " + tenant.getTenantId());
            SpringLiquibase liquibase = this.getSpringLiquibase(dataSource, tenant.getSchema());
            liquibase.afterPropertiesSet();
            log.info("Liquibase ran for tenant " + tenant.getTenantId());
        }
    }

    protected SpringLiquibase getSpringLiquibase(DataSource dataSource, String schema) {
        SpringLiquibase liquibase = new SpringLiquibase();
        liquibase.setResourceLoader(getResourceLoader());
        liquibase.setDataSource(dataSource);
        liquibase.setDefaultSchema(schema);
        liquibase.setChangeLog(liquibaseProperties.getChangeLog());
        liquibase.setContexts(liquibaseProperties.getContexts());
....
        return liquibase;
    }

}
~~~

And the config:

~~~java
@Configuration
@ConditionalOnProperty(name = "multitenancy.tenant.liquibase.enabled", havingValue = "true", matchIfMissing = true)
public class TenantLiquibaseConfig {

    @Bean
    @ConfigurationProperties("multitenancy.tenant.liquibase")
    public LiquibaseProperties tenantLiquibaseProperties() {
        return new LiquibaseProperties();
    }

    @Bean
    public DynamicSchemaBasedMultiTenantSpringLiquibase tenantLiquibase() {
        return new DynamicSchemaBasedMultiTenantSpringLiquibase();
    }

}
~~~

The liquibase configuration is externalized into application.yml as before:

~~~yaml
...
multitenancy:
  master:
...
    liquibase:
      changeLog: classpath:db/changelog/db.changelog-master.yaml
  tenant:
...
    liquibase:
      changeLog: classpath:db/changelog/db.changelog-tenant.yaml
~~~

### What have we achieved?

We now have a dynamic implementation of the Schema-per-tenant Multi Tenancy pattern! Since we now use one single DataSource, we can expect the scalability to be much better in that respect.

A fully working, minimalistic example can be found in the [Github repository] in the [schema branch].

## What's next?

The Schema-per-tenant pattern provides a reasonably strong data separation between tenants. Most databases supports a large number of achemas, so we should likely have no problem in scaling this solution to thousands of tenants.

A scalability concern may however arise with the database migrations: Since we duplicate all tables for each tenant using Liquibase, running migrations for all tenants may take a substantial time. In our current implementation, we run any required migrations on application start (which is the default behavior for Liquibase with Spring Boot). This may lead to a very long startup time. Even when there are no new migrations to apply, Liquibase will still do a negotiation with the database to find that out.

Hence for a large number of tenants, we would most likely need to rethink when database migrations are carried out (for instance by applying them on beforehand, while the application is still running on the previous verions and before restarting). But that's a story of its own.

In the [next part](/blogg/teknik/2020/10/17/multi-tenancy-with-spring-boot-part5/)
, we'll instead implement the Shared database with Discriminator Column pattern, using Hibernate Filters and some AspectJ magic. Stay tuned!
