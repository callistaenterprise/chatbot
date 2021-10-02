XMPP, aka Jabber, is making great strides into the world of instant messaging. Since Jeremie Miller released the first version in 1998, it has been the obvious alternative for those preferring open protocols over the proprietary networks pushed by ICQ, AOL, MSN and others. With big guys like Apple and Google using XMPP it began making noise in the corporate world. Now, with AOL (one of the biggest IM network provider) looking at XMPP, the road to world dominance seems clear ahead.

So what's in it for us, the application developers? One example is keeping an eye on our applications. XMPP provides two perfectly fitting concepts:

- Presence - what modules are up and running
- Messages - communicate with your application

Let's have a look at a simple example. Note this is a demo code, quality code might use things like clever things like exception handling and external configuration. But for now, this will do.

First of all, you need two Jabber/GTalk accounts. Go create them (if you don't already have a few), make sure they are buddies and get back here... back already? That was fast.

Now, let's write a simple OSGi bundle that sends its presence based on the state in its life cycle. Feel free to imagining how this would work with Spring or EJB life cycle if that's tickles you more. OSGi has what is called a BundleActivator that keeps track of when a bundle is started and stopped (that's InitializingBean and DisposableBean for all of you in Spring land). Let's create an implementation.

Choose one of many XMPP clients available in Java. One of the easier is the Smack client from Jive^H^H^H^H Ignite Realtime, also available for all your Maven needs. Let's create and connect one when our BundleActivator is created:

I did tell you this is demo-quality code, right. If this were production code you would certainly want to inject that connection into your code rather than hard coding it. Fine, now, let's show when the bundle goes active or is stopped by indicating our presence:


We're almost done. Why not get a message that tells us that the bundle has started and all is good. This is the complete code listing:

We're done with coding. An OSGi bundle requires some extra attributes in the manifest but I won't describe them in any detail here, go read any of the OSGi tutorials or the surprisingly readable specification if you want to understand them.

Now package all of that into a JAR, including the Smack JAR, and fire up your favorite OSGi implementation. You do have a a favorite one, right?

For me, that means the Apache Felix shell:

Start the bundle by running "start 4" and you should see the Jabber user getting online and get a message saying that everything is okay. Stop it with "stop 4" and you should get a message and see it go offline. Imagining having that with all your components and not having to depend on that monitoring system or wading through log files.

For all you OSGi geeks, have a go at wrapping this code into a service that all your bundles can use. That's what I do.

Seems useful? Got any ideas as to where you could use XMPP communicating with you?
