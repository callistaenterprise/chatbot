---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: 'Technical aspects of ontologies, part 1'
authors:
  - bjorngenfors
---
Many are the situations where there’s a need to organize information for subsequent use, and one way to do this is to use a controlled vocabulary. This need may arise in a limited setting, where your requirements can be managed off the cuff, or it could arise in a setting where secondary use of information is foreseen but exactly how is unknown. In these more intricate circumstances, an ontology may serve you well.
 
-[readmore]-

In this short blog series, I intend to explore the topic of ontologies, with a focus on the technical aspects of those. But to discuss this topic, we first need to settle on a terminology. To do that, we need to explore the terminology of terminology itself, and the semiotic triangle in particular.

## The semiotic triangle

As any triangle, the semiotic triangle has three vertices. These are:

- **Symbol/term**: A symbol is some item used to denote some concept. Mostly when we communicate, the symbol is a word or a set of words. This symbol we call a **term**. 
- **Concept** (sw. “begrepp”): A concept is the abstract idea of something.
- **Referent**: A referent is an actual example of a concept, and the set of all referents are the set of all actual examples of that concept.

![]({{site.baseurl}}/assets/Semiotic%20triangle1.png)

For a less theoretical explanation: an example. The symbol here is the string “tree”, which expresses the concept of a tree. The referents are actual trees.

![semiotic triangel2.png]({{site.baseurl}}/assets/semiotic triangel2.png)

## An example closer to home

Since we work with IT, I’ll add an example closer to our everyday business. Assume you and your colleagues are going on a retreat (or a “bootcamp” as we say here at Callista). To accommodate the wishes of the restaurant, dinner needs to be pre-ordered. To gather responses, your boss creates a poll on Slack. Let’s say there are three options for the main course: meat, fish and vegetarian. Let’s also say there are twelve responses, eight fish and four vegetarian.

There are three concepts, the three possible choices: “a choice of main course where the main ingredient is meat of some kind”, “a choice of main course where the main ingredient is fish of some kind” and “a choice of main course which is vegetarian”. There are three corresponding terms: “meat”, “fish” and “vegetarian” (let’s disregard that Slack numbers each option).
The referents in this case are the actual responses from you and your colleagues: 8 responses of fish, 4 responses of vegetarian, and 0 responses of meat. As you can see, it is possible that a concept has no actual referents. That doesn’t make it any less of a concept.

So far, I haven’t yet touched on the actual topic of ontologies, but this theoretical foundation will be important in later parts of this series. The [following posts](https://callistaenterprise.se/blogg/teknik/2020/06/29/ontologies-part2/) will discuss different scenarios (i.e. what are your requirements) and technical aspects of creating and managing an ontology.


Links for further reading:

[In My Own Terms](https://inmyownterms.wordpress.com/mysmartterms/mysmarterms-5-the-semantic-triangle-words-dont-mean-people-mean/)

[Glossary of terminology management](https://termcoord.eu/glossary-of-terminology-management/)

[Glossary of terms used in terminology ](https://benjamins.com/catalog/term.4.1.08bes/fulltext/term.4.1.08bes.pdf)
