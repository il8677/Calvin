import urllib.request
from bs4 import BeautifulSoup
from time import sleep, time
import pickle
import queue
import threading
import math

HYPER_EXPANSION_LIMIT = 2 #How many levels of links is it allowed to follow
HYPER_DEFAULT_LINK = "https://en.wikipedia.org/wiki/Vitamin_A"
HYPER_DEFAULT_SEARCH = "Vitamin A"
HYPER_DEFAULT_THREAD_TIMEOUT = 100

alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_=+{}[]'\\./,<>?:\";'1234567890 "

parsedLinks = []
parsedLinksCount = 0

q=queue.Queue

def getGeneratorLen(gen):
    count=0
    for i in gen:
        count+=1
    return count
def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches
def getNextStringIndexFromIndex(string, searchstring, index):
    for i in range(index, len(string)):
        #print("[DEBUG] Iterating " + str(i) + "/" + str(len(string)))
        if(str(string[i])==str(searchstring)):
            return i
    return -1

def getMainInformation(text, searchString):
    final = ""
    if(searchString not in text):
        return 0
    else:
        position=1
        indexies = find_all(text, searchString)
        for index in indexies:
            print("[DEBUG : MAIN INFO] Interating through index " + str(position) + "/" + str(getGeneratorLen(indexies)))
            sentanceEnd = getNextStringIndexFromIndex(text, ".", index)
            final+=text[index:sentanceEnd]
            final+="\n"
            position+=1
    return final
def summarise(link,word):
    print("Parsing " + link)
    try:
        with urllib.request.urlopen(link) as source:  # Parse Wikipedia Page
            http = source.read()
        soup = BeautifulSoup(http, 'html.parser')
    except ValueError:
        print(link + " is not a valid link!")
        return -1


    # Inform user
    print("Parsed " + soup.title.string)
    print("Getting paragraph text...")
    paragraph = soup.p.getText()
    print("Retrived text")
    print("Retriving important information...")
    if (word not in paragraph):
        print("Error, search string " + word + " has no occurance, trying non-plural form")
        if(word not in paragraph):
            print("Non-Plural valid")
            final = getMainInformation(paragraph, word[:-1])
            return final
        else:
            print("Plural invalid")
            return -1
    else:
        final=getMainInformation(paragraph, word)
        if (getMainInformation(paragraph, word) == paragraph):
            print("Parsed text is the same as summarised text")
    return final
def getWebsiteExists(link):
    try:
        urllib.request.urlopen(link)
    except:
        print(link + " is not a valid link!")
        return -1
    return 0

parsedInformation={}
def getLinkInfo(aElement, betweenTag,word):
    if (aElement.string != "None"):
        try:
            if (len(betweenTag.split(" ")) > 1 or word == betweenTag):
                return
            else:
                parseLink = aElement.get("href")
                if (str(parseLink) == "None"):
                    print("Passing due to missing href")
                    return
                if (parseLink[0:6] == "/wiki/"):
                    parseLink = "https://en.wikipedia.org" + parseLink
                    print("Link not formatted correctly, correcting to " + parseLink)
                if ("File:" in parseLink or "Main_Page" in parseLink or parseLink == "https://wikimediafoundation.org/"):
                    print("Continuing due to file or main page")
                    return
                if (any(parseLink in str(s) for s in parsedLinks)):
                    print("Passing due to already parsed " + betweenTag)
                    return
                parsedLinks.append(parseLink)
                if (getWebsiteExists(parseLink) == -1):
                    return
                else:
                    parsedInformation[betweenTag] = summarise(parseLink, betweenTag)
                    print("Thread Completed")
        except AttributeError:
            return
    else:
        return
def readLinks(link,word):
    print("Parsing links to level " + str(HYPER_EXPANSION_LIMIT) + "...")
    checkedLinks = 0

    with urllib.request.urlopen(link) as source:  # Parse Wikipedia Page
        HTTP = source.read()
    SOUP = BeautifulSoup(HTTP, 'html.parser')
    threads = []
    threadtimes = []
    linkCount = len(SOUP.find_all("a"))

    for aElement in SOUP.find_all("a"):
        print("\n")
        print("Creating thread " + str(checkedLinks) + "/" + str(linkCount))
        betweenTag = aElement.getText()
        checkedLinks += 1
        threads.append(threading.Thread(target=getLinkInfo, args=(aElement,betweenTag,word)))

    print("Starting Threads")
    for thread in threads:
        thread.start()
        threadtimes.append(math.floor(time()))
    print("Waiting for thread completion")
    sleep(1)
    for i in range(0,len(threads)-1):
        threads[i].join()
    print("Parsed " + str(parsedLinksCount) + " links, check " + str(checkedLinks))
    sleep(3)
    print(parsedInformation)
    pickle.dump(parsedInformation, open("save.p", "wb"))

