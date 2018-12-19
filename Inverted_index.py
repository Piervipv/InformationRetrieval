
# coding: utf-8

# #### In this section we build the inverted_index indexing the previously crawled documents:

# In[1]:


from bs4 import BeautifulSoup
import os
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
import math
import re


# In[2]:


directory_input = input('Please provide directory_path where the documents of the collection are contained. \n To select the default option | ./documents2 | press d ')
if (directory_input.lower() == 'd'):
    
    directory_path ='./documents2' #TODO: read from user inmput
else:
    directory_path=directory_input
    
documents=os.listdir(directory_path)
print(directory_path)


# In[3]:


tokenizer=RegexpTokenizer('[a-z]+[-]?[0-9a-z]*')
stemmer=PorterStemmer()
#retrive the list of stopwords
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


# In[4]:


class token_class:
    def __init__(self, count= 0, idf=0,containing_documents= {}):
        self.idf=idf #number of containing docs
        self.containing_documents=containing_documents


# Some useful functions:

# In[5]:


def remove_punt_and_number(string):
    remove_list=['0','1','2','3','4','5','6','7','8','9' ]
    #remove_list=[]
    string2=''
    for i in range(0,len(string)):
        if not(string[i] in remove_list):
            string2=string2 +string[i]
    return string2


# In[6]:


#function to perform preprocessing: remove puntaction,tokenize,stemming, stopwords and words of 1,2 characters
#return the list of tokens in the string/document
def preprocess(string,stopwords_list ):
   # re.findall
    tokens=[]
    tokenizer=RegexpTokenizer('([a-z]*[-]?[a-z]+[-]?[a-z]*|[0-9]+[-]?[a-z]+|[a-z]+[-]?[0-9]+)') #matches only alphabetical characters
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


# In[7]:


#count the occurencies of a word:String in a document: List of tokens
def occurencies(List, String):
    count=0
    for x in List:
        if x==String:
            count=count +1
    return count 


# In[8]:


#count the occurencies of each token in each documents_dictionary element, if >0 add document_id : occurencies 
#returns count and hash Map containing_docs : freq
def index_token(token, documents_dictionary):
    containing_documents={}
    count=0
    idf=0
    for i in range (0,len(documents_dictionary)): 
        doc_freq=occurencies(documents_dictionary[str(i)], token)
        if doc_freq>0:
            count += doc_freq
            idf += 1
            key=str(i)
            value=doc_freq
            containing_documents[key] = value
    return count,idf, containing_documents
    


# documents_dictionary["1"]

# x =inverted_index["uic"]
# x.containing_documents.keys()

# weighted_norm(str(0), documents_dictionary, inverted_index)

# inverted_index["uic"]

# In[9]:


#compute the weighted norm of a document
def weighted_norm(document_id, documents_dictionary, inverted_index):
    tokens=documents_dictionary[document_id] #retrieve the tokens in the document
    #print(tokens)
    sum=0
    for token in tokens:
        term_freq=tf(token, document_id,inverted_index)
        #print(term_freq)
        idfe=idf(token, documents_dictionary, inverted_index)
        weight=term_freq*idfe
        sum += weight * weight
    return sum**(0.5)


# def query_norm(query_tokens, documents_dictionary, inverted_index):
#     #quertokens=documents_dictionary[document_id]
#     sum=0
#     term_freq=0
#     for token in set(query_tokens):
#         #print(term_freq)
#         term_freq=occurencies(query_tokens, token)
#         idfe=idf(token, documents_dictionary, inverted_index) #documents_dictionary is used to retrieve N
#         weight=term_freq*idfe
#         #print(weight) #debug
#         sum += weight * weight
#         #print(sum) #debug
#     return sum**(0.5)

# def retrive_docs(query_tokens, documents_dictionary, inverted_index):
#     matching_docs=set()
#     token_list=list(inverted_index.keys())
#     for tokens in query_tokens:
#         #print("token:")
#         #print(tokens)
#         if (tokens in token_list):
#             x=inverted_index[tokens]
#             #print("containing docs:")
#             #print(list(x.containing_documents.keys()))
#             documents=list(x.containing_documents.keys())
#             #print("documents")
#             #print(documents)
#             matching_docs.update(documents)
#     #print(matching_docs) #debug
#     return matching_docs

# #query is a list of tokens, matching docs is a list of documents' IDs
# #for each token, incrementally compute cosine_similarity for each document
# #at the end, divide by document and query norm
# #returns a hash doc_id : similarity value
# def compute_similarity(query, matching_docs, documents_dictionary, inverted_index, documents_weighted_norm):
#     similarity={}
#     score=0
#     #initialize similarity dictionary
#     for doc in matching_docs:
#         key=doc
#         value=int(0)
#         similarity[key]=value
#     #compute the accumulated similarity
#     for token in query:
#         for doc in matching_docs:
#             key=doc
#             score=tf(token,doc,inverted_index)*idf(token,documents_dictionary,inverted_index)**2
#             similarity[key] += score #increment the similarity
#     #divide by document and query's norm
#     for doc in matching_docs:
#         key=doc
#         divider=documents_weighted_norm[key]
#         #print(divider)
#         divider= divider * query_norm(query, documents_dictionary, inverted_index)
#         #print(divider)
#         similarity[key] = similarity[key] / divider
#     #print ("similarity_dict")
#     #print (similarity) #debug
#     return similarity

# #ranks the documents
# #returns an ordered list of tuples
# def rank_docs(similarity_dictionary):
#     from operator import itemgetter
#     sorted_docs = sorted(similarity_dictionary.items(), key=itemgetter(1), reverse=True)
#     #debug
#     #print("sorted docs:")
#     #print(sorted_docs)
#     #print(type(sorted_docs))
#     #print(sorted_docs[1])
#     return sorted_docs
#     

