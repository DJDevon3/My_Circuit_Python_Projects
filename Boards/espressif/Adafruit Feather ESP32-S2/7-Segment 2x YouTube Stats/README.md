# Dual 7-Segment Backpack YouTube Stats (for ESP32-S2)
- pulls info from YouTube API in JSON format
- parses JSON data to a format circuit python can display
- displays your channel data on double 7-segment backpack display (from Adafruit)

![YouTube_Stats_Screenshot](https://user-images.githubusercontent.com/49322231/233680295-88db7074-7cb7-42c8-a014-0a88cd4438e2.JPG)

## Hardware Used:
- [1 Adafruit Feather ESP32-S2](https://www.adafruit.com/product/5000)
- [2 Adafruit 0.56" 4-Digit 7-Segment Display Backpack (with or without Stemma)](https://www.adafruit.com/product/1002)

## Requirement:
- [YouTube Developer Account & API Token](https://console.cloud.google.com/apis/dashboard)

## Demonstration Serial Print Output:
- Good for debugging. Pure serial output format can be helpful.
```py
===============================
Connecting to WiFi...
Connected!

Attempting to GET YouTube Stats!
===============================
Matching Results:  1
Response Kind:  youtube#channelListResponse
Request Kind:  youtube#channel
Channel ID:  UCHpvNfMNs7qdsUjOad2_FWg
Videos:  273
Views:  6821944
Subscribers:  11200
Success!
Next Update in 15 minutes
===============================
```
You can use this working example to customize the YouTube channel data you want (tons more data available) for your project. 

I'm only pulling basic data for the purpose of displaying on a 7-segment display. 

Consult the [YouTube API Docs](https://developers.google.com/youtube/v3/docs/channels/list) to see the oodles of JSON data you can pull from.
