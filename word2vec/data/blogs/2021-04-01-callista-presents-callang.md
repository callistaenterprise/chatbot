---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: 'Callista launches new nano-services language: Callang(TM)'
tags: programming language callang april joke
authors:
  - davidstrom
---
Over the past 18 months a crack-team of software developers and IT architects from Callista Enterpise, lead by the formidable trio Magnus Larsson, Peter Larsson and Fredrik Larsson has developed a new programming language for the nano-service, cross-cloud, no-platform based programming model.

It has now become time to share the good news and release this paradigm changing novel programming language to the wider community. We sincerely hope you will enjoy it!

-[readmore]-

### A new programming model

The Callang programming model introduces some rather novel concepts, such as Domain Model Missinterpretation Detection, or DMMD for sort, as well as extensive cross language support at compile time. This creates a completely new programming model where the programmer can focus on writing cool stuff, fast, and deploy fast without need for the whole build-test-deploy life-cycle of traditional development.

Some key requirements have of course been real-time start-up capability, ubiqious support for any communication protocol, as well as the mentioned cross languge support, to be able compile and run any code witten for any of the other top languages such as Java, Golang, C/C++, Python or even Rust.

The new Domain Modelling Missinterpretation Detection (DMMD) feature is based on the use of advanced deep learning algorithms to detect and correct domain modelling missinterpretations at compile time. A new feature, but something that we believe will become more of a standard as languages evolve and become smarter over time.

### Example code and comparision results

The development team for the Callang language are proud to present the results from some early trials and comparisions to other leading programming languages. I should mention that the team consist of, apart from the lead trio, also the senior members Björn Gylling, Björn Beskow, and Björn Genfors. But first let's look at some code!
As mentioned Callang a new feature for detecting and correcting the domain model of any appllication. This enables some pretty amazing new code styles, such as this api for crud operations:

~~~

load domain

api:
	public common data_layer
	public get(any id):
		give domain.model(data_layer->get(id))

	public post(any data):
		model = domain.as_model(data)
		give data_layer->save(model).id

	public put(any data):
		new_data = domain.as_model(data_layer->get(data.id)).merge(data)
		give data_layer->save(model)

~~~

And now some results, comparing with Go and Java, measuring computation time for factoral operations:

![Measurements, factoral calculations between languages](/assets/blogg/april_first/measurements_blogg.png "Measurements graph")


So, with these initially very promising results we want to invite our friends and collegues to try out our new programming language for the future, Callang, the Callista language! Go to [www.callistaenterprise.se/april_first.html](https://callistaenterprise.se/) to find out more!
