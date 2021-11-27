Are you one of those that think that Ant is not really the right way to do it and that the ideas behind Maven are really great, but you have never really felt comfortable using it. You might just be one of those that just think that XML is a big step for mankind in no particular direction at all or that XML is just not a very good tool for writing computer programs. Then you should check out a new build system for Java applications that lives in the Apache incubator. The build system is called Buildr and was born out of the frustration of using Maven.

Buildr is a nice DSL written in Ruby targeted at building Java applications based on Rake, the build system used for Ruby. It is a drop in replacement for Maven 2 and reuses both Mavens dependency management and file structure. If you have a Maven 2 project it is very easy to get started. Just install Ruby and Buildr (installed using gems) and go to your project directory and type 'buildr' and Buildr will create a nice buildfile to get you started with.

A Buildr project definition can be as easy as this one:


This definition will download the Axis dependencies, compile and test your source and package it nicely into a jar file.

If you get to the point where you do feel that the builtin tasks in Buildr are not enough for what you want to do you are free to extend it using Ruby and the Ruby libraries. Buildr also integrates with Ant, so if you think that you have just the right Ant task for the problem just call it from Buildr.

A nice Buildr screencast tutorial can be found here
