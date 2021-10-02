---
layout: details-blog
published: true
categories: blogg teknik
heading: Get rid of your tedious and error-prone release process
authors:
  - magnusekstrand
tags: build buildautomation tools
topstory: true
comments: true
---

It's best practice to tag each of your stable releases in your version control system for futurereference. However, it is very rare that this sort of work is free from failure. Like many tedious, error-prone tasks, it is one of those things that could do with a bit of automation.

Luckily, the **Maven Release plugin** can help you automate the whole process of upgrading your POM version number and tagging a release version in your version control system, and all of this with a single maven command. You can even automate the entire release process by running the command in a cronjob or a Continuous Integration system. Amazing!

Here is an extract from a project's top POM file, showing the version number that uniquely identifies this version.

~~~ markup
<project>
  ...
  <groupId>se.nll.mhp</groupId>
  <artifactId>mhp</artifactId>
  <packaging>pom</packaging>
  <version>1.1-SNAPSHOT</version>
  ...
</project>
~~~

The SNAPSHOT suffix means that each time I deploy this version, a new snapshot will be deployed into my local Maven repository. Anyone who wants to use the latest, bleeding-edge SNAPSHOT version can add a SNAPSHOT dependency in their project. Snapshots, by definition, tend to be fairly unstable beasts.

~~~ markup
<project>
  ...
  <dependencies>
    ...
    <dependency>
      <groupId>se.nll.mhp</groupId>
      <artifactId>mhp-bc</artifactId>
      <version>1.1-SNAPSHOT</version>
    </dependency>
    ...
  </dependencies>
  ...
