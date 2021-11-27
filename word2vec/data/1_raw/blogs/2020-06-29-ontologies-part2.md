---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: 'Technical aspects of ontologies, part 2'
authors:
  - bjorngenfors
---
So, what is an ontology? In the broadest sense, an ontology is knowledge representation, symbolically encoded as to allow for computerized reasoning. Simplified: to use the terminology [from the previous post](https://callistaenterprise.se/blogg/teknik/2020/06/10/ontologies-part1/), an ontology describes concepts and their relation to other concepts using a formalized language. This enables powerful computerized “thinking”, but creating a well-formed ontology is a big task.

-[readmore]-

There are a multitude of concepts that are similar: ontology, classification, taxonomy, nomenclature, thesaurus, controlled vocabulary, enumerated type and code system (sw. “kodverk), to name a few. I won’t differentiate these, but instead I will try to pick them apart.


## When do you need an ontology?

The first thing to notice is that I’ve (purposefully) mixed apples and oranges, or rather content and containers. For example: an enumerated type is a data type used in cases where you need to represent a fixed set of concepts, e.g. when creating a Slack poll for food preferences ([see last blog post](https://callistaenterprise.se/blogg/teknik/2020/06/10/ontologies-part1/)). We need to differentiate between the container (the data type) and the content (the set of enumerators). Ontologies are about semantics, so from this point on we’ll stick with the old Bill Gates adage: content is king.

The second thing to notice is that content in this case means a fixed set of concepts to choose from in a given situation. This is basically what we call a controlled vocabulary. These are used for catalogization of information and making data entry consistent in order to make information retrieval and reusage easier. In the simplest cases, like for most cases where enums are used, the controlled vocabulary is an ad hoc list, which is fine for

- single purpose uses (use scope is very contained)
- where the content is well defined (no ambiguity)
- where the content is definitionally complete (think of the set of four suits in a deck of cards).

In these cases, the overhead of creating a full ontology is a waste of time. Please note that I’m not talking about the size of the content.


Vice versa:
- The larger your scope of usage and the less control you have over the circumstances in which the information is used
- The larger and more complex your subject area and the less well defined the domain
- The more prone to change some set of information is the likelier it is that an ontology will be a good match for your needs.


## Fictional use case

These dimensions aren’t black and white, each one is a sliding scale. Again, let’s use a simple example to concretize - you run an online community, and one piece of information the members can divulge about themselves is their nationality. For this purpose, you need to create a list of all the countries in the world. This will be a list of some 200 countries.

![people_world_map.png]({{site.baseurl}}/assets/people_world_map.png)

## Complexity, state of definition and longitudinal stability of subject area

The task of creating a list of the nations of the world isn’t complex, it’s a one-dimensional list. As opposed to, say, a list where your users can enter information about their occupation (an entry which can reflect the tasks they do, their educational background, their place in an organizational hierarchy and the permanence of their position, to name a few things).

Although the subject area of “all the nations of the world” is decently well defined, there are still some contested territories. This means you need to choose which nations to include with some care. Case in point: if you include Taiwan in your list, you will make many Chinese people angry. If you don’t include Taiwan in your list, you will make many Taiwanese people angry.

Lastly, this list will need to be maintained. Changes over time are small in this case, and the ramifications of not instantly keeping up to date are likely small. These are both arguments for an ad hoc list. Other types of data, where there is constant change, might benefit from an ontology approach.


## Size of scope
If your scope is simply to let a user enter nationality to display on a member profile page, this is what I call single purpose use. Enter once, display in one place. If you also want to display a flag next to this information, you’re still close to single purpose use - enter once, use twice.

When you want to view aggregate user statistics or personalize (“nationalize”) the experience on your site, you’re slowly moving away from single purpose territory. When you additionally want to correlate statistics with other databases (e.g. CIA World Factbook) or display user statistics on a map (e.g. integrate with Google Maps), you get further away yet. You are still in control over how your information is used. Any problems that may arise in integrations, you yourself can manage, so this is still some kind of middle ground.

Finally, when your small community is no longer that small, and you release API:s for outside app developers to use aggregate information about your members, you’ve deep into multipurpose use territory. 
