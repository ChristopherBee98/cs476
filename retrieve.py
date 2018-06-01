#CMSC 476 Information Retrieval Homework 4
#Austin Bailey
#baustin1@umbc.edu
#(apologies for the wall of text)

#Create a command line retrieval engine. Search for terms and it should display the ten top-ranking document identifiers or filenames to the user.
#Example:
#$ retrieve dog cat mouse
#013.html 0.8
#404.html 0.3
#332.html 0.25
#...
#Due on April 23rd, 2018 at 11:59 PM
#Idea: Last project, we created 2 things: dictionary and postings list. To access the documents that the specific
#term appears in, use the dictionary to start where the list of documents it appears in the postings list. From there,
#use the data (maybe create dict for quick access?) to record the list of document ids. Do this for each term entered.
#To know when the list ends, keep checking if the next document id is less than the starting one for that term. After this, calculate the cosine
#similarity (check email sent from professor) and then rank the documents by the highest score. You can skip documents that don't contain at least
#one of the terms entered in the query.
#To start: Take the query and make it into a list. We will go through the list and do stuff with the terms.
#Cosine Similiarity: Dot product(d1, d2) / ||d1|| * ||d2||
#Dot product (d1, d2): d1[0] * d2[0] + d1[1] * d2[1] * ... * d1[n] * d2[n]
#||d1||: square root(d1[0]^2 + d1[1]^2 + ... + d1[n]^2)
#||d2||: ... (same as above but for d2)
#Note: d1 is the query, d2 is the current document. The term weights for each term in each document are in the postings list that was calculated
#last homework. Each term has a term weight in the query, and use that when doing the formula.
#Take all the documents that at least one term appears in, and perform cosine similarity.
#Don't know how many terms will be entered; have a for loop create as many lists as there are terms in the query. These lists will correspond with the list of
#total documents that contain at least one term (in order; example: documents 100 200 300 400 are the documents. so the term weights for each term in their list
#should correspond with the weights in that specific document. (look at https://janav.wordpress.com/2013/10/27/tf-idf-and-cosine-similarity/ matrix as an visual
#example). This is to make it easier to calculate cosine similarity. (use dict to store "list" of all documents with at least one term; useful for access and sort
#from smallest to largest once all of the entries have been added; maybe swap keys and values? see later)

#IMPORTANT: The cosine similarity is between query (treat it as a document; make a dictionary for it where key is term and
#value is term weight (calculate tf-idf for it). Use that as d1. 
#More advice: Add a condition when appending the dictionary list that checks for one of the terms entered in the commandline. If it's a match, do another append
#to this new list as well that will contain the 3 aspects of the normal dictionary list.

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

def calcQueryWeight(freqInDoc, amountOfTokens, totalDocFreq, key, htmlList):
    #create query weights
    tfWeight = float(freqInDoc) / amountOfTokens
    idfWeight = len(htmlList) / float(totalDocFreq)
    idfWeight = math.log(idfWeight)
    termWeight = tfWeight * idfWeight
    return termWeight

