---
layout: details-blog
published: true
categories: blogg teknik
heading: Android - TLS/SSL Mutual Authentication
authors:
  - marcuskrantz
tags: android java mobile security
topstory: true
comments: true
---

Due to the explosion of smart phones on the market, the need for exposing existing enterprise systems through the mobile channel is growing rapidly. One of the first questions that will come up is how we can establish a secure communication channel with the existing enterprise system.

In this article, I will cover both how to trust a server certificate for secure communication with the server, as well as providing a client certificate to the server for mutual authentication. The client certificate is bundled with the app and of course, the server needs to trust this certificate.

-[readmore]-

## Setup
Before we can start, keys and certificates need to be in place. My article [Creating self-signed certificates for use on Android](/blogg/teknik/2011/11/24/creating-self-signed-certificates-for-use-on-android/) covers how to create keys and certificates as well as importing them into supported key stores. If you don't have any keys or certificates, create the required files by reading that article.

### Android and self-signed certificates
I assume that you already figured out how to create a simple Android app. However, I do not assume that you have put `clienttruststore.bks` or `client.bks` in your Android project’s `res/raw` directory. Before you continue, make sure the two files are there. These files were created in [Creating self-signed certificates for use on Android](/blogg/teknik/2011/11/24/creating-self-signed-certificates-for-use-on-android/) but you can replace them with your own, just make sure that your keystores uses the [Bouncy Castle Provider](http://www.bouncycastle.org/latest_releases.html).

## Implementation
This section covers how you can implement a custom `HttpClient` by registering a scheme for https communication and load a keystore and a truststore into a `SSLSocketFactory`.

### Extend HttpClient
Android uses Apache Commons HttpClient but since we want communicate securely we must extend the `DefaultHttpClient` with some custom behavior (load our keystores). Therefore, we start by creating `SecureHttpClient.java` and extend the `HttpClient`.

~~~ java
public class SecureHttpClient extends DefaultHttpClient {
  private int securePort;

  public SecureHttpClient(final int port) {
    this.securePort = port;
  }
}
~~~

Simply put, we need to do two things to get our mutual authentication to work. 1) Create an `SSLSocketFactory` where we load our keystores and 2) Register a scheme for https communication that uses our custom `SSLSocketFactory`. This method will load our keystores.

### Create SSLSocketFactory and load the keystores
Extend the `SecureHttpClient` with the two new methods found below. If you do not want to use mutual authentication you can just load the trust store in which the server's certificate is. The resulting `SSLSocketFactory` will later be used when creating a scheme for https-communication.

~~~ java
private SSLSocketFactory createSSLSocketFactory(final Context context) {
  Log.d(TAG, "Creating SSL socket factory");

  final KeyStore truststore = this.loadStore(context.getResources().
      openRawResource(R.raw.clienttruststore, "password", "BKS");
  final KeyStore keystore = this.loadStore(context.getResources().
      openRawResource(R.raw.client, "password", "BKS");

  return this.createFactory(keystore, this.keystorePassword, truststore);
}

private SSLSocketFactory createFactory(final KeyStore keystore,
    final String keystorePassword, final KeyStore truststore) {

  SSLSocketFactory factory;
  try {
    factory = new SSLSocketFactory(keystore, this.getKeystorePassword(), truststore);
    factory.setHostnameVerifier(
      (X509HostnameVerifier) SSLSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER);
  } catch (Exception e) {
    Log.e(TAG, "Caught exception when trying to create ssl socket factory. Reason: " +
        e.getMessage());
    throw new RuntimeException(e);
  }

  return factory;
}
~~~

We now have a method that loads our keystores and return an SSLSocketFactory.

### Register a scheme for https
Before we can communicate with our server, we must register a scheme for https communication that uses our `SSLSocketFactory`. The `createConnectionManager()` in `HttpClient` allows us to register our scheme. Override the `createConnectionManager()` method and provide the following implementation:

~~~ java
@Override
protected ClientConnectionManager createClientConnectionManager() {
  Log.d(TAG, "Creating client connection manager");

  final SchemeRegistry registry = new SchemeRegistry();

  Log.d(TAG, "Adding https scheme for port " + securePort);
  registry.register(new Scheme("https", this.createSSLSocketFactory(), this.securePort));

  return new SingleClientConnManager(getParams(), registry);
}
~~~

That's about it. We now have the `SecureHttpClient` class that we can use from our Android app to communicate over Https.

## Using the Secure client
It is time to use our `SecureHttpClient` and make a call to a web server. Since this is just a test, we can basically make the call from anywhere in the app and I choose to make it in an Activity's `onCreate()`-method. The test server I used is a simple Jetty server (jetty-maven-plugin) where I added configuration for SSL containing a trust store and the server's certificate. You can see how a simple server with SSL can be setup in the article: [Quick Start - Jetty, Maven and SSL](/blogg/teknik/2011/11/24/quick-start-jettys-maven-plugin-with-ssl/).

To make a https call to the server, simply provide an implementation like the one below:

~~~ java
@Override
public void onCreate(Bundle savedInstanceState) {
  final HttpClient client = new SecureHttpClient(443);

  // Provide ip or address to where your test server is runnning
  final HttpGet request = new HttpGet("https://192.168.0.10:8443/example-server")
  final HttpResponse response = client.execute(request);

  Log.d("ExampleActivity", "Response code: " + response.getStatusLine().getStatusCode());
}
~~~
