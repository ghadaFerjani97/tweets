import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
import seaborn as sns
sns.set(style="whitegrid")
import twint
import nest_asyncio
import time
from igraph import *
import networkx as nx
import community as co
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import FrenchStemmer
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer
lemmatizer = FrenchLefffLemmatizer()

french_stop_words = set(stopwords.words('french'))
french_stop_words.add("http")
french_stop_words.add("il")
french_stop_words.add("co")
french_stop_words.add("est")
french_stop_words.add("https")
french_stop_words.add("sur")
french_stop_words.add("avoir")
french_stop_words.add("être")
french_stop_words.add("tout")
french_stop_words.add("cela")
french_stop_words.add("quand")
french_stop_words.add("plus")
french_stop_words.add("comme")
french_stop_words.add("celui")
french_stop_words.add("EST")
french_stop_words.add("w3ybfwvxk")

        
def get_dataframe_from_table(table_name, number=None, columns=None):
    df = None
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='tweeter',
                                             user='ghada',
                                             password='ghada')
        if number is not None:
            if columns is not None:
                sql_select_query = "select t.%s from %s t limit %d" % (',t.'.join(columns), table_name, number)
            else:
                sql_select_query = "select * from %s limit %d" % (table_name, number)

        else:
            if columns is not None:
                sql_select_query = "select t.%s from %s t " % (',t.'.join(columns), table_name)
            else:
                sql_select_query = "select * from %s " % table_name

        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        columns_names = [field[0] for field in cursor.description]
        print("Total number of rows in " + table_name + " is: ", cursor.rowcount)
        df = pd.DataFrame(np.array(records), columns=columns_names)
        # print(columns_names)

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            cursor.close()
            print("MySQL connection is closed")
            return df




        
def get_frensh_tweets_dataframe(table_name,limit_index):
    
    df = None
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='tweeter',
                                             user='ghada',
                                             password='ghada')

        sql_select_query = "SELECT * FROM "+table_name+" WHERE lang='fr' ORDER BY RAND() LIMIT "+str(limit_index)
        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        columns_names = [field[0] for field in cursor.description]
        df = pd.DataFrame(np.array(records),columns=columns_names)
        
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            cursor.close()
            print("MySQL connection is closed")
            return df
        

def harmonize_form_words(x):
    # Important word written in upper case
    if(x.isupper()):
        return x
    else:
        return x.lower()
    
def stemming(x):
    #Using a mathematic formula truc the word's end
    stemmer = FrenchStemmer()
    return stemmer.stem(x)

def lemmatization(x):
    import spacy
    from spacy_lefff import LefffLemmatizer, POSTagger
    #spacy_lefff installed package to lemmatize french (since it is not available in NLTK)
    # install language model python -m spacy download fr
    nlp = spacy.load('fr_core_news_md')
    french_lemmatizer = LefffLemmatizer()
    nlp.add_pipe(french_lemmatizer, name='lefff')
    doc = nlp(x)
    return " ".join([d.lemma_ for d in doc])

import re 
regex = '^[a-zA-Z]*$'
# Define a function for 
# for validating an Email 

def check_word(word):  
    # pass the regualar expression 
    # and the string in search() method 
    if(re.search(regex,word)):  
        return True  
    else:  
        return False  
    
def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)
        
    return input_txt  

from collections import Counter

def remove_freqwords(text):
    """custom function to remove the frequent words"""
    return " ".join([word for word in str(text).split() if word not in FREQWORDS])


def preprocessing(tweets):
    cnt = Counter()
    for text in tweets:
        for word in text.split():
            cnt[word] += 1
    new_tweets= []
    for tweet in tweets:
        lemmatized_tweet = lemmatizer.lemmatize(tweet)
        token_words = [word for word  in word_tokenize(lemmatized_tweet, language='french') if ((len(word) > 2 and check_word(word) ) or word in ["ne","ni"] )]
        large_harmononized_tokens_words = [harmonize_form_words(word) for word in token_words ]
        large_lemmetized_harmononized_stop_words_removed_tokens_words = [word for word in large_harmononized_tokens_words if(word not in french_stop_words)]
  
        tweet_ = " ".join(large_lemmetized_harmononized_stop_words_removed_tokens_words)
        new_tweets.append(tweet_)
    return new_tweets

    
def histogramme_vectorised_data(t,n,k):
    vectorizer = CountVectorizer(lowercase=False,stop_words=french_stop_words ,ngram_range=(n,n))
    tweet_text = vectorizer.fit_transform(t)
    tweet_words=vectorizer.get_feature_names()
    tweet_matrix=tweet_text.toarray()
    occu_words=tweet_matrix.sum(axis=0)
    occu_words_modified = pd.Series(list(occu_words))
    nlargest_occ= occu_words_modified.nlargest(k)
    index_words=nlargest_occ.index.values.tolist()
    nlargest_occ_words=[tweet_words[i] for i in index_words]

    fig= plt.figure(figsize=(20,20), dpi=80)
    ax = sns.barplot(x=nlargest_occ_words, y=nlargest_occ) 
    
    
def edge_to_remove(G):
    
    dict1=nx.edge_betweenness_centrality(G)
    list_of_tuples=dict1.items()
    #sorting the list using the betweeness centrality value
    list_of_tuples.sort(key=lambda x:x[1], reverse=True)
    return list_of_tuples[0][0]
    
    
def grivan(G):
    #checking if the graph is connected or not
    c=nx.connected_component_subgraphs(G) 
    print('the number of connected components are',l)
    #removing edges
    while(l<2):
        G.remove_edge(*edge_to_remove(G))
        c=nx.connected_component_subgraphs(G) 
        l=len(c)
        print('the number of connected components are',l)
    
    return c
        

    
