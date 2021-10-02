---
layout: details-blog
published: true
categories: blogg teknik
heading: Apache Cassandra and time series with TimeUUIDType in Java
authors:
  - peterlarsson
tags: apachecassandra java opensource
topstory: true
comments: true
---

As almost everybody knows; one of the main benefits with Apache Cassandra is the possibility to create column indexed time series, i.e. use `TimeUUIDType` as comparator and you get a chronologically arranged list of indexed column names and an excellent performance when performing slice queries.

-[readmore]-

> If millisecond precision is good enough for you to create an unique id, then you might skip the rest of this article.

However Apache Cassandra uses UUID of type 1, and `java.util.UUID` has poor support for this type. Fortunately a utility class [com.eaio.uuid.UUIDGen](https://github.com/stephenc/eaio-uuid) created by Johann Burkard  can be used to create unique `java.util.UUID` of type 1, and this utility also is included in the Hector Client API.

~~~ java
...
// create a unique java.util.UUID of type 1, and use it to create a column name (Hector API)
UUID uuid = new UUID(UUIDGen.createTime(timestamp), UUIDGen.getClockSeqAndNode());
HColumn<UUID, Composite> column = HFactory.createColumn(uuid, <some_value>,
    UUIDSerializer.get(), CompositeSerializer.get());
...
~~~

## The problem
Now I wan't to query my columns, and the main question is; how do I create a `java.util.UUID` of type 1 to position my slice query in the column name index?

`UUIDGe`n is designed to generate unique times (nano), but the actual algorithm to create a corresponding query `java.util.UUID` is not provided, i.e. `UUIDGen` can only be used to create new unique `java.util.UUID` column names. There's actually an implementation in `me.prettyprint.cassandra.utils.TimeUUIDUtils`, but this method  is private, so this class can calculate the original timestamp in millis, but can't help out creating UUID for queries.

## The solution
To solve the problem, I had to copy the actual unique time generation from `UUIDGen` and remove the stuff that makes the generated time unique, and then it was pretty simple to create `java.util.UUID` that could be used in my queries. Furthermore to retrieve the original timestamp in millis the helper `TimeUUIDUtils.getTimeFromUUID` fix this for you.

### Steps
1. Create a unique UUID based on an origin timestamp in millis with `UUDIGen` and use this as a column name
2. Create a query UUID with your own `createQueryTime` described  below.
3. Retrieve the actual origin timestamp in millis with `TimeUUIDUtils.getTimeFromUUID`

> Pretty heavy stuff to perform such a simple task, and please enlighten me if I've missed something fundamental!

Method to use to cerate query UUIDs:

~~~ java
private static long createQueryTime(long currentTimeMillis) {
  long time;
  final long timeMillis = (currentTimeMillis * 10000) + 0x01B21DD213814000L;
  time = timeMillis << 32;
  time |= (timeMillis & 0xFFFF00000000L) >> 16;
  time |= 0x1000 | ((timeMillis >> 48) & 0x0FFF); // version 1
  return time;
}
~~~

And now it's just to start browsing the column name index with timestamps that means something like log record timestamps etc.

~~~ java
...
UUID queryUUID = new UUID(createQueryTime(timestamp), UUIDGen.getClockSeqAndNode());
SliceQuery<Composite, UUID, Composite> query = HFactory.createSliceQuery(getKeySpace(),
    CompositeSerializer.get(), UUIDSerializer.get(), CompositeSerializer.get());
query.query.setColumnFamily("someCF").setKey(someKey);
query.setRange(queryUUID, null, false, 100);
...
// use TimeUUIDUtils to get the original timestamp in millies
...
long timestamp = TimeUUIDUtils.getTimeFromUUID(col.getName());
...
~~~

> Finally

See also this [article](http://blog.nikhilism.com/2012/04/apache-cassandra-iterate-over-all.html) for a nice way to iterate over a lot of columns, at least with some modifications attached.
