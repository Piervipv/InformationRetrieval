
# coding: utf-8

# note: run again inverted index and weighted norm

# In[1]:


import io
import re
from nltk.stem import PorterStemmer
import operator
import math
from nltk.tokenize import RegexpTokenizer


# In[2]:


#load stopwordList
#retrive the list of stopwords
stemmer=PorterStemmer()

stop_words_input = input('Please provide stop_words_path txt file . \n To select the default option "./stopwords.tx" press d ')
if (stop_words_input.lower() == 'd'):
    
    stopwords_path ="./stopwords.txt"  
else:
    stopwords_path =stop_words_input
print(stopwords_path)
stopwords = open(stopwords_path).read()
stopwords_list=stopwords.split()
for stop in stopwords_list:
    temp = stemmer.stem(stop)
    if not (temp in stopwords_list):
    
       stopwords_list.append(temp)


# ##### We have to apply to the queries the same preprocess used during the indexing:

# In[3]:


#remove pintaction and numbers
def remove_punt_and_number(string):
    remove_list=['0','1','2','3','4','5','6','7','8','9' ]
    #remove_list=[]
    string2=''
    for i in range(0,len(string)):
        if not(string[i] in remove_list):
            string2=string2 +string[i]
    return string2


# In[4]:


#function to perform preprocessing: remove puntaction,tokenize,stemming, stopwords and words of 1,2 characters
#return the list of tokens in the string/document
def preprocess(string):
    tokens=[]
    #define regular expression for tokens
    tokenizer=RegexpTokenizer('([a-z]*[-]?[a-z]+[-]?[a-z]*|[0-9]+[-]?[a-z]+|[a-z]+[-]?[0-9]+)') 
    tokens=tokenizer.tokenize(string.lower())
    #remove_punt_and_number(string)#remove puntanction
    stemmer=PorterStemmer()
    stemmed_tokens=[]
    for word in tokens:
        token=remove_punt_and_number(word)
        token=stemmer.stem(token);
        token=token.strip("-")
        alpha=re.findall('[a-z]', token)
        if not(token in stopwords_list or len(alpha)<3): #condition to eliminate stopwords
            stemmed_tokens.append(token) #stemming
    return stemmed_tokens


# In[5]:


#query is a list of tokens,
#matching docs is a list of documents' IDs

#for each token, incrementally compute cosine_similarity for each document
#at the end, divide by document and query norm
#returns a hash doc_id : similarity value

def compute_similarity(query, matching_docs, weight_dictionary):
    similarity={}
    score=0
    #initialize similarity dictionary
    for doc in matching_docs:
        key=doc
        value=int(0)
        similarity[key]=value
    #compute the accumulated similarity
    for token in query:
        weight = 1
        
        #weight_dictionary contains the weight for the token coming from query expansion
        #the weight is the similarity of the expanded token w.r.t. the original token
        if token in weight_dictionary.keys():
            weight = weight_dictionary[token]
            
        #if the token is not in the weight_dictionary
        #it means that is not an expanded token but a 
        #token that was present in the original query,
        #so its weight is equal to 1
        
        for doc in matching_docs:
            key=doc
            score= weight * tf(token,doc)*idf(token)**2 
            similarity[key] += score #increment the similarity
            
    #divide by document and query's norm
    for doc in matching_docs:
        key=doc
        
        #take the norm of the document
        divider=weighted_norm_dictionary[key]
        #####TODO:
        #if (divider==0):
            #divider+=1
        #print(divider)
        
        #we don't need the qouery norm so the line below is commented
        #divider= divider * query_norm(query)
        #print(divider)
        
        similarity[key] = similarity[key] / divider
        
    #debug    
    #print ("similarity_dict")
    #print (similarity)
    
    return similarity


# In[6]:


#retrieve only the documents that contains at least 1 token of the query
def retrive_docs(query_tokens):
    matching_docs=set()
    token_list=list(inverted_index.keys())
    
    ### TODO:: use try catch
    for tokens in query_tokens:
        #print("token:")
        #print(tokens)
        if (tokens in token_list):
            x=inverted_index[tokens]
            #print("containing docs:")
            #print(list(x.containing_documents.keys()))
            documents=list(x.containing_documents.keys())
            #print(documents)
            #print("documents")
            #print(documents)
            matching_docs.update(documents)
    #print(matching_docs) #debug
    return matching_docs


