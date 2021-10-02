---
categories: blogg teknik
layout: details-blog
published: true
heading: Using Metrics To Manage Risk in a CD Environment
authors: 
  - martinholt
tags: metrics microservices
topstory: true
comments: true

---

Working in a continuous delivery environment can feel a little daunting - any changes you make will be rapidly delivered 
to your production environment. Although the intention is to provide immediate benefit for your customer, without proper 
risk management there is a real risk of exposing bugs and triggering outages. In this blog post I will look at one strategy 
that uses metrics to reduce those risks.

# Scenario
The scenario starts with a familiar email:

> "Hi team. According to us you are consumers of V1 of our service. We have just released V2 which includes a wealth of 
> great new features. We have deprecated V1 and would appreciate your help to remove this as soon as possible".

Our application used V1 to fetch data to provide a rich customer experience. In certain cases the data was not available 
and to handle this we applied a fallback. This feature was not mission critical but as we were proud of our customer 
experience we much preferred the rich data over the somewhat ugly fallback.

# Risks
As we had a little time to spare we decided to prioritise the migration to V2. This meant that we would be the first users 
of V2 in a customer facing environment. Being early adopters carried with it the risk that we would be exposed to any 
unfound bugs in the new service. 

The API itself had been restructured - fields had been renamed, moved and extended. After some discussions with the service 
providers and after a few manual experiments we made some assumptions about the behaviour of V2. These assumptions were 
difficult to test in our staging environment and could only first be proven when running at scale in production. If our 
assumptions were incorrect then the customer would be the first to know.

# Migration Strategy
With these risks now identified we decided that switching from V1 to V2 in a single step was not an option. We decided 
to split the migration into a number of small steps where any negative consequences of the migration could be hidden from 
the customer until we were happy we had gotten it right. Each step was considered complete when the content of that step 
had been delivered to the production environment. As a side note this strategy allowed the team to re-prioritise as other 
needs arose without blocking the delivery pipeline and without the need for complex merges in a migration branch.

The first step was to add an endpoint to our application where internal users (not customers) could make a call that in 
turn only called V2. This step allowed us to test our client code and configuration - here we picked up, for example, that the 
credentials used by V2 had been deployed incorrectly which would have caused an outage had we been running at scale. 

# Adding Metrics To The Mix
We were now ready to run V2 at scale however we were still worried about whether the service would behave as we had 
assumed. To deal with this we decided to call both V1 and V2, to expose the result of V1 to the customer and to throw 
away the V2 result. We added a metric - in this case a [Counter](https://micrometer.io/docs/concepts#_counters) - 
to distinguish whether our V2 call managed to fetch rich data or was forced to choose the ugly fallback response. 
This [Counter](https://micrometer.io/docs/concepts#_counters) was then transformed into a 
[Hit Rate](https://en.wikipedia.org/wiki/Hit_rate) (over a given time interval):

    Hit Rate = sum of rich responses / (sum of rich responses + sum of fallbacks)

The Hit Rate was added to one of our dashboards and displayed prominently on a monitor for the entire team to monitor.

We now realised that we had never determined a lower boundary for an acceptable Hit Rate, or gone as far as to formalise this 
metric as a service level indicator (for more on SLIs see the 
[Google Site Reliability](https://landing.google.com/sre/sre-book/chapters/service-level-objectives) book). 
Instead we guessed - a Hit Rate of 95% would be acceptable to us. Imagine our shock when the Hit Rate for V2 
fluctuated as low as 60%!

Obviously something was not behaving as expected, but was the result for V2 better or worse than V1? After a quick 
retrofit to add metrics to V1 we found a Hit Rate of around 80% - still significantly less than our lower boundary of 95% 
but notably better than V2. With the help of some targeted logging we could then locate a number of bugs in the V2 service 
and identify some incorrect assumptions in our application. We even located a bug in V1 that had crept into V2. 
After these fixes the hit rate of V2 was consistently above 95%.

Before exposing our customers to V2 we monitored the Hit Rate for a period of time 
to see how our application behaved during the peaks and troughs of our business cycle. This involved no effort other 
than casting an occasional glance at our dashboard. A few requests were timing out at peak traffic but this was easily 
resolved by adding a number of retries and did not significantly impact the Hit Rate.

# Moving to V2
Now we felt confident that we could expose the customer to V2 and to remove V1. The switch was made and we continued 
to monitor the Hit Rate of V2. Migration had been a success and the customer actually ended up with a richer experience than 
they had before without being exposed to any bugs or outages on the way!

# Cleaning up
The final step was to perform some clean up. We removed our V1 client and informed the service providers that 
they could safely revoke our credentials and mark us as migrated. 

We also removed the metrics associated with the Hit Rate for V2. This feature was not considered mission critical. 
The effort required to maintain and monitor the Hit Rate was not justifiable - there was always the risk that by 
keeping the metric on the dashboard any visible degradation would trigger effort that may be better applied to more 
mission critical activities.

# Conclusion
By using metrics we were able to confidently make potentially risky changes, at each step gauging the impact quickly and 
visibly in a production environment yet without harming the customer experience. These metrics allowed us to learn about 
the behaviour of the new service. These learnings were used both to plan our next step and to provide feedback to the service provider allowing them in turn to improve quality for all consumers. Although this process contained significantly 
more steps than a [big-bang adoption](https://en.wikipedia.org/wiki/Big_bang_adoption) the effort involved was not 
significantly different (monitoring dashboards is not considered as effort) and avoided the uncertainties and stress 
associated with a rollback had things gone wrong.