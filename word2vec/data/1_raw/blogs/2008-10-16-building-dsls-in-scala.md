---
layout: details-blog
published: true
categories: blogg teknik
heading: Building DSLs in Scala
authors:
  - parwenaker
tags: dynamiclanguages
topstory: true
comments: true
---

Imagine that you could write code like this:

~~~ scala
create an Order where ( Id is 1, Number is 2 ) named "order_1"
~~~

This is a simple DSL that lets you create an order with specific attributes. Quite obvious isn't it? This does not really look like something from a programming language, but it is actually valid Scala code. Let me show you how that can be.

Let's start with the first part (create an Order). Scala allows you to skip the dot notation when calling a method, taking only one parameter, on an object. Instead of writing `object.say("hello")` you can write `object say "hello"`. This makes the first part of our DSL simple to express. We create an object called 'create', gives it a method called 'an' that takes an object 'Order'. Scala let's you create singleton objects directly without requiring a class for them:

~~~ scala
object create {
  def an(o: DO) = o match {
    case Order => ...
    case _     => throw new IllegalDSLException
  }
}
~~~

What is then that DO stuff? DO is a class (short for Domain Object, sorry) and the Order object is an instance of that class. The declaration of that little class hierarchy looks like this:

~~~ scala
abstract case class DO()
  case object Order extends DO
~~~

Don't bother so much about the match/case stuff. It lets you do pattern matching on the objects and classes. Pattern matching is like if/else statements on steroids. In the `an` method above we match on the parameter `o` and if it is an `Order`, what is substituted by the ... is executed. If it is not an `IllegalDSLException` is thrown.

We now have two singleton objects, one named `create` and the other named `Order`. The `Order` object is of type `DO` and the `an` method on the `create` object takes any `DO` type as parameter. If we send it an `Order` object it will match on the first case clause and whatever  goes after the `=>` in the case clause gets executed. Let's define what should go there then.

We begin by creating a class and give that class a method called `where`. The `where` method should take some list of arguments of some type (the `Id is 1` etc stuff). Since Scala has support for varargs we use that instead of a list. The `where` method taking a varargs parameter of type `Op` (more on that type later on) on our new class `OrderDSL` looks like this. We wait a little with the definition of what the method is actually supposed to do.

~~~ scala
class OrderDSL { def where (op: Op*) = ...}
~~~

The asterisk after the type in the method declaration turns it into a varargs.

Ok, so we have an `OrderDSL` class that has a where method and the where method takes a number of `Op` parameters. The pattern match in the create object's `an` method above should return an instance of this type. The declaration of the `create` object is now complete and will be:

~~~ scala
object create {
  def an(o: DO) = o match {
    case Order => new OrderDSL()
    case _     => throw new IllegalDSLException
  }
}
~~~

What is then the `Op` parameter? Let's define a class hierarchy like this:

~~~ scala
abstract case class Op()
  case class IdOp(i: Int) extends Op
  case class NumberOp(i: Int) extends Op
~~~

An `Op` is either an `IdOp` or an `NumberOp`. Sounds close to what we are after, but we are not really there yet. We have to get from `Id` is 1, `Number` is 2 to the `IdOp` and `NumberOp` objects. That turns out to be simple and if you have followed along you know how to do it. Define objects `Id` and `Number` and give them `is` methods that returns the type of objects you want. In this case it is instances of `IdOp` and `NumberOp`.

~~~ scala
object Id { def is (i : Int) = IdOp(i) }
object Number { def is (i : Int) = NumberOp(i) }
~~~

A little strange notation maybe, but case classes come with companion objects (among other things) that allows creation of the object without the `new` keyword. When we now call:

~~~ scala
Id is 1
~~~

we get an `IdOp` object that encapsulate the number 1 in the `i` property.

We still have not defined the supposed return value from the `where` method on `OrderDSL`. I guess that we should return something that is some kind of order object. Suppose that we have an order class defined like an ordinary Java bean class. In Scala we can import it under a new name, so that we do not get a name conflict. Remember we already have an Order object.

