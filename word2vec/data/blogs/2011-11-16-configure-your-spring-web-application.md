---
layout: details-blog
published: true
categories: blogg teknik
heading: Configure your spring web application
authors:
  - andersasplund
tags: övrigt
topstory: true
comments: true
---

This post is the first in a series of two blog posts where I will try to give some useful tips on how to make your spring applications more configurable. Too often I see application configuration files embedded somewhere deep down in the application referenced only by its classpath location.

-[readmore]-

~~~ markup
<context:property-placeholder location="classpath:config.properties" />
~~~

By injecting the configurations this way they will be packaged inside the application in and you will have to rebuild and deploy it if you need to make any changes. Considered you have environment specific configurations you will also have to build an artifact for each and every environment.

A better way to handle the configuration files is to put them outside of the application in a separate location on the server. Changing configuration using this setup will at most force you to restart your application to make Spring reload them. I normally put the configuration files in a separate folder under my home catalog, i.e. `~/.myapp/config.properties`. In the spring config file you will inject the configurations using:

~~~ markup
<context:property-placeholder
    location="file:${user.home}/.myapp/config.properties" />
~~~

`user.home` is a standard JVM system property which is resolved by Spring using the `${...}` placeholder to the home catalog of the user running the server. You can even make the configuration location configurable through an environment variable:

~~~ markup
<context:property-placeholder location="file:${MY_APP_CONFIG}" />
~~~

But what if you want to package some default configurations within you application but still give the opportunity to manipulate them without the need to rebuild and make it possible to choose your own config location? No problem use:

~~~ markup
<context:property-placeholder
    location="classpath:config.properties, file:${user.home}/config.properties, file:${MY_APP_CONFIG}" />
~~~

Spring will read and merge the configuration files in the order they appear and will override duplicated configurations. This means that you can override the default configurations by adding them in `${user.home}/config.properties` or `${MY_APP_CONFIG}`.

Ok, now I showed how to configure the property files but what if you want to configure the Spring application context? What if you want to configure the way your application is put together? Lets take an example: If an application uses JNDI to retrieve the database connection you will first need to configure your server with a database connection and a JNDI-name. Secondly you will need to create a datasource bean in you application context which is injected into your DAO:s, i.e:

The dao:

~~~ java
public class OrderDao {
  private JdbcTemplate jdbcTemplate;
  public void setDataSource(DataSource dataSource) {
    this.jdbcTemplate = new JdbcTemplate(dataSource);
  }
}
~~~

The spring config file `dao-config.xml`:

~~~ markup
<bean id="myDao" class="com.example.OrderDao">
  <property name="dataSource" ref="dataSource"/>
</bean>
~~~

Using JNDI will force you to configure the server to before you can run the application. But as a developer of you don't change the JNDI configuration on your server for every application you work on. Instead it would be great if you could create a direct connection using Spring, this would remove the need of server configuration. Here is two example showing the datasource bean configured to use JNDI in the first case and a direct connection in the second case:

JNDI - `datasource-jndi-config.xml`:

~~~ markup
<bean id="dataSource" class="org.springframework.jndi.JndiObjectFactoryBean">
  <property name="jndiName" value="${datasource.jndiName}" />
</bean>
~~~

Direct - `datasource-direct-config.xml`:

~~~ markup
<bean id="dataSource" class="org.springframework.jdbc.datasource.DriverManagerDataSource">
  <property name="driverClassName" value="${datasource.driverClassName}" />
  <property name="url" value="${datasource.url}" />
  <property name="username" value="${datasource.username}" />
  <property name="password" value="${datasource.password}" />
</bean>
~~~

In the `dao-config.xml` it is now possible choose which one of the two datasources I would like to use by importing the corresponding file.  When deploying on the dev-environment use:

~~~ markup
<import resource="datasource-direct-config.xml" />
~~~

and when deploying to production use:

~~~ markup
<import resource="datasource-jndi-config.xml" />`
~~~

It could be quite annoying having to switch like this, but luckily Spring has a solution for this. Using the `${...}` placeholder we can inject which type of datasource connector we would like to use, we could even give it a default value incase we don't inject a connector type. This is done by adding a :(colon) in the placeholder like this:

~~~ markup
<import resource="datasource-${datasource.connector:jndi}-config.xml" />`
~~~

The `${...}` placeholder picks up parameters from System properties, environment variables and the property files we injected earlier. So this mean that we Now have an application context that is externally configurable. By setting a property named `datasource.connector=direct` we could easily change the application to use a direct connection to the database instead of retrieve it from JNDI.

Great we are done? No, unfortunately the `${...}` placeholder is unable to pick up an property from a property file injected to a property-placeholder bean if it is used in an import-tag, why I will explain in the next blog post. This will limit us to set the datasource connector using either a System property (i.e. use `-Ddatasource.connector=direct` when starting you server) or an environment variable. To be really happy want to keep all configuration parameters in `config.properties` but in the way Spring works this is not possible out of the box. In my next blog post I will explain why this isn't possible and I will also show a solution to the problem.
