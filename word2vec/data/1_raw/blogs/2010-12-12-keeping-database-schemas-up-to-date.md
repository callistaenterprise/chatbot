---
layout: details-blog
published: true
categories: blogg teknik
heading: Keeping Database Schemas up to date
authors:
  - janvasternas
tags: opensource tools database liquibase
topstory: true
comments: true
---

How many databases/schemas does your project use ? One common setup is to have one for each staging environment (development, test, customer, education, qa, production) and one for each developer and tester in the project. Maybe you even need a set of schemas free to use for anyone at special occasions. If the application is deployed in multipel versions for different customers that will multiply the number as well. I have been in projects where 30 different database schemas have been used.

Obviously the schema definition and content has to change when the code changes. So the challenge is to keep each schema consistent with the version of the code that is run against that schema. At any time there may be any number of deployed version of the code at the different environments, and many developers may be busy working on different features requiring database changes.

So how do you manage this in an efficient way ?

## One solution
One recent project used a database script containing "CREATE TABLE" statements. Over time the script evolved to contain all sorts of statements expressing both new tables and upgrades between later versions of the schema. Every time you ran the script all sorts of errors occurred but that was considered "normal" and always ignored. The result of this approach was very costly for the project.

Sometimes panic mail urging everyone to run a supplied upgrade in there own schema were sent out. No-one could tell with certainty which version of a schema that was used in different environments, we had several bugs due to the fact that inconsistent versions of databas and code was used.  Maintaining the script was almost impossible, no-one understood how to do it and since the script always produced a lot of errors it was hard to tell if your change was correct or not. Reverting to a previos version meant you had to guess which lines in the script that was added after that version created, in practice an impossible task.

The project was in a maintenance phase meaning the database change rate was very low, I can only imagine the total chaos this approach would lead to in a busy development phase.

## A different solution
My current project uses the [liquibase](http://www.liquibase.org/) library to managed database schema management. Liquibase is an open source (Apache 2.0 Licensed), database-independent library for tracking, managing and applying database changes. We have found that it gives the project

- reproducible results
- clarity
- control
- an easy way for all project members to understand and create changes

Most common use case for us is to

- create a schema from scratch in a specific version
- upgrade a specific schema from one version to another keeping existing data

Not only do we do the normal stuff in database changes like adding tables, columns, renaming stuff, creating constraints. indexes etc we also maintain data in some tables that are considered to be part of the installation.

All changes related to upgrade to one version from the previous are kept in a separate file with the name of the version of the software making it easy to find. This is called a change set in liquibase lingo. All change sets are listed in a changelog file.

When you want to upgrade a schema you run a small scripts that promts for schema name and password and the applies the appropriate changes. It is very simple to use. After this is done 2 new tables are created in the schema by liquibase recording the changes that has been made.

A sample change set file containing only on change is found at the liquibase site:

~~~ markup
<?xml version="1.0" encoding=UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog/1.9"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog/1.9
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-1.9.xs">

  <changeSet id="1" author="b">
    <createTable tableName="department">
      <column name="id" type="int">
        <constraints primaryKey="true" nullable="false"/>
      </column>
      <column name="name" type="varchar(50)">
        <constraints nullable="false"/>
      </column>
      <column name="active" type="boolean" defaultValueBoolean="true"/>
    </createTable>
  </changeSet>
</databaseChangeLog>
~~~

This show the xml-intense way of defining changes.

The other way is replace everything within the <changesSet> tag by simple sql. If you do that you loose the possibility to apply the change to different databases with minor differences in sql syntax. Liquibase currently supports 14v different databases so if you use a mix of any of these or plan to change database within the system lifetime it might be a good idea to use the xml version.

There are a lot of features in liquibase that we have not tried out yet. You can produce a javadoc style report on what changes that has been made in a database [see sample here](http://www.liquibase.org/dbdoc/index.html).

## Summary
After we started to use liquibase the time wasted on chasing errors due to inconsistent database state has been reduced to a mimimum.  We feel we have a reliable mechanism for upgrading our different database schemas.