def go(action):
    global parsedInformation
    readLink=False
    if(action=="PARSE"):
        link=input("What do you want me to parse?\n")
        word=input("What do you want me to learn about?\n")
        parsedInformation[word] = summarise(link, word)
        readLink=True
    elif(action=="TEST"):
        link = HYPER_DEFAULT_LINK
        word = HYPER_DEFAULT_SEARCH
        parsedInformation[word] = summarise(link, word)
        readLink=True
    elif(action=="LOAD"):
        parsedInformation=pickle.load(open("save.p", "rb"))
    if(action=="SAVE"):
        pickle.dump(parsedInformation, open("save.p", "wb"))
    if(readLink):
        readLinks(link,word)
def getParsedInformation():
    return parsedInformation
def listParsedInformation(slow = False):
    print("Learnt topics:")
    for key in parsedInformation.keys():
        print(key)
        if(slow):
            sleep(0.5)
def searchParsedInformation(text, slow = False):
    for key in parsedInformation.keys():
        if(text in key or key in text):
            print(key)
def queryParsedInformation(text, slow= False):
    occured = False
    for key in parsedInformation.keys():
        try:
            print(parsedInformation[key])
            if(text in parsedInformation[key]):
                print("Term found in " + key)
                occured = True
        except:
            continue
    if(not occured):
        print("No occurance found")
def getInformation(key):
    return

def filter():
    global parsedInformation
    newList={}
    for key in parsedInformation.keys():
        delete=False
        for letter in key:
            if letter not in alphabet:
                print(key + " is not english")
                delete=True
        if not delete:
            newList[key] = parsedInformation[key]
    parsedInformation=newList

"""
GET
    Gets the information from a key
LIST
    Lists all of the keys

    Extra Args
        SLOW
            Prints the entries slower
GO [COMMAND]
    Executes one of the opening commands:
    Test
        Tests the program on one of the default sites
    Parse
        Parses a specific link
    Load
        Loads a specific link

QUIT
    Exits info stream

SEARCH [STRING]
    Searches the keys for a string

QUERY [STRING]
    Searches keys and text bodies for a string
FILTER
    Takes all the non-english keys out
"""
def takeAction(action):
    if (action[0] == "GET"):
        return("Information on " + action[1] + ":\n" + parsedInformation[action[1]])
    elif (action[0] == "LIST"):
        try:
            if (action[1] == "SLOW"):
                if (True):
                    listParsedInformation(True)
                else:
                    return
            else:
                listParsedInformation()
        except IndexError:
            listParsedInformation()
    elif (action[0] == "GO"):
        try:
            go(action[1])
        except IndexError:
            return("Not enough arguments")
    elif (action[0] == "QUIT"):
        return
    elif (action[0] == "SEARCH"):
        hasArgument = False
        try:
            action[2] == action[2]
        except IndexError:
            hasArgument = False
        else:
            hasArgument = True
        if (hasArgument):
            searchParsedInformation(action[1], True)
        else:
            try:
                searchParsedInformation(action[1])
            except IndexError:
                return("Error! you must specify a search string")
    elif (action[0] == "QUERY"):
        hasArgument = False
        try:
            action[2] == action[2]
        except IndexError:
            hasArgument = False
        else:
            hasArgument = True
        if (hasArgument):
            queryParsedInformation(action[1], True)
        else:
            try:
                queryParsedInformation(action[1])
            except IndexError:
                return("Error! you must specify a query string")
    elif (action[0] == "FILTER"):
        filter()
    elif (action[0] == "PRINT"):
        return(parsedInformation)
    else:
        return("Error, not valid command")
        sleep(0.2)
    sleep(0.2)
def main():
    print(parsedInformation)
    print("Initiating info loop")
    while True:
        action = input("What should I do?\n")
        action = action.upper()
        action = action.split(" ")
        print(takeAction(action))
if(__name__ == "__main__"):
    main()