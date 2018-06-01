#CMSC 476 Information Retrieval Homework 3
#Austin Bailey
#baustin1@umbc.edu

#Produce the following:
#- A dictionary file which contains the following:
#1. the word
#2. the number of documents that contain that word (corresponds to the number of records that word gets in the postings file)
#3. the location of the first record for that word in the postings file
#- A postings file which contains:
#1. the document id
#2. the normalized weight of the word in the document
#Posting File Position: wherever it starts (array position 0 would be position 1 as an example)
#Make a hash table of lists (recreate the matrix in proj3 page)
#Need to go through and "finish" each term throughout corpus before moving on to next word
#TDM key is the word, and the value is a list that contains the word and all of its weights throughout the documents
#Need to fix something here for part4; words are said to be showing in documents that aren't in them (look at woods in dictionary file and then posting file)

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
from collections import defaultdict

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
    outputDir = 'indexTokens'
    #if inputdir and outputdir are given as arguments
    if (len(sys.argv) == 3):
        inputDir = sys.argv[1]
        outputDir = sys.argv[2]
    start_time = time.time()
    htmlList = []
    index = 0
    countOfHtml = 0
    firstPos = 1 #position start in posting file
    dictOfLists = defaultdict(list)
    postList = [] #postings file
    dictList = [] #dictionary file
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
        for t in tempDict:
            #checks for existence
            if len(dictOfLists[t]) == 0:
                dictOfLists[t].append(t)
            if t in dictOfLists:
                #determines position for term
                positionOfTerm = countOfHtml - len(dictOfLists[t])
                for pos in range(0, positionOfTerm + 1):
                    dictOfLists[t].append(0)
                dictOfLists[t].append(weightDict[t])
        for tempT in dictOfLists:
            if (not(tempT in weightDict)):
                dictOfLists[tempT].append(0)
        print(i)
    #making dictionary and postings list
    for word in dictOfLists:
            tempList = dictOfLists[word]
            wordFreqCount = 0
            dictList.append(word) #1 dict
            dictList.append(totalDocDict[word]) #2 dict
            dictList.append(firstPos) #3 dict
            #problem: document is 1 ahead of what it should be; make it minus one
            for tempW in tempList:
                if (not(tempW == 0) and (not(tempW == word))):
                    tempHolder = wordFreqCount - 1
                    postList.append((tempHolder, tempW)) #1 post and #2 post
                wordFreqCount += 1
            firstPos += totalDocDict[word] #move on to next first position for next word
    #outputting tokenized document
    dictName = "dictionaryFile"
    postName = "postingFile"
    dictDir = os.path.abspath(os.path.join(outputDir, dictName + ".csv"))
    postDir = os.path.abspath(os.path.join(outputDir, postName + ".csv"))
    with open(dictDir, 'w') as file:
        file.write(json.dumps(dictList))
    #then make it look nicer (formatting)
    formatInfo(dictDir)
    file.close()
    #outputting tokenized document
    with open(postDir, 'w') as file:
        file.write(json.dumps(postList))
    #then make it look nicer (formatting)
    formatInfo(postDir)
    file.close()
    #runtime for program overall (can very)
    print "My program took", time.time() - start_time, "to run."
main()
