---
categories: blogg teknik
published: true
heading: Spring Boot App as a Windows Service
authors: 
  - peterlarsson
tags: "spring-boot, windows, java"
topstory: true
comments: true
---


Spring Boot is great and in combination with Docker it's really fun to develop production grade applications. Though, in one of my recent projects the target execution platform turned out to be Windows (2008 R2) on "physical" servers (_sigh_...). 

Attempting to be a good citizen the Spring Boot App in question preferably should be managed as yet another Windows Service. Hmm... appear to be an old problem with several well-known solutions, but after some googleing I decided to share our solution.  

### Open Source Alternatives

Our requirements was only a few:

1. Open source always is preferred
2. Support for Java 8 (64 and 32 bit)
3. Simple to install, uninstall and upgrade the Java App 
4. Nice to have an option to customize the App icon (co-location with other Apps on the same server)

I've had some experience (long time ago) with [Apache Commons Daemon](http://commons.apache.org/proper/commons-daemon/) which probably would do the job. Anyway, googled for alternatives and found [WinRun4J](http://winrun4j.sourceforge.net), which seemed surprisingly simple. The decision was to give the later a try (after all it's always more fun to do something new).

I will not dig deep into all of the capabilities of WinRun4J, since all you need to know is neatly summarized at their [site](http://winrun4j.sourceforge.net). There are differences regarding licensing, and WinRun4J is licensed under the "copyleft" [Common Public License (CPL)](http://www.eclipse.org/legal/cpl-v10.html). In our specific project it's not a big deal since the App in question not is subject to be distributed.

### WinRun4J solution

Both alternatives above needs a small custom Java wrapper class to handle Windows service events. Main problem to solve is launching/bootstrapping of the Spring Boot App, and Spring already has a solution in place with the `PropertiesLauncher` class.

With WinRun4J it's enough to write a custom wrapper class extending an WinRun4J `AbstractService` class. A generic Spring Boot Launcher wrapper class example is demonstrated below. The magic Spring Boot launch line of code is: `PropertiesLauncher.main(new String[0])`.

**Implementation of a generic Spring Boot Wrapper**

~~~~
import org.boris.winrun4j.AbstractService;
import org.boris.winrun4j.EventLog;
import org.boris.winrun4j.ServiceException;
import org.springframework.boot.loader.PropertiesLauncher;

/**
 * Winrun4j service, only to be used when deploying as a windows service.
 */
public class SpringBootLauncherService extends AbstractService {
    static final int CHECK_FOR_SHUTDOWN_INTERVAL = 6 * 1000;
    static final int PING_INTERVAL = 60 * 1000;
    
    public int serviceMain(String[] args) throws ServiceException {
        launchSpringBootApp();
        waitUntilShutdown();
        return 0;
    }

    protected void launchSpringBootApp() throws ServiceException {
        log("Launch spring boot application");
        try {
            PropertiesLauncher.main(new String[0]);
        } catch (Throwable e) {
            log(e);
            throw new ServiceException("Error while launching spring boot application", e);
        }
    }

    protected void waitUntilShutdown() {
        for (int count = 0; !isShutdown(); ) {
            try {
                Thread.sleep(CHECK_FOR_SHUTDOWN_INTERVAL);
            } catch (InterruptedException e) {}
            if (++count > (PING_INTERVAL / CHECK_FOR_SHUTDOWN_INTERVAL)) {
                log("Ping");
                count = 0;
            }
        }
    }
    protected void log(String message) {
        log(false, message);
    }
    protected void log(Throwable throwable) {
        log(true, throwable.toString());
    }
    // Windows logging can be improved in WinRun4J (binary message at the time)!
    private void log(boolean error, String message) {
        EventLog.report("SpringBootLauncherService", (error ? EventLog.ERROR : EventLog.INFORMATION), message);
    }
}
~~~~

### WinRun4J deploy and run

WinRun4j provides Windows executables for 32 and 64 bit, and a deployment package contains at least the following (assembled by maven in our project)

- Executable (myapp.exe)
- Configuration (myapp.ini)
- WinRun4J Jar library (with the custom Wrapper class)
- Application Spring Boot Jar library

Installing is extremely simple:

1. Make sure a standard Java JRE is installed (in our case 64 bit Java 8 JRE)
2. Unapck the files above into an App folder of your choice
3. Configure App
4. Install App
5. Start App

**Configure (myapp.ini)**

~~~~
;  parameters only valid during installation
; Our Wrapper (see above)
service.class=SpringBootLauncherService
service.id=myapp
service.name=MyApp Services
service.description=More details here
service.startup=auto
; parameters valid on each startup
; Service log, probably not the application log
log=c:/Windows/Temp/myapp-service.log
log.overwrite=true
log.file.and.console=true
; Nice feature, define amount of memory in percent of available RAM
vm.heapsize.max.percent=35
; Som custom configurations overriding Spring Boot (application.yaml)
vmarg.1=-Ddb.host=localhost
; ....
classpath.1=myapp-*.jar
classpath.2=winrun4j.jar
~~~~

The actual Spring Boot application logged to disk (logback RollingFileAppender) and also to a central syslog server, i.e. not to any native Windows log.

**Install**

_Note: the basename of app (myapp) must be same as the basename of the ini file_

~~~~
> myapp.exe --WinRun4J:RegisterService
~~~~

**Start**

_Note: Windows Services UI might also be used_

~~~~
> sc start myapp
~~~~

**Stop**

_Note: Windows Services UI might also be used_

~~~~
> sc stop myapp 
~~~~

**Upgrade**

To upgrade your Spring Boot application replace the current application JAR `myapp-<version>.jar` and then restart (stop/start) the service.

**Uninstall**

_Note: Reboot after to get rid of everything_

~~~~
> sc stop myapp
> myapp.exe --WinRun4J:UnregisterService
~~~~

### Experiences

With a tiny written instruction the application has been successfully installed on a bunch of servers by a remote technician (with no assistance from the development team), and all seems to run without any hassle.
