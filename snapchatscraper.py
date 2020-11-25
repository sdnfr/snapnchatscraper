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
    DownloadAll(src,dest)
    

def UnzipFolder(path, dest):
    src = os.path.join(dest,"src")
    print(src)
    if not os.path.isfile(src):
        try:
            os.mkdir(src)
            with zipfile36.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(src)
        except:
            print("failed to create src directory")
            return src

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
    src = os.path.join(src,"html","memories_history.html")
    file = open(src, "r")
    html = file.read()
    pq = PyQuery(html)
    rows = pq("tr")
    triples = []
    for row in rows.items():
        pq2 = PyQuery(row.html())
        tds = pq2("td")
        if not len(tds.text())==0:
            i = 0
            for td in tds.items():
                i += 1
                if (i==1):
                    yearmonth = td.text()
                    month =yearmonth[5:7]
                    year = yearmonth[0:4]
                if (i==2):
                    type = td.text()
                if (i==3):
                    ref = td("a").attr["href"]
                    if ref is not None:
                        ref = ref.replace("javascript:downloadMemories('","")
                        ref = ref.replace("');","")
                    else:
                        ref = None
            triple = (year,month,yearmonth[0:16].replace(":","-").replace(" ","_"),type,ref)
            triples.append(triple)
    DownloadTriples(triples,src,dest)



def DownloadTriples(triples,src,dest):
    yearmonths = []
    for item in triples:
        yearmonth = item[0] + "-" + item[1]
        yearmonths.append(yearmonth)
    CreateFolders(yearmonths,dest)
    imageCounter = -1
    count = len(triples)
    for item in triples:
        imageCounter +=1
        print("downloading " + item[3] + " " + str(imageCounter) + " of total of " + str(count) + " files...")
        destPath = os.path.join(dest,item[0],item[1])
        filename = item[2] + "_" + str(imageCounter)
        if item[3]=="VIDEO":
            fileextension = ".mp4"
        if item[3]=="PHOTO":
            fileextension = ".jpg"
        finalPath = os.path.join(destPath,filename+fileextension)
        url = item[4]
        snapchatResponse = requests.post(url)
        r = requests.get(snapchatResponse.content)
        open(finalPath, 'wb').write(r.content)




            
def CreateFolders(yearmonths,dest):
    for item in yearmonths:
        year = item[0:4]
        month = item[5:7]
        yearPath = os.path.join(dest,year)
        monthPath = os.path.join(yearPath,month)
        if not os.path.isdir(yearPath):
            os.mkdir(yearPath)
        if os.path.isdir(yearPath):
            if not os.path.isdir(monthPath):
                os.mkdir(monthPath)
    




    # refs = []
    # for f in files.items():
    #     ref = f.attr["href"]
    #     if ref is not None:
    #         ref = ref.replace("javascript:downloadMemories('","")
    #         ref = ref.replace("');","")
    #         refs.append(ref)
    # print(refs[1])
    # url = refs[1]
    # snapchatResponse = requests.post(url)
    # text = snapchatResponse.content.decode("utf-8") 
    # print(snapchatResponse.content)
    # r = requests.get(snapchatResponse.content)
    # if text.__contains__("mp4"):
    #     open(os.path.join(dest,"test2.mp4"), 'wb').write(r.content)
    # if text.__contains__("jpg"):
    #     open(os.path.join(dest,"test2.jpg"), 'wb').write(r.content)




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






