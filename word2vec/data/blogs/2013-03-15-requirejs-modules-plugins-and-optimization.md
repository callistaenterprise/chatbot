---
layout: details-blog
published: true
categories: blogg teknik
heading: RequireJS - modules, plugins and optimization
authors:
  - kristinluhr
tags: architecture javascript tools web backbone requirejs webapplications
topstory: true
comments: true
---

In my current project we are rewriting a feature-packed Struts application [^1] into a single page web app using Backbone and Bootstrap. The need for architectural patterns is becoming more and more evident as the application grows and we realize how many different ways you can use Backbone to do the same thing.

-[readmore]-

The good thing is that for me, coming from an enterprise Java and OO world, the Backbone objects feel really natural to work with. I get to write `this` and can refactor my handler code into separate methods to avoid too deep callback nesting.

Another realization is the need for a logical file organization, to store all views in one folder soon became unwieldy so we decided to group them by application functionality instead. With the amount of files increasing, the headache of load order and dependency management could have been a constant source of errors. But that is not a problem in this project and I’d like to share the solution with you.

## Require to the rescue
We are using a module loader called [RequireJS](http://requirejs.org) that solves many of our problems. It is based on the concept of modularization, so all my Backbone objects are specified as [AMD](https://github.com/amdjs/amdjs-api/wiki/AMD) modules. An AMD module is an encapsulated and reusable piece of JavaScript code that can be loaded asynchronously because it contains a declaration of all other modules that must be loaded before it can run. To define a module I simply wrap my function in a define call:

~~~ javascript
define([
  "backbone"
], function (Backbone) {
  // Create a new Backbone Model class
  var MyModel = Backbone.Model.extend({ ... });
  // In here I can create helper functions or other inner objects that
  // are only used internally finally return the reusable object, this
  // is what I'll use if I use this module elsewhere
  return MyModel;
});
~~~

Now I have a module that can be reused, e.g. to define a `Collection` that uses `MyModel`:

~~~ javascript
define([
  "backbone",
  "mymodel"
], function (Backbone, MyModel) {
  var MyList = Backbone.Collection.extends({
    model : MyModel
  });
  return MyList;
});
~~~

I prefer to think of the dependency array as "imports", but there is another benefit hidden in the define wrapper – namespaces. Inside my module I have a private namespace, and I can name my dependencies to whatever makes my code understandable without having to worry about name collisions. I don’t have to work with long namespaced variables, even though I have grouped my files in an elaborate hierarchy. This is a great way to encapsulate code and separate concerns.

The third benefit is loading, RequireJS helps me load all dependencies in the correct order. All I import in the index page is a config file, that specify where my modules are located and the module to load to startup my application. If I need to use any third party libraries that are not AMD modules, I can use a "shim" to help require interpret them as modules. If you have certain parts of an application that can be loaded later, RequireJS supports on the fly loading as well.

## Optimization
This sounds like there will be a lot of files and these days best practices dictates that we minify them and bundle them together. RequireJS also provides a tool for this, called [r.js](http://requirejs.org/docs/optimization.html). It can be run in the browser, on Node or Rhino. I tried with node and was happy to see that all it took was a simple `npm install` [^2] call to install.

~~~
$ npm install -g requirejs
$ r.js -o app.build.js
~~~

The `app.build.js` is a build file that describes where my js-files are located and where to put the minified files. All my files were minified and concatenated into one ready to deploy file. Naturally, the order of the concatenation is handled by RequireJS. Since we use a shim to define Backbone as a module and declare its dependencies, we need to use the `mainConfigFile` option, otherwise the shimmed modules are ignored and not included. This is my basic `app.build.js`:

~~~ javascript
({
    appDir: './app',
    baseUrl: './scripts',
    dir: './release',
    mainConfigFile : 'app/scripts/config.js', // same config file that is loaded in index.html
    optimize: 'uglify'
})
~~~

## Templates and plugins
Another thing that RequireJS does is provide plugins, that can be loaded in the same way as other dependencies. The most important plugin is called "text" and it allows me to move my template markup into a separate file. I can then load the template into my module and access it via a variable just like any other module. There are many other plugins, e.g i18n. Take a look at [http://requirejs.org/docs/plugins.html](http://requirejs.org/docs/plugins.html) for a list of plugins and also information on how to create your own. That could also be a good way to encapsulate some reusable logic in your application.

## Summary
I’m really happy that we chose RequireJS, it keeps saving my sanity when we switch plugins and other dependencies or refactor our code. The templates and text plugin helps in keeping the html in separate files, which is a big bonus. The code is modular and easier to maintain.

Since I can’t show you my project code, I have rewritten our [Backbone tutorial app from the 2013 Cadec](https://github.com/callista-software/spa-cadec-2013) into an app using RequireJS. The new version is in the folder solution-require. If you like to try the conversion yourself there is a chapter in the tutorial guiding you step by step, see [https://github.com/callista-software/spa-cadec-2013/wiki/Require-modules](https://github.com/callista-software/spa-cadec-2013/wiki/Require-modules).

I also used the text plugin, to illustrate how easy it is to separate the markup into files. The templates are inlined as text in the modules when running the optimizer, so the separate files is only for development.

## Links
* [http://requirejs.org](http://requirejs.org)
* [http://addyosmani.github.com/backbone-fundamentals/#modular-development](http://addyosmani.github.com/backbone-fundamentals/#modular-development)
* [http://requirejs.org/docs/whyamd.html](http://requirejs.org/docs/whyamd.html)

[^1]: Struts application: JavaEE, server-generated webapp, early 2000
[^2]: npm installs a module in Node, -g installs it globally
