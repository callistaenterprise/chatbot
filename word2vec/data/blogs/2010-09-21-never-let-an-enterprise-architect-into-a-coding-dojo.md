---
layout: details-blog
published: true
categories: blogg teknik
heading: Never let an enterprise architect into a coding dojo
authors:
  - johaneltes
tags:
topstory: true
comments: true
---

I'm an enterprise architect. My work is to define architectures that span systems, organizations and sometimes countries. Not because architectures become better if they do. No, because business-, enterprise- and pan-european integration projects depend on an agreed abstraction (in the sense of frameworks) of IT so that focus can shift from plumbing to system-level design. I usually approach a new assignment by listening to people with long experience in designing solutions for the problem domain at hand (be it healthcare, supply chain or manufacturing). The way they think about solutions is often the key to finding the right abstractions from which I can then define a candidate reference architecture. A reference architecture that is not the tool vendors blueprint for corporate bullshit SOA ("SOA aligns business and IT" yadayada), but a reference architecture that gives structure to a very small set of significant, structural problems of the domain. It is a bit like picking the most appropriate class hierarchy for a domain model. What ever abstraction you chose, you win something and sacrifice something else. But you can't just start solving the first little problem that crosses your way and then the next and then the next when working at that scale.

Well, if you don't have access to people who have been designing solutions in the domain for a long time you may have to find ways of building that experience in a high velocity using agile principles. It will likely be extremely costly for the customer though. "Refactoring" is usually not possible at the enterprise level. What you crank out will be an obstacle for evolution of the business for half a man-age or so. Since there are so many factors that influence the outcome of an enterprise architecture, I think one shouldn't bother about it unless the possibility to harvest relevant abstractions from many, many years of domain experience is at hand.

For me, my first coding dojo turned out to mirror the same process, but at the speed of light. Three days rather than thirty years. For an enterprise architect, three days equals the speed of light. A typical feed-back cycle is 2 years. Because the problem (the kata) was at such a small scale, we thought we could compensate for the lack of domain solution experience by using agile principles. We reviewed the requirements (the kata) and started the ever ongoing test-a-little, code-a-little, refactor-a-little-cycle. During the two-hours with the fizz-buzz kata we collectively solved the problem without any up-front design at all. The result was a solution hard-wired to the explicit requirements. Without access to people who have developed and maintained solutions for the domain over decades, we were on our own and the best we could do was to iterate our way to a shallow understanding of the domain. The solution didn't carry any promise for evolution of the business, but everyone could understand it.

After a coding dojo, you should be able to repeat the solution at home, on your own. But hey - I'm an architect. After this short exposure to a new domain, I didn't need to repeat anything. I felt ready for THE abstraction! So I chose among a set of possible dimensions. My choice fell on a rule-based structure with two properties: a list for additive rules and a then a fallback-rule. With this abstraction of a fizz-buzz kata, I had a path to a reference architecture that could be used to govern a family of fizz-buzz-like game projects.

Now that I have found the abstraction that will allow business people (designers of fizz-buzz-like games) to reason about all significant variation of their domain, I need to show that there is a viable, realization of this fizz-buzz pattern/abstraction that can be re-used across all projects that target a fizz-buzz-like game.

I decided to use the dynamic Groovy language to implement a higher-order language tailored for creating fizz-buzz-like solutions.
The result? It had all the qualities of an abstraction made without access to experienced solution architects of the domain:

- The abstraction turned out to be irrelevant. There was no such thing as a fizz-buzz-"like" game
- Solutions implemented using the framework perform badly
- Solutions are so hard to maintain (since the framework does not naturally represent the problem), that no one dared to maintain it. As a result, the fizz-buzz game hasn't evolved over the past 20 years.

Oh - the code? You find it [here](http://bitbucket.org/johaneltes/katas/src/tip/fizzbuzz/fizzbuzz_groovy/) accompanied by a portable enterprise build script of a size that exceeds the code it builds.
