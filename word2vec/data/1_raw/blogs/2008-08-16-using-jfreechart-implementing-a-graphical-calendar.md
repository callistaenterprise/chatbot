---
layout: details-blog
published: true
categories: blogg teknik
heading: Using JFreeChart implementing a graphical calendar
authors:
  - annicasunnman
tags: opensource
topstory: true
comments: true
---

I am amazed each time I am working with timestamps and calendars - how hard can it be? It's hard to meet all requirement since each person is used to their own calendar. Latest I been implementing a calendar, to be displayed graphcial, in [Eclipse RCP](/blogg/teknik/2007/09/15/overraskande-positiva-erfarenheter-fran-eclipse-rcp/).

Imaging a calendar that is representing working hours for a factory or shop, the working hours is represented in duties and breaks that is represented in the database in open intervals. A day could look like:

- Monday 08:00-12:00
- Lunch: 12:00-12:45
- Afternoon: 12:45-17:00

Then of course each day of a year is not equal to another - Christmas is a thing that happens each year, I have heard. Another thing that could affect the normal calendar is of course meetings, education etc. So besides the normal duty and open times we need to have some kind of deviation handling.

The easy deviation - close down whole days, for example on Christmas eve is one type of deviation. Another type of deviation is when someone has a birthday for example - cake break! Then you need to add deviations to just close hours and minutes, so you have your original schema with duties and breaks, and then add an extra cake break:

- Monday 08:00-12:00
- Lunch: 12:00-12:45
- Afternoon: 12:45-15:00
- Break: 15:00-15:30
- End day: 15:30-17:00

In the data base the open intervals will be saved in only the open interval:

1. 08:00-12:00
2. 12:45-15:00
3. 15:30-17:00

To show this graphical I am using [JfreeChart](http://www.jfree.org/jfreechart/). There are some good graphical samples to download. The samples code is only "free" for those who buy a licence for the development tool.

It was quite easy to implement an easy Gantt renderer to get the first outline.

_Bild saknas_

Code if someone is interested:

~~~ java
TaskSeries taskSeries = new TaskSeries(new Timestamp(viewStart.getTime()).toString());

Date startChart = new Date(viewStart.getTime());
Date endChart = new Date(viewEnd.getTime());
Task task = new Task("", startChart, endChart);

// Loop data and add the dates to get the open times
for (OpenTime open : openTimes) {
  Timestamp localstarttime = DateFormat.getLocalTime(open.getStart());
  Timestamp localstoptime = DateFormat.getLocalTime(open.getEnd());
  Task subtask = new Task("", new Date(localstarttime.getTime()),
      new Date(localstoptime.getTime()));
  task.addSubtask(subtask);
}

JFreeChart chart = ChartFactory.createGanttChart("", "", "", dataset, false, true, false);
GanttRenderer renderer = (GanttRenderer) chart.getCategoryPlot().getRenderer();

chartComposite.setChart(chart);
~~~

There is some default zooming out and in on the calendar that works instant. But the calendar is not that functional only showing the open times in green:

_Bild saknas_

I added tooltip when hovering over the green open times to display more information about each duty. Unfortunately the business wants information about the red part sometimes, when a deviation is added on normal open time. That I haven't solved yet. Since the chart is based on the open times, I am not sure if it is possible to add information about the closed times without changing the setup in the database.

To improve the display and show more information about each duty and break I added tooltip when mouse hovering over the green open times. The tooltip generator was not complete for the default implementation so I implemented my own with ids for each open times:

_Bild saknas_

The implementation of Jfreechart is quite straight forward, but as always when using a new tool it takes times to get the finish of the graphical layout. It was a lot of trial and error the see what happens each time you change a setting or property.

We are not sure if this will be enough for the business to display the calendar - the JfreeChart was probably not the best tool to show a calendar. But we will try it for the first release and then investigate what the business use and not use. JfreeChart have a lot of renderer to display other charts in various ways, look into the samples on the [homepage](http://www.jfree.org/jfreechart/).
