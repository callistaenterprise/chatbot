---
layout: details-blog
published: true
categories: blogg teknik
heading: Advanced Debugging
authors:
  - andersasplund
tags: debugging java opensource
topstory: true
comments: true
---

In a project I have been working in recently a strange problem appeared.

We had a third-party dependency provided by the application server and as a consequence the same dependency marked as provided in our maven build script. In one of our own classes we called a static method in class supplied by the third-party dependency.

~~~ java
Foo.bar()
~~~

The application compiled and run perfectly on my development environment and all the tests passed nicely so I happily deployed it to the company test server.  Clicking thru the application suddenly something went wrong and I had a nice error page on the screen. After consulting the server log my only clue was the following exception:

~~~
java.lang.NoSuchMethodError: com.example.Foo.bar()
~~~

For a while I was pretty confused since I was certain of the existence of both the class and the method on the server. And after trying to figure out what could differ between the two environments the only thing I could think of was, me running a community edition of the third-party dependency while the server was running an enterprise edition of the same dependency  (due to license regulations). Surely this couldn’t be a problem?  The different editions were still from the same code base and had the same version?

But since this was my only idea I had to dig into it, so I decided to disassemble CompanyThreadLocal on the server, using javap,  and take a look at the method signatures. The class was embedded in a jar file but this little script fixed it for me:

~~~
$ javap -classpath third-party-dep.jar -s $(jar -tf third-party-dep.jar | grep Foo.class | sed 's/.class//g')
~~~

The following output told me that the class and the method existed as expected on the server:

~~~
public com.example.Foo();
Signature: ()V
public static java.lang.Long bar();
Signature: ()Ljava/lang/Long;
~~~

Then I did the same thing on our own class but used the –verbose switch on javap instead. An excerpt of that output:

~~~
47:                      ifne                      58
50:                      invokestatic                      #15; //Method com/example/Foo.bar:()J
53:                      lconst_0
~~~

Breakthrough!! Our class was expecting return type J from Foo.bar() which indicates a primitive long. But the class signature on the server indicated that it returned the class Long (signature V). To verify I did the same disassembling on my local Foo which confirmed my suspicions that the Enterprise Edition of Foo differed from the Community Edition. So even thou they had the same version number they differed in patch level.

Case closed!