# In[7]:


#compute the query_norm (if needed)
def query_norm(query_tokens):
    #quertokens=documents_dictionary[document_id]
    sum=0
    term_freq=0
    for token in set(query_tokens):
        #print(term_freq)
        term_freq=occurencies(query_tokens, token)
        idfe=idf(token) #documents_dictionary is used to retrieve N
        weight=term_freq*idfe
        #print(weight) #debug
        sum += weight * weight
        #print(sum) #debug
    return sum**(0.5)


# In[8]:


#ranks the documents
#returns an ordered list of tuples
def rank_docs(similarity_dictionary):
    from operator import itemgetter
    sorted_docs = sorted(similarity_dictionary.items(), key=itemgetter(1), reverse=True)
    
    #debug
    #print("sorted docs:")
    #print(sorted_docs)
    #print(type(sorted_docs))
    #print(sorted_docs[1])
    
    return sorted_docs


# In[9]:


def retrive_ranked_docs(query, smart):
    #smart component:
    #expand the query with semantically similar words
    # we need the unprocessed words of the query
    q = query
    unprocessed_query_tokens = query.split()
        
    weigh_dictionary = {}
    
    #print(unprocessed_query_tokens)
    
    #if smart option == 1
    #expand the query with model1
    if (smart == 1):
        for token in unprocessed_query_tokens:
            #retrieve most similar words
            try:
                pairList = model.most_similar(positive=[token])
                #for each similar word add th word in the query and
                #an entry in the weight_dictionary to take into account the value of the similarity during the ranking phase
                for pair in pairList:
                    #consider only similar terms with similarity > 0.5
                    if pair[1] > 0.6:
                        q += " " + pair[0]
                        weigh_dictionary[pair[0]] = pair[1]
            except:
                print("word: " + token + " not in the model vocaboulary")
                
                
    #if smart option == 2
    #expand the query with model2
    if (smart == 2):
        for token in unprocessed_query_tokens:
            #retrieve most similar words
            try:
                pairList = model2.most_similar(positive=[token])
                #for each similar word add th word in the query and
                #an entry in the weight_dictionary to take into account the value of the similarity during the ranking phase
                for pair in pairList:
                    #consider only similar terms with similarity > 0.5
                    if pair[1] > 0.6:
                        q += " " + pair[0]
                        weigh_dictionary[pair[0]] = 0.9 * pair[1]
            except:
                print("word: " + token + " not in the model vocaboulary")
    
    print("New expanded query: ")
    print()
    print('"' + q + '"')
    print()
    
    query_tokens=preprocess(q)
    #print("query tokens")
    #print(query_tokens)
    
    #query_weighted_norm=query_norm(query_tokens, documents_dictionary, inverted_index)
    
    #retrieve matching documents
    matching_documents= retrive_docs(query_tokens)
    print('Number of matching documents:')
    print(len(matching_documents))
    print()
    print("ranking the documents...")

    #we pass the weigh_dictionary because 
    #the score for the expanded token has to be multipliaed 
    #for the similarity wrt the original token
    similarity_dictionary=compute_similarity(query_tokens, matching_documents, weigh_dictionary)
    
    #print(ranking)
    ranking=rank_docs(similarity_dictionary)
    
    #print("ranking")
    #print (ranking)
    return ranking


# In[10]:


#load the dictionary documentId-> url from file
#urlDictionary

print("Loading the url dictionary...")

url_dictionary_path = "url_dictionary2.txt" #if needed change it

with io.open(url_dictionary_path, 'r', encoding="utf-8") as file:
        temp_doc=file.read()
        #parse the file
        elemList = temp_doc.split("<element>")
        #print(elemList)
        elemList= elemList[:-1]
        #urlDictionary
        urlDictionary = {}
        for elem in elemList:
            id = elem.split("<id|url>")[0]
            value = elem.split("<id|url>")[1]
            #print("id: " + id)
            #print("value: " + value)
            urlDictionary[id] = value
            #print()


