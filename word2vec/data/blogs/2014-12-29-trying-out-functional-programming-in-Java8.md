---
layout: details-blog
published: true
categories: blogg teknik
heading: Trying out functional programming in Java 8
authors: 
  - magnuslarsson
tags: java8 functional-programming lambda-expression stream-api
topstory: true
comments: true
---

I guess you have noted that [functional programming](http://en.wikipedia.org/wiki/Functional_programming) is gaining popularity?

## Object model and query API

![](/assets/blogg/trying-out-functional-programming-in-Java8/model.png)

I decided to write a query API that could be used to answer the following questions:
public interface QueryApi {

public List<Product> getProductsByDateAndCategoryOrderByWeight(

    int minOrderValue, int maxOrderValue, int minProductWeight, int maxProductWeight) {


    LocalDate minDate, LocalDate maxDate, String category) {


>

    int minOrderValue, int maxOrderValue, int minProductWeight, int maxProductWeight) {