# def retrive_ranked_docs(query,documents_dictionary,inverted_index,documents_weighted_norm,stopwords_list):
#     query_tokens=preprocess(query,stopwords_list)
#     #print("query tokens")
#     #print(query_tokens)
#     #query_weighted_norm=query_norm(query_tokens, documents_dictionary, inverted_index)
#     matching_documents= retrive_docs(query_tokens, documents_dictionary, inverted_index)
#     #print('matching docs')
#     #print(len(matching_documents))
#     #print(matching_documents)
#     similarity_dictionary=compute_similarity(query_tokens, matching_documents, documents_dictionary, inverted_index, documents_weighted_norm)
#     #print(ranking)
#     ranking=rank_docs(similarity_dictionary)
#     #print("ranking")
#     #print (ranking)
#     return ranking

# def retrieve_top_N_docs(ranked_docs, N):
#     return ranked_docs[:N]

# In[10]:


doc_id_extractor=RegexpTokenizer('[0-9]+') #to extract the document ID


# Let's build the hash map documentID: list of contained tokens

# In[11]:


import io
documents_dictionary={} #document id : list of tokens
all_tokens_in_the_collection=set([]) #needed to extract the set and cycle over the tokens
#for each document extract ID(key) and preprocess the text (value)
print('Building documents dictionary Id: list of contained tokens...')
for document in documents:
    #temp_doc=open(directory_path +'/'+ document).read().decode('utf-8')
    
    with io.open(directory_path +'/'+ document, 'r', encoding="utf-8") as file:
        temp_doc=file.read()

    #extract title and text from the html file
    temp = document.split(".")
    key=temp[0]
    
    text = temp_doc.replace('\n',' ')
    value=text.replace('/',' ')
    
    #value= title + " " + text + " "
    #preprocess the document
    #print(type(value))
    value=preprocess(value, stopwords_list) #value changes from String to list of preprocessed tokens
    #print(type(value))
    value2=set(value)
    all_tokens_in_the_collection.update(value2) #update the collection of tokens
    documents_dictionary[key] = value #add in the map ID: list of tokens
print(len(all_tokens_in_the_collection))

print('done.')


# In[12]:


documents_dictionary['3199']


# In[13]:


#print(all_tokens_in_the_collection)


# In[14]:


distinct_tokens_collection=set(all_tokens_in_the_collection)
x=len(distinct_tokens_collection)
#print(type(x))
#print(x)
print('In the collection there are ' + str(x) + ' distinct preprocessed tokens.')


# In[15]:


print('In the collections there are ' + str(len(documents_dictionary)) + ' documents.')


# Let's build the inverted index:

# In[16]:


#inverted_index is an hash map
#key: token , value: token_class containing tf, idf and another hash map (containing document id : frequencies )
import io
inverted_index={}
print("Building inverted index...")
i = 0
with io.open("./inverted_index.txt", 'w', encoding="utf-8") as file:
    
    for token in distinct_tokens_collection:
        tf, idf, containing_documents = index_token(token, documents_dictionary)
        key=token
        #print(token)
        
        #write to file to be parsed later just before query time
        file.write(key + "<key|idf>" + str(idf) + "<idf|cont_docs>" + str(containing_documents) + "</element>")
        #file.write("<idf>" + str(idf) + "</idf>")
        value=token_class(tf, idf, containing_documents)
        inverted_index[key]=value
        i +=1
        if ((i % 500) == 0):
            print(str(i))
        ##just to stop it before
        #if (i==10):
              # break
        

print('done.')
    
    


# x=inverted_index["function"]
# print(list(x.containing_documents.keys()))
# print(len(list(x.containing_documents.keys())))

# ##Let's write the inverted index into file
# import io
# with io.open("inverted_index.txt", 'w', encoding="utf-8") as file:
#     for key in inverted_index.keys():
#                 file.write("<key>" + key + </key>)
#                 file.write("\n")
#                 file.write(str(inverted_index[key])
# 

# In[17]:


#debug
#x=list(inverted_index.keys())
#print(type(x))
#type(x[1])
#print(x.containing_documents.keys())
#print(inverted_index['investig'].idf)
#print(idf("investig", documents_dictionary, inverted_index))


# In[18]:


#debug
#tf("investig", '1' ,inverted_index)
#tf('order', '14',inverted_index)


# In[19]:


#debug
#weighted_norm('1', documents_dictionary, inverted_index) #should be 99....


# Let's build a dictionary doc_id : doc_norm

# In[20]:


#returns the idf of the token
def idf(token, documents_dictionary, inverted_index):
    N=len(documents_dictionary)
    token_list=list(inverted_index.keys())
    if not(token in token_list):
        return 0
    df=inverted_index[token].idf #number of containing docs
    n=(N//df)
    idf=math.log(n,2)
    return idf


# In[21]:


def tf(token, document_id ,inverted_index):
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


# In[22]:


documents_dictionary["0"]


# In[23]:


documents_weighted_norm={}
print("computing the norm of each document...")
i = 0;
for x in documents_dictionary:
    key=x
    value= weighted_norm(x, documents_dictionary, inverted_index)
    documents_weighted_norm[key]=value
    i +=1
    if ((i % 50) == 0):
        print(str(i))
print("done.")


# In[24]:


documents_weighted_norm['1']


# In[25]:


#write to file the documents_weighted_norm dictionary
with io.open("weighted_norm_dictionaryfull.txt", 'w', encoding="utf-8") as doc:
    i=1
    for document in documents_weighted_norm.keys():
        doc.write(document + "<id|value>" +str(documents_weighted_norm[document]) + "<element>")
        i+=1

