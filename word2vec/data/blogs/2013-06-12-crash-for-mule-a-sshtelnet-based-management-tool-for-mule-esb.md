---
layout: details-blog
published: true
categories: blogg teknik
heading: CRaSH for Mule, a ssh/telnet based management tool for Mule ESB
authors:
  - magnuslarsson
topstory: true
comments: true
---

Earlier this year David Dossot announced the availability of [CRaSH for Mule](http://blog.dossot.net/2013/02/crash-for-mule-introduction.html), an open source based command line management tool for Mule ESB based on remote access using either plain telnet or ssh. It relies on the management functionality exposed by Mule ESB via JMX but makes it so much easier to use compared to direct JMX usage with JConsole et al. On the other hand, as David clearly points out, CRaSH for Mule is far less capable then the very powerful Mule Management Console that comes with Mule ESB EE. Read Davids [blog](http://blog.dossot.net/2013/02/crash-for-mule-introduction.html) for more background info.

Let's try it out!

-[readmore]-

## Installation
First we need to install it :-)

That's really a no-brainer, just download, extract and deploy as a Mule App!

1. Download [crash-1.2.6-mule-app.tar.gz](https://code.google.com/p/crsh/downloads/detail?name=crash-1.2.6-mule-app.tar.gz).
2. Extract its content
3. Locate the app, `crash-mule-app.zip`, in the extracted content and copy it to your running Mule instance apps-folder and it will auto-deploy (as usual)

## Start the tool and get a list of commands
Since I prefer ssh over telnet I'll go with that (use password `mule`):

~~~
$ ssh -p 4022 -l root 33.33.33.33
root@33.33.33.33's password:
 ______
 .~      ~. |`````````,       .'.                   ..'''' |         |
|           |'''|'''''      .''```.              .''       |_________|
|           |    `.       .'       `.         ..'          |         |
 `.______.' |      `.   .'           `. ....''             |         | 1.2.6

Follow and support the project on http://www.crashub.org
Welcome to singleserver.local + !
It is Wed Jun 12 08:41:04 UTC 2013 now

%
~~~

To see the available commands simply submit the command "mule":

~~~
% mule
usage: mule COMMAND [ARGS]

The most commonly used mule commands are:
 app              control an application
 connector        control a connector
 endpoint         control an endpoint
 connectors       list all the connectors of an application
 endpoints        list all the endpoints of an application
 stats            print the statistics for an application or a flow within an application
 broker           control the broker
 flows            list all the flows of an application
 apps             list the names of all deployed applications
 info             print information about the broker

%
~~~

## Get info regarding mule, applications, flows and endpoints
Get info about the Mule ESB instance:

~~~
% mule info
name                value                                                                                                                                                         
--------------------------------------------------------------                                                                                                                    
Mule Version        3.3.1                                                                                                                                                         
Build Number        25116                                                                                                                                                         
Build Date          2012-Dec-10 12:56:47                                                                                                                                          
Host IP             127.0.0.1                                                                                                                                                     
Hostname            singleserver.local                                                                                                                                            
OS                  Linux (2.6.32-279.19.1.el6.x86_64, amd64)                                                                                                                     
JDK                 1.7.0 (mixed mode)                                                                                                                                            
Launched As Service true                                                                                                                                                          
Debug Enabled       false                                                                                                                                                         
Java PID            14012                                                                                                                                                         
JVM Id              1                                                                                                                                                             

%
~~~

List available applications in the Mule ESB instance:

~~~
% mule apps
name              start time                   initialized stopped                                                                                                               	 
-------------------------------------------------------------------                                                                                                               
crash-mule-app    Tue Jun 11 19:24:54 UTC 2013 true        false                                                                                                                  
default           Tue Jun 11 19:24:54 UTC 2013 true        false                                                                                                                  
vp-services-2.1.0 Tue Jun 11 19:39:54 UTC 2013 true        false                                                                                                                  

%
~~~

List what flows does the `vp-services-2.1.0 app` have:

~~~
% mule flows -a vp-services-2.1.0
name                                                                   type                                                                                                       
----------------------------------------------------------------------------

GetSupportedServiceContracts-flow                                      Flow                                                                                                       
PingForConfiguration-rivtabp20-flow                                    Flow                                                                                                       
PingForConfiguration-rivtabp21-flow                                    Flow                                                                                                       
PingService-flow                                                       Flow                                                                                                       
ServiceGroups-flow                                                     Flow                                                                                                       
crm-scheduling-GetSubjectOfCareScheduleInteraction-virtualisering-flow Flow                                                                                                       
htmlDashboardService-flow                                              Flow                                                                                                       
itinfra-tp-ping-virtualisering-1.2-SNAPSHOT-flow                       Flow                                                                                                       
log-error-receiver-flow                                                Flow                                                                                                       
log-info-receiver-flow                                                 Flow                                                                                                       
log-publisher-flow                                                     Flow                                                                                                       
log-store-receiver-flow                                                Flow                                                                                                       
resetHsaCache-flow                                                     Flow                                                                                                       
resetVagvalCache-flow                                                  Flow                                                                                                       
vagval-dynamic-routing-flow                                            Flow                                                                                                       

%
~~~

...and maybe even more interesting its endpoints and their addresses's:

~~~
% mule endpoints -a vp-services-2.1.0
name                                                                                                              address                                                         
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
endpoint.http.localhost.10000.test.Ping.Service                                                                   http://localhost:10000/test/Ping_Service                        
endpoint.http.localhost.21000.monitor.ping                                                                        http://localhost:21000/monitor/ping                             
endpoint.http.localhost.22000.monitor.dashboard                                                                   http://localhost:22000/monitor/dashboard                        
endpoint.http.localhost.23000.resetcache                                                                          http://localhost:23000/resetcache                               
endpoint.http.localhost.24000.resethsacache                                                                       http://localhost:24000/resethsacache                            
endpoint.http.localhost.8070.vp.GetSubjectOfCareSchedule.1.rivtabp21                                              http://localhost:8070/vp/GetSubjectOfCareSchedule/1/rivtabp21   
endpoint.https.localhost.20000.monitoring.service.groups                                                          https://localhost:20000/monitoring/service-groups               
endpoint.https.localhost.20000.vp.GetSubjectOfCareSchedule.1.rivtabp21                                            https://localhost:20000/vp/GetSubjectOfCareSchedule/1/rivtabp21
endpoint.https.localhost.20000.vp.Ping.1.rivtabp20                                                                https://localhost:20000/vp/Ping/1/rivtabp20                     
endpoint.https.localhost.23001.vp.GetLogicalAddresseesByServiceContract.1.rivtabp21.connector.VPProducerConnector https://localhost:23001/vp/GetLogicalAddresseesByServiceContract/1/rivtabp21?connector=VPProducerConnector                     
endpoint.https.localhost.23001.vp.GetSupportedServiceContracts.1.rivtabp21                                        https://localhost:23001/vp/GetSupportedServiceContracts/1/rivtabp21                                                            
endpoint.https.localhost.23001.vp.PingForConfiguration.1.rivtabp20                                                https://localhost:23001/vp/PingForConfiguration/1/rivtabp20     
endpoint.https.localhost.23001.vp.PingForConfiguration.1.rivtabp21                                                https://localhost:23001/vp/PingForConfiguration/1/rivtabp21     
endpoint.jms.SOITOOLKIT.LOG.ERROR                                                                                 SOITOOLKIT.LOG.ERROR                                            
endpoint.jms.SOITOOLKIT.LOG.INFO                                                                                  SOITOOLKIT.LOG.INFO                                             
endpoint.jms.SOITOOLKIT.LOG.STORE                                                                                 SOITOOLKIT.LOG.STORE                                            

%
~~~

Some runtime statistics from a specific flow:

~~~
% mule stats -a vp-services-2.1.0 -f crm-scheduling-GetSubjectOfCareScheduleInteraction-virtualisering-flow
name                  value                                                                                                                                                         
----------------------------                                                                                                                                                        
SyncEventsReceived    20                                                                                                                                                           	 
AsyncEventsReceived   0                                                                                                                                                             
TotalEventsReceived   20                                                                                                                                                            
ExecutionErrors       0                                                                                                                                                             
FatalErrors           0                                                                                                                                                             
ProcessedEvents       20                                                                                                                                                            
MinProcessingTime     198                                                                                                                                                           
MaxProcessingTime     3467                                                                                                                                                          
AverageProcessingTime 486                                                                                                                                                           
TotalProcessingTime   9729                                                                                                                                                          
%
~~~

## Start and stop applications and the Mule ESB instance
Stop an application by:

~~~
% mule app -a vp-services-2.1.0 stop
Action stop successfully run. Application intialized: true, stopped: true

%
~~~

Ensure it is stopped (stopped flag is now set to true):

~~~
% mule apps
name              start time                    initialized  stopped                                                                                                                   
-------------------------------------------------------------------
	                  
crash-mule-app    Tue Jun 11 19:24:54 UTC 2013 true         false                                                                                                                     
default           Tue Jun 11 19:24:54 UTC 2013 true         false                                                                                                                     
vp-services-2.1.0 null                         true         true                                                                                                                      

%
~~~

Start the application again:

~~~
% mule app -a vp-services-2.1.0 start
Action start successfully run. Application intialized: true, stopped: false

%
~~~

Ensure it is back on-line (stopped flag is now back to false):

~~~
% mule apps                          
name               start time                   initialized  stopped                                                                                                                   
-------------------------------------------------------------------

crash-mule-app    Tue Jun 11 19:24:54 UTC 2013 true         false                                                                                                                     
default           Tue Jun 11 19:24:54 UTC 2013 true         false                                                                                                                     
vp-services-2.1.0 Wed Jun 12 09:11:54 UTC 2013 true         false                                                                                                                     

%
~~~

Even the Mule ESB instance itself can be restarted if required:

~~~
% mule broker restart
Action restart successfully run.

%

% mule appsConnection to 33.33.33.33 closed.                                                                  
~~~

For very natural reasons you will be disconnected during the restart but after a while you can connect again and see all apps upp and running:

~~~
$ ssh -p 4022 -l root 33.33.33.33
root@33.33.33.33's password:
 ______
 .~      ~. |`````````,       .'.                   ..'''' |         |
|           |'''|'''''      .''```.              .''       |_________|
|           |    `.       .'       `.         ..'          |         |
 `.______.' |      `.   .'           `. ....''             |         | 1.2.6

Follow and support the project on http://www.crashub.org
Welcome to singleserver.local + !
It is Wed Jun 12 09:19:32 UTC 2013 now

% mule apps
name              start time                   initialized stopped                                                                                                                  
-------------------------------------------------------------------
	                    
crash-mule-app    Wed Jun 12 09:18:45 UTC 2013 true        false                                                                                                                    
default           Wed Jun 12 09:18:46 UTC 2013 true        false                                                                                                                    
vp-services-2.1.0 Wed Jun 12 09:18:59 UTC 2013 true        false                                                                                                                    

%
~~~

## Summary
We have just seen some of the most common functions in the tool in action but I guess that you already agree with me that in environments where you don't have access to the Mule Management Console this is really a useful management tool, specially if you have multiple Mule ESB instances spread over a number of servers!

Give it a try your self!