~~~ scala
import com.callistaenterprise.model.{Order => MyOrder}
~~~

For now on `MyOrder` is just an alias for the `Order` class and that is an ordinary Java object written in the Java language.

Now we need to be able to create `MyOrder` objects somehow. It would be nice if we just could write `new MyOrder()`, but remember the `IdOp` and `NumberOp` classes. They had companion objects that could be used as factories for creating them. Let's do something similar for the `MyOrder` class. Let's create a `MyOrder` object that creates instances of the `MyOrder` class (that still just is an alias for our good old Java Order class).  We create a functor or function object. That is an object that can be called just like a function. It is done in Scala by creating an object with an apply method, in this case like this:

~~~ scala
object MyOrder extends DO {
  def apply(op: Op*) = {
    var id  : Int = 0
    var num : Int = 0
    op.foreach( _ match {
      case IdOp(i) => id = i
      case NumberOp(i) => num = i
    })
    new MyOrder(id,num)
  }
}
~~~

The apply method takes a varargs of `Op` and produces a `MyOrder` instance . It will iterate over the varargs using the foreach method and it will pattern match each `Op` against the actual class and extract the value it is holding. When all values have been extracted it will create the `MyOrder` instance and return it.

When we make a call using the functor the apply method is not visible. We just make the call like this.

~~~ scala
MyOrder( IdOp(1), NumberOp(2) )
~~~

The Scala compiler will look for an apply method that takes a vararg of `Op` on the `MyOrder` object and call it. Let's fill in that last ... in the OrderDSLs 'where' method to finish up that class.

~~~ scala
class OrderDSL { def where (op: Op*) = MyOrder(op:_*)}
~~~

That strange `:_*` after the op parameter ensures that the vararg is passed along to the `MyOrder` functor.

The code that we have produced so far let's us write

~~~ scala
create an Order where ( Id is 1, Number is 2 )
~~~

and get one of our domain objects (`com.callistaenterprise.model.Order`) back, filled in with `id=1` and `number=2`. But we have to put the returned object somewhere. Normally we would put it in a variable, but let's not bother our domain-expert-DSL-writers with that technicality. Let's just put it in a `HashMap` under a name. This is where the last part with the call to the `named` method comes in. But the `Order` class does not have a `named` method, so we are stuck aren't we?

Turns out we are not (surprise!). Scala allows you to do a trick that looks like you are dynamically adding new methods to an existing class. The trick is to use Scala implicit conversions. That is a really powerful feature that I guess could turn any program into a mess if it is used the wrong way. Implicit conversions allows you to instruct the compiler to convert one object to another if it is required in the context. Sounds strange? In this particular case it would mean that when the compiler sees a call to the `named` method on the `Order` class and it finds that the `Order` class does not have such a method, it will start looking for an implicit method that can convert the `Order` to an object of some other class that has a `named` method taking a String as argument.

Let's define that class, `RichMyOrder`, and the convert method, `toRichMyOrder`:

~~~ scala
class RichMyOrder(o: MyOrder) {
  def named (n: String) = orders += n -> o
}
implicit def toRichMyOrder(o: MyOrder) = new RichMyOrder(o)
~~~

This will allow the compiler to convert the `Order` object to an `RichOrder`, since it finds the convert method, `toRichMyOrder` and `RichMyOrder`has a `named` method that takes a String. When the `named` method is called, the `Order` object is put into a hash map ( orders ) under the name n. The Scala notation for putting stuff in hash maps is

~~~ scala
map += key -> value
~~~

Quite intuitive actually. Key points to the value and append (`+=`) key/value pair to the map.

Now we are finished!

Scala is a very powerful language as you can see and it let's you derive your own language from it. As you saw when we follow the pattern 'object' 'method' 'object' 'method' etc. we can define a near-English-looking-DSL. Nice isn't it? I have recently used exactly this technique for developing a simple DSL that let's you define test case scenarios for a web service client application. The bonus here is that since Scala is statically typed, the statements defined by the DSL are type safe and the compiler will help you getting them right!
