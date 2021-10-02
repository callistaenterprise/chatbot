---
layout: details-blog
published: true
categories: blogg teknik
heading: Subclipse vs Subversive
authors:
  - annicasunnman
tags: tools
topstory: true
comments: true
---

Getting back from one year off demands some effort to get started on a whole new computer.

I installed Eclipse and then installed the subclipse plugin to connect to Subversion through the “Install new software” in Eclipse. No problems. My code was already checkout on disk and created as Eclipse project with maven and imported as existing project. After installation of the subclipse plugin I tried to share the projects to the repository in subversion and got my first error: JavaHL library is missing. Reading and searching on the internet I tried two solutions:

1. Installed the JavaHL library
2. Unmark the use of JavaHL and use the SVNKit, Pure Java instead

The first solution resulted in mysterious things, the .svn files was suddenly gone on disk. I then had to copy my old project on disk to save the changes I had done, check out the project from SVN perspective in Eclipse. Copy the changes into the new project and then be able to commit the changes. Got tired of this procedure.

I tried the second solution, run on SVNKit instead. Could not join the project proper, the repository just complained that the project “was already existing” in the repository and the folders are not allowed to exist when committing.

I removed all installations regarding subclipse and then installed subversive plugin instead. Restarted eclipse and voila: All projects were now connected by default when entering eclipse and I could do my changes and commit perfectly. And even restart Eclipse and still, all projects are connected!

Conclusion: I will use subversive plugin from now on. Ohh and did I mention, I am doing this on a Mac – can’t imagine that it has something to do with it… There is probably some more technical differences to consider, but this will be my choice for now.
