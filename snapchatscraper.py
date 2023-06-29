import os
import sys
import re
import requests
from pyquery import PyQuery
import sys
import zipfile36

# This script uses the zip file from snapchat containing the personal information. 
# It expects a folder called html which contains the memories_history.html 
# memories_history.html is containing the links of all media that is stored.

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

        try:
            snapchatResponse = requests.post(url)
            r = requests.get(snapchatResponse.content)
            open(finalPath, 'wb').write(r.content)
        except:
            print("could not import: " + filename + " with link " + url)

            
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






