---
layout: details-blog
published: true
categories: blogg teknik
heading: Creating self-signed certificates for use on Android
authors:
  - marcuskrantz
tags: android mobile security
topstory: true
comments: true
---

A while ago I started to implement TLS/SSL mutual authentication on Android. How to actually implement the functionality on the Android platform is covered in my other article [Android - TLS/SSL Mutual Authentication](/blogg/teknik/2011/11/24/android-tlsssl-mutual-authentication/). Before such implementation can be done, it is important to have the keys and certificates prepared. In this article demonstrate how you can create these. However, this article is not just applicable to Android and should be usable in other scenarios as well.

-[readmore]-

For this article to be useful, the required tools are: openssl, Java's Keytool and the [BouncyCastle-provider](http://www.bouncycastle.org/latest_releases.html). There are also some resources that I strongly recommend and has been very useful:

* [SSL Certificates Howto](http://www.tldp.org/HOWTO/SSL-Certificates-HOWTO/)
* [OpenSSL Keys Howto](http://www.openssl.org/docs/HOWTO/keys.txt)
* [OpenSSL Certificates Howto](http://www.openssl.org/docs/HOWTO/certificates.txt)
* [Java Keytool](http://download.oracle.com/javase/6/docs/technotes/tools/solaris/keytool.html)

One might argue why I don't use keytool to generate the keys and certificates and use them right away. Well, I was very curious about learning more about openssl and how to deal with various formats of keys and certificates.

## 1. Create private keys
Let's start from scratch. First of all we need private keys. We use openssl to create these:

~~~
$ openssl genrsa -des3 -out client_key.pem 2048
$ openssl genrsa -des3 -out server_key.pem 2048
~~~

This will create the two keys; `client.pem` and `server.pem`. We will use these in the next step to sign our certificates with. In normal cases we would create a CA-signing request, that is sent to a CA who will issue your certificates. But since we want to self-sign our certificates this step is redundant.

## 2. Create self-signed certificates

~~~
$ openssl req -new -x509 -key client_key.pem -out client.pem -days 365
$ openssl req -new -x509 -key server_key.pem -out server.pem -days 365
~~~

Additionally, instead of being prompted for the certificate's subject line you can use the `-subj` parameter and pass it to the `openssl req` command. What we just did was basically creating a CA signing request using our private keys to sign the outgoing x509-certificates. The certificates will be coded in pem-format and valid for 365 days.

## 3. Create trust stores
In order to use our keys and certificates in Java applications we need to import them into keystores. First of all, we want the client to trust the server certificate. To do this we must create a client trust store and import the server’s certificate.

~~~
$ keytool –importcert -trustcacerts –keystore clienttruststore.bks –storetype bks –storepass <truststore_password> -file server.pem -provider org.bouncycastle.jce.provider.BouncyCastleProvider –providerpath <path_to_bcprov_jar>
~~~

> **Note:** On the client side, which in our case will be an Android app we use Bouncy Castle as our provider since it is supported on the Android platform.

Create a trust store for the server and import the client's certificate into it.

~~~
$ keytool –importcert -trustcacerts –keystore  servertruststore.jks –storetype jks –storepass <server_truststore_password> -file client.pem
~~~

Currently, we have two trust stores one for the server in which we imported the client’s certificate and one for the client in which we imported the server’s certificate.

## 4. Combine keys and certificates
A problem with Java’s keytool application is that it won’t let us do such a simple thing as importing an existing private key into a keystore. The workaround to this problem is to combine the private key with the certificate into a pkcs12-file (which is understood by Java’s keytool) and then import this pkcs12 keystore into a regular keystore.

Combine the certificate and the private key for the server and client respectively:

~~~
$ openssl pkcs12 –export –inkey  client_key.pem –in client.pem –out  client.p12
$ openssl pkcs12 –export –inkey server_key.pem –in server.pem –out server.p12
~~~

## 5. Convert from pkcs12
Import the created keystores to new ones with common formats:

~~~
$ keytool –importkeystore –srckeystore client.p12 –srcstoretype pkcs12 –destkeystore client.bks –deststoretype bks –provider org.bouncycastle.jce.provider.BouncyCastleProvider –providerpath <path_to_bcprov_jar>
$ keytool –importkeystore –srckeystore server.p12 –srcstoretype pkcs12 –destkeystore server.jks –deststoretype jks
~~~

We should now have all files we need for a successful TLS/SSL mutual authentication. The files we move to our Android project will be: `clienttruststore.bks` and `client.bks`. The files we move to our server will be: `servertruststore.jks` and `server.jks`.
