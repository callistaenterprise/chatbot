---
layout: details-blog
published: true
categories: blogg teknik
heading: Changes to .attr() in JQuery 1.6.x
authors:
  - christianhilmersson
tags: jquery javascript ria web
topstory: true
comments: true
---

This is somewhat old news by now but during this summer I ran into some problems while trying to upgrade a big Javascript code base from JQuery 1.4 to 1.6. It seems that the step to JQuery 1.6 has been cumbersome not only for me but for a lot of JQuery users out there so I would try to explain the (IMHO) biggest pitfall with this migration in my way as well.

-[readmore]-

In JQuery 1.6 there is a new function named `.prop()` to access DOM properties and alongside with that the existing `.attr()` function was changed to handle only attributes.

Previously you have been able to use the `.attr()` to change both attributes and properties which the JQuery team intended to change in 1.6.

To simplify you could say that the difference between an attribute  and a DOM property is that attributes are more or less the tag's/element's attributes that are stated in  the HTML document while properties are the same values/properties but on the DOM objects, that are the browsers internal representation of the page elements,  produced by parsing the HTML. This, more or less, means that  attributes are not changed after the page is loaded but properties are updated as the user interacts with the page and for example checks a  checkbox but there are also other small differences.

The JQuery team describes it in this way on their blog:

> Generally, DOM attributes represent the state of DOM information as retrieved from the document, such as the `value` attribute in the markup `<input type="text" value="abc">`. DOM properties represent the dynamic state of the document; for  example  if the user clicks in the input element above and types `def` the `.prop("value")` is `abcdef` but the `.attr("value")` remains `abc`.

The JQuery team went ahead and implemented the change in 1.6, which made it necessary for JQuery developers to learn about the difference of attributes and properties, but they received a lot of complaints from the users for this. The critique forced the team to rewrite `.attr()` once again to be more backwards compatible in 1.6.1 which was released rather quickly after 1.6.0.

Unfortunately it is still not a hundred percent backwards compatible when it comes to boolean values. There is for example a difference in the value that makes a checkbox  checked by  default. The default state of an `input` tag with `type=checkbox` is   steered only by the  existence of the `checked` attribute and  not by the value of the `checked` attribute. The value  of the DOM property checked, on the other hand, is denoting  the curent state.

That is, the following tag ...

~~~ markup
<input type="checkbox" checked="checked"/>
~~~

... will make the checkbox  checked by default and the attribute value is `checked` but the DOM property `checked` will get value `true` and  not `checked`.

The other case is where we have the checkbox unchecked by default ...

~~~ markup
<input type="checkbox"/>
~~~

... then the `checked` attribute wouldn't be set at all while the `checked` property now is false.

The changes in managing boolean values are excellently described by the creator of JQuery, John Resig, here: [http://news.ycombinator.com/item?id=2513702](http://news.ycombinator.com/item?id=2513702)

All of this and the reasoning behind the changes is described in detail at John Resig's own blog [http://ejohn.org/blog/jquery-16-and-attr](http://ejohn.org/blog/jquery-16-and-attr) as well as in the JQuery blog here [http://blog.jquery.com/2011/05/12/jquery-1-6-1-released](http://blog.jquery.com/2011/05/12/jquery-1-6-1-released) and here [http://blog.jquery.com/2011/05/03/jquery-16-released](http://blog.jquery.com/2011/05/03/jquery-16-released)