# In[11]:


#urlDictionary["1"]


# In[12]:


class token_class:
    def __init__(self, idf=0,containing_documents= {}):
        self.idf=idf #number of containing docs
        self.containing_documents=containing_documents   


# ##### Load inverted index from file:

# In[13]:


#extract dictionary of containing document for the parsing of inverted_index
def extract_dictionary (string):
    containing_docs = {}
    #remove '{' and '}'
    string = string.strip()
    string = string[1:-1]
    #print(string)
    ##split over ',' to extract pair document:tf
    pairList = string.split(",")
    # for pair in pairList
    for pair in pairList:
        #extract key(documentID) and value(frequency)
        id= pair.split(":")[0]
        #remove quotes sourrounding id
        id = id.strip()
        id = id[1:-1]
        #print(id)
        tf= pair.split(":")[1]
        tf=tf.strip()
        #print(tf)
        #add an entry in the dictionary
        containing_docs[id] = int(tf)

        
    #return the dictionary
    return containing_docs


# In[14]:


#load inverted_index
inverted_index = {}
with io.open("inverted_index.txt", 'r', encoding="utf-8") as file:
        temp_doc=file.read()
        #parse the file
        elemList = temp_doc.split("</element>")
        #print(elemList)
        elemList= elemList[:-1]
        #weighted_norm dictionary
        #weighted_norm_dictionary = {}
        i = 0
        print("loading inverted index..")
        print()
        for elem in elemList:
            ##extract the word
            word = elem.split("<key|idf>")[0]
            ##etract the idf
            idf = elem.split("<key|idf>")[1]
            idf = idf.split("<idf|cont_docs>")[0]
            #extract the dictionary of containing words
            cont_docs = elem.split("<idf|cont_docs>")[1]
            #parse the dictionary
            dictionary = extract_dictionary(cont_docs)
            
            #create an instance of the Class token and add it to inverted_index
            key=word
            value=token_class(idf, dictionary)
            inverted_index[key]=value
            i+=1
            if (i%10000 == 0):
                print(str(int(i*100/63000)) + "% done")
                print()
            
            #print(i)
            #print("word: " + word)
            #print("idf: " + idf)
            #print("cont_docs: " + cont_docs)
            #print()
            #weighted_norm_dictionary[id] = float(value)
            #print()'''
        print("done!")


# In[15]:


#inverted_index.keys()


# In[16]:


#urlDictionary["2201"]


# In[17]:


#load documents_weighted_norm from file
print("Loading the documents' norm from file...")
with io.open("weighted_norm_dictionaryfull.txt", 'r', encoding="utf-8") as file:
        temp_doc=file.read()
        #parse the file
        elemList = temp_doc.split("<element>")
        elemList= elemList[:-1]
        #print(elemList)
        #weighted_norm dictionary
        weighted_norm_dictionary = {}
        for elem in elemList:
            id = elem.split("<id|value>")[0]
            value = elem.split("<id|value>")[1]
            #print("id: " + id)
            #print("value: " + value)
            weighted_norm_dictionary[id] = float(value)
            #print()
print("done!")


# In[18]:


#weighted_norm_dictionary


# In[19]:


def retrieve_top_N_docs(ranked_docs, N):
    return ranked_docs[:N]


# In[20]:


#return a list of ranked documents for the query
# query is the user input
def retrieve(query, smart = 0):
    q = userInput.get()
    print("Input:")
    print()
    print('"' + q + ' "\n')
    
    result_query=retrive_ranked_docs(q, smart)
    doc_list = map(operator.itemgetter(0),result_query)
    ranking=list(doc_list)
    print("Done!")
    showResults(ranking, q)


# In[21]:


#count the occurencies of a word:String in a document: List of tokens
def occurencies(List, String):
    count=0
    for x in List:
        if x==String:
            count=count +1
    return count 


# In[22]:


def tf(token, document_id):
    #TODO:: use try catch
    token_list=list(inverted_index.keys())
    if not(token in token_list):
        return 0
    x=inverted_index[token]
    #print(document_id)
    keys=list(x.containing_documents.keys())
    if document_id in keys:
        tf=x.containing_documents[document_id] 
    else:
        tf=0
    return tf


