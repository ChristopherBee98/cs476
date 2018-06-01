#CMSC 476 Information Retrieval Homework 1
#Austin Bailey
#baustin1@umbc.edu

#Produce the following:
# -a directory of all tokenized documents (one output file per input file)
# -a file of all tokens and their frequencies sorted by token
# -a file of all tokens and their frequencies sorted by frequency

#note: might not need html parser; just need to tokenize and sort all words
#this
    #idea: use beautiful soup to delete all puncuation from the document, then make it a list. make a for loop that goes through each html document, then
    #inside that for loop make a while loop that goes through the current html document. this for loop will check the first value of the list, see how frequent it is,
    #and store that word in another independent list. then all instances of that word are deleted through beautiful soup in the list. continue doing this until
    #the html document (list) is empty, then move on to next html document.

import time
import os
import json
import operator
import errno
import sys
from os import listdir
from os.path import isfile, join
import re
import nltk
import codecs
from HTMLParser import HTMLParser
import tokenize
from bs4 import BeautifulSoup

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print "Encountered a start tag:", tag

    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag

    def handle_data(self, data):
        print "Encountered some data  :", data

#reuse for formatting all the tokenized files
def formatInfo(directory):
    #formats info
    with open(directory, 'r+') as formatDic:
        temp = formatDic.read()
        temp = temp.replace("{"," ")
        temp = temp.replace("}","")
        temp = temp.replace("\"","")
        temp = temp.replace(",","\n")
        temp = temp.replace(":",",")
        formatDic.close
    formatDic = open(directory, 'w')
    formatDic.write(temp)
    formatDic.close()

def main():
    inputDir = 'files'
    outputDir = 'tokens'
    #if inputdir and outputdir are given as arguments
    if (len(sys.argv) == 3):
        inputDir = sys.argv[1]
        outputDir = sys.argv[2]
    start_time = time.time()
    htmlList = []
    index = 0
    countOfHtml = 0
    #directory to path that parse.py is in
    tokenFilePath = os.path.abspath(os.path.join("sortedByTokens.csv"))
    frequencyFilePath = os.path.abspath(os.path.join("sortedByFrequency.csv"))
    #dictionary for all words and their frequencies
    bigDict = dict()
    #makes a list of whatever html files are in my directory 'files'
    htmlList = [f for f in listdir(os.path.abspath(inputDir)) if isfile(join(os.path.abspath(inputDir), f))]
    for i in htmlList:
        countOfHtml += 1
        #path to directory program is running in
        tokenDir = os.path.abspath(os.path.join(outputDir, str(countOfHtml)+"tokens.csv"))
        doc = codecs.open(os.path.abspath(inputDir + '/' + i), 'r')
        tempString = doc.read()
        soup = BeautifulSoup(tempString, 'html.parser')
        #gets text from html document
        tempText = soup.get_text()
        #lowers the case
        tempText = tempText.lower()
        #creates a list
        tempText = tempText.split()
        #gets rid of unwanted characters
        for index in range(0, (len(tempText) - 1)):
            tempText[index] = ''.join(e for e in tempText[index] if e.isalnum())
            index += 1
        tempDict = dict() #for each html file
        #create entries and add to frequency if it already exists
        for j in tempText:
            if (not(j in tempDict)):
                tempDict[j] = 1
            else:
                tempDict[j] += 1
            if (not(j in bigDict)):
                bigDict[j] = 1
            else:
                bigDict[j] += 1
        #sort tokens by token (alphabetically) and by frequency; output these to 2 files for each html file
        bigDict.pop("", None)
        tempDict.pop("", None)
        print(i)
        #outputting tokenized document
        with open(tokenDir, 'w') as file:
            file.write(json.dumps(tempDict))
        #then make it look nicer (formatting)
        formatInfo(tokenDir)
        file.close()
    #sort by tokens and frequencies, then output to 2 files
    tokenFile = sorted(bigDict.items(), key=operator.itemgetter(0))
    #note: reverse is true so the list goes from most frequent to least
    frequencyFile = sorted(bigDict.items(), key=operator.itemgetter(1), reverse=True)
    with open(tokenFilePath, 'w') as file:
        file.write(json.dumps(tokenFile))
    formatInfo(tokenFilePath)
    file.close()
    with open(frequencyFilePath, 'w') as file:
        file.write(json.dumps(frequencyFile))
    formatInfo(frequencyFilePath)
    file.close()
    #runtime for program overall (can vary)
    print "My program took", time.time() - start_time, "to run."
main()
