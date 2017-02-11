import urllib.request
from bs4 import BeautifulSoup
from time import sleep, time
import pickle
import queue
import threading
import math

HYPER_EXPANSION_LIMIT = 2
# How many levels of links is it allowed to follow
HYPER_DEFAULT_LINK = "https://en.wikipedia.org/wiki/Vitamin_A"
HYPER_DEFAULT_SEARCH = "Vitamin A"
HYPER_DEFAULT_THREAD_TIMEOUT = 100

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_=+{}[]'\\./,<>?:\";'1234567890 "

status = ""

parsedLinks = []
parsedLinksCount = 0

q = queue.Queue
threads = []
threads2 = []
times=[]

currentThreadsActive = 0


def getGeneratorLen(gen):
    count = 0
    for i in gen:
        count += 1
    return count


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)  # use start += 1 to find overlapping matches


def getNextStringIndexFromIndex(string, searchstring, index):
    for i in range(index, len(string)):
        # print("[DEBUG] Iterating " + str(i) + "/" + str(len(string)))
        if str(string[i]) == str(searchstring):
            return i
    return -1


def getMainInformation(text, searchString):
    final = ""
    if searchString not in text:
        return 0
    else:
        position = 1
        indexies = find_all(text, searchString)
        for index in indexies:
            # print("[DEBUG : MAIN INFO] Interating through index " + str(position) + "/" + str(getGeneratorLen(indexies)))
            sentanceEnd = getNextStringIndexFromIndex(text, ".", index)
            final += text[index:sentanceEnd]
            final += "\n"
            position += 1
    return final


def summarise(link, word):
    # print("Parsing " + link)
    try:
        with urllib.request.urlopen(link) as source:  # Parse Wikipedia Page
            http = source.read()
        soup = BeautifulSoup(http, 'html.parser')
    except ValueError:
        # print(link + " is not a valid link!")
        return -1

    # Inform user
    # print("Parsed " + soup.title.string)
    # print("Getting paragraph text...")
    paragraph = soup.p.getText()
    # print("Retrived text")
    # print("Retriving important information...")
    if word not in paragraph:
        # print("Error, search string " + word + " has no occurance, trying non-plural form")
        if word not in paragraph:
            # print("Non-Plural valid")
            final = getMainInformation(paragraph, word[:-1])
            return final
        else:
            # print("Plural invalid")
            final = 0
    else:
        final = getMainInformation(paragraph, word)
    if(final != 0):
        return final


def getWebsiteExists(link):
    try:
        urllib.request.urlopen(link)
    except:
        # print(link + " is not a valid link!")
        return -1
    return 0


parsedInformation = {}


def getLinkInfo(aElement, betweenTag, word):
    global currentThreadsActive
    global status
    startTime = time()
    if aElement.string != "None":
        try:
            if len(betweenTag.split(" ")) > 1 or word == betweenTag:
                return
            else:
                parseLink = aElement.get("href")
                if str(parseLink) == "None":
                    # print("Passing due to missing href")
                    return
                if parseLink[0:6] == "/wiki/":
                    parseLink = "https://en.wikipedia.org" + parseLink
                    # print("Link not formatted correctly, correcting to " + parseLink)
                if (
                                    "File:" in parseLink or "Main_Page" in parseLink or parseLink == "https://wikimediafoundation.org/"):
                    # print("Continuing due to file or main page")
                    return
                if any(parseLink in str(s) for s in parsedLinks):
                    # print("Passing due to already parsed " + betweenTag)
                    return
                parsedLinks.append(parseLink)
                if getWebsiteExists(parseLink) == -1:
                    return
                else:
                    parsedInformation[betweenTag.upper()] = summarise(parseLink, betweenTag)
                    endtime = time()
                    timeSpent = math.floor((endtime-startTime) * currentThreadsActive-1)
                    times.append(timeSpent)
                    if len(times) > 10:
                        del times[0]
                    totalTimeSpent = 0
                    for t in times:
                        totalTimeSpent+=t
                    averageTimeSpent = math.floor(totalTimeSpent/len(times))
                    status = str(math.floor(averageTimeSpent/60)) + "m Remaining"
                    currentThreadsActive -= 1
                    del threads[threads.find(threading.current_thread())]
        except AttributeError:
            return
    else:
        return


def readLinks(link, word):
    global threads
    global currentThreadsActive
    print("Parsing links to level " + str(HYPER_EXPANSION_LIMIT) + "...")
    checkedLinks = 0

    with urllib.request.urlopen(link) as source:  # Parse Wikipedia Page
        HTTP = source.read()
    SOUP = BeautifulSoup(HTTP, 'html.parser')
    threadtimes = []
    linkCount = len(SOUP.find_all("a"))

    for aElement in SOUP.find_all("a"):
        print("\n")
        print("Creating thread " + str(checkedLinks) + "/" + str(linkCount))
        betweenTag = aElement.getText()
        checkedLinks += 1
        threads.append(threading.Thread(target=getLinkInfo, args=(aElement, betweenTag, word)))
        currentThreadsActive += 1
    print("Starting Threads")
    for thread in threads:
        thread.start()
        threadtimes.append(math.floor(time()))
    print("Waiting for thread completion")
    sleep(1)
    for i in range(0, len(threads) - 1):
        threads[i].join()
    print("Parsed " + str(parsedLinksCount) + " links, check " + str(checkedLinks))
    sleep(3)
    # print(parsedInformation)
    pickle.dump(parsedInformation, open("save.p", "wb"))