</project> `
~~~

When the version 1.1 is ready, you need to:

1. update the POM file
2. commit the new POM file to version control
3. tag this version as a release
4. and then move on to work on version 1.2

The Maven Release plugin can automate much of this process. However, before the Maven Release plugin can do its work, you need to make sure you have everything it needs set up in your POM file.

First of all, you need to be working with a SNAPSHOT release. However, when you are ready to release your new version, you should **remove any references to snapshots in your dependencies**. This is because a release needs to be stable, and a build using snapshots is, by definition, not always reproducible. Maven will not accept any snapshot references and force the user to change it during the release process. If you answer is no (as below) to the question of resolving dependencies or not, Maven will fail your build.

~~~
[INFO] Checking dependencies and plugins for snapshots ...
There are still some remaining snapshot dependencies.: Do you want to resolve them now? (yes/no) no: : no
[INFO] ---------------------------------------------------------
[ERROR] BUILD FAILURE
[INFO] ---------------------------------------------------------
[INFO] Can't release project due to non released dependencies :
eu.jakubiak:jakubiak-red5-core:jar:0.9-SNAPSHOT:provided in project 'mhp-red5' (se.nll.mhp:mhp-red5:war:1.1-SNAPSHOT)
~~~

The next thing you need is another section in your POM file. Maven will tag your project and commit it to your source control system. So it needs to know the location of your source control system. You generally don’t need to specify credentials as Maven inherits those from the environment. If Maven needs credentials it will prompt you during the release process.

~~~ markup
<project>
  ...
  <scm>
    <connection>scm:svn:https://svn.forge.osor.eu/svn/mhp/code/trunk</connection>
    <developerConnection>scm:svn:https://svn.forge.osor.eu/svn/mhp/code/trunk</developerConnection>
    <url>https://svn.forge.osor.eu/svn/mhp/code/trunk</url>
  </scm>
  ...
</project>
~~~

You can find reference documentation for the `<scm>` tag [here](http://maven.apache.org/scm/scm-url-format.html).

Next, you need to configure the Release plugin itself. This mainly involves telling Maven where your release tags go, via the "tagBase" configuration element. If you are using the Subversion trunk/tags/branches convention, Maven will automatically put release tags in the "tags" directory. I prefer to use a a slight variation on the normal convention, and place releases in the "tags/releases" directory:

~~~ markup
<project>
  ...
  <plugins>
    ...
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-release-plugin</artifactId>
      <configuration>
        <tagBase>https://svn.forge.osor.eu/svn/mhp/code/tags/releases</tagBase>
      </configuration>
    </plugin>
    ...
  </plugins>
  ...
</project>
~~~

Now it's time to get down to business, and try out a (semi-)automated release. The first thing you need to do is to make sure all your latest changes have been committed to your SCM system. If there are any outstanding changes, Maven won't let you do a release. First of all, you need to prepare the release, using the "prepare" goal:

~~~
$ mvn release:prepare
~~~

This goal will ask you a series of questions to confirm:

- what version number you want to release
- what new snapshot version number you want to use
- where you want to place the release tag.

If you have set up your POM file correctly, these will have sensible defaults, and you won't have to do much thinking. If you which you can disable these questions using the "--batch-mode" command line option. But to me it's a good last healthy check walking through these questions.

If you want to know exactly what Maven will do to your POM file and your SCM ahead of time (generally a good idea), you can run the operation in the "dry-run" mode, as shown here.

~~~
$ mvn release:prepare -DdryRun=true
~~~

This useful trick simulates the SCM operations by writing them out to the console, and creates three sample POM files that you can consult:

- `pom.xml.tag`, which is the pom file that will be committed to Subversion and tagged
- `pom.xml.next`, which contains the next snapshot version number

I recommend you to do a dry-run the first time you're doing you use the Maven Release plugin. It is very useful and will learn you about the set up of your own project and sub-projects. When you're satisfied with what Maven will do, you can do it for real:

~~~
$ mvn release:clean release:prepare
~~~

Things you should know about the prepare goal:

1. The command checks for local modifications. If you have any modified files but not checked in, the command will stop and ask you to first check-in modified files.
2. Your project cannot have any SNAPSHOT dependencies in your project. It's a requirement.
3. You will be asked to specify versions for the release and the next SNAPSHOT (e.g. going from "1.1-SNAPSHOT" to "1.1"). Accept the default values if unsure.
4. Maven will run all your unit tests to make sure they work after changing the project version in `pom.xml`.
5. Commit the changes made to the POM file
6. If all tests pass, Maven will tag the source in the source control with the release version you specified in step 3 above.
7. Update the SNAPSHOT version number to a new SNAPSHOT version (e.g. going from "1.1" to "1.2-SNAPSHOT")
8. Maven collects all the information that you provide and write a local file called `release.properties`. This file lets you continue from where you left in case of errors.
9. You can undo everything you’ve done so far with `mvn release:clean` to start all over.

Indeed, the prepare goal does quite a lot. Once you're finished, you have your release version tagged in Subversion and you are working on a new SNAPSHOT version.

## Release it

So far we have only set everything up in preparation for the release. Nothing have actually been released yet. But dont worry, performing the release is easy. Just use `mvn release:perform` command:

~~~
$ mvn release:perform
~~~

This will effectively do a mvn deploy with the release we have just created. More precisely, it will use the release.properties file generated by the release:prepare goal to do the following:

- Check out the release we just tagged
- Build the application (compiling, testing and packaging)
- Deploy the release version to local and remote repositories

However, both of these steps can be made into a single line command and placed, for example, on a Hudson server.

## Single line release process

This single line command will tag source control, bump up the current pom.xml, version and push a tagged artifact (jar or war) to a remote repo.

~~~
$ mvn release:prepare release:perform -B
~~~

For example, if your current project version was 1.1.2-SNAPSHOT

1. The release version will be 1.1.2
2. The next development version will be 1.1.3-SNAPSHOT
3. The SCM tagged version will be artifactId-1_1_2

If you want to specify the versions manually, then you use the commands described earlier. A single line release command is good for productivity and great for automation. You can make a build plan on your Continuous Integration server with the above command to automatically tag the current version, bump the SNAPSHOT version and deploy to a repository of your choice.

## Publish release to remote repository

After versioning your project, Maven can deploy, if configured, your project artifact (jar or war) to a remote repository of your choice. You can do this by using scp, webdav, sftp etc. I will descripe how to set up your pom.xml for scp and sftp.

Assume you have a Maven repository and you have SSH access to the repository, then you can publish your artifacts using **scp**:

~~~ markup
<distributionManagement>
  <!--  Publish the versioned releases here -->
  <repository>
    <id>repo</id>
    <name>Callista  Enterprise Maven 2 repository</name>
    <url>scp://username@maven.callistaenterprise.se/home/maven2/html</url>
  </repository>
</distributionManagement>
~~~

When using **sftp**, the XML configuration looks like this

~~~ markup
<distributionManagement>
  <!-- Publish the versioned releases here -->
  <repository>
    <id>repo</id>
    <name>Callista Maven 2 repository</name>
    <url>sftp://maven.callistaenterprise.se/repo</url>
  </repository>
</distributionManagement>
~~~

If using either **scp** or **sftp** for publishing, and having SSH as your underlying transfer mechanism, you could setup SSH without password on the repository machine. If not, Maven will ask you to enter password each time doing these operations.

Alternatively you can specify the remote repository credentials in your `M2_HOME/settings.xml` file. On Linux/Mac OS X operating systems you should find the file here: `~/.m2/settings.xml`

Open the file and use these setting

~~~ markup
<settings>
  <servers>
    <server>
      <!-- this is the id of the repo tag specified in distributionManagement -->
      <id>repo</id>
      <username>yourusername</username>
      <password>yourpassword</password>
    </server>
  </servers>
</settings>
~~~

As an alternative of deploying your artifacts to a remote Maven repository (i.e. those spedcified in `<distributionManagement>`), you could use the following command:

~~~
$ mvn deploy -DaltDeploymentRepository=local::default::file:///tmp/foo
~~~

The command will deploy your artifacts to the directory `/tmp/foo` on your local machine. The command binds by default to the lifecycle phase: deploy.

## Summary

Releasing software is difficult. It is usually tedious and error prone, full of manual steps that need to be completed in a particular order. Worse, it happens at the end of a long period of development when all everyone on the team wants to do is get it out there, which often leads to omissions or short cuts. Finally, once a release has been made, it is usually difficult or impossible to correct mistakes other than to make another, new release.

To make the release management process smooth, consistent and free from errors, working with a good tool is vital. Maven provides a release plugin that provides the basic functions of a standard release process. If you have work with Maven before, try it out. In the end, it will save you a lot of valuable time.

## Reference

- [Official Maven Release Plugin documentation](http://maven.apache.org/plugins/maven-release-plugin/introduction.html)
