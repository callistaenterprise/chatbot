---
categories: blogg teknik
layout: "details-blog"
published: true
topstory: true
comments: true
heading: A first look at PacketBeat
authors: 
  - hansthunberg
---

We have a new fish in the pool! PacketBeat has joined the [elastic](https://www.elastic.co/) company as an open source data shipper and analyzer of network packets, integrated with the [ELK stack](/blogg/presentationer/2015/01/28/elk/).

-[readmore]-

![PacketBeat](/assets/blogg/PacketBeat/packetbeat.png)

## Short recap on the ELK stack

In [CADEC 2015](https://callistaenterprise.se/event/cadec/2015/) we had a talk on addressing the problem with IT organizations that don’t have enough insight in whats happening in their system landscape. Typical reasons for these problems are technical challenges when it comes to distributed applications, restricted access to environments and correlating events.

We introduced [monitoring logs in real time using the ELK stack](/blogg/presentationer/2015/01/28/elk/) (Elasticsearch, Logstash and Kibana) as an open source alternative for collecting, indexing, searching and analyzing log data.

## Introducing PacketBeat

Just recently the [elastic](https://www.elastic.co/) company introduced the [Beats](https://www.elastic.co/products/beats) platform, data shippers for elasticsearch, starting with [PacketBeat](https://www.elastic.co/products/beats/packetbeat). 

[PacketBeat](https://www.elastic.co/products/beats/packetbeat) is a lighweight network analyzer, a shipper for collecting network metrics. It enables the possibility to sniff for network packet data to be able to monitor performance, find problems and analyze trends in the different network protocols used. Similar functionality can be found in tools like [Wireshark](https://www.wireshark.org/) and [Tcpdump](http://www.tcpdump.org/).

Some of the capabilities is to
- Capture network traffic between application servers
- Decode application layer protocols (HTTP, MySQL and Redis already exists, MongoDB is on the way to be released)
- Correlate requests and responses in network transactions

[PacketBeat](https://www.elastic.co/products/beats/packetbeat) comes with
- an agent to be installed on the servers
- predefined [Kibana 4](https://www.elastic.co/products/kibana) views to help monitoring the network events

![elk_packetbeat.jpg](/assets/blogg/PacketBeat/elk_packetbeat.jpg)


Other Beats implementations are discussed in the active community, for example FileBeat (replaces existing logstash-forwarder) and other upcoming {Future}Beats.

### Monitor MySQL
PacketBeat enables monitoring of the MySQL protocol, used between MySQL clients and MySQL servers, to get information like:
- Number of errors
- Methods used (SELECT, INSERT, etc)
- Reponse times
- Throughput

This enables us to monitor and identify:
- Queries taking long time
- The amount of queries executed
- The relation between reads and writes in the database

In [Kibana 4](https://www.elastic.co/products/kibana) the throughput can be visulaized like this:

![mysql-throughput.png](/assets/blogg/PacketBeat/mysql-throughput.png)


### Monitor HTTP
PacketBeat enables monitoring of the HTTP protocol to get information like:
- HTTP codes
- Methods used (GET, POST, etc)
- HTTP headers used
- Client IP address

This enables us to monitor and identify:
- Total number of web transactions
- Trends on errors
- Latency

In [Kibana 4](https://www.elastic.co/products/kibana) the number of web transactions can be visulized like this:

![webtransactions-sum.png](/assets/blogg/PacketBeat/webtransactions-sum.png)

Or, why not visualize the number of transactions based on clients ip address and geographical location:

![webtransations-geo.png](/assets/blogg/PacketBeat/webtransations-geo.png)

## Summary
We have been introduced to [PacketBeat](https://www.elastic.co/products/beats/packetbeat), a tool integrated in the [ELK stack](/blogg/presentationer/2015/01/28/elk/) to collect various network metrics. In a distributed and complex environment this can help IT organizations to do analytics and identify trends based on events occurring in the network layers. Together with [Kibana](https://www.elastic.co/products/kibana) we can visualize the network metrics and events to get a good overview on what's happening in the system landscape. When writing this blog post PacketBeat was still in 1.0.0-Beta1.
