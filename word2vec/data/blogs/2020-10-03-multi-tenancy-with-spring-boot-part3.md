---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: 'Dynamic Multi Tenancy with Spring Boot, Hibernate and Liquibase Part 3: Implement the Database-per-tenant pattern using Hibernate'
tags: multi tenancy spring boot data hibernate liquibase postgres database migration aspect
authors:
  - bjornbeskow
---
In this part, we'll implement the Database-per-tenant pattern using Hibernate out-of-the-box support for Multi Tenancy, with Database Migrations using Liquibase and support for dynamically adding new tenants.

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
[database branch]: https://github.com/callistaenterprise/blog-multitenancy/tree/database

[comment]: # (Images)
[neighbours]: /assets/blogg/multi-tenancy-with-spring-boot/undraw_neighbors_ciwb.png
[Database Plan]: /assets/blogg/multi-tenancy-with-spring-boot/database-plan.jpg

### Blog Series Parts
- [Part 1: What is Multi Tenancy](/blogg/teknik/2020/09/19/multi-tenancy-with-spring-boot-part1/)
- [Part 2: Outlining an Implementation Strategy for Multi Tenant Data Access](/blogg/teknik/2020/09/20/multi-tenancy-with-spring-boot-part2/)
- Part 3: Implementing the Database per Tenant pattern (this part)
- [Part 4: Implementing the Schema per Tenant pattern](/blogg/teknik/2020/10/10/multi-tenancy-with-spring-boot-part4/)
- [Part 5: Implementing the Shared database with Discriminator Column pattern using Hibernate Filters](/blogg/teknik/2020/10/17/multi-tenancy-with-spring-boot-part5/)
- [Part 6: Implementing the Shared database with Discriminator Column pattern using Postgres Row Level Security](/blogg/teknik/2020/10/24/multi-tenancy-with-spring-boot-part6/)
- Part 7: Summing up (forthcoming)

A fully working, minimalistic example for this part can be found in the [Github repository] in the [database branch].

## Hibernate Multi Tenancy support

[Hibernate] provides out-of-the-box support for the two first multi-tenancy patterns (database-per-tenant and schema-per-tenant), and [experimental support for the shared-database-using-discriminator-column pattern]. The built-in support is activated by configuring an Hibernate Entity Manager with the desired `MultiTenancyStrategy` and inject suitable implementations of the `CurrentTenantIdentifierResolver` and `MultiTenantConnectionProvider` interfaces.

~~~java
properties.put(AvailableSettings.MULTI_TENANT, MultiTenancyStrategy.DATABASE);
properties.put(AvailableSettings.MULTI_TENANT_IDENTIFIER_RESOLVER, tenantResolver);
properties.put(AvailableSettings.MULTI_TENANT_CONNECTION_PROVIDER, connectionProvider);
~~~

Since these properties needs to be set when the Entity Manager is created, we need to override the default EntityManger configuration provided by Spring Boot with an explicit configuration.

### Implementing CurrentTenantIdentifierResolver

The `CurrentTenantIdentifierResolver` encapsulates a strategy for resolving which tenant to use for a specific request, whereas the `MultiTenantConnectionProvider ` encapsulates a strategy for selecting an appropriate database connection for that tenant. From [the last episode](/blogg/teknik/2020/09/20/multi-tenancy-with-spring-boot-part2/),
 we already have a transparent mechanism for retrieving the Current Tenant. Let's just package that mechanism up as an Hibernate-specific implementation: 


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

The `MultiTenantConnectionProvider` responsibility is to provide tenant-aware JDBC connections.

~~~java
public interface MultiTenantConnectionProvider extends Service, Wrapped {
	/**
	 * Allows access to the database metadata of the underlying database(s) in situations where we do not have a
	 * tenant id (like startup processing, for example).
	 */
	public Connection getAnyConnection() throws SQLException;

	/**
	 * Release a connection obtained from {@link #getAnyConnection}
	 */
	public void releaseAnyConnection(Connection connection) throws SQLException;

	/**
	 * Obtains a connection for Hibernate use according to the underlying strategy of this provider.
	 *
	 * @param tenantIdentifier The identifier of the tenant for which to get a connection
	 */
	public Connection getConnection(String tenantIdentifier) throws SQLException;

