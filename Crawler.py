
# coding: utf-8

# #### In this notebook we build a Web Crawler to visitit and save the content of pages inside the uic domain:

# In[1]:


from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
# import libraries
#import urllib2
from bs4 import BeautifulSoup
import PyPDF2
import requests
import io

# We are going to create a class called LinkParser that inherits some
# methods from HTMLParser which is why it is passed into the definition
class LinkParser(HTMLParser):
    already_visited = []
    
    #remove '/' at the end of the url
    def normalizeUrl(url):
        #print("ciao4")
        if url.endswith('/'):
            url = url[:-1]
            #print("trimmed")
        return url
    
    # This is a function that HTMLParser normally has
    # but we are adding some functionality to it
    def handle_starttag(self, tag, attrs):
        # We are looking for the begining of a link. Links normally look
        # like <a href="www.someurl.com"></a>
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    # We are grabbing the new URL. We are also adding the
                    # base URL to it. For example:
                    # www.netinstructions.com is the base and
                    # somepage.html is the new URL (a relative URL)
                    #
                    # We combine a relative URL with the base URL to create
                    # an absolute URL like:
                    # www.netinstructions.com/somepage.html
                    newUrl = parse.urljoin(self.baseUrl, value)
                    
                    #check if url contains an hashtag i.e .uic/#artificialinteligence
                    if ("#" in newUrl):
                        #we have to take off the hashtag to normalize the link
                        pos = newUrl.find("#")
                        newUrl=newUrl[:pos]
                        #print("hashtag!")
                        #print(newUrl)
                    # And add it to our colection of links:
                    
            
                    if str(newUrl).endswith('/'):
                        newUrl = str(newUrl)[:-1]
                        
                    #when url starts with https
                    #check if the same url but with http is not already present
                    normUrl = newUrl
                    flag = False
                    if ("https" in newUrl):
                        #find first occurence of s (in https:)
                        pos = newUrl.find("s")
                        normUrl = newUrl[:pos] + newUrl[pos+1:]
                        flag = True
                        #print("https!!")
                        #print(normUrl)
                        # print(newUrl)
                            
                    if not(newUrl in self.already_visited) and not(normUrl in self.already_visited)  and ('.uic.edu' in newUrl):
                        self.already_visited.append(newUrl)
                        if (flag):
                            self.already_visited.append(normUrl)
                
                        self.links = self.links + [newUrl]

    # This is a function to get links
    # that the spider() function will call
    def getLinks(self, url):
        self.links = []
        # Remember the base URL which will be important when creating
        # absolute URLs
        self.baseUrl = url
        # Use the urlopen function from the standard Python 3 library
        response = urlopen(url)
        # Make sure that we are looking at HTML and not other things that
        # are floating around on the internet (such as
        # JavaScript files, CSS, or .PDFs for example)
        print(response.getheader('Content-Type'))
        
        #check if it is a HTML page
        if 'text/html' in response.getheader('Content-Type'):
            htmlBytes = response.read()
            #html = urllib.urlopen(url).read()
            soup = BeautifulSoup(htmlBytes)
            #text=soup.body.replace('\n',' ')

            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()    # rip it out

            # get text
            text = soup.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            #check if the parsing success
            #print(text)
            
            # (A change from Python 2.x to Python 3.x)
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            #print(self.links)
            return text, self.links
        else:
            if 'application/pdf' in response.getheader('Content-Type'):
                print("PDF FOUND!!!")
                string = ""
                r = requests.get(url)
                f = io.BytesIO(r.content)
                reader = PyPDF2.PdfFileReader(f)
                if reader.isEncrypted:
                    reader.decrypt('')
                contents =""
                for p in range(reader.getNumPages()):
                    contents += reader.getPage(p).extractText()
                    #print(contents)
                return contents,[]
                    
            return "-1",[]

   


# In[2]:


# And finally here is our spider. It takes in an URL, a word to find,
   # and the number of pages to search through before giving up
import codecs
import re
def spider(url,maxPages):  
   pagesToVisit = [url]
   numberVisited = 0
   parser = LinkParser()
   id = 0
   #dictionary id-> url of the web page
   urls_dictionary={}
   # The main loop. Create a LinkParser and get all the links on the page.
   # Also search the page for the word or string
   # In our getLinks function we return the web page
   # (this is useful for searching for the word)
   # and we return a set of links from that web page
   # (this is useful for where to go next)
   while numberVisited < maxPages and pagesToVisit != []:
       # Start from the beginning of our collection of pages to visit:
       url = pagesToVisit[0]
       parser.already_visited.append(url)
       #pop url
       pagesToVisit = pagesToVisit[1:]
       try:
           print(numberVisited, "Visiting:", url)
           #parser = LinkParser()
           data, links = parser.getLinks(url)
           #print(type(data))
           #print(data)
           
           #check if the url we just crawled is a url to crawl
           alpha=re.findall('[a-z]', data)
           if (data=="-1") or (len(alpha)<3):
               #print("URL NOT CRAWLED")
               continue
             
           ###write data into file
           with io.open("./documents2/" +str(id) +".txt", 'w', encoding="utf-8") as file:
               file.write(url)
               file.write("\n")
               file.write(data) 
               
           #update the list of pages to visit    
           pagesToVisit = pagesToVisit + links
           print("done " + str(numberVisited))
           #print(pagesToVisit)
           #add the entry id-> url in the dictionary
           urls_dictionary[id]=url
           id +=1
           numberVisited = numberVisited +1
       except Exception as e:
           print(e)
           print(" **Failed!**")

   return urls_dictionary


# In[4]:


dictionary = spider("https://www.cs.uic.edu", 3200)


# In[5]:


dictionary.keys()


# #### To run this cell, convert it in code cell
# ##write the url_dictionary into file
# with io.open("url_dictionary2.txt", 'w', encoding="utf-8") as doc:
#     i=1
#     for document in dictionary.keys():
#         doc.write(str(document) + "<id|url>" + dictionary[document] + "<element>")
#         #doc.write("<value>"+str(documents_weighted_norm[document])+"</value> <element> ")
#         #doc.write("\n")
#         i+=1
#         #if (i==10):
#         #    break
