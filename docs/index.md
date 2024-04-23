# PiRate

## Abstract:
PiRate is a standalone security scanner which emphasizes usability and customizability. Many security scanners exist on the market such as Nessus and OpenVAS. They all have
one thing in common: they are unusable for most people, and they are not customizable. Pirate attempts to answer these shortcomings by making a security scanner that is
simple to use and that can be easily extended.

The device works by connecting to a client computer through a direct LAN connection (the client computer must be taken off all other networks). The client accesses the PiRate controller through a webpage served by PiRate. The controller UI allows the client to run a number of security tests, display and evaluate the results, and even create their own custom tests.

Having a directly-connected LAN between the PiRate device and the client allows the PiRate software to safely emulate attack vectors and test security weaknesses of the client device, without exposing either device to an internet-connected network. After a user runs a test or a set of tests, the results will be displayed in a table on the webpage. Users can then go through and delete any test results they don't want to keep, and save the remaining results to a file. 

PiRate can be beneficial for any researcher, engineer, or penetration tester desiring to run a fully-customizable testing framework for a single machine. Users can take advantage of the current testing suite while also having the ability to create and add any test they desire.

## Members:
 - Cole Gilmore
 - Max Hanson
 - Casey Lewis

## What We Actually Built:
PiRate uses a python based controller that will run security tests against a client computer from an externally connected Raspberry Pi. The tests have been structured according to the layout provided to you within our angular website's test upload page. With that said, the entire website is run using angular and is hosted on a node express server which will gather your IP address, as well as the directories that the tests reside in and any potential results from previous tests. After gathering this information it will get passed back to be viewed on the angular website and will update whenever a new test is added to the tests directory. The results of running tests can be saved to an external log file for later viewing, as well as the program remembering your device or being able to upload old test results.

![Imgur](https://imgur.com/5iyfEWk.png)
![Imgur](https://imgur.com/n9W60Aj.png)
![Imgur](https://imgur.com/rnxX2nZ.png)