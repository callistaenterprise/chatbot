This week, Google's announcement of Google App Engine (GAE) got a lot of attention. The initial 10 000 test accounts ran out in a few hours.

With GAE you can run your own web application on Google's infrastructure. Initially they support applications written in Python, but more languages are already considered for future versions. Data can be persisted using the DataStore API, and there is also an API for integrating with Google Accounts. Of course, there are some limitations on what your webapp can do, this blogpost gives you a good overview of what they are.

A lot of people have already compared GAE to Amazon Elastic Compute Cloud (Amazon EC2), even though they are quite different. Amazon EC2 gives you your own VM where you can run basically whatever you want, whereas GAE only lets you run Python web applications in a sand box. The similarity, of course, lies in the fact that they both offer a way to scale your application on demand, by using infrastructure already available and proven.

GAE is certainly not as flexible as EC2; but on the other hand it seems very easy to get something up and running with GAE. Not to mention the fact that it's free. Google lets you use up to 500MB of persistent storage and enough CPU and bandwidth to serve about 5 million page views a month. If you want to scale beyond that, you'll have to start paying. Currently it is not official how much it will cost, the preview version released so far only covers the limited free accounts.

For small web applications, traditionally hosted in shared environments, the GAE approach is very appealing, if you're not too afraid of the lock in and can live with the limitations.

It will be interesting to watch the evolvment of GAE as well as EC2 in the future.
