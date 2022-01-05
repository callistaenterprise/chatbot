---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Energy monitoring with AWS services and Go, part 3.
authors: 
  - eriklupander
tags: "aws lambda go golang cdk timestream tibber watty gonum go-echarts"
topstory: true
comments: true
---
This is the third part of a short [blog-series](https://callistaenterprise.se/blogg/teknik/2021/04/13/energy-meter-with-aws/) about using CDK and AWS services to build and deploy a personal solution for monitoring electricity usage. This part is just a little follow-up on how the solution is doing, some improvements and most importantly - the costs I've been billed since the solution's inception back in april.

-[readmore]-

{:.no_toc}
* This line will be replaced with the {:toc}
{:toc}

The full CDK and Go source code for this project can be found here: [https://github.com/eriklupander/powertracker](https://github.com/eriklupander/powertracker)

_Note: I am in no way affiliated with or working for Tibber, Easee, AWS or any other company or service provider mentioned in this blog post. I'm only doing this for educational purposes and personal enjoyment._

# 1. Solution overview
As a short recap from [part 1](https://callistaenterprise.se/blogg/teknik/2021/04/13/energy-meter-with-aws/), here's the system overview:
![img alt](/assets/blogg/powertracker/powertracker.png)

# 2. How are we doing?
So, since april 2021, my "recorder" lambda has happily been executing every five minutes, setting up that short-lived GraphQL subscription against the Tibber API, recording the electricity usage and storing the retrieved value in the AWS TimeStream database.

Here's an excerpt from september in the new HTML report:

![html report](/assets/blogg/powertracker/full-september-html.png)

And here's a goplot graph from the first half of september:

![goplot](/assets/blogg/powertracker/half-september-png.png)

While the usefulness of this data can be argued, one can clearly see that due to pandemic work-from-home and limited travelling, we're not charging our electric vehicle very often. However, when we do charge it - we're indeed pulling the max 11 kW AC current the EV accepts with a bit to spare on my house's 20A main.

# 3. The HTML report
As seen above, I've added HTML-based reporting based on the awesome [https://github.com/go-echarts/go-echarts](https://github.com/go-echarts/go-echarts) library.

The overall solution for serving these new HTML reports works pretty much the same as the existing goplot reports, i.e:
1. Load time-series data points from AWS TimeStream given the date range passed using HTTP request parameters.
2. Use [https://github.com/ahmetb/go-linq](https://github.com/ahmetb/go-linq) to aggregate data points according to the request parameters.
3. Pass the aggregated data as [time series](https://github.com/go-echarts/go-echarts/blob/master/charts/bar.go#L42) to the go-echarts library

Here's a code snippet showing how we transform go-linq aggregated `entries` into go-echarts `XAxis` (time) and `opts.BarData` (usage) representations before calling `Render`:
```go
    // ... of course some code before this excerpt...
	xData := make([]string, 0)
	barData := make([]opts.BarData, 0)
	for _, ex := range entries {
		e := ex
		xData = append(xData, e.Created.Format(timeFormat))
		barData = append(barData, opts.BarData{Value: toFixed(e.CurrentUsage, 2)})
	}

	// Put data into instance
	bar.SetXAxis(xData).
		AddSeries("Power (Wattage)", barData)

	out := new(bytes.Buffer)
	err := bar.Render(out)

    // ... and of course some more code afterwards as well!
```
This blog post isn't meant to be a go-echarts tutorial, so if you're interested in that, check out their [github repo](https://github.com/go-echarts/go-echarts).

go-echarts can do all sorts of neat stuff, including both bar-charts as seen above, as well as this line-chart with min/max/mean values plotted on data from May 2021.
![may line html](/assets/blogg/powertracker/may-line-html.png)

# 4. Cost
This is actually the main reason for this little follow up. How much has this little solution set me back over the last 6 months or so?

As a recap, the solution is built on the following AWS services:
* AWS API Gateway
* AWS Lambda
* AWS TimeStream
* AWS EventBridge
* AWS Secrets Manager
* _(provisioned using AWS CDK)_

How many records have we ingested into AWS TimeStream? A simple query tells us:
```sql
SELECT COUNT(*)
 from powertracker.power_record pr

43686
```
_(As a sidenote, my [Watty](https://tibber.com/se/store/produkt/watty-smart-energimatare) energy monitor has silently crashed a few times including most of july - requiring a manual reboot to produce data again - so there's actually fewer records than there should be given the time frame)_

The exact number of lambda execution milliseconds I've used isn't that high, since each full "recorder" invocation uses less than 300 ms on average. `12 calls/hour * 24h * 30 days` equals approx 8640 `recorder` calls per month, which keeps me well within the AWS lambda free tier. As far as I can tell - the API Gateway and Lambda calls has this far been basically free of charge. 

The numbers of the AWS billing report should speak for themselves:

![cost](/assets/blogg/powertracker/cost.png)

Yes, those numbers are correct. On average, the solution used sets me back **less than $0.5** per month. And of those ~50 cents, the majority stems from my single AWS Secrets Manager secret and the tax that entails. S3 for storing my Go-based lambdas is just a few cents per month (about 20 Mb totally for the two Go-based lambdas packaged as docker images). AWS TimeStream billing is even less, perhaps in the single-cent range. I guess AWS TimeStream is usually used for storing substantially larger amounts of data, as well as running queries much more often than I do.

# 5. Summary
That's it for this little update. The solution is humming along nicely and not setting me back by even a dollar per month. 

I've yet to expand on the solution with some cool integrations including electricity pricing, price-optimized charge schedules and perhaps trying to access the VW API that can tell me the State-of-Charge on my car. Perhaps I'll get around to that sometime. 

In the meantime, I'm currently collecting some data on public fast DC-charger availability over time, since my travels this past summer revealed that the main issue here in Sweden with non-Tesla EVs isn't EV range or max DC charge speed - it's charger availability and being able to forecast charger availability on a longer trip may very well save both time and reduce frustration in my future travels. Hoping to get back to you on that in an upcoming blog post!
