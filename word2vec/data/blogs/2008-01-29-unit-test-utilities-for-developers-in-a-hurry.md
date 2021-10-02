What do you get when you try to say "Unit Test" and "Utilities" very fast? Unitils, of course! This new Open Source project gathers most of the productivity utilities and refactorings of typical JUnit/DbUnit/EasyMock code that most projects develop for internal use, over and over again (Jan reported on some of them in his Cadec 2008 talk).

What about reflection-based assertions, to avoid the need for equals() implementations that only makes sense for unit tests:

Or DbUnit-based prepopulation of test data using annotations:

Or creating an EasyMock mock object for a dependee and inject it into the unit under test, also using annotations:

Its funny that we tend to solve those minor, small inconveniences over and over again in an ad-hoc, project-specific manner, not always realizing that exactly the same inconveniencies will bother us again in the next project. Hence even if they're minor, they are real time theives, and deserve a well thought out solution. Unitils is such a well thought out solution.
