---
categories: blogg teknik
layout: details-blog
published: true 
topstory: true
comments: true
tags: microservices rsocket architecture
authors:
  - parwenaker
tags: reactive rsocket async asynchronous stream distributed microservices
heading: An introduction to RSocket
---

[RSocket] is a new communication protocol that promises to solve the issues we have with HTTP, and together with that, it might also simplify the way we design and build distributed systems and microservices. I will come back to that last statement in a later blog post. 

-[readmore]-

[comment]: #(Links)
[Reactive Streams]: http://www.reactive-streams.org/
[Reactive Principles]: https://www.reactivemanifesto.org/
[RSocket]: https://rsocket.io/
[Netifi]: https://www.netifi.com/
[Pivotal]: https://tanzu.vmware.com/pivotal
[Lightbend]: https://www.lightbend.com/
[frame header]: http://rsocket.io/docs/Protocol.html#frame-header-format
[RSocket specification]: https://rsocket.io/docs/Protocol.html 
[SETUP frame]: https://rsocket.io/docs/Protocol.html#setup-frame-0x01
[REQUEST_RESPONSE frame]: https://rsocket.io/docs/Protocol.html#request_response-frame-0x04
[PAYLOAD frame]: https://rsocket.io/docs/Protocol.html#payload-frame-0x0a
[REQUEST_FNF frame]: https://rsocket.io/docs/Protocol.html#request_fnf-fire-n-forget-frame-0x05
[REQUEST_STREAM frame]: https://rsocket.io/docs/Protocol.html#request_stream-frame-0x06
[REQUEST_CHANNEL frame]: https://rsocket.io/docs/Protocol.html#request_channel-frame-0x07
[REQUEST_N frame]: https://rsocket.io/docs/Protocol.html#request_n-frame-0x08
[ERROR frame]: https://rsocket.io/docs/Protocol.html#error-frame-0x0b
[comment]: #(Images)

<img src="/assets/blogg/rsocket-part-1/rsocket-logo.svg" height="60px">

## Intro
This blog is the first in a series that covers RSocket, a new reactive communication protocol. I first read about RSocket in late 2019, and my first thought was that this protocol could revolutionize the way we build distributed systems and microservices. Since the Spring team at Pivotal has embraced it, I am sure that it is here to stay. The specification has not yet reached 1.0, but the Spring Framework includes the Java implementation since version 5.2. I recommend the [blogs](/blogg/teknik/2020/05/24/blog-series-reactive-programming/) my colleague Anna has written on the subject if you are new to reactive programming. 

## Background
When building modern distributed applications (call it microservices if you will), we are faced with several challenges. One of them is how our services communicate and exchange information over the network. HTTP is probably the most widely used protocol both between services inside our data centers and to the outside. It has become a de-facto standard due to its superior interoperability. 

The use of HTTP presents some problems, though.
* It only supports the request/response interaction model.
* It's inefficient.
* It's not reactive

A modern application architecture often needs to support other communication patterns, like streaming and fire-and-forget. When that need arises, we often bring in a message broker to support those use-cases, even if we don't need the durability of messages. 

HTTP is a text-based protocol whose primary usage is fetching documents over the Internet. Using this protocol in a data center is inefficient, especially the earlier versions 1.0 and 1.1. Why is performance relevant? Because inefficiency in memory, CPU, and network utilization are in today's systems often directly translated into Cloud costs. 

And last but not least, HTTP is not reactive! There is no problem with using HTTP in a reactive context, but the protocol itself has no concepts of reactiveness.

