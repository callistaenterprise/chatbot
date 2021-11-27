Many organizations gradually improve in maturity when it comes to web application development. The value of an explicit, governed best-practice has been learned the hard way.

- Architectural layers have been sorted out to make sure concerns are separated for flexibility and maintainability.
- Roles and disciplines have been sorted out to make sure the right skill comes into play for the various aspects of the architecture (look-and-feel, workflow logic, enterprise services, back-end integration, O/R- and database modeling etc).
- A framing reference architecture has been sorted out, providing a right-grained model shared across all technical disciplines, to drive best-practice governance.

Then the portal project started. It started as an infrastructure project. A portal platform is to be implemented. The focus is initially on security and CMS. Eight weeks later, the portal project is eight times larger. The portal project has been out there talking to business users. They've learned what the users need. The users need information at their fingertips, currently hidden in silos across the IT landscape. Users are happy. Suddenly someone show up from IT to ask what they need - ready to deliver value - now!

## On the hunt for a quick win

Yes, the portal project depends on a quick win. The big portal server is running out there with a calendar, a news feed and a link to the time reporting system. Not very exciting. Some real business data easily available, could justify the investment. Suddenly the portal cowboys are everywhere. Html consultants are buying expensive high-end IDE wizardry bound to the portal vendor, so that they can point-and-click their way to JSP/JSF/SDO/Vendor X glue/JCA/almost JSR 168 portlets that integrates with CICS, MySAP and the database API of the legacy order system. By the way, there was a checkbox in IDE, that that made it wrap all back-end access into web services. A single click in the IDE deployed it all to the portal server. The ad-hoc web services turned out to be popular for re-use. The portal guys deliver new services in a fraction of time (and cost) compared to the sturdy ESB guys.

## Architecture fighting back

But what about test-driven development, contract first canonical web services, portable builds, lightweight, open source IDE with all build files generated from Maven build files, portability across web apps and portlet apps, in-house glue to avoid vendor lock-in and all other best-practice principles applied? They started where we started and don't want to be any more. Let's stop them! Let's catch them in our enterprise architecture governance process!

No, don't! They represent a sound approach to business-driven IT. And they deliver. Well, there may be some issues once a service interface is broken, the platform is to be upgraded, load increases jada-jada. Of cause agile, business focused portal development is suitable for some solutions and less suitable for others.

## The learning governance model

Instead of "to conform or not to conform", it may be time to extend the reference architecture to support (incorporate) business-driven portlet projects. In the sought for a governance model, we came up with a portlet classification model as an initial idea. What do you think? Does it help sorting out borderlines between portal and application responsibilities?

_Bild saknas_

Each type (1 -> 3) differentiates in its relationship to information services.

- Type 1 integrates purely at the html level and thus strictly tied to web browser and presentation skills. Integration of Google Maps could illustrate this type.
- Type 2 portlets consume information with low semantic structure. They are typically developed "on-line" using tools within the portal server itself. The focus is on creating information mash-ups from various sources, using XML-scentric languages like xpath and xslt, or tools that generate such constructs. The skill set is comparable to the integration developer role.
- Type 3 portlets contribute business process tools that consume semantically rich services - both for information retrieval and also for invoking transactions that change the state of the back-end system. Type 3 portlets are developed by software engineers using todays best-practice within Java development. These portlets are developed, integration tested, versioned and finally released through the standard software release process of the enterprise. They consume governed, enterprise services. A type 3 portlet may - due to its mature change control environment - be exposed for remote consumption in other portals via WSRP.

## Ad-hoc services

What about the ad-hoc services? Type 3 (and maybe even type 2) portlet projects may create services to support the architecture of the portlet solution. These services may however not be consumed by any other solution, unless it is first "upgraded" to an enterprise services (according to the SOA governance practice of the enterprise). This is typically done by a different team, in control of established contract- and versioning strategies.
