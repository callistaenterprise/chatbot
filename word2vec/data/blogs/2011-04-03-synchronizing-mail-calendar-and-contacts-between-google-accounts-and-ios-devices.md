---
layout: details-blog
published: true
categories: blogg teknik
heading: Synchronizing Mail, Calendar and Contacts between Google accounts and iOS devices
authors:
  - christianhilmersson
tags: mobile calendar contacts gmail google googleapps ios ipad iphone ipodtouch mail microsoftexchange push synchronization
topstory: true
comments: true
---

Since people are using more and more devices to manage communication and planning data in their daily life, both for personal and professional use, there seems to be a growing challenge to keep the data on all those devices up to date and synchronized.

-[readmore]-

As most devices (smart phones, tablets, laptops etc) are online these days it might obviously be a good idea to let them work with the same online master data, such as a for example a Google Apps or a Gmail account, for synchronizing calendars, mail and contact information.

The longer title of this article would be **Synchronizing Mail, Calendar and Contacts between Google Apps or Gmail accounts and iOS devices (iPhone, iPad, iPod Touch)** and as the title hints, this article describes one way of getting your Apple iOS devices synchronized with your Google Apps account (or ordinary Gmail accounts) in terms of calendars, mail and contacts utilizing Microsoft Exchange as protocol for instant synchronization (using push).

## Create a Google account
First of all you need to have a Google Apps or Gmail account, which you probably already have if you are reading 	this. Otherwise you can create one here: [http://apps.google.com](http://apps.google.com/) or here: [https://www.google.com/accounts/NewAccount?service=mail](https://www.google.com/accounts/NewAccount?service=mail)

## Important notice
It is a good idea to follow Google's and Apple's recommendations to backup your existing data before setting 	up synchronization to be on the safe side if something unexpected should happen during the synchronization process.

## Managing Google Sync (configuring which calendars to synchronize with your device)
The following has to be done on each device for which you want to configure Google Sync. And also once for each account, if you have more than one.

1. At your device, open up a browser pointing at [http://m.google.com](http://m.google.com/sync)
2. Tap in the square near the bottom saying something like **Are you using Google Apps? Click Here to configure your domain** and a dialog will appear.
3. In the dialog box saying **Enter your Google Apps-domain** enter your Google Apps domain e.g. `mycompany.com` and press the button to save your domain.
4. Tap on one of your Google Apps, for example the Calendar. Just to get to your Google Apps login 	page.
5. Login with your Google Apps credentials.
6. Now, while you are logged in to your account, open up the URL [http://m.google.com/sync](http://m.google.com/sync)

> If you get an error messages  saying that your device is not supported, try tapping the **Change language** button and change language to English (US)

7. You should now have got a list of your devices that are registered for synchronization.
8. Tap on the device you want to manage synchronization for, e.g. iPad.
9. In the opened view you can choose which calendars you want to be synchronized to your device.

## Adding the account to your device
1. Start up the Settings app and open the **E-mail, contacts, calendars** section.
2. Tap the **Add new account…**, choose **Microsoft Exchange** and enter the following:
	1. E-mail; enter your e-mail address e.g. `your.mail@mycompany.com` (`your.mail@gmail.com` if Gmail account).
	2. Domain; Leave blank
	3. Username; enter your e-mail address e.g. `your.mail@mycompany.com` (`your.mail@gmail.com` if Gmail account)
	4. Password; enter your Google Apps/Gmail password
	5. Description: Give a short description of the account e.g. `My Company`
3. Tap **Next** and a Server field will appear
	1. Server; enter `m.google.com`
4. Choose what you want to synchronize (Mail, Contacts and Calendars)

## Ready to go
Your account is now configured and your device will start to synchronize mail, contacts and your chosen calendars in the background (if you choosed push). After a 	couple of minutes your account should be synchronized and the data will be visible in 	their respective iOS app (Calendar, Mail and Contacts).
