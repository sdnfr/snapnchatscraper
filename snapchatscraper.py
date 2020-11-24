import os
import sys
import re
import requests
import json
from datetime import datetime
import io
from time import sleep
from pyquery import PyQuery
from getpass import getpass
import sys
import msvcrt
import zipfile36


SessionCookie = {}
headerz = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,de;q=0.8",
    #"Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Length": "88",
    "Content-Type": "application/x-www-form-urlencoded",
    #"Cookie" : "URGripsLayout=Schmal; MoodleSession=qg6nq3qsdjeko2hme1h7vothup", 
    "Host": "elearning.uni-regensburg.de",
    "Origin": "https://elearning.uni-regensburg.de",
    "Referer": "https://elearning.uni-regensburg.de/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"

}







def DownloadMemories(path,dest):
    if Debug:
        print("you are trying to download into directory at " + dest)
        x = input()
        if x == "n":
            return False    
       
        if not os.path.isfile(path):
            print("ZIP file could not be found at "+ path)
            return False
        if not os.path.isfile(dest):
            try:
                os.mkdir(dest)
                print("destination folder did not exist. created directory at: " + dest)
            except:
                print("failed to create directory")

    src = UnzipFolder(path,dest)
    DownloadMemories(src,dest)
    

def UnzipFolder(path, dest):
    src = os.path.join(dest,"src")
    print(src)
    os.mkdir(src)
    with zipfile36.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(src)
    return src


def Login(userdata):

    postURL = "https://elearning.uni-regensburg.de/login/index.php"
    # debug
    # htmlFilePath = "grips.html"
    # with io.open(htmlFilePath, 'w', encoding='utf8') as f:
    #     f.write(x.text)



    ##post using cookie
    #post = requests.post(postURL, data = json.dumps(jsonData), cookies = reqCookie, headers= header)
    p = requests.post(postURL, data = userdata)

    #get cookie from redirecting
    for resp in p.history:
        for cookie in resp.cookies:
            SessionCookie[cookie.name] =  cookie.value

    html = p.text

    return { "success": True, "response": html}

def GetFolderStructure(html):
    folderStructure = dict()

    pq = PyQuery(html)
    folderList = pq('ul#qa-blocklist').children() #for some reason children func does not return object, only list of tags
    if len(folderList) < 1:
        print("No folders found on Grips course. Please use folders")
        return None
    
    for folder in folderList:
        folderID = folder.values()[0]
        coursesList = pq('li#'+folderID)('ul#qa-courselist').children()
        folderStructure[folderID] = []
        for course in coursesList:
            courseID = course.values()[0]
            htmlLinkTag = pq('li#'+courseID).children()[0]
            courseTitle = htmlLinkTag.values()[0]
            courseLink = htmlLinkTag.values()[1]
            folderStructure[folderID].append([courseTitle,courseLink])

    #print(folderStructure)
    with open("folderStructure.json", 'w', encoding='utf8') as outfile:
        json.dump(folderStructure, outfile, ensure_ascii=False)
    return folderStructure

# def UpdateFolders(folderStructure, path):
#     for folderName in folderStructure:
#         folderPath = os.path.join(path,folderName)
#         CreateFolder(folderPath)
#         for course in folderStructure[folderName]:
#             coursePath = os.path.join(folderPath,course[0])
#             if needsUpdate(course):
#                 print("individual course" + str(IndividualCourses))
#                 if IndividualCourses:
#                     print("Do you want to update course \"" + course[0] + "\" ? (y/n)")
#                     x = input()
#                     if x == "y":
#                         CreateFolder(coursePath)
#                         UpdateCourse(course, coursePath)
#                 else:
#                     UpdateCourse(course,coursePath)


def DownloadAll(src, dest):
    return True



# def oldstuff(course):
#     url = course[1]
#     x = requests.get(url, cookies=SessionCookie)
#     html = x.text 
#     pq = PyQuery(html)
#     files = pq("a.a_btn_ls")
#     for f in files.items():
#         fileURL = f.attr["href"]
#         fileName = f.text()
#         print("     Do you want to download file \"" + fileName + "\" ? (y/n)")
#         x = input()
#         if x == "n":
#             continue
#         r = requests.get(fileURL, cookies=SessionCookie)
#         open(os.path.join(coursePath,fileName + ".pdf"), 'wb').write(r.content)




def needsUpdate(course):
    url = course[1]
    x = requests.get(url, cookies=SessionCookie)
    html = x.text 

    htmlFilePath = "grips.html"
    with io.open(htmlFilePath, 'w', encoding='utf8') as f:
        f.write(x.text)



    
    return True

def CreateFolder(folderPath):
    if not os.path.isdir(folderPath):
        os.mkdir(folderPath)
        print("created new folder at: " + folderPath)
    return


Debug = True
if __name__ == "__main__":
    if len(sys.argv)<2:
        print("please provide destination -path: and -des: name or type -help")
        sys.exit()
    else:
        path = None
        dest = None
        for i, arg in enumerate(sys.argv):
            if re.match( r'-help', arg, re.M|re.I):
                print("use syntax python pythonscraper.py -path:PATH")
            if re.match( r'-path:', arg, re.M|re.I):
                path = arg.replace("-path:","")
            if re.match( r'-dest:', arg, re.M|re.I):
                dest = arg.replace("-dest:","")
        if (dest and path) is not None:
            DownloadMemories(path,dest)