	/**
	 * Release a connection from Hibernate use.
	 */
	public void releaseConnection(String tenantIdentifier, Connection connection) throws SQLException;

	/**
	 * Does this connection provider support aggressive release of JDBC
	 * connections and re-acquisition of those connections (if need be) later?
	 */
	public boolean supportsAggressiveRelease();
}
~~~

As we can see, we need a 'master' dataSource for Hibernate to query for database Metadata during startup, and separate 'tenant' dataSources for each tenant. Since we must be able to add new tenants dynamically, adding new dataSources for new tenants must be dynamic as well. The general idea is to use a *master repository* for managing information about each tenant (including database connection details as required).

Let's start by defining a master datasource:

~~~java
@Component
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

}
~~~

Next, we define a JPA entity to represent meta data about a Tenant:

~~~java
@Entity
public class Tenant {

    @Id
    @Size(max = 30)
    @Column(name = "tenant_id")
    private String tenantId;

    @Size(max = 30)
    @Column(name = "db")
    private String db;

    @Size(max = 30)
    @Column(name = "password")
    private String password;

    @Size(max = 256)
    @Column(name = "url")
    private String url;

}
~~~

A Spring Data Repository allows us to query for tenant information, given a tenantId:

~~~java
public interface TenantRepository extends JpaRepository<Tenant, String> {

    @Query("select t from Tenant t where t.tenantId = :tenantId")
    Optional<Tenant> findByTenantId(@Param("tenantId") String tenantId);
}
~~~

