---
layout: details-blog
published: true
categories: blogg teknik
heading: The programming languages of tomorrow
authors:
  - sofiajonsson
tags: dynamiclanguages
topstory: true
comments: true
---

Now that dynamic languages such as Python, Groovy and Ruby have started to become mainstream, it is time to glance at a different branch of languages for influences. I've just come home from the [QCon conference](http://qcon.infoq.com) where one of the tracks was called [Programming Languages of Tomorrow](http://jaoo.dk/london-2008/tracks/show_track.jsp?trackOID=86). All of the languages presented in the track were (more or less) functional.

## Haskell - a pure functional language

[Simon Peyton-Jones](http://research.microsoft.com/%7Esimonpj/)gave a fun and inspiring talk on [Haskell](http://www.haskell.org/), focusing mainly on the concept of purity. A pure function is one that has no side effects, meaning that each call to the function always has the same result. According to Simon, purity has a lot of advantages such as:

- Its easy to understand what each function does.
- Improved testability.
- Easier maintenance.
- Easier to optimize the algorithms.
- Parallelism - pure programs are "naturally parallel".

Unfortunately, a program which has no side effects at all does nothing useful, for example it is impossible to do I/O without side effects. Haskell, being a pure functional language, has solved the dilemma with something called [monads ](http://en.wikipedia.org/wiki/Monads_in_functional_programming). I'm not even going to try to explain what it is other than to say that it's a very controlled way to do side effects. According to Simon one of the most challenging tasks for all programming languages over the coming years will be to combine the advantages of purity with doing something useful. In this area imperative languages such as Java can benefit from glancing at functional languages such as Haskell and vice versa.

## Erlang - a concurrent language which happens to be functional

Simon was followed by Joe Armstrong, who gave an equally inspiring talk about [Erlang](http://www.erlang.org/). He described Erlang as a "concurrent language which happens to be functional", i.e. its main focus is on concurrency.

Due to a paradigm shift in how hardware and CPUs are designed (CPUs are no longer getting faster by the year, they're actually getting slower; instead multiple cores are used), a sequential program written today will actually run slower in a couple of years time. A concurrent program on the other hand will run faster as the number of cores increases. This means that languages like Java will need to improve its concurrency features, allowing for us developers to take advantage of the multiple cores. The concurrency implementation available in Java today is not at all satisfactory.

Even though both Erlang and Haskell have been around for some twenty years now, interest in them has grown a lot recently and they have also given inspiration to new functional languages.

## F# and Scala - the new kids on the block

The other two languages presented within the track was [F#](http://research.microsoft.com/fsharp/fsharp.aspx) (a functional language for the .Net platform) and [Scala ](http://www.scala-lang.org) (see Pär's blogpost about it [here](/display/CallistaCom/2007/12/04/Scale+with+Scala)), both of which are quite new languages. Scala, which is written for the JVM (it has an implementation targeting the CLR too), integrates both object-oriented and functional features and focuses on concurrency in very much the same way as Erlang.
