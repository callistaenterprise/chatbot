---
layout: details-blog
published: true
categories: blogg teknik
heading: Creating custom components in Flex
authors:
  - janvasternas
tags: ria
topstory: true
comments: true
---

A common use case in a UI is to enter some data and submit it to the server. One way to do this in flex is to define an mxml like this with a Form

_Bild saknas_

To get some validation you add validators

_Bild saknas_

By doing this the user get visual assistance when entering data in the input fields.

Errors are reported by default in a tooltip and a red frame is drawn around the input field that it is errror.

Taking the phone input field there are some thing that I would like to change

1. The validator implementation requires 10 characters to be entered and this is not possible to change
2. The validator kicks in when the user leaves a field, I want the content to be validated each time it changes
3. The error messages should be in swedish instead of english
4. I want to be able to check the state of the field, is it valid or not? to enable/disable the submit button of the form
5. Lets go a little wild and crazy and bundle the input field and validator into one reusable component.

We define a new class in ActionScript that extends the `PhoneNumberValidator`.

_Bild saknas_

The constructor changes the error messages to swedish (fixes item 3 above).

Looking at the source code of PhoneNumberValidator it seems like the length check is the last thing that is made. Assuming that the first error is the one that is displayed we can write a solution that will work with the current implemetation of `PhoneNumberValidator` but needs to be revised when that changes. If the only reported error is the wrongLength error and the size is greater than 7 charachters, we reset the results varable(fixes item 1 above).

Lets make the composite component (item 5 above), a new class that extends TextInput and contains a `SwedishPhoneNumberValidator`

Lets call it `ValidatedPhoneNumberInput`. I did that and the plan was to make a Validated....Input class for each type of content (Email, PhoneNumber or simple text). After doing that I realized that where very few differences between the three. So I decided to refactor and create an abstract base class called ValidatedTextInput containing all the common behaviour.

_Bild saknas_

The variable validator has the validator that should be used to validate the input field. It must be supplied by subclasses by implementing the getValidator() function.

The `isValid` variable is public (fixes item 4 above). It is set everytime the contant is changed.


The constructor wires the validator together with the TextInput and adds a listener to the Change Event()(fixes item 3 above)..

The listener function calls the validator and saves the result of the validation.

The implementation of `ValidatedPhoneNumberInput` is now very simple

_Bild saknas_

Now it is possible to simplify the mxml file to

_Bild saknas_

No validators specified any more.

This version also contains the enabling/disabling of the submit button depending on if the input fields are valid or not.

_Bild saknas_

My conclusion is that creating reusable components in Flex makes a lot of sense and is pretty simple to do.
