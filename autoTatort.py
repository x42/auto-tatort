#!/usr/bin/python
import sys, codecs, locale
import feedparser
import datetime
import urlparse
import os.path
import re
from urllib import urlopen, urlretrieve
import json

#Wrap sysout so we don't run into problems when printing unicode characters to the console.
#This would otherwise be a problem when we are invoked on Debian using cron: 
#Console will have encoding NONE and fail to print some titles with umlauts etc
#might also fix printing on Windows consoles
#see https://wiki.python.org/moin/PrintFails
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout);

RSS_URL = "http://www.ardmediathek.de/tv/Tatort/Sendung?documentId=602916&bcastId=602916&rss=true"

# -1 = download highest quality available
# 0.0 320x180 (53k audio)i
# 1.0 512x288 (93k audio)
# 1.1 480x270 (61k audio)
# 2.0 640x360 (189k audio)
# 2.1 960x540 (189k audio)

#you can currently only select the highest quality within one tier. So 1 will dowload 1.1 and 2 will download 2.1. 0 will download 0.0
QUALITY = -1


#set to False if you don't want subtitles
SUBTITLES = True

TARGET_DIR = "/data/tatort/"


feed = feedparser.parse( RSS_URL )

items = feed.entries

today = datetime.date.today()
#today = datetime.date(2015,8,30)


for item in items:
   year = item["date_parsed"][0];
   month = item["date_parsed"][1];
   day = item["date_parsed"][2];
   feedDate = datetime.date(item["date_parsed"][0], item["date_parsed"][1], item["date_parsed"][2])

   if (today - feedDate).days < 7:
      title = item["title"]
      link = item["link"]
      parsed = urlparse.urlparse(link)
      docId = urlparse.parse_qs(parsed.query)['documentId']
      docUrl = 'http://www.ardmediathek.de/play/media/' + docId[0] + '?devicetype=pc&features=flash'

      response = urlopen(docUrl)
      html = response.read()

      if 'http://www.ardmediathek.de/-/stoerung' == response.geturl():
        print "Could not get item with title '" + title + "'. Got redirected to '" + response.geturl() + "'. This is probably because the item is still in the RSS feed, but not available anymore."
        continue

      try:
        media = json.loads(html)
      except ValueError as e:
        print e
        print "Could not get item with title '" + title + "'. Original item link is '" + link + "' and parsed docId[0] is '" + docId[0] + "', but html response from '" + docUrl + "' was '" + html + "'"
        continue

      if '_mediaArray' not in media or len(media["_mediaArray"]) == 0:
        print "Skipping " + title + " because it does not have any mediafiles"
        continue

      #ignore some contrib files
      if re.search('H.rfassung', title):
        print "Skipping " + title
        continue
      if re.search('Die Klassiker:', title):
        print "Skipping " + title
        continue
      if re.search('Making-Of', title):
        print "Skipping " + title
        continue
      if re.search('IFA:', title):
        print "Skipping " + title
        continue
      if re.search('Tatort - Extra:', title):
        print "Skipping " + title
        continue

      mediaLinks = media["_mediaArray"][1]["_mediaStreamArray"]

      downloadQuality = QUALITY

      #get best quality?
      if downloadQuality == -1:
        downloadQuality = 0
        for mediaLink in mediaLinks:
          if mediaLink["_quality"] > downloadQuality and '_stream' in mediaLink:
            downloadQuality = mediaLink["_quality"]


      downloadedSomething = 0

      for mediaLink in mediaLinks:
         if downloadQuality == mediaLink["_quality"]:
            stream = mediaLink["_stream"]
            mediaURL = ""
            #check if the selected quality has two stream urls
            if type(stream) is list or type(stream) is tuple:
              if len(stream) > 1:
                mediaURL = stream[1]
              else:
                mediaURL = stream[0]
            else:
              mediaURL = stream

            fileName = "".join([x if x.isalnum() or x in "- " else "" for x in title])

            if os.path.isfile(TARGET_DIR + fileName + ".mp4"):
              print "Already downloaded: ", mediaURL, TARGET_DIR + fileName + ".mp4"
              continue

            print "Downloading '" + title + "'"
            urlretrieve(mediaURL, TARGET_DIR + fileName + ".mp4")
            downloadedSomething = 1

            #download subtitles
            try:
              if SUBTITLES and '_subtitleUrl' in media and len(media["_subtitleUrl"]) > 0:
                offset = 0
                if '_subtitleOffset' in media:
                 offset = media["_subtitleOffset"]

                subtitleURL = 'http://www.ardmediathek.de/' + media["_subtitleUrl"]
                print "Downloading subtitles for '" + title + "'"
                urlretrieve(subtitleURL, TARGET_DIR + fileName + "_subtitleOffset_" + str(offset) + ".xml")
            except Exception as e:
              #print and resume with download
              print e
              print subtitleURL

      #check whether we download something
      if downloadedSomething == 0:
        print "Could not download '" + title + "' because of an error or nothing matching your quality selection"

