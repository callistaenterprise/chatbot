---
categories: blogg teknik
layout: "details-blog"
published: true
heading: "Notes from Gartner's AADI conference"
authors: 
  - johanzetterstrom
tags: ""
topstory: true
comments: true
---

I recently participated in Gartner’s ”Application architecture, development & integration” conference, and here I want to share a couple of impressions from that event.

First I want to say that it was a really good conference, both considering the organisation and the speakers, where the latter was a clear step up from The Rich Web Experience, which I attended a year ago. The agenda was mostly targeted at architects and other types of decision-makers, but developers with an eye on ”the bigger picture” could also find a lot of interrest. The architectural view was throughout the conference kept pretty technical and connected to real-world problems.

## Microservices
Microservices are gradually given a more defined place in the larger architectural picture. The view that a microservice is created when needed, to solve problems concerning agility and scalability, seems to be the dominating one, and there was less talk about ”microservice architecture” than ”microservices in the architecture”. Anne Thomas, in her presentation ”Microservices: the future of SOA and PaaS”, delivered the strategic planning assumption that ”By 2017, more than 90% of organizations that try microservices will find the paradigm too distruptive and use miniservices instead”. (Miniservices = refactored SOA, driven by composition and reuse. Microservices = web-scale SOA, driven by agility and scalability). The reason for this seemingly negative assumption is that microservices are a highly complex architecture which requires unfamiliar patterns and new infrastructure. Microservices may be the solution to your problems, but you need to make sure you have the right expertise!

## Old vs. new spaghetti
SOA was once presented as the solution to the mess created by point-to-point integration. You’ve seen the images: Systems along the edges, and the center filled with arrows representing the integrations. Spaghetti. Enter SOA architecture, services defined on a central ESB, and voila! These days, the services are depicted as the new spaghetti, and they seem to have moved out of the ESB as they are spread out all over the place. Enter the API control gateway (which, at least to a certain extent, acts as an ESB) and a separation of inner and other API:s. This brings the order back. It’s magic! Sarcasm aside, part of the reason for this change is that what is defined as a service has changed.  It has shifted from mainly beeing the interface definition to including the implementation of the functionality. Services used to access backend systems, now they access data.