def main():
    start_time = time.time()
    inputDir = 'files'
    #if inputdir and outputdir are given as arguments
    if (len(sys.argv) < 2):
        print("Need at least one term for retrieval.")
    else:
        htmlList = []
        index = 0
        countOfHtml = 0
        firstPos = 1 #position start in posting file
        dictOfLists = defaultdict(list)
        postList = [] #postings file
        dictList = [] #dictionary file
        shortList = [] #used for quick access when retrieving
        #directory to path that parse.py is in
        tokenFilePath = os.path.abspath(os.path.join("sortedByTokens.csv"))
        frequencyFilePath = os.path.abspath(os.path.join("sortedByFrequency.csv"))
        #make a list of stopwords
        stopWordDoc = codecs.open(os.path.abspath(os.path.join("stoplist.txt")))
        tempWord = stopWordDoc.read()
        wordSoup = BeautifulSoup(tempWord, 'html.parser')
        stopWordList = wordSoup.get_text()
        stopWordList = stopWordList.split("\n")
        #contains every document that has at least one of the terms from the query
        dictWithOneTerm = dict()
        dictWithSingleTerm = []
        retrievalDict = dict()
        #contains each term from query, and value is the term weight (treat query as a document)
        queryDict = dict()
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
            #if one of the terms entered, also append to shortList
            appendShort = 0
            shortCounter = 1
            while (shortCounter < len(sys.argv)):
                if (word == sys.argv[shortCounter]):
                    appendShort = 1
                shortCounter += 1
            if (appendShort == 1):
                shortList.append(word)
                shortList.append(totalDocDict[word])
                shortList.append(firstPos)
            for tempW in tempList:
                if (not(tempW == 0) and (not(tempW == word))):
                    tempHolder = wordFreqCount - 1
                    postList.append((tempHolder, tempW)) #1 post and #2 post
                wordFreqCount += 1
            firstPos += totalDocDict[word] #move on to next first position for next word
        #checks to see if at least one of the terms is in the corpus
        inCorpus = 0
        #calculate query tf-idf, and then add to the dictionary queryDict
        queryCounter = 1
        #sets queryDict entries to 0 for conditional in next while loop
        while (queryCounter < len(sys.argv)):
            queryDict[sys.argv[queryCounter]] = 0
            queryCounter += 1
        queryCounter = 1
        while (queryCounter < len(sys.argv)):
            freqOfWord = 0
            for i in range(queryCounter, len(sys.argv)):
                if sys.argv[i] == sys.argv[queryCounter]:
                    freqOfWord += 1
            #checks to see if all terms are in the corpus; if one of them aren't, set to zero
            if (sys.argv[queryCounter] in totalDocDict):
                termWeight = calcQueryWeight(freqOfWord, (len(sys.argv) - 1), totalDocDict[sys.argv[queryCounter]], sys.argv[queryCounter], htmlList)
                inCorpus += 1
            else:
                print("")
                print "Term " + str(sys.argv[queryCounter]) + " was not used in search (either not in corpus or was filtered out by preprocessor)."
                termWeight = 0
            if (queryDict[sys.argv[queryCounter]] == 0):
                queryDict[sys.argv[queryCounter]] = termWeight
            queryCounter += 1
        #compile all documents with at least one of the terms (dictWithOneTerm)
        #startOfPost is 2 since the format of dictionary file is term, amount of appearances, and start position (increment each by 3)
        if (inCorpus == 0):
            print("")
            print "No results. Try different terms."
            #runtime for program overall (can very)
            print "My program took", time.time() - start_time, "to run."
            sys.exit()
        amountOfIterations = 1
        startOfPost = 2
        i = 1
        while (i < len(sys.argv)):
            #makes sure that the involved term is in the corpus
            if (sys.argv[i] in totalDocDict):
                j = 0
                counterOfDocuments = shortList[startOfPost] - 1
                while (j < shortList[amountOfIterations]):
                    #go through and add to dictionary
                    dictWithSingleTerm.append(postList[counterOfDocuments])
                    j += 1
                    counterOfDocuments += 1
                amountOfIterations += 3
                startOfPost += 3
            i += 1
        i = 0
        #adding the entries to the actual dictionary
        while (i < len(dictWithSingleTerm)):
            dictWithOneTerm[dictWithSingleTerm[i][0]] = 1
            i += 1
        dictWithOneTerm = sorted(dictWithOneTerm)
        #now using previous lists and dictionaries, calculate cosine similarity for the documents
        #go through each document and calculate the cosine similarity for each, then set it to the key in dictWithOneTerm
        dotProduct = 0
        queryAbs = 0
        #creates first abs value for cosine similarity
        for key in queryDict:
            queryAbs += math.pow(queryDict[key], 2)
        queryAbs = math.sqrt(queryAbs)
        currAbs = 0
        cosSim = 0
        #print(dictWithSingleTerm)
        for key in dictWithOneTerm:
            #set the word, to know which word currently on; used for accessing the terms query term weight (queryDict)
            #iterate the 3 short list aspects by 3
            startOfTerm = 0
            tempTerm = shortList[startOfTerm]
            shortCounter = 0
            genCounter = 0
            amountOfIterations = 1
            startOfPost = 2
            endIter = shortList[amountOfIterations]
            while (genCounter < len(dictWithSingleTerm)):
                if (shortCounter >= endIter):
                    prevIter = endIter
                    startOfTerm += 3
                    amountOfIterations += 3
                    startOfPost += 3
                    tempTerm = shortList[startOfTerm]
                    endIter = shortList[amountOfIterations] + prevIter
                currentWeight = 0
                #print("Key: ", key)
                #print("Current Doc: ", dictWithSingleTerm[shortCounter][0])
                if (key == dictWithSingleTerm[shortCounter][0]):
                    #if the term appears in current document, access the term weight (tfidf)
                    currentWeight = dictWithSingleTerm[shortCounter][1]
                currAbs += math.pow(currentWeight, 2)
                dotProduct += queryDict[tempTerm] * currentWeight
                shortCounter += 1
                genCounter += 1
            currAbs = math.sqrt(currAbs)
            #cosine similarity = Dot product(d1, d2) / ||d1|| * ||d2||
            cosSim = dotProduct / (queryAbs * currAbs)
            retrievalDict[key] = cosSim
            currAbs = 0
            dotProduct = 0
        #now to print the top ten documents
        retrievalDict = sorted(retrievalDict.items(), key=operator.itemgetter(1), reverse=True)
        onlyTen = 0
        print("")
        print("Top ten related documents: ")
        for key, value in retrievalDict:
            if (onlyTen < 10):
                if (key < 100):
                    if (key < 10):
                        print "00" + str(key) + ".html " + str(value)
                    else:
                        print "0" + str(key) + ".html " + str(value)
                else:
                    print str(key) + ".html " + str(value)
            onlyTen += 1
    #runtime for program overall (can very)
    print "My program took", time.time() - start_time, "to run."
main()