# In[23]:


#returns the idf of the token
def idf(token): #document dictionary can be eliminated
    N=len(urlDictionary) #total number of document in the collection
    token_list=list(inverted_index.keys())
    if not(token in token_list):
        return 0
    df=inverted_index[token].idf #number of containing docs
    n=(N//float(df))
    idf=math.log(n,2)
    return idf


# query = " hackathon"

# rank =retrieve(query, 1)
# print("done")

# In[24]:


###smart component
print("Loading Smart Component: GoogleNews-vectors-negative300 ")
print("It could take a couple of minutes..")
print()
try:
    from gensim.models import KeyedVectors
    filename = 'GoogleNews-vectors-negative300.bin'
    model = KeyedVectors.load_word2vec_format(filename, binary=True)
except Exception as e:
    print(e)
    print("Coud not load global Model")


# In[25]:


print("Loading Smart Component: OwnWordToVecModel ")
print("It could take a couple of minutes..")
print()
from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec
model2 = Word2Vec.load("ownModel.model")


# In[26]:


from tkinter import *
from tkinter.ttk import *
import webbrowser
import subprocess
class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        canvas.configure(background="LightBlue2")
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


# In[27]:


def OpenUrl(url):
    webbrowser.open_new(url)
    
def showMoreRes(index,button, scframe, rank):
    end = False
    for i in range(index,index+10):
        button.append(Button(scframe.interior, text=urlDictionary[str(rank[i])], command=lambda aurl=urlDictionary[str(rank[i])]:OpenUrl(aurl),  bg="DeepSkyBlue2"))
        button[i].pack()
        if (i>= (len(rank) -2)):
            endButton = Button(scframe.interior,text="no more results to show", bg="light goldenrod")
            endButton.pack()
            end = True
            break;
        
    counter = index + 10
    
    if not(end):
        showMore = Button(scframe.interior,text="show more results",command= lambda cont=counter:showMoreRes(counter,button, scframe, rank),  bg="light goldenrod")
        showMore.pack()


# In[28]:


def showResults(rank, input):
    results = Tk()
    results.title("Results for: " + input)
    results.configure(background="LightBlue2")

    scframe = VerticalScrolledFrame(results)
    scframe.pack()
    
    button = []
    counter = 0
    for i in range(10):
        if (i>= (len(rank) -1)):
            endButton = Button(scframe.interior,text="no more results to show", bg="light goldenrod")
            endButton.pack()
            break;
        button.append(Button(scframe.interior, text=urlDictionary[str(rank[i])], command=lambda rurl=urlDictionary[str(rank[i])]:OpenUrl(rurl),  bg="DeepSkyBlue2"))
        button[i].pack()
        counter += 1
        
        if(i==9):
            showMore = Button(scframe.interior,text="show more results",command= lambda cont=counter:showMoreRes(counter,button, scframe,rank),  bg="light goldenrod")
            showMore.pack()
    mainloop() 


# In[ ]:


from tkinter import *
import subprocess



gui = Tk()
gui.title('Search Engine')
gui.configure(background="LightBlue2")
Label(gui, text='Query Input:',  bg="DeepSkyBlue2").grid(row=2)

userInput = Entry(gui) 
userInput.grid(row=2, column=1)

messageLabel = Label(gui, text = "Hello! Please insert a query.",  bg="light goldenrod").grid(row=0)

searchButton = Button(gui,command=lambda input=userInput.get():retrieve(input,0),text="Search", bg="DeepSkyBlue2")
searchButton.grid(row=3,column=0)
searchSmartButton1 = Button(gui,command=lambda input=userInput.get():retrieve(input,1),text="Search globally Smart", bg="DeepSkyBlue2")
searchSmartButton1.grid(row=3,column=1)
searchSmartButton2 = Button(gui,command=lambda input=userInput.get():retrieve(input,2),text="Search locally Smart", bg="DeepSkyBlue2")
searchSmartButton2.grid(row=3,column=2)
mainloop() 

