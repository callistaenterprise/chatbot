Here at CQon there is a track dedicated to service-oriented architecture - mainly focused technical aspects. When things get complicated or structured to a level where the fun or the productivity or both are gone, application architects and developers tend to look for new approaches - typically more agile than current best-practice.

We have seen Corba go for SOAP, C++ go for Java, pure HTML apps go for Ajax etc. Currently there seem to be two major trends being debated - at least here at QCon:

- Java versus dynamic languages, like Ruby and Groovy.
- Web Services versus HTTP Services ("RESTFul services")

The most animated discussions are definitely on the SOA arena: Web Services versus REST.

When a technology matures, you typically forget all the problems you had before the technology was available. You get focused on the other side of the coin - the price-tag of getting the problems fixed by a new technology. Looking eight years back, Simple Object Access Protocol (original interpretation of SOAP) arrived to rescue projects from Corba complexity:


SOAPs major merits was its heritage of the technologies that boosted the success of the World Wide Web: HTTP and XML. Then, all the dream went into reality. Application interop requires more than an agreed wire format at the syntactic level (well-formed XML). WSDL arrived to extend SOAP with a standard for expressing service metadata. The term Web Service was coined. Then, requirements for security, integrity, reliability and more was added through more or less coordinated standardization efforts commonly referenced as "WS-*". The WebService interoperability Organisation was created to standardize the standardizations. Again, we went from over simplified to over-complicated:

And the reaction to over-complexity arrived with the increasing popularity of REST -"SOAP done right":

REST has a lot of promise. Although, it is a very accessible technology, it also represents a different perspective on architecture, than SOA in general. REST views services as resources uniquely identified by a URL and and the finite set of operations that can operate on these resources. the operations are defined by the HTTP protocol: GET, PUT, POST, DELETE. This style of architecture is squeezed into WS-* by a strangely named specification named WS-Transport. However, WS-Transport still lacks the accessibility of REST, due to its roots in SOAP.

Former Web Service evangelist, like Steve Vinosk (Iona, Virtue), Mark Little (HP, WS-* spec-lead, JBOSS) are spending the time bashing SOAP and WS-\*. HTTP Web Services and the architecture represented by REST is the new reaction to the over-complicated best-practice. REST has been used for many years and is core interfacing technology at global players like Google. Amazon is also increasing the use of REST. Looking at the history, is there anything specific with REST, that prevents it from starting its journey up the complexity scale, repeating the history of mainstream pre-decessors? Either that, or fail due to inability of accommodating new requirements? Are we heading REST-\* ?

