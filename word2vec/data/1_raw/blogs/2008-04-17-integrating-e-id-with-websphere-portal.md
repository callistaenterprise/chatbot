I'm currently working on a project where we, despite its [many drawbacks](http://www.jroller.com/rickard/entry/bank_eid_in_sweden_a), have decided to use the "[BankId](http://www.bankid.com/)" solution to authenticate our users. But this is not the whole truth; since not all Swedish banks have agreed on using BankId we have to use three different solutions in order to cover (most) users: BankId, Nordea and Telia. The whole solution is sometimes referred to as _electronic identification_, or simply e-id.

Fortunately, the server side parts have been packaged together into one common interface, in our case hosted by a third party. Even so we still have to handle the fact that the three solutions use different clients, which means generation of different client side code. Nordea and Telia uses different installed PKI-clients whereas BankId currently uses an applet (recently [they announced](http://www.bankid.com/BankidCom/Templates/NewsPage.aspx?id=98&epslanguage=SV) that the applet-solution will be replaced with an installed client, the same one as Nordea uses). In all cases, multiple steps are needed to gather the information needed by the authentication service:  

1. Ask the user which of the three solutions he/she uses.
2. For some clients: call the authentication service to generate a "challenge".
3. Present the appropriate client side code to the user (including the generated challenge).
4. Gather user input and send authentication request to the authentication service. 

This means no simple one-step, form-based authentication.  

The application is built on WebSphere Portal, so one of our main questions right now is how to best integrate the e-id authentication into WebSphere? My initial thought was that this must surely have been done by someone else, before us. If not with WebSphere Portal, then at least with WebSphere application server. But no such luck; even if someone indeed has done it we haven't found anyone willing to share their solution.

Currently we have three different tracks which we are discussing. None of them have been verified, so they are all more or less hypothetical at the moment.

## 1. Simple Java-based solution

We implement a simple Java-based solution on top of the Portal instead of integrating with WebSphere's security features.  

Pros:

- Straightforward, we know how to do this and we can reuse the general code examples provided for us.

Cons:

- No full integration means we can't use portal specific roles, i.e. we can't configure which portal pages and portlets a specific user can see depending on his/her role. Even though this is a common way to use a portal our particular application won't use those features anyway so this is ok by us.
- We have to manually handle storing and retrieving information about the logged in user in the session (which also means that we have to turn on anonymous sessions in the portal).
- If we need it, we have to manually handle SSO between the portal and the backend systems. Currently our users aren't actors in any of the backend systems anyway (i.e. they can't log in) but there might be cases like that in the future.

## 2. Custom JAAS-login module

WebSphere security is based on the [JAAS standard](http://java.sun.com/javase/6/docs/technotes/guides/security/jaas/JAASRefGuide.html), so integration could be done by implementing a custom JAAS-login module for e-id.

Pros:

- JAAS is a Java standard so the solution might be reusable elsewhere.

Cons:

- The solution still requires WebSphere specific code and configuration.
- Implementing a custom JAAS login module and integrating it with WebSphere Portal isn't trivial. In fact, we haven't yet verified that this is a possible solution. For example we don't know how to handle the generation of the different client side code (including conversations in multiple steps). One hypothesis is that this could be done by implementing a custom [CallbackHandler](http://java.sun.com/javase/6/docs/technotes/guides/security/jaas/JAASRefGuide.html#CallbackHandler).

## 3. SSO reverse proxy

We use a separate solution altogether for authentication (a SSO reverse proxy) and integrate that with WebSphere Portal using a [Trust Association Interceptor](http://www.skywayradio.com/tech/WAS51/Trust_Associations.php) (TAI).

Pros:

- Other applications can take advantage of the same solution.
- There are already integrations (TAIs) available for some of the available SSO reverse proxy products on the market.
- Implementing SSO against the backend systems will probably be easier than with our own custom solution (at least that seems to be the promise when buying such a product).

Cons:

- The integration is a WebSphere specific solution, i.e. we cannot reuse the TAI to integrate with another (Java EE) server.
- The project/organisation has to cover the cost of another (possibly expensive) product and get the specific competence needed for configuring it.
- We have to integrate the e-id authentication with the reverse proxy. Nothing says that this is any simpler than integrating with WebSphere directly. However, it might be worth it considering others can reuse the solution once it's there.

From a "Keep it Simple, Stupid"-perspective, alternative one is the most appealing. It's the simplest and probably cheapest solution that still covers all of our (current) requirements and the ability to reuse proven code examples is a big plus.

However, currently we are leaning slightly towards alternative number three, mainly because there seem to be other applications who also want to use e-id for authentication. Having a separate and reusable solution in place might be the cheapest solution in the long run. Since we haven't started looking seriously at any of the products on the market yet, we still have quite a long way ahead of us.
