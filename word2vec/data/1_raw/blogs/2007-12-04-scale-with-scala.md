There are many languages targeting the Java VM right now. The most popular seem to be the dynamic languages like. A rising star that has caught lots of attention recently is the statically type language [Scala](http://www.scala-lang.org). Scala integrates both object-oriented and functional features, compiles to Java byte code and integrates seamlessly with the Java VM and the Java class libraries. Scala does also target the .NET platform CLR.

In Scala everything is an object, even functions. This makes it possible to pass functions as arguments, assign them to variables and return them from functions. The following code declares a function addTo (not very useful I admit) that takes an integer x as an argument and returns a function that will add the number x to its argument.

You can use this function like this:

A call to add3(5) evaluates to 8

Simple numbers are of course also objects in Scala. Java has primitive types like int and long but in Scala these are objects with methods. So if you write 2 + 4, that actually means 2.+(4) in Scala. You call the method + on the first object with the argument 4. This type of infix syntax can be used for all methods that take one argument. So instead of writing

you can simply write

which is pretty much plain English and this feature makes Scala suitable for writing domain specific languages.

Scala is, as I mentioned earlier, a type safe language, but that does not mean that you have to explicitly declare the type everywhere. The Scala compiler does a good job of inferring the type of objects from the context in which they are declared and this makes the resulting code very compact. Scala also integrates fully with your Java classes. You can specify imports of java classes in your Scala code and use them easily.

Maybe the most interesting feature of Scala is that it has adopted the concurrent oriented programming style found in. The concurrent oriented programming style is based on lightweight processes that pass messages between them. The lightweight processes in Scala (Actors) are event based and does not have a one-to-one mapping to the underlying operating system threads. This enables great scalability on multi core processors. Since the trend of processor technology seems to be an increasing number of cores and constant or decreased clock speed, this is a very valuable property. The great thing with the Scala implementation of Actors is that it is not a core feature of the language, but is implemented as a library. This shows that Scala is a very expressive language.

Scala also has XML built in as a first class entity of the language. You can mix XML right into the code and it is recognized by the compiler and replaced by objects from the scala libraries.

The has lots of documentation and an Eclipse plugin is available, so go check it out. And while you are at it, check out the web framework that is written in Scala.
