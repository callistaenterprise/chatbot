---
layout: details-blog
published: true
categories: blogg teknik
heading: Curl, Mutual Authentication and Web Services
authors:
  - marcuskrantz
tags: security tools
topstory: true
comments: true
---

In a recent project, I was assigned to setup monitoring of a set of web services. The idea was to call the web services every 5th minute and check whether they operated normally or not, i.e a valid SOAP response was returned. The web services used SSL Mutual Authentication to authenticate the calling client. Since I just wanted to make an easy setup; without invoking a "real" web service client (a Java web service client for instance), I decided to use [Curl](http://curl.haxx.se/) because of its completeness, available on most platforms, and the ability to easily connect it with [Nagios](http://www.nagios.org/) that would perform scheduled checks of the web services. This article can be of use when you simply want to call a web service from the command line or when you are in a headless environment.

-[readmore]-

When I started I had a pkcs12 file (which contained a certificate, a private key, and CA certificate) for authentication, the endpoint address of the web service, and an xml file that should be used as input data to the web service.

## Keys and certificates
[Curl’s man page](http://curl.haxx.se/docs/manpage.html) provides great documentation for setting up an http(s) call and I will later describe which parameters that I had to set. Before I could continue I needed to do something about my PKCS12 file. Curl does not support a combined file with keys and certificates so I had to extract and convert this data to pem format which is a format that works with curl. To extract the keys and certificates I used [OpenSSL](http://www.openssl.org/) and executed following commands in my terminal:

~~~
$ openssl pkcs12 -in my.p12 -out ca.pem -cacerts –nokeys
~~~

(Outputs CA certificates from `my.p12` file into `ca.pem`)

~~~
$ openssl pkcs12 -in my.p12 -out client.pem -clcerts -nokeys
~~~

(Outputs client certificates from `my.p12` file into `client.pem`)

~~~
$ openssl pkcs12 -in my.p12 -out key.pem -nocerts
~~~

(Outputs private keys from `my.p12` into `key.pem`)

For more information about the commands above check the [pkcs12 man page](http://www.openssl.org/docs/apps/pkcs12.html). When I had my key and certificates in place (in pem format) I could start building my command to call the web services.


## Building the Web Service client call
I had my three pem files for authentication, then endpoint of the web service, and I had my request xml file to post to the web service. To pass data to Curl I simply used the `–-data` parameter and since I had a file with my data I prepended @ to the file name. But using this option makes Curl to set the `Content-Type` http header to `application/x-www-form-urlencoded`. I wanted to pass a soap xml file, and according to the standard it requires that when a soap message is placed in a http body the `Content-Type` header must be set to `application/soap+xml` ([click here](http://www.w3.org/TR/soap12-part0/#Ref47748839611) for further information). I formed my initial Curl command like:

~~~
$ curl –-data @my-request.xml -H "Content-Type:text/xml;Charset='UTF-8'" https://localhost:8080/ws/MyService
~~~

I tried to execute the command just for fun but to no surprise it did not work. Curl complained that it tried to verify the server certificate using a default bundle of ca certificates. This was not what I wanted because I trusted the server certificate. To tell curl to not perform this verification I included the `–k` or `-–insecure` parameter in my call. Of course, once again, Curl complained about bad certificate. Since I had my client certificate and the private key I combined the `–-cert` and `-–key `parameters that formed the following command:

~~~
$ curl –k –-cert client.pem:<password> --key key.pem –-data @my-request.xml -H "Content-Type:text/xml;Charset='UTF-8'" https://localhost:8080/ws/MyService
~~~

The call above gave me a SOAP response. However, it contained a SOAP fault:

~~~ markup
<faultcode>soap:ActionNotSupported</faultcode>
~~~

After some research, I discovered that I had missed to add the `SOAPAction` http header as required ([click here](http://www.w3.org/TR/2000/NOTE-SOAP-20000508/#_Toc478383528) for further information). I added the header and formed my final command:

~~~
$ curl –k –-cert client.pem:<password> --key key.pem –-data @my-request.xml -H "Content-Type:text/xml;Charset='UTF-8'" –H SOAPAction:”MyOperation” https://localhost:8080/ws/MyService
~~~

Finally, success!

As you may have noticed I haven’t used the `cacert.pem` file, which I created earlier. This is because the `–k` parameter simply ignores the verification of the CA certificate. If I want to verify the server certificate using Curl, I simply removed the `–k` flag and added the `–-cacert <cacert>` parameter. The final command now looked like:

~~~
$ curl –-cert client.pem:<password> --key key.pem –-cacert ca.pem –-data @my-request.xml -H "Content-Type:text/xml;Charset='UTF-8'" –H SOAPAction:”MyOperation” https://localhost:8080/ws/MyService
~~~

Now, when we have a proper Curl call to a web service, we can easily use it together with Nagios for scheduled monitoring. How to configure Nagios is however out of scope of this article.

This article has shown that it can useful to use Curl to call web services under some circumstances. Especially in a closed, headless environment where there is no access to graphical tools. It is a quick way to just test if the authentication works and that it is possible to get result from a web service. The last thing I would like to mention about Curl, that is very useful, is the `–-trace-ascii <outfile>` parameter. Setting this, all incoming and outgoing data in your call is dumped to a file. I found it especially useful for debugging SSL/TLS handshakes.
