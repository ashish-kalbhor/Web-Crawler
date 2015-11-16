_author_ = 'Ashish Kalbhor'

from urllib.request import urlopen
from urllib import parse
import requests
import time
import os
import re
from bs4 import BeautifulSoup


# Basic counters.
relevantUrlCount = 0
allUrlCount = 0

'''
Validate the URL based on given rules:
 -- The url should start with "https://en.wikipedia.org/wiki/" i.e. Wikipedia Page
 -- The url should not be 'Main_Page'
 -- The url should not be wikipedia help and administration pages i.e. should not contain ':'
 -- The url should not redirect to itself i.e. should not contain '#'
'''
def valid(url, tagUrl):
        if ('#' not in tagUrl) and (':' not in tagUrl) and ('https://en.wikipedia.org/wiki/' in  parse.urljoin(url,tagUrl)) and ('Main_Page' not in tagUrl):
                return True
        return False

# Search the content for given keyword (case insensitive).
def searchKeyword(keyword, url, soup):
        texts = soup.get_text()
        if keyword.lower() in texts.lower():
                return True
        return False

# A recursive crawler function.
def recursiveCrawler(url, depth, search, processed, isFocused, file):
        global relevantUrlCount
        global allUrlCount

        if (isFocused and relevantUrlCount == 1000) or (not isFocused and allUrlCount == 1000):
        #if allUrlCount == 1000: (This was used during testing)
                print("Url counter limit reached !")
                writeOutput(file, allUrlCount, relevantUrlCount, search, isFocused, processed)
                os._exit(0)

	# Read only that URL which has not been crawled already.
        if (not url in processed):
                processed.append(url)

                # Implementing politeness policy by adding a delay of 1 second between URL Requests.
                time.sleep(1)
                
                try:
                        res = requests.get(url)
                        contents = res.text
                        # Using BeautifulSoup4 for HTML parsing.
                        # It reads all the contents throough html parser and stores in soup object.
                        soup = BeautifulSoup(contents,"html.parser")
                        allUrlCount += 1
                except:
                        # Error in connection, skip the url and move ahead.
                        print("Error in network connection ! Cannot open the link")
                        # Giving some time for the internet to breathe
                        time.sleep(10)
                        return
                        
		#Read the content of webpage only for focused crawling
                if isFocused:

                        '''
                         Workaround for "index" keyword.
                         This Regular expression is NOT USED.
                         byteContents = re.sub('href=".*'+search+'/..*"',' ', byteContents)
                         byteContents = re.sub('action=".*'+search+'/..*"',' ', byteContents)
                        '''
                        # If keyphrase found, write the url in output file.
                        if searchKeyword(search, url, soup):
                                relevantUrlCount += 1
                                print("Found keyphrase at Url no. ",relevantUrlCount ,":",url)
                                file.write("\n %s" %(url))
                else:
                        # For non-focused crawling, just write the crawled url.
                        print("Url no. ", allUrlCount, ":", url)
                        file.write("\n %s" %(url))

                # Till depth becomes 1 (root).
                if depth - 1:
                        # Find all tags in the content which are urls (href is the url).
                        for tag in soup.findAll('a',href=True):
                                if valid(url, tag['href']):
                                        # Joining the url with base url, since wiki tags usually start with '/wiki/Example'
                                        tag['href'] = parse.urljoin(url,tag['href'])
                                        recursiveCrawler(tag['href'], depth-1, search, processed, isFocused, file)


# Writing all the information in the output file.
def writeOutput(file, allUrlCount, relevantUrlCount, search, isFocused, processed):
        # Final stats
        print("Total traversed Urls => ", allUrlCount)
        file.write("\nTotal traversed Urls => %s" %(allUrlCount))
        
        if isFocused:
                print("Total relevant Urls  => ", relevantUrlCount)
                print("Proportion of relevant Urls for keyword '", search, "' is ", relevantUrlCount/allUrlCount)
                file.write("\nTotal relevant Urls => %s" %(relevantUrlCount))
                file.write("\nProportion of relevant Urls for keyword %s" %(relevantUrlCount/allUrlCount))

        file.close()

        
# THE MAIN FUNCTION WHICH WILL BE CALLED BY THE USER.
def crawl(url,*key):

        processed = []
        file = open("Crawler_Output.txt","w")
        
        if key:
                print("Focused crawling for term '%s'" %(key[0]))
                file.write("Focused crawling for the term '%s'" %(key[0]))
                recursiveCrawler(url,5,key[0],processed, 1, file)
        else:
                print("Non-focused crawling.")
                file.write("Non-focused crawling:\n")
                recursiveCrawler(url,5,"",processed, 0, file)       
        

#-------------------------------------------------------------------------
#crawl("https://en.wikipedia.org/wiki/Hugh_of_Saint-Cher","concordance")
#crawl("https://en.wikipedia.org/wiki/Hugh_of_Saint-Cher")
#-------------------------------------------------------------------------
