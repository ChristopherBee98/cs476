#CMSC 476 Information Retrieval Homework 2
#Austin Bailey
#baustin1@umbc.edu

#Produce the following:
#- extend the preprocessing as follows: remove stopwords, remove words that occur only once in the entire corpus, and words of length 1 (Done)
#- calculate the term weights for the tokens that occur in each document in your collection (Done)

#note: You may use any of the tf * idf variants discussed in class and/or the textbook to weight your terms. Be sure to clearly describe the formula you chose to use 
#in your report. You must normalize the term weights by the length of the documents. The easiest normalization is to use freq(wordi in documentj) / totalfreq(all 
#tokens in documentj), but you may choose to do the proper sqrt of sum of squares vector normalization or any other normalization that takes some measure of document 
#length into account.

#idea: utilize len() for the amount of tokens in each individual document. that'll act as the totalfreq. each word has its value being the frequency, so use that as
#the freq. do freq/totalfreq for normalization.
#note: totalfreq needs to be clarified. it could either mean all the original tokens, or more likely its all the remaining ones after the extended preprocessing.
#if that's the case, use a dict method to find out how many keys are in the dict, then use that for totalfreq.
#idea: dict for each html file (weightdict) that has the word as the key, and then has the term weight as the value

#remember: change directories for output
#reminder: fix it so in the second for loop, bigDict is used to check and see if the word has only appeared once in the entire corpus (Done)
#reminder: log idf don't forget

import math
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
    outputDir = 'weightTokens'
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
    #make a list of stopwords
    stopWordDoc = codecs.open(os.path.abspath(os.path.join("stoplist.txt")))
    tempWord = stopWordDoc.read()
    wordSoup = BeautifulSoup(tempWord, 'html.parser')
    stopWordList = wordSoup.get_text()
    stopWordList = stopWordList.split("\n")
    wordDict = dict()
    #make a dict of the stop words
    for word in stopWordList:
        wordDict[word] = 1
    stopWordDoc.close()
    #dict for number of documents word is in
    totalDocDict = dict()
    #dict for all words
    bigDict = dict()
    #makes a list of whatever html files are in my directory 'files'
    htmlList = [f for f in listdir(os.path.abspath(inputDir)) if isfile(join(os.path.abspath(inputDir), f))]
    for i in htmlList:
        countOfHtml += 1
        #path to directory program is running in
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
        #create entries and add to frequency if it already exists
        tempDict = dict()
        for j in tempText:
            #makes sure there are no stop words and the length of the word is greater than 1
            if (not(j in wordDict) and (len(j) > 1)):
                if (not(j in tempDict)):
                    tempDict[j] = 1
                else:
                    tempDict[j] += 1
                if (not(j in bigDict)):
                    bigDict[j] = 1
                else:
                    bigDict[j] += 1
                if (not(j in totalDocDict)):
                    totalDocDict[j] = 1
                else:
                    if (tempDict[j] == 1):
                        totalDocDict[j] += 1
        #sort tokens by token (alphabetically) and by frequency; output these to 2 files for each html file
        tempDict.pop("", None)
        totalDocDict.pop("", None)
    bigDict.pop("", None)
    countOfHtml = 0
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
        weightDict = dict() #for tf weights
        #create entries and add to frequency if it already exists
        for j in tempText:
            #makes sure there are no stop words and the length of the word is greater than 1
            if (not(j in wordDict) and (len(j) > 1) and bigDict[j] > 1):
                if (not(j in tempDict)):
                    tempDict[j] = 1
                else:
                    tempDict[j] += 1
        #sort tokens by token (alphabetically) and by frequency; output these to 2 files for each html file
        tempDict.pop("", None)
        #remove all words with only one entry
        for key, value in tempDict.items():
            #goes through and creates term weights using tf and idf, then tf-idf
            tfWeight = float(value) / len(tempDict.keys())
            idfWeight = len(htmlList) / float(totalDocDict[key])
            idfWeight = math.log(idfWeight)
            weightDict[key] = tfWeight * idfWeight
        print(i)
        #outputting tokenized document
        with open(tokenDir, 'w') as file:
            file.write(json.dumps(weightDict))
        #then make it look nicer (formatting)
        formatInfo(tokenDir)
        file.close()
    #runtime for program overall (can vary)
    print "My program took", time.time() - start_time, "to run."
main()
