---
layout: details-blog
published: true
categories: blogg teknik
heading: My write-up on Software Craftsmanship 2010
authors:
  - johannescarlen
tags: agile softwarecraftsmanship tdd
topstory: true
comments: true
---

Yesterday I attended the [Software Craftsmanshop 2010](http://parlezuml.com/softwarecraftsmanship/) conference held at the Bletchley Park Mansion. If you don't know it already [Bletchley Park](http://www.bletchleypark.org.uk/) is claimed to be the birthplace of modern computing with machines such as the Colossus decoder as well as the Turing-Welchman Bombe machine which cracked a massive amount of enigma codes during WW2. Really cool stuff.

So what about the conference itself? Well, this was not an ordinary conference with speakers and keynotes. No this was all hands-on with 130 delegates and their computers (oh, soo many MBP's) doing some serious (!?) coding. Personally I attended these three sessions; the Refuctoring Master Class, The Refactoring Golf and the Robot tournament. This is a brief writeup of what was going on in these sessions.

It started off really great with Jason Gormans tutorial on "refuctoring" (yes you read it correctly). Jason started up showing us some good examples of mortgage driven development, the way to make code so unreadable that no one other than yourself can maintain it. The way this was illustrated was to take the hello world example and gradually refactor the code into an almost unreadable form. Then we all paired up to continue this "code scrambling" task. The next step was to switch pairs and let a new partner add some new requirement into the code, which for many in the group obviously had a hard time accomplish. I must admit that there were some circular dependencies I was particularly proud of...

After a short break it was time for a round of golf, ahum, refactoring golf I meant to say. This session was about , as in real golf, to take on a couple of "holes" and finish off with as few points as possible. A hole in this case was a code example in two states, one "before" and one "after". The task was to refactor the before-code to equal the after-code in as few steps as possible. You were getting various points on every move you'd make and the pair with the miminum score for each hole was up on display to show their moves. The task at hand was in itself quite challenging and the session showed us that it is important to know your IDE and its possibilities to help you write clean code. I can't tell if this was the real intent of the session but there were at least a couple of aha's for me in that one.

After a heavy lunch of english sandwiches and a fascinating tour of the Bletchley Park premises it was time for the last session...

It was time for war. Time to fight. Time to separate the men and women from the chickens. It was time... for the Robot tournament. Ok, hm, after that intro, obviously there were about 50 computer geeks in the room so how cool could it be, eh? Well it turned out to be pretty cool actually. To describe the battles in more detail, it was all about playing games (Rock-Paper-Scissors and Tic-Tac-Toe) where all contenders went up against each other. This was realized on a server setup by the session leader, Matt Wynne. Every contender could code their robot in whatever language they preferred as long as it could be run with a bash script on Matt's Linux machine. The robot was then "curled" to the server and every now and then a round of matches started where every robot was up against each other whereafter a score board with the results was presented. The purpose of the session was to illustrate the notion of continous delivery, starting simple so you can release early and often, not striving for perfection before relasing anything. At the end of the session Matt posed the question how many of us used unit testing to build our robots and how useful those tests were. In my opinion, starting off with a test made understanding how to solve the task in the best way much easier and also made me deliver value much faster. It was a really engaging session with lots of adrenaline...

All in all, Software Craftsmanship 2010 was a pretty great conference with lots of great and inspiring people. I am definately going home with some new experience in my portmanteau. One thing though, there are a lot of people travelling around conferences worldwide advocating the software craftsmanship way of being. Where were they this sunny day of hands-on sessions in Bletchley Park?

Thanks to @jasongorman for organizing this event!
