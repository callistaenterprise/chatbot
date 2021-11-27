---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: React native workshop summary from React Europe 2019
authors:
  - parantonwestbom
---
I attended a two days workshop before React Europe in Paris. It was two intense days where I picked up some new things and gor a deeper understanding of react native.
The first day was mainly about react-navigation  an then a shorter section about react-native-web,
Second day was the main topics performance and animations.

-[readmore]-

## Preparations
Preparations before the workshop was to have the computer setup with react native and expo.
So you could run expo-cli and especially
```$expo init```
to kickstart a new project.
All about that could be found in expos documentation
[https://docs.expo.io/versions/latest/](https://docs.expo.io/versions/latest/)

## React-navigation
Since the course was held by Brent Vatne which is the main committer to the library, his knowledge about the domain was excellent. He also has a pleasant voice and a pedagogical approach.
https://reactnavigation.org/docs/en/getting-started.html
Navigation is vital in todays app development especially on a mobile since the screen is small, there will be many screens.
React-navigation is a mature and excellent documented library to help with this.
I have worked with react native now for almost a year using react-navigation and for me this part of the course was good to get a deeper understanding of it.
Things I haven’t used yet but will look into after the course are.
StackNavigator intialRouteKey - a key of the initialroute which will always bring you back to the start of the app
Different visual options like cardShadowEnabled and cardOverlayEnabled to try to get the navigation experience just like you want.
React-navigation also exports its own Scrollview, FlatList and SectionList.These built-in components are wrapped in order to respond to events from navigation that will scroll to top when tapping on the active tab as you would expect from native tab bars.  
React-navigation also have support for safe areas with a SafeAreaView component to help out with these new cool phones like IphoneX etc.
If you choose to use react-navigation, go through there guides and see what it can help you with.
If you really wanna have control over the transitions at navigation I recommend to have a look at 
react-navigation-animated-switch.
It gives you a switchNavigator with a transition prop where you can give it a Transition component from react-native-reanimated.
Check it out at https://github.com/react-navigation/animated-switch
If you have need for different themes in your app you should head over to this page
[https://reactnavigation.org/docs/en/themes.html#docsNav](https://reactnavigation.org/docs/en/themes.html#docsNav)


## React-native-web
React-native-web makes it possible to run React Native components on the web using React DOM.
The part about react-native-web was also about how Expo can support it in its developer experience  stack.
Evan Bacon was having this part. It was very interesting and cool but also a big challenge.
It is under development and not production ready Evan has a nice blog about it here.  
[https://blog.expo.io/expo-cli-and-sdk-web-support-beta-d0c588221375](https://blog.expo.io/expo-cli-and-sdk-web-support-beta-d0c588221375)

## Performance
When it comes to performance the main thing to look out for is unnecessary rerendering especially if using a stacknavigator since it doesn’t unmount your component so often so there are a lot of components that could rerender even they aren’t in focus.
To our help on finding such bottlenecks we used react-devtools and started it as a standalone app most people will be familiar with this tool as a chrome extension.
How to run it as a standalone app can be found here
[https://github.com/facebook/react-devtools/blob/master/packages/react-devtools/README.md](https://github.com/facebook/react-devtools/blob/master/packages/react-devtools/README.md)
Then we started to record in the profiler tab of the tool and clicked around in the app and finally stopped the recording and then analysing the data.
Common pitfalls that was pointed out was:
 -avoid things in shouldcompentUpdate and do it on a suitable focus event such as willFocus, didBlur etc. 
-If using Redux only subscribe to the data your are interested in, don’t be lazy :-)
-If possible use PureComponent

If you suspect a component to render to often and slowing things down add
    ```$stall(1000)```
to it, todo it even more painful and see if that is the problem.

## React-native-gesture-handler
React Native Gesture Handler provides native-driven gesture management APIs for building best possible touch-based experiences in React Native.
With this library gestures are no longer controlled by the JS responder system, but instead are recognised and tracked in the UI thread. It makes touch interactions and gesture tracking not only smooth, but also dependable and deterministic.
This library looks great and something everybody who wants to make a first class app should look into.
[https://kmagiera.github.io/react-native-gesture-handler/docs/getting-started.html](https://kmagiera.github.io/react-native-gesture-handler/docs/getting-started.html)

## Webbrowser, notifications 
Expo also has a webbrowser component which could be used if you for example wanna seamlessly integrate a browser window.
Expo can  also help you with the cumbersome task of pushnotifications

## Summary
The workshop was excellent the tempo was high but manageable and a lot of ground was covered so I think everybody at the course got some useful stuff with them home and the teachers really knew what they where talking about.
