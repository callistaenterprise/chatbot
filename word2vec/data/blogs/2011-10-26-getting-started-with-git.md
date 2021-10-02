---
layout: details-blog
published: true
categories: blogg teknik
heading: Getting started with git
authors:
  - janvasternas
tags: övrigt
topstory: true
comments: true
---

Having used Subversion for a long time I wanted to learn how to use a distributed versioning system. The selling points for these products are very interesting.

For instance the possibility to separate commit from delivery seems like a nice option. If you work on something that takes a couple of days to do, you want to commit often even when only parts of the work is ready without disturbing your colleagues. You want to commit even if all tests are not green. You want to be able to experiment and throw some stuff away by going back to previous committed versions. With a DVCS (Distributed Versioning Control System) you do all of this in your local repository and only when you are finished you deliver to the project repository where other people then can use it.

-[readmore]-

Which product should you use ? Git and Mercurial seems to be the popular choices. Based on the post [Git is McGywer and Mercurial is James Bond](http://importantshock.wordpress.com/2008/08/07/git-vs-mercurial) I choose Git, although I'm not a command-line wizard.

Installation on OS-X is very easy as expected. I used <http://git-scm.com/download>. In windows it is a bit more complicated because you have to choose between 2 different setups. I choose the option without Cygwin and running bash in command windows. I wonder who has the balls to choose the third option in this question?

[![](/assets/blogg/getting-started-with-git/git-install.png)](/assets/blogg/git-install.png)

Anyway creating a repository and checking files in is very easy

~~~
$ mkdir repo
$ cd repo
$ git init
Initialized empty Git repository in /Users/jan/repo/.git/

$ touch file1
$ git add .
$ git commit -m "Added empty file1"
[master (root-commit) a08c807] Added empty file1
 0 files changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 file1
~~~

The `init` command will create the repository. The only bit of magic is the `git add` command. It will add one or many files to something called the index. Only changes added to the index will we affected by the next `git commit`.

Now you can start playing around with creating branches, make changes and merging branches. Working with branches is much less expensive than you thing and a recommended way of using git.

But having only a single repository probably is not want you want to do. Collaboration between different team members is of course the next thing to try out. In order to understand how that work I did like this.

~~~
$ cd ..
$ git clone repo clone1
Cloning into clone1...
done.

$ git clone repo clone2
Cloning into clone2...
done.
~~~

Now you have three complete repositories. You can imagine that `clone1` and `clone2` are local repositories at different users and that repo the a project common repository. I used three different command windows, one for each repo. Then it was easy to change something in `clone1`, push it to repo an pull the changes to `clone2`. Also simulating conflicts and how to resolve them is very easy since you have full control of all three repos.

~~~
$ cd clone1
$ touch file2
$ git add .
$ git commit -m "added file2"
[master bacb66b] added file2
 0 files changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 file2

$ git push
Counting objects: 3, done.
Delta compression using up to 2 threads.
Compressing object: 100% (2/2), done.
Writing objects: 100% (2/2), done.
Total 2 (delta 0), reused 0 (delta 0)
Unpacking objects: 100% (2/2), done.
To /Users/jan/repo
   a08c807..bacb66b  master -> master

$  cd ../clone2
$ ls -l
total 0
-rw-r--r--  1 jan  staff  0 Oct 26 08:07 file1

$ git pull
remote: Counting objects: 3, done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 2 (delta 0), reused 0 (delta 0)
Unpacking objects: 100% (2/2), done.
From /Users/jan/repo
   a08c807..bacb66b  master     -> origin/master
Updating a08c807..bacb66b
Fast-forward
 0 files changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 file2

$ ls -l
-rw-r--r--  1 jan  staff  0 Oct 26 08:07 file1
-rw-r--r--  1 jan  staff  0 Oct 26 08:17 file2
~~~

In conclusion getting started with Git is easy. Mastering all (or much) of the Git functionality and different distributed repository topologies will probably take much longer.

Martin Fowler makes an interesting comparison between different products

![](/assets/blogg/getting-started-with-git/vcs-plane.png)

From this you can see that Git and Mercurial are useful but more complex to learn.

When it comes to topologies I think that [Scott Chacon](http://github.com/schacon) has some nice pictures, how about this one :

![](/assets/blogg/getting-started-with-git/workflow-c.png)

## Some useful resources
* [http://help.github.com/git-cheat-sheets/](http://help.github.com/git-cheat-sheets/)
* [http://book.git-scm.com/index.html](http://book.git-scm.com/index.html)
* [http://ndpsoftware.com/git-cheatsheet.html#loc=remote_repo;](http://ndpsoftware.com/git-cheatsheet.html#loc=remote_repo;)
* [http://whygitisbetterthanx.com/#](http://whygitisbetterthanx.com/#)
* [http://martinfowler.com/bliki/VersionControlTools.html](http://martinfowler.com/bliki/VersionControlTools.html)

And .. this video is a must

<div class="ce-video">
  <iframe src="http://www.youtube.com/embed/CDeG4S-mJts?feature=oembed" frameborder="0" allowfullscreen></iframe>
</div>
