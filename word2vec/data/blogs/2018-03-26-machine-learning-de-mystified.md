---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: Machine Learning de-Mystified
authors:
  - davidstrom
---
Too often when I hear someone talk about artificial intelligence (AI), or more recently machine learning (ML), the Terminator/Matrix scenario is repeated, a warning that we shouldn't meddle with powers we don't understand and that the consequences of not adhering to this warning can be dire indeed.

This bothers me a little. I don't mean to say that AI/ML won't ever pose a risk in the future (I still think we have a long way to go before the Matrix or Terminator situation though), but what bothers me is that I think this fear has the telltale signs of _a fear of the unknown_. AI and machine learning are seen as something mysterious and therefore threatening, concepts shrouded in mystique and understood only by a few Gnostics of the AI/ML cult. I don't think it has to, or should be, that way.

So, what is machine learning? How does it work? What are the real risks? By diving into these questions, and maybe some new ones on the way, I think we can shred the clouds of mystique and start to look at machine learning in a more rational way.


## What is Machine Learning?
[Tom Mitchell](https://en.wikipedia.org/wiki/Tom_M._Mitchell) coined the following definition of machine learning in 1998: _"A computer program is said to learn from experience E with respect to some task T and some performance measure P, if its performance on T, as measured by P, improves with experience E"_. Now, I can't argue with that definition, but allow me to elaborate a bit. Machine learning, including deep artificial neural networks, are algorithms that can be adapted to process widely diverse input data and still produce the desired expected output. An ML algorithm can even be expected to produce the desired output for inputs it has never before encountered. This is possible because ML algorithms, during their adaptation - or training - phase, are made to identify the underlying patterns of the input data and its correlation with the desired output.

What machine learning is not, is something sentient - or mysterious for that matter. Something that has its own will and desires. I think that there is a great risk of inferring more meaning into the words machine learning and artificial intelligence than what is really there, and thereby create a growing-ground for misconceptions about this group of algorithms. One big problem is of course that we still don't really know or understand from where all our own wants and desires originate, and that means that we are hard pressed to answer if machines through some advanced algorithms will ever develop wants and desires for themselves. But that is food for an endless philosophical debate and another blog post.  

## How Does it Work?

First of all, an exhaustive detailed analysis of the machine learning field is obviously too much to cover in a single blog post, but I will attempt to cover the common aspects of the most common ML algorithms (logistic and linear regression, artificial neural networks, k-means, support vector machines). Note that I will not delve into any of the functions that are used by these algorithms, such as different cost or optimization functions. In this blog post I will try to keep things simple and general, in later ones I will dive into more specifics regarding certain algorithms and tools.

One thing is very important though, if you, like me, come from a software developer background your focus has probably been on the implementation of algorithms (i.e. the program code), in machine learning though, the data really comes into play. Bigly.

Machine learning starts with the assumption that there is some correlation between data that you have, or are in a position to acquire, and whatever it is your ML algorithm is expected to produce, but that this correlation is difficult to capture solely in program code. However, it might be possible to capture using a combination of arithmetic calculations and the right, and right amount of input data.

### Starting a Machine Learning Project
Before we go into the workings of the ML algorithms it is important to understand that machine learning involves a lot more than just passing a bunch of data through an intelligent algorithm and then you somehow - magically - get the output you desired. Now, you are of course free to run your ML project as you see fit, but in one way or another we all need to at least consider the following activities (note that depending on your project time frame and problem domain many more activities might be appropriate or even necessary).

#### Data Collection and Selection
What data do you have available and what data is relevant to your task? You might have some databases you can tap for data, but also log files, some external but available data are good potential sources. What data you can use for your algorithm will have a great impact on the performance on your machine learning task, so spend time on this and try different datasets, can you simulate some data that you might not have?

It is also important to practice, and eventually get comfortable with, data visualization. It is by visualization many key features of your data will become apparent.

#### Preprocessing the Data
When you have a relatively good notion about the data you want to use in your machine learning algorithm it is time to look at how the data should be fed to the algorithm. This can involve for example some cleaning, formatting, sampling and grouping of your data.

Cleaning of data is the task of dealing with incomplete data and data that you suspect might be faulty. When it comes to missing data the question is if you should attempt to estimate the missing values or discard that data altogether and when it concerns suspiciously looking data you have to ask yourself if you trust the data or not? ... Well, do you?

Formatting is somewhat simpler, basically making sure the data is in a format that is understood by the algorithm.

Sampling and grouping the data concerns making sure you have representative data covering the as much as possible of the problem domain, and that you have data that can be used for training, cross-validation, and testing.

#### Data Transformation
After having preprocessed your data you might actually be ready to start training your machine learning algorithm, but in order to get even better results some data transformation activities might come in handy. Data transformation involves e.g. scaling, aggregation, decomposition, and synthesizing of data.

Scaling is about making sure the values across different features are on a similar value scale. This ensures that no one single feature becomes overly dominant in the machine learning algorithm.
Aggregation and decomposition of data involves turning multiple features into one or vice versa, also known as feature engineering. This is about finding the features that are really relevant to your task, e.g. if you have the times a user logged in and logged out from your system you might want to aggregate those into a feature that tells you for how long the user was logged in. 

Decomposition of features is used for the same reason but require that you can deconstruct the data into its constituent parts. An example of data decomposition could be to break down email addresses into the part before the @-sign and the internet domain part, or datetime values into distinct date and time values.

Synthesizing data might not be the most common of techniques used in machine learning but useful in for example image recognition projects. Synthesizing data means to artificially create completely new data, e.g. by distorting images through the use of some image manipulation software, for example create gray-scale versions of full color images etc.

### The Workings of a Machine Learning Algorithm
Independent of which machine learning algorithm you implement they all have a few common traits that can be useful to know about. We have talked about the input data and features of the data, but how does this data look? We can think of the input data as a matrix of values, where each row represents one instance of the input data and each column a data feature. This is one such common feature between all machine learning algorithms, and one reason why all machine learning algorithms are heavily dependent on matrix operations.

Another common trait between machine learning algorithms is the use of weights to manipulate the input values. An algorithm has one weight per feature of the input data (typically plus one for bias, but let's ignore bias for now). During the training of the algorithm the weights gets updated in ways particular for each algorithm, but it is the update of these weights that eventually improves the performance of the machine learning algorithm as it is trained.

#### Different Types of Algorithms for Different Problems
The purpose of this blog post is not to delve too deep into the particulars of different machine learning algorithms, but it can be useful to point out that there are a lot of machine learning algorithms available out there, and that they are useful for different things. Typical problems suited for machine learning algorithms are forecasting/continuous value prediction and classification problems, and different algorithms have been developed to handle these problems. 

Further, the algorithms are often divided into supervised and un-supervised algorithms where supervised means that the training of the algorithm requires training data with known expected output, whereas un-supervised algorithms don't and are typically used for grouping data into clusters. Below is a small table with typical machine learning problems and some common corresponding algorithms.


| |	Supervised | Un-supervised |
| ---------- | ---------- | ---------- |
| Forecast/continuous value | Linear regression | |
| Classification | Logistic regression, Support vector machines, Artificial neural networks | K-means |

#### Training and Cost Functions
How do machine learning algorithms "learn"? I think this is key in order to de-mystify the machine learning algorithms. As mentioned above the weights of the algorithm gets updated during training and this causes the algorithm to perform better. How to they get updated? When you train your machine learning algorithm you let all your training data pass through your algorithm and record its output for each instance of training data. In case you are using a supervised learning algorithm you can then compare the output from the training run to the expected output and calculate a "cost" of using your current set of weights. In order to calculate the cost there are different cost functions you can utilize, depending on which machine learning algorithm you are using. Important to understand here is that you can use a cost function to calculate the relative cost of a certain set of weight for your algorithm.

Next, we will try to minimize the cost, or output value of the cost function by manipulating the weight parameters. Again, different functions can be utilized for this, but one so common it must be mentioned is gradient decent, which uses a typically quite small value called "the learning rate" to manipulate the derivative, or gradient, of the cost value and then subtracts this from the weights of the algorithm to make bit by bit lessen the cost and optimize the algorithm.
1. Make test run with test data. Record output.
2. Calculate cost of current set of weights by comparing real output and expected output in a cost function.
3. Manipulate algorithm weights in order to produce output closer to expected output, e.g. by using derivative of cost in a gradient decent function.
4. Repeat until the algorithm is no longer improving.

## The Real Risks of Machine Learning
There are many real and current risks with machine learning, and I will just mention a few to show there are more acute ones than machines turning us into bio-electric slaves or turn our skulls into cobble stones.

### Malicious Manipulation of Training Data
An ML algorithm will learn from its training data, but it is often very hard to see just how the algorithm reaches its final output. This makes it very difficult to detect maliciously placed backdoors or unintended flaws that causes the algorithm to respond in unexpected ways. If you are interested, this article in [Wired](https://www.wired.com/story/machine-learning-backdoors/) bring up just such a case of a maliciously placed backdoor.

### Who to Blame?
Well, we can safely assume that even the best ML algorithm will eventually get something wrong (or at least not as we humans intended it), but as long as it is better at it than a human doing the same task everything is fine, right? But what do we do when things eventually do go wrong and the consequences are serious? It is too easy to become complacent and say _"as long as the AI does the job better than a human, what's the problem?"_. But algorithms can't go to court, simply put.

### Complexity
Machine learning is a very powerful and diverse tool and being such a powerful and diverse tool, it will inevitably be put to work on many problems. This will make ML algorithms more and more pervasive in our society and in our organizations. But these algorithms are complex and hard to supervise, and things get even more complex when we combine many ML systems together to solve ever more complex problems. The problem with this is that we end up with a situation where it is extremely difficult to see how some very important decisions were made, when the data that was the basis for the decision has passed through a number of black-box ML systems on the way.

So, these are just three (of many more) very real risks or challenges with ML algorithms that we need to watch out for, if we remain cool-headed and rational and all that.

## Reflections
As I said in the beginning of this blog post I think there exist a level of anxiety about machine learning that has to do with not fully understanding how it works or even what it is. If you encounter such fears but are unsure how to counter them I hope that this blog post gives you a bit of ammunition, hopefully without too many false claims.

Finally, when I myself got interested in machine learning I tried to read as much as I could on different blogs and guides online, but I often got stuck on many (for me) new concepts and algorithms and I found it hard to get a bird's-eye view of the field. This blog is in no way an exhaustive cover of the field at any level, but I have also tried to write this blog such as I would have liked to read it when I first started looking at this field. Please feel free to leave any comments, good or bad, and thank you for reading this far.
