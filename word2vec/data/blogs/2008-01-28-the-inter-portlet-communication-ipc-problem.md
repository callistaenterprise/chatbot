Recently I joined my first portal project. Almost immediately we ran into the problem of inter-portlet communication (IPC). Version 1.0 of the portlet specification, JSR 168, doesn't address any type of interaction between portlets. Since this is a very common requirement, the next portlet specification, JSR 286, is (almost...) all about IPC, with major new features including:

- Event handling - portlets will be able to send and receive events.
- Public render parameters - portlets will be able to share parameters with other portlets.
- Resource serving - The ability for a portlet to serve a resource.

JSR 286 is currently in the state _Public Final Draft_, so hopefully it will soon be finalized. After that it will take some time before the portal servers start supporting it.

In the meantime almost every portal vendor offers their own implementation. The question, off course, is how to solve the problem without vendor lock-in (preferably in a way that won't require too much rewriting once JSR 286 is here...).

A common solution to the most basic IPC cases is to let one portlet store data in the PortletSession during the action phase. If the data is stored in the application scope other portlets within the same web application can read the data during the render phase. This means that the solution only works for portlets that are packaged and deployed in the same web application. In most cases this won't be a problem since we probably don't want unrelated portlets to depend on each other anyway.

The solution is perhaps not the most elegant but it does the job, with the advantage of doing it in a vendor independent way. We will probably want to minimize the use of IPC altogether but when it's absolutely necessary this solution will be sufficient. Another advantage, compared to the vendor specific implementation (in our case, IBM WebSphere Portal), is that it doesn't rely on IDE wizards that changes and updates files all over the place.

## Links

- Inter-portlet communication tip on java.net
- JSR 168
- JSR 286
