import os

from sklearn.metrics import classification_report
from sklearn.naive_bayes import BernoulliNB, MultinomialNB

os.environ["NLTK_DATA"] = "/home/cs9414/nltk_data"
os.environ["SKLEARN_SITE_JOBLIB"]="TRUE"


import re
import sys
import pandas as pd
import numpy as np
from sklearn import tree
from sklearn.feature_extraction.text import CountVectorizer




def predict_and_test(model, X_test_bag_of_words):
    predicted_y = model.predict(X_test_bag_of_words)
    # print(classification_report(y_test, predicted_y,zero_division=0))
    for i in range(0, len(predicted_y)):
        print(str(test_data_no[i]).strip(" ") + ' ' + str(predicted_y[i]).strip(" "))

train_filename = sys.argv[1]
test_filename = sys.argv[2]
testset = pd.read_csv(test_filename,sep='\t',header=None)
trainset = pd.read_csv(train_filename,sep='\t',header=None)

test_data_no,test_data_sentence,test_data_class = np.array(testset).T[:1][0],np.array(testset).T[1:2][0],np.array(testset).T[2:3][0]
train_data_sentence,train_data_class = np.array(trainset).T[1:2][0],np.array(trainset).T[2:3][0]

train_sentence=[]
for sen in train_data_sentence:
    sentence = []
    sen = re.sub(r'((www\.[\S]+)|(https?://[\S]+))', ' ', sen)
    sen = re.sub("[^@#$%_0-9a-zA-Z]+", " ", sen)
    sen = re.sub(" u[0-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z]", ' ', sen)
    for word in sen.split(" "):
        if len(word) >= 2:
            word = word.strip('\'"?!,.():;/')
        sentence.append(word)
    if "" in sentence:
        sentence.remove("")
    data_sentenec=" ".join(sentence)
    train_sentence.append(data_sentenec)
test_sentence=[]
for sen in test_data_sentence:
    sentence = []
    sen = re.sub(r'((www\.[\S]+)|(https?://[\S]+))', ' ', sen)
    sen = re.sub("[^@#$%_0-9a-zA-Z]+", " ", sen)
    sen = re.sub(" u[0-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z]",' ',sen)
    for word in sen.split(" "):
        if len(word)>=2:
            word = word.strip('\'"?!,.():;/')
        sentence.append(word)
    if "" in sentence:
        sentence.remove("")
    data_sentenec=" ".join(sentence)
    test_sentence.append(data_sentenec)
X_train = train_sentence
X_test = test_sentence

y_train = train_data_class
y_test = test_data_class
n=len(X_train)
count = CountVectorizer(token_pattern=r"(?u)\b\w\w+\b|@\w+|#\w+|\$\w+|\w+\$|\d\d\%",lowercase=False)
X_train_bag_of_words = count.fit_transform(X_train)
X_test_bag_of_words = count.transform(X_test)

clf = MultinomialNB()
model = clf.fit(X_train_bag_of_words, y_train)
predict_and_test(model, X_test_bag_of_words)



