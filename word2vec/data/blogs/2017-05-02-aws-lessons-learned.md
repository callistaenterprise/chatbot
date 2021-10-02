---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Lessons learned from a year with AWS.
authors: 
  - jonasbehmer
tags: aws cloud lambda elasticsearch faas kinesis 
topstory: true
comments: true
---

For more than a year, since the end of 2015, I’ve been working on a project based on [Amazon web services](https://aws.amazon.com) (AWS). One important design decision for the project was to not allow any “traditional” servers in the backend as the customer wanted to move away from maintaining servers on their own, thus we aimed to be serverless. Cloud container platforms like [AWS EC2](https://aws.amazon.com/ec2/) was off limits to us and that meant that [AWS Lambda](https://aws.amazon.com/lambda/) was the only option we had.

All though my lessons learned might be perceived as being sligthly negative that is by no means representative for my overall experience which in contrary has been overwhelmingly positive. Using Lambda, for instance, has been most rewarding and has just worked with very little hassle. The support for [Node.js](https://nodejs.org/en/), that we use, has been first rate with really no breaking changes.

## Don’t build your own build and deploy tool
Unfortunately we had to build our own build and deploy tool due to the lack of options back in 2015 and now we have to live with all of its warts. We would, if we could, move out of it in an instant. Today when we create new subprojects we use the [Serverless framework](https://serverless.com). Serverless will make it a breeze to deploy and abstracts away the boring [AWS Cloudformation](https://aws.amazon.com/cloudformation/) templating stuff in a nice way. Serverless also comes with a plethora of community contributed [plugins](https://github.com/serverless/plugins) that cater for all kinds of specific needs that aren’t covered by the core plugins.

## Modularize your deployment resources
We provision all AWS resources we need in a single cloudformation stack, thus we have no modularization to speak of. I guess this monolithic approach is how many projects start out but in hindsight it would have been wise to break out resources that seldom change into their own stacks, e.g. [Elasticsearch](https://www.elastic.co) clusters. A modular approach would also allow for easier additions of new functionality and reuse of existing cloudformation templates. The cloudformation template we are sitting on today is a monster in size.

## You can't use kinesis if you have near realtime expectations
[AWS Kinesis](https://aws.amazon.com/kinesis/streams/) caters for all of your streaming needs and it is a great tool when you need to handle big amounts of data. It is probably also the cheapest way of shuffling that same data out of an AWS account. However, when you have flows that need to be near realtime (NRT) you can’t really use kinesis as it will add a considerable amount of latency to your flow. Used in conjunction with Lambda we have, at best, been able to get down to 1000 ms added latency. If your application doesn’t have the need for NRT events, then there is nothing better to use than Kinesis.

We use [MQTT](http://mqtt.org), through [AWS IoT](https://aws.amazon.com/iot/) for our NRT purposes. Using MQTT is also, at the time of writing, the only way of setting up websockets in a truly serverless fashion, i.e. without provisioning an EC2 instance to handle it.

## Use API Gateway in front of Lambda
Our API is based on a client directly invoking a lambda and not going through [AWS API Gateway](https://aws.amazon.com/api-gateway/) at all.
I would have preferred a REST API on top of the lambdas. I think the purpose of API Gateway is well put in the following quote:

> Amazon API Gateway handles all the tasks involved in accepting and processing up to hundreds of thousands of concurrent API calls,
> including traffic management, authorization and access control, monitoring, and API version management.

Thus, API Gateway is about handling the http side of things and lambda is about doing your backend chores. That we use lambda is really an implementation detail and nothing you want the user of your api to adhere to.

## Get your Lambda error handling correct
It has happened to us on several occasions that a kinesis stream has filled up without any records being processed due to a payload in one record causing the lambda to throw an error. Not taking care of the error inside of the Lambda means that the same kinesis batch will be processed over and over, until it is removed automatically when it falls out of kinesis 24 hour gliding window.

I think that non returning lambdas that aren’t part of a traditional request/response flow nearly always need to handle all errors inside of the lambda to avoid getting stuck and use a [dead letter queue](https://en.wikipedia.org/wiki/Dead_letter_queue) (DLQ) for those requests that can not be processed by the lambda. Typically an event is, after a certain number of retries, automatically moved to the DLQ.

## You will suffer if you use Lambda with RDS
In one subproject we used Lambda in conjunction with [AWS RDS](https://aws.amazon.com/rds/), i.e. a relational database service. There is a definitive upside to this in that it enables local testing by allowing you to run an in memory db in place of the real db.
The biggest issue we have had with this, and this is a big one in my opinion, is that your Lambda have to run in the same virtual private cloud (VPC) as the RDS instance, in effect forcing you to do lots of VPC configuration. This turned out to be non trivial and I would rather not do it again. If you do it wrong, like I did, you will lose public access to internet and soon you’ll start wondering why services like [AWS KMS](https://aws.amazon.com/kms/) has ceased to work all of a sudden.

The statefulness of database connection pooling is another thing that goes against the grain of the Lambda stateless nature. For the time being I consider [AWS DynamoDB](https://aws.amazon.com/dynamodb/) to be the best fit for usage with Lambdas if you truly want to stay as close to a serverless vision on AWS. DynamoDB of course it has its own quirks and it is obviously not a relational db either.

## You will have to deal with AWS limits
The are a big list of [limits](http://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html) for AWS Accounts. Some of these limits are hard ones, meaning there is no way you can change them and then there are soft limits that you can change, like how many concurrent lambdas you can have. Unfortunately it is not always possible to know, by the list itself, wether or not a particular limit is hard or soft. Only by asking a support contact at Amazon will, hopefully, give you the answer.

The hard lesson we’ve learnt, regarding limits in AWS, is that you will run in to limits and it will be the ones you least expect. So take a good look at the limits and have a plan from the beginning.
