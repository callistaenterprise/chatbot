Vendors continuously try to retrofit the term Enterprise Service Bus (ESB) to the architecture of their offering. I like the definition contributed by Paul Fremantle at WSO2 in his article Reclaiming the ESB. It makes sense to define it as SOA infrastructure, based on a rather enterprisey requirement of canonical service interfaces. I would like to add - though - that most of the "EAI"-products rebranded into ESBs, are good tools for employing this architecture. At the same time, they are packaged for the swiss-army-knife definition EAI of an ESB.

I think it is utterly important to make a distinction between product and architecture. As an example, JBI is a standard for a category of products in the integration space, with a focus on service semantics (interfaces, operations, messages) rather EAI semantics (events, messages and endpoints). It is a container architecture for tools that are practical in an end-to-end perspective. This includes the ESB, as defined by the article, but also adapter tooling (for adapting protocols, application specific xml and finally to canonical service interfaces). A JBI product also supports tooling for realization of service composition and orchestration (e.f. BPEL engines).

You need all these kind of tools to create the end-to-end solution. Same goes for proprietary platforms with EAI heritage, like IBM WebSphere Message Broker. The architecture described in the article is considered "best practice" at many enterprises to day. Whether the same tool family is used for multiple parts of the architecture does not make the solution more or less SOA, or more or less implemented. Whether "the product" should include the ESB, rich adapter technology, service composition technology and service orchestration technology or just the ESB (again - as defined by the referenced article) is a completely different question.

Once you've defined your reference architecture, you'll find your self with a gap between the vision and the current system landscape. You need tooling to fill that gap.  Typically, you need two completely different set of tools - one for a "pure SOA" vision, driven by BPM and another for "accept that the process is embedded into my ERP, so that I'm left with message transformation services with no value to my strategic BPM vision". In technical terms, the BPM vision heavily relies upon request/response web services, while the second one depends on traditional asynchronous messaging.

The architecture described in the article, applies to both, but it resolves into two chunks of platform requirements. JBI is unique, in that it intends to support both of them, based on a single interface model - that of Web Services. IBM  WebSphere Message Broker does not support the BPM-targeting reference architecture. IBM targets the BPM vision with an alternative product stack centered around WebSphere Process Server. SAP NetWeaver has an integrated stack with explicit layers for both challenges (integration engine vs process engine with a common meta model for message definitions and service architecture).

In order to decide for SOA tooling, the architecture as described in the referenced article is a good starting-point for defining a reference architecture for SOA. But there are many more aspects that needs to be incorporated before a tooling strategi can safely be outlined. Most high-end products bundle technology covering ESB, adapter-solutions, orchestration and service composition. This is (including JBI) however often without making the clear distinction between adapter and ESB.

This makes up a challenge for governance, but most of all for funding and skill allocation. The author of the article means that a product could help resolving these challenges. I don't. A solid reference architecture needs to be in place. The reference architecture must have impact on how projects are organized, funded and managed. This can only happen when architecture is rooted in the programme office. And that is most likely to happen when the reference architecture can be motivated in terms of positive impact on business challenges.