def go(action):
    global parsedInformation
    readLink = False
    if action == "PARSE":
        link = input("What do you want me to parse?\n")
        word = input("What do you want me to learn about?\n")
        parsedInformation[word.upper] = summarise(link, word)
        readLink = True
    elif action == "TEST":
        link = HYPER_DEFAULT_LINK
        word = HYPER_DEFAULT_SEARCH
        parsedInformation[word.upper] = summarise(link, word)
        readLink = True
    elif action == "LOAD":
        parsedInformation = pickle.load(open("save.p", "rb"))
    if action == "SAVE":
        pickle.dump(parsedInformation, open("save.p", "wb"))
    if readLink:
        # noinspection PyUnboundLocalVariable,PyUnboundLocalVariable
        readLinks(link, word)


def getParsedInformation():
    return parsedInformation


def listParsedInformation(slow=False):
    # print("Learnt topics:")
    keys = parsedInformation.keys()
    for key in keys:
        print(key)
        if slow:
            sleep(0.5)


def searchParsedInformation(text):
    keys = parsedInformation.keys()
    for key in keys:
        if text in key or key in text:
            print(key)


def queryParsedInformation(text):
    keys = parsedInformation.keys()
    for key in keys:
        try:
            print(parsedInformation[key])
            if text in parsedInformation[key]:
                print("Term found in " + key)
        except:
            continue


def getInformation(key):
    return parsedInformation[key]


def filter():
    global parsedInformation
    newList = {}
    keys = parsedInformation.keys()
    for key in keys:
        delete = False
        for letter in key:
            if letter not in alphabet:
                # print(key + " is not english")
                delete = True
        if type(parsedInformation[key]) != str:
            delete = True
        if not delete:
            newList[key] = parsedInformation[key]


    parsedInformation = newList


def selfExpand(initialLink, word):
    global currentThreadsActive
    print("Expanding on " + initialLink)
    sleep(1)
    summarise(initialLink, word)
    with urllib.request.urlopen(initialLink) as source:  # Parse Wikipedia Page
        HTTP = source.read()
    SOUP = BeautifulSoup(HTTP, 'html.parser')
    title = SOUP.find("div", {"id": "firstHeading"})
    for aElement in SOUP.find_all("a"):
        betweenTag = aElement.getText()
        threads2.append(threading.Thread(target=getLinkInfo, args=(aElement, betweenTag, title)))
        currentThreadsActive += 1
    sleep(1)
    for thread in threads2:
        thread.start()
        thread.join()
    print("Threads done")
    for aElement in SOUP.find_all("a"):
        if getWebsiteExists(aElement.get("href")) > 0:
            print("Valid link " + str(aElement.get("href")) + " found, recursing.")
            selfExpand(str(aElement.get("href")), aElement.getText)


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
        Loads the save file
    Save
        Saves to save file
QUIT
    Exits info stream

SEARCH [STRING]
    Searches the keys for a string

QUERY [STRING]
    Searches keys and text bodies for a string
FILTER
    Takes all the non-english keys out
LEARN
    Start the background load process
THREADS
    Lists the threads
"""


def takeAction(action):
    global threads
    global currentThreadsActive
    if action[0] == "GET":
        return "Information on " + action[1] + ":\n" + str(parsedInformation[action[1]])
    elif action[0] == "LIST":
        print("Listing " + str(len(parsedInformation)) + " entries")
        try:
            if action[1] == "SLOW":
                if True:
                    listParsedInformation(True)
                else:
                    return
            else:
                listParsedInformation()
        except IndexError:
            listParsedInformation()
    elif action[0] == "GO":
        try:
            go(action[1])
        except IndexError:
            return "Not enough arguments"
    elif action[0] == "QUIT":
        return
    elif action[0] == "SEARCH":
        try:
            action[2] == action[2]
        except IndexError:
            hasArgument = False
        else:
            hasArgument = True
        if hasArgument:
            searchParsedInformation(action[1])
        else:
            try:
                searchParsedInformation(action[1])
            except IndexError:
                return "Error! you must specify a search string"
    elif action[0] == "QUERY":
        try:
            action[2] == action[2]
        except IndexError:
            hasArgument = False
        else:
            hasArgument = True
        if hasArgument:
            queryParsedInformation(action[1])
        else:
            try:
                queryParsedInformation(action[1])
            except IndexError:
                return "Error! you must specify a query string"
    elif action[0] == "FILTER":
        filter()
    elif action[0] == "PRINT":
        return parsedInformation
    elif action[0] == "LEARN":
        threads.append(threading.Thread(target=selfExpand, args=(HYPER_DEFAULT_LINK, HYPER_DEFAULT_SEARCH)))
        currentThreadsActive += 1
    elif action[0] == "THREADS":
        if(len(threads) + len(threads2) > 15):
            print("There are " + str(len(threads2) + len(threads)) + " threads, display? y/n")
            if(input("").upper() == "y"):
                print("First Threads")
                for thread in threads:
                    print(thread)
                    sleep(0.3)
                print("Level two threads")
                for thread in threads2:
                    print(thread)
                    sleep(0.3)
    elif action[0] == "STATUS":
        print(status)
    else:
        return "Error, not valid command"
    sleep(0.2)


def main():
    print(parsedInformation)
    print("Initiating info loop")
    while True:
        for thread in threads:
            if not thread.isAlive():
                try:
                    thread.start()
                except RuntimeError:
                    continue
        action = input("What should I do?\n")
        action = action.upper()
        action = action.split(" ")
        print(takeAction(action))


if __name__ == "__main__":
    main()