## RSocket
[RSocket] is an open-source, binary encoded protocol designed by people that used to be at Netflix, helping develop [Reactive Streams] together with [Pivotal], [Lightbend] and others. Companies that are currently actively supporting the protocol includes [Netifi], [Pivotal], Facebook, and Alibaba, among others. Implementations exist in many different programming languages. RSocket is message-based and requires some lower-level transport protocol to carry the messages. The requirements put on the transport protocol are that it should be reliable, connection-oriented, and byte stream-based, so protocols like TCP, Websockets, and Aeron can be used. If the transport protocol does not have framing (like TCP doesn't), then RSocket provides it.

Contrary to HTTP, RSocket is symmetric and operates on a single stateful and persistent _connection_ between two communicating peers. The peers can assume either the _client_ or the _server_ role, but that distinction is only relevant during connection establishment. The _client_ connects to the _server_, but both can act as _requester_ or _responder_ in further interactions. The requester is the party initiating a communication interaction, called _stream_ in the [RSocket specification]. For example, this means that the server can act requester and send requests to the client, where the client might be a Javascript application on a web page, and the server might be a back-end Java server. 

RSocket defines four types of interaction models or streams.

1. Request / Response
2. Fire And Forget
3. Request / Stream
4. Channel

The specification defines the connection as "an instance of a transport session", and the protocol supports _session_ resumption. Session resumption allows for the recovery of long-lived streams across different connections and transport protocols. It is typically useful for mobile communication where network connections can be dropped and reconnected on another transport. Each stream exists for a finite period, and a Stream ID identifies it. The Stream ID is bound either by the lifetime of the connection or, if session resumption is in use, by the lifetime of the Session (which can span multiple transport connections). Messages relating to the connection uses a Stream ID of 0.

Let's have a closer look at how RSocket maps the reactive streams concepts on the wire. To follow along in detail in every bit and byte, I recommend that you follow along with the [RSocket specification] open.

### Frame Header

All frames start with a [frame header], which includes Stream ID, Frame Type, and flags. Two flags (I)gnore and (M)etadata are always present, but the others depend on the frame type.

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|0|                         Stream ID                           |
+-----------+-+-+---------------+-------------------------------+
|Frame Type |I|M|     Flags     |     Depends on Frame Type    ...
+-------------------------------+
```

### Connection Setup

The client has to connect to the server to set up a connection, and as soon as the connection is established, it sends a SETUP frame. Let's assume that the transport protocol is TCP, then the [SETUP frame] looks like this if resumption is not in use:
```
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 28 00 00 00 00 04 00 00 01 00 00 00 00 4e |..(............N|
|00000010| 20 00 01 5f 90 0a 74 65 78 74 2f 70 6c 61 69 6e | .._..text/plain|
|00000020| 0a 74 65 78 74 2f 70 6c 61 69 6e                |.text/plain     |
+--------+-------------------------------------------------+----------------+
```
TCP has no framing, so the first 24 bits (3 bytes) indicate the frame length (in this case 0x28 or 40 bytes), then there are 32 bits of stream ID, 0x00000000 since the frame is associated with the connection. Next, we have 6 bits of frame type and 10 bits of flags. The frame type is 0x01 (SETUP), followed by the flags, which are all 0, giving the next two bytes the value 0x0400. After the flags come, the protocol major and minor version (0x0001 and 0x0000). Two numbers follow the version. The first one is the number of milliseconds between KEEPALIVE frames (0x00004e20, 20,000 milliseconds). The second one is the max lifetime that the client allows the server not to reply on keep-alive frames until it considers the server dead (0x00015f90, 90,000 milliseconds). Finally, we have metadata and data encoding mime-types, which are text/plain for both in this example.

### Request / Response
![request response](/assets/blogg/rsocket-part-1/request-response.jpg)<br>
Request/response is probably still the most common interaction model, but in RSocket as well as in [Reactive Streams] semantics, this interaction model is just a special case of request/stream where the response stream only has one element or frame. The requester sends one request frame, and the responder replies with a stream of one frame. 

The request frame carries the Stream ID and frame type (in this case, REQUEST_RESPONSE). If the client initiates the stream ID, it is odd and starts with 1 for the first stream. The server uses even stream IDs beginning with 2. Here below is an example of a request/response interaction with an echo service using TCP. The client is the requester and sends a "Hello World!" message to the server that is the responder and echoes the message back.
```
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 12 00 00 00 01 10 00 48 65 6c 6c 6f 20 57 |.........Hello W|
|00000010| 6f 72 6c 64 21                                  |orld!           |
+--------+-------------------------------------------------+----------------+
```
Similar to the SETUP frame above, framing is used, and the frame is 18 bytes (0x12) long. The Stream ID is one (0x00000001), the frame type is 0x04 for [REQUEST_RESPONSE frame], and all flags are 0. You can see the response from the echo service below. 
```
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 12 00 00 00 01 28 60 48 65 6c 6c 6f 20 57 |.......(`Hello W|
|00000010| 6f 72 6c 64 21                                  |orld!           |
+--------+-------------------------------------------------+----------------+
```
The response frame is of the same length, but the type is now [PAYLOAD frame] with an identifier of 0x0A. Two flags, the (N)ext, and the (C)omplete flag are both set to 1, indicating the availability of payload data in the frame and the completion of the steam. These flags trigger the invocation of reactive callbacks _onNext(payload)_ and _onComplete()_  on the subscriber on the requester side. 

Notice that the connection does not terminate after the response message. The two peers are still connected and able to initiate new interactions or streams, possibly switching requester and responder roles.

### Fire And Forget
![fire and forget](/assets/blogg/rsocket-part-1/fire-and-forget.jpg)<br>
Fire and Forget is an optimized stream where the requester is not expecting any response. This type of interaction cannot be achieved by HTTP since HTTP, by default, has a response, and even if the requester ignores the response, it is sent and processed by both peers. One useful scenario for Fire and Forget streams could be logging.
```
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 12 00 00 00 03 14 00 48 65 6c 6c 6f 20 57 |.........Hello W|
|00000010| 6f 72 6c 64 21                                  |orld!           |
+--------+-------------------------------------------------+----------------+
```
The frame type is now 0x05 [REQUEST_FNF frame]. The Stream ID is 0x00000003 since this is the second stream initiated by the client. Again all flags are set to 0.

### Request / Stream
![request stream](/assets/blogg/rsocket-part-1/request-stream.jpg)<br>
In a Request/Stream interaction, the requester sends one request, and the responder responds with a Stream of items. The stream can potentially be infinitely long. In the example here, the requester sends a "Hello World!" message and the responder echoes back the same message twice in a stream of two items. 
```
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 16 00 00 00 05 18 00 7f ff ff ff 48 65 6c |.............Hel|
|00000010| 6c 6f 20 57 6f 72 6c 64 21                      |lo World!       |
+--------+-------------------------------------------------+----------------+
```
As can be seen, the stream ID is once again incremented by two to 0x00000005. The frame type is now 0x06 [REQUEST_STREAM frame], and all flags are 0. The frame also has a field for _demand_ or "Initial Request N" that signals how many items the requester can handle. A peer uses demand signaling to enable backpressure. In this particular case, the responder signals that it can receive (0x7fffffff) items, which is the maximal amount, so in effect, no backpressure is applied.

The requester receives the response in three frames.
```
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 12 00 00 00 05 28 20 48 65 6c 6c 6f 20 57 |.......( Hello W|
|00000010| 6f 72 6c 64 21                                  |orld!           |
+--------+-------------------------------------------------+----------------+
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 12 00 00 00 05 28 20 48 65 6c 6c 6f 20 57 |.......( Hello W|
|00000010| 6f 72 6c 64 21 00 00 06 00 00 00 05 28 40       |orld!.......(@  |
+--------+-------------------------------------------------+----------------+
```
The response frames are of sizes 0x12, 0x12, and 0x06, and they all have a stream ID of 0x00000005. All three framed are of [PAYLOAD frame]s (0x0A), and the first two have (N)ext flag set, resulting in the invocation for the _onNext(payload)_ method on the requester's subscriber. The final frame has the (C)omplete flag set, resulting in the invocation of the _onComplete()_ method (observe that the first block of data contains the first frame and the second block of data includes the last two).

### Channel
![channel](/assets/blogg/rsocket-part-1/channel.jpg)<br>
The final interaction pattern is the Channel stream. This interaction opens a bi-directional channel with two potentially infinite streams between the requester and the responder. The request frame from the responder is more or less identical to the initial frame sent in the Request/Stream case except for the frame type which is now 0x07 [REQUEST_CHANNEL frame] 

```
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 16 00 00 00 07 1c 00 7f ff ff ff 48 65 6c |.............Hel|
|00000010| 6c 6f 20 57 6f 72 6c 64 21                      |lo World!       |
+--------+-------------------------------------------------+----------------+
```
Stream ID is 0x00000007, all the flags are set to 0, so frame type and flags become 0x1c00, and demand has the max value of 0x7fffffff, so in effect, no backpressure is applied. 
```
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 0a 00 00 00 07 20 00 7f ff ff ff 00 00 12 |....... ........|
|00000010| 00 00 00 07 28 20 48 65 6c 6c 6f 20 57 6f 72 6c |....( Hello Worl|
|00000020| 64 21 00 00 12 00 00 00 07 28 20 48 65 6c 6c 6f |d!.......( Hello|
|00000030| 20 57 6f 72 6c 64 21                            | World!         |
+--------+-------------------------------------------------+----------------+
```
The responder sends back three frames with sizes 0x0a, 0x12, and 0x12. The last two are [PAYLOAD frame]s (0x0A) identical to the ones sent in the Request/Stream case, but the first one is a [REQUEST_N frame] (0x08) that signals demand from the responder. Max demand (0x7fffffff) is signaled from the responder as well. So in the Channel stream, both sides can signal demand and thereby enable backpressure. The requester continues the stream with a second "Hello World!" message and then it terminates the stream.
```
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 12 00 00 00 07 28 20 48 65 6c 6c 6f 20 57 |.......( Hello W|
|00000010| 6f 72 6c 64 21                                  |orld!           |
+--------+-------------------------------------------------+----------------+
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 06 00 00 00 07 28 40                      |.......(@       |
+--------+-------------------------------------------------+----------------+
```
The requester sends another payload frame with the (N)ext flag set (0x2820), and then it terminates the stream with an empty payload frame with the (C)omplete flag set (0x2840).

The responder echoes this message twice. 
```
         +-------------------------------------------------+
         |  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f |
+--------+-------------------------------------------------+----------------+
|00000000| 00 00 12 00 00 00 07 28 20 48 65 6c 6c 6f 20 57 |.......( Hello W|
|00000010| 6f 72 6c 64 21 00 00 12 00 00 00 07 28 20 48 65 |orld!.......( He|
|00000020| 6c 6c 6f 20 57 6f 72 6c 64 21 00 00 06 00 00 00 |llo World!......|
|00000030| 07 28 40                                        |.(@             |
+--------+-------------------------------------------------+----------------+
```
It sends two payload frames with "Hello World!" and (N)ext flag set (0x2820) and finishes with an empty payload frame with (C)omplete flag set (0x2840), which terminates the stream from the responder.

### Conclusions
In this post, I have shown how the reactive concept maps into the RSocket protocol. The callbacks _onNext_ and _onComplete_ of the Subscriber interface translates from the flags in the payload frame. I didn't show it, but there is also an [ERROR frame] (0x0B), that translates to an _onError_ call in the subscriber. I have also shown how demand signaling between the peers results in backpressure. In the next blog post, I will show how you can use RSocket, with code examples in Java.