We surely don't want to store passwords in plain text for tenants, so let's assume a simple encryption service to at least store encrypted passwords (we'll provide a simple implementation of it further on).

~~~java
public interface EncryptionService {
    String encrypt(String strToEncrypt, String secret, String salt);
    String decrypt(String strToDecrypt, String secret, String salt);
}
~~~

We are now ready to implement the `MultiTenantConnectionProvider` interface. Since we will need a separate dataSource per tenant, we store the dataSources in a LoadingCache which creates a new dataSource for a tenant on first access and evicts and closes dataSources for tenants which hasn't been active for a while.

~~~java
@Slf4j
@Component
public class DynamicDataSourceBasedMultiTenantConnectionProvider
        extends AbstractDataSourceBasedMultiTenantConnectionProviderImpl {

    private static final String TENANT_POOL_NAME_SUFFIX = "DataSource";

    @Autowired
    private EncryptionService encryptionService;

    @Autowired
    @Qualifier("masterDataSource")
    private DataSource masterDataSource;

    @Autowired
    @Qualifier("masterDataSourceProperties")
    private DataSourceProperties dataSourceProperties;

    @Autowired
    private TenantRepository masterTenantRepository;

    @Value("${multitenancy.datasource-cache.maximumSize:100}")
    private Long maximumSize;

    @Value("${multitenancy.datasource-cache.expireAfterAccess:10}")
    private Integer expireAfterAccess;

    @Value("${encryption.secret}")
    private String secret;

    @Value("${encryption.salt}")
    private String salt;

    private LoadingCache<String, DataSource> tenantDataSources;

    @PostConstruct
    private void createCache() {
        tenantDataSources = CacheBuilder.newBuilder()
                .maximumSize(maximumSize)
                .expireAfterAccess(expireAfterAccess, TimeUnit.MINUTES)
                .removalListener((RemovalListener<String, DataSource>) removal -> {
                    HikariDataSource ds = (HikariDataSource) removal.getValue();
                    ds.close(); // tear down properly
                    log.info("Closed datasource: {}", ds.getPoolName());
                })
                .build(new CacheLoader<String, DataSource>() {
                    public DataSource load(String key) {
                        Tenant tenant = masterTenantRepository.findByTenantId(key)
                                .orElseThrow(() -> new RuntimeException("No such tenant: " + key));
                        return createAndConfigureDataSource(tenant);
                    }
                });
    }

    @Override
    protected DataSource selectAnyDataSource() {
        return masterDataSource;
    }

    @Override
    protected DataSource selectDataSource(String tenantIdentifier) {
        try {
            return tenantDataSources.get(tenantIdentifier);
        } catch (ExecutionException e) {
            throw new RuntimeException("Failed to load DataSource for tenant: " + tenantIdentifier);
        }
    }

    private DataSource createAndConfigureDataSource(Tenant tenant) {
        String decryptedPassword = encryptionService.decrypt(tenant.getPassword(), secret, salt);

        HikariDataSource ds = dataSourceProperties.initializeDataSourceBuilder().type(HikariDataSource.class).build();

        ds.setUsername(tenant.getDb());
        ds.setPassword(decryptedPassword);
        ds.setJdbcUrl(tenant.getUrl());

        ds.setPoolName(tenant.getTenantId() + TENANT_POOL_NAME_SUFFIX);

        log.info("Configured datasource: {}", ds.getPoolName());
        return ds;
    }

}
~~~

### Configuring Hibernate EntityManagers

We now need to configure two entityManagers: One master entityManager to provide meta data for the tables and to host the tenant repository, and a separate entityManager to serve the tenant-specific databases. The entityManagers need their own transaction managers as well.

We start with the master entityManager:

~~~java
@Configuration
@EnableJpaRepositories(
        basePackages = { "${multitenancy.master.repository.packages}" },
        entityManagerFactoryRef = "masterEntityManagerFactory",
        transactionManagerRef = "masterTransactionManager"
)
@EnableConfigurationProperties({DataSourceProperties.class, JpaProperties.class})
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
    public LocalContainerEntityManagerFactoryBean masterEntityManagerFactory(
            @Qualifier("masterDataSource") DataSource dataSource) {
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

This configuration is very similar to the Spring Boot auto-configuration. Since we need dual entityManagers, we still have to configure it explicitly.    

We do the same for the tenant entityManager, but this time we configure the Hibernate multi-tenancy properties:

~~~java
@Configuration
@EnableJpaRepositories(
        basePackages = { "${multitenancy.tenant.repository.packages}" },
        entityManagerFactoryRef = "tenantEntityManagerFactory", 
        transactionManagerRef = "tenantTransactionManager"
)
@EnableConfigurationProperties(JpaProperties.class)
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
            @Qualifier("dynamicDataSourceBasedMultiTenantConnectionProvider") MultiTenantConnectionProvider connectionProvider,
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
        properties.put(AvailableSettings.MULTI_TENANT, MultiTenancyStrategy.DATABASE);
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

Since we mark the tenantEntityManagerFactory and tenantTransactionManager as `@Primary`, they will be used by default in any component that autowires a PersistentContext or EntityManager.

We have externalized most of the configuration into properties, which we define in application.yml:

~~~yaml
...
multitenancy:   
  datasource-cache:
    maximumSize: 100
    expireAfterAccess: 1
  master:
    repository:
      packages: se.callista.blog.service.multi_tenancy.repository
    entityManager:
      packages: se.callista.blog.service.multi_tenancy.domain
    datasource:
      url: jdbc:postgresql://localhost:5432/blog
      username: postgres
      password: secret
...
  tenant:
    repository:
      packages: se.callista.blog.service.repository
    entityManager:
      packages: se.callista.blog.service.domain
    datasource:
      url-prefix: jdbc:postgresql://localhost:5432/
      hikari:
        maximumPoolSize: 2
        minimumIdle: 0
        idleTimeout: 30000
...
encryption:
  secret: verySecret
  salt: jozo
...
~~~

### Onboarding new Tenants

Next step is to create a mechanism to onboard new Tenants, by creating the Database and User to use for the new Tenant. We do this using raw SQL which is database vendor specific, since there is no standardized way to do this. The example below contains SQL for PostgreSQL, you may need to tweek it to work with another database:

~~~java
        jdbcTemplate.execute((StatementCallback<Boolean>) stmt ->
            stmt.execute("CREATE DATABASE " + db));
        jdbcTemplate.execute((StatementCallback<Boolean>) stmt ->
            stmt.execute("CREATE USER " + db + " WITH ENCRYPTED PASSWORD '" + password + "'"));
        jdbcTemplate.execute((StatementCallback<Boolean>) stmt ->
            stmt.execute("GRANT ALL PRIVILEGES ON DATABASE " + db + " TO " + db));
~~~

This will create a new Database and Database User with the same name as the TenantId. We will also need to create the database tables for the newly created tenant, using a Liquibase migration.

~~~java
    try (Connection connection = DriverManager.getConnection(url, db, password)) {
        DataSource tenantDataSource = new SingleConnectionDataSource(connection, false);
        SpringLiquibase liquibase = new SpringLiquibase();
        liquibase.setResourceLoader(resourceLoader);
        liquibase.setDataSource(dataSource);
        liquibase.setChangeLog(liquibaseChangeLog);
        liquibase.setContexts(liquibaseContexts);
...
        liquibase.afterPropertiesSet();
    } catch (SQLException | LiquibaseException e) {
        throw new TenantCreationException("Error when populating db: ", e);
    }
~~~

We'll wrap this up in a `TenantManagementService`:

~~~java
@Service
@EnableConfigurationProperties(LiquibaseProperties.class)
public class TenantManagementServiceImpl implements TenantManagementService {

    private final EncryptionService encryptionService;
    private final DataSource dataSource;
    private final JdbcTemplate jdbcTemplate;
    private final LiquibaseProperties liquibaseProperties;
    private final ResourceLoader resourceLoader;
    private final TenantRepository tenantRepository;

    private final String urlPrefix;
    private final String secret;
    private final String salt;

    @Autowired
    public TenantManagementServiceImpl(EncryptionService encryptionService,
                                       DataSource dataSource,
                                       JdbcTemplate jdbcTemplate,
                                       @Qualifier("tenantLiquibaseProperties")
                                       LiquibaseProperties liquibaseProperties,
                                       ResourceLoader resourceLoader,
                                       TenantRepository tenantRepository,
                                       @Value("${multitenancy.tenant.datasource.url-prefix}")
                                       String urlPrefix,
                                       @Value("${encryption.secret}")
                                       String secret,
                                       @Value("${encryption.salt}")
                                       String salt
    ) {
        this.encryptionService = encryptionService;
        this.dataSource = dataSource;
        this.jdbcTemplate = jdbcTemplate;
        this.liquibaseProperties = liquibaseProperties;
        this.resourceLoader = resourceLoader;
        this.tenantRepository = tenantRepository;
        this.urlPrefix = urlPrefix;
        this.secret = secret;
        this.salt = salt;
    }

    private static final String VALID_DATABASE_NAME_REGEXP = "[A-Za-z0-9_]*";

    @Override
    public void createTenant(String tenantId, String db, String password) {

        // Verify db string to prevent SQL injection
        if (!db.matches(VALID_DATABASE_NAME_REGEXP)) {
            throw new TenantCreationException("Invalid db name: " + db);
        }

        String url = urlPrefix+db;
        String encryptedPassword = encryptionService.encrypt(password, secret, salt);
        try {
            createDatabase(db, password);
        } catch (DataAccessException e) {
              throw new TenantCreationException("Error when creating db: " + db, e);
        }
        try (Connection connection = DriverManager.getConnection(url, db, password)) {
            DataSource tenantDataSource = new SingleConnectionDataSource(connection, false);
            runLiquibase(tenantDataSource);
        } catch (SQLException | LiquibaseException e) {
            throw new TenantCreationException("Error when populating db: ", e);
        }
        Tenant tenant = Tenant.builder()
                .tenantId(tenantId)
                .db(db)
                .url(url)
                .password(encryptedPassword)
                .build();
        tenantRepository.save(tenant);
    }

    private void createDatabase(String db, String password) {
        jdbcTemplate.execute((StatementCallback<Boolean>) stmt ->
            stmt.execute("CREATE DATABASE " + db));
        jdbcTemplate.execute((StatementCallback<Boolean>) stmt ->
            stmt.execute("CREATE USER " + db + " WITH ENCRYPTED PASSWORD '" + password + "'"));
        jdbcTemplate.execute((StatementCallback<Boolean>) stmt ->
            stmt.execute("GRANT ALL PRIVILEGES ON DATABASE " + db + " TO " + db));
    }

    private void runLiquibase(DataSource dataSource) throws LiquibaseException {
        SpringLiquibase liquibase = getSpringLiquibase(dataSource);
        liquibase.afterPropertiesSet();
    }

    protected SpringLiquibase getSpringLiquibase(DataSource dataSource) {
        SpringLiquibase liquibase = new SpringLiquibase();
        liquibase.setResourceLoader(resourceLoader);
        liquibase.setDataSource(dataSource);
        liquibase.setChangeLog(liquibaseProperties.getChangeLog());
        liquibase.setContexts(liquibaseProperties.getContexts());
...
        return liquibase;
    }
}
~~~

The process for onboarding new tenants will likely differ from case to case. Since there is an upper limit on the scalability when using a database per tenant, the number of tenants must be reasonably small. Hence there is most likely some administrative procedure in place before onboarding a new tenant. Let's for simplicity add a simple, administrative REST endpoint to create new tenants.

~~~java
@Controller
@RequestMapping("/")
public class TenantsApiController {

    @Autowired
    private TenantManagementService tenantManagementService;

    @PostMapping("/tenants")
    public ResponseEntity<Void> createTenant(@RequestParam String tenantId, @RequestParam String db, @RequestParam String password) {
        tenantManagementService.createTenant(tenantId, db, password);
        return new ResponseEntity<>(HttpStatus.OK);
    }
}
~~~

Let's also for completeness add a simplistic encryption implementation, to encrypt the tenant passwords.

~~~java
@Slf4j
@Service
public class EncryptionServiceImpl implements EncryptionService {

    public static final String HASH_ALGORITHM = "PBKDF2WithHmacSHA256";
    public static final String CIPHER = "AES/CBC/PKCS5Padding";
    public static final String KEY_ALGORITHM = "AES";
    public static final int ITERATION_COUNT = 65536;
    public static final int KEY_LENGTH = 256;

    @Override
    public String encrypt(String strToEncrypt, String secret, String salt) {
        try
        {
            byte[] iv = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
            IvParameterSpec ivspec = new IvParameterSpec(iv);

            SecretKeyFactory factory = SecretKeyFactory.getInstance(HASH_ALGORITHM);
            KeySpec spec = new PBEKeySpec(secret.toCharArray(), salt.getBytes(), ITERATION_COUNT, KEY_LENGTH);
            SecretKey tmp = factory.generateSecret(spec);
            SecretKeySpec secretKey = new SecretKeySpec(tmp.getEncoded(), KEY_ALGORITHM);

            Cipher cipher = Cipher.getInstance(CIPHER);
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, ivspec);
            return Base64.getEncoder().encodeToString(cipher.doFinal(strToEncrypt.getBytes("UTF-8")));
        } catch (Exception e) {
            log.error("Error while encrypting: ", e);
            return null;
        }
    }

    @Override
    public String decrypt(String strToDecrypt, String secret, String salt) {
        try
        {
            byte[] iv = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
            IvParameterSpec ivspec = new IvParameterSpec(iv);

            SecretKeyFactory factory = SecretKeyFactory.getInstance(HASH_ALGORITHM);
            KeySpec spec = new PBEKeySpec(secret.toCharArray(), salt.getBytes(), ITERATION_COUNT, KEY_LENGTH);
            SecretKey tmp = factory.generateSecret(spec);
            SecretKeySpec secretKey = new SecretKeySpec(tmp.getEncoded(), KEY_ALGORITHM);

            Cipher cipher = Cipher.getInstance(CIPHER);
            cipher.init(Cipher.DECRYPT_MODE, secretKey, ivspec);
            return new String(cipher.doFinal(Base64.getDecoder().decode(strToDecrypt)));
        } catch (Exception e) {
            log.error("Error while decrypting: ", e);
            return null;
        }
    }

}
~~~

### Database Migrations

The last piece required is a mechanism to extend Liquibase-based Database Migrations to apply the migrations not only to the Master database (where the tables are used to provide metadata to Hibernate but not store any actual data) but to each tenant's database as well. By default in Spring Boot, if liquibase is enabled, a database migration is executed on application startup, if needed. We extend this to include the tenant databases as well.

We'll start with the liquibase config for the master database:

~~~java
@Configuration
@ConditionalOnProperty(name = "multitenancy.master.liquibase.enabled", havingValue = "true", matchIfMissing = true)
@EnableConfigurationProperties(LiquibaseProperties.class)
public class LiquibaseConfig {

    @Bean
    @ConfigurationProperties("multitenancy.master.liquibase")
    public LiquibaseProperties masterLiquibaseProperties() {
        return new LiquibaseProperties();
    }

    @Bean
    public SpringLiquibase masterLiquibase(@LiquibaseDataSource ObjectProvider<DataSource> liquibaseDataSource) {
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

Let's continue with the ctenant database migrations. We'll need to query the TenantRepository for all tenants, and run a migration on each of them:

~~~java
/**
 * Based on MultiTenantSpringLiquibase, this class provides Liquibase support for
 * multi-tenancy based on a dynamic collection of DataSources.
 */
@Getter
@Setter
@Slf4j
public class DynamicDataSourceBasedMultiTenantSpringLiquibase implements InitializingBean, ResourceLoaderAware {

    @Autowired
    private EncryptionService encryptionService;

    @Autowired
    private TenantRepository tenantRepository;

    @Autowired
    @Qualifier("tenantLiquibaseProperties")
    private LiquibaseProperties liquibaseProperties;

    @Value("${encryption.secret}")
    private String secret;

    @Value("${encryption.salt}")
    private String salt;

    private ResourceLoader resourceLoader;

    @Override
    public void afterPropertiesSet() throws Exception {
        log.info("DynamicDataSources based multitenancy enabled");
        this.runOnAllTenants(tenantRepository.findAll());
    }

    protected void runOnAllTenants(Collection<Tenant> tenants) throws LiquibaseException {
        for(Tenant tenant : tenants) {
            log.info("Initializing Liquibase for tenant " + tenant.getTenantId());
            String decryptedPassword = encryptionService.decrypt(tenant.getPassword(), secret, salt);
            try (Connection connection = DriverManager.getConnection(tenant.getUrl(), tenant.getDb(), decryptedPassword)) {
                DataSource tenantDataSource = new SingleConnectionDataSource(connection, false);
                SpringLiquibase liquibase = this.getSpringLiquibase(tenantDataSource);
                liquibase.afterPropertiesSet();
            } catch (SQLException | LiquibaseException e) {
                log.error("Failed to run Liquibase for tenant " + tenant.getTenantId(), e);
            }
            log.info("Liquibase ran for tenant " + tenant.getTenantId());
        }
    }

    protected SpringLiquibase getSpringLiquibase(DataSource dataSource) {
        SpringLiquibase liquibase = new SpringLiquibase();
        liquibase.setResourceLoader(getResourceLoader());
        liquibase.setDataSource(dataSource);
        liquibase.setChangeLog(liquibaseProperties.getChangeLog());
        liquibase.setContexts(liquibaseProperties.getContexts());
....
        return liquibase;
    }

}
~~~

Finally, we just need to wire up the config:

~~~java
@Configuration
@ConditionalOnProperty(name = "multitenancy.tenant.liquibase.enabled", havingValue = "true", matchIfMissing = true)
@EnableConfigurationProperties(LiquibaseProperties.class)
public class TenantLiquibaseConfig {

    @Bean
    @ConfigurationProperties("multitenancy.tenant.liquibase")
    public LiquibaseProperties tenantLiquibaseProperties() {
        return new LiquibaseProperties();
    }

    @Bean
    @DependsOn("masterLiquibase")
    public DynamicDataSourceBasedMultiTenantSpringLiquibase tenantLiquibase() {
        return new DynamicDataSourceBasedMultiTenantSpringLiquibase();
    }

}
~~~

The liquibase configuration is externalized into application.yml:

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

We now have a dynamic implementation of the Database-per-tenant Multi Tenancy pattern!

A fully working, minimalistic example can be found in the [Github repository] in the [database branch].

## What's next?

The Database-per-tenant pattern provides strong data separation between tenants, but has an obvious upper limit on how many tenants it can cater for: Each tenant requires a separate dataSource and corresponding separate database connections, hence it won't scale beyond say maybe a hundred tenants.

In the [next part](/blogg/teknik/2020/10/10/multi-tenancy-with-spring-boot-part4/), we'll tweak the solution to implement the Schema-per-tenant pattern, still using Hibernate's out-of-the-box support.

### References

The following links have been very useful inspiration when preparing this material:

[www.bytefish.de/blog/spring_boot_multitenancy.html](https://www.bytefish.de/blog/spring_boot_multitenancy.html)

[sunitkatkar.blogspot.com/2018/05/adding-tenants-without-application.html](https://sunitkatkar.blogspot.com/2018/05/adding-tenants-without-application.html)
