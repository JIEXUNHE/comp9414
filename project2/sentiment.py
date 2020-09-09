import os

from sklearn.metrics import classification_report,accuracy_score
os.environ["NLTK_DATA"] = "/home/cs9414/nltk_data"
os.environ["SKLEARN_SITE_JOBLIB"]="TRUE"


import re
import sys
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn import svm


#
# def predict_and_test(model, X_test_bag_of_words):
#     right=0
#     predicted_y = model.predict(X_test_bag_of_words)
#     print(accuracy_score(y_test,predicted_y))
#     print(classification_report(y_test, predicted_y,zero_division=0))
#     # for i in range(0, len(predicted_y)):
    #     if predicted_y[i]==test_data_class[i]:
    #         right+=1
        #print(str(test_data_no[i]).strip(" ") + ' ' + str(predicted_y[i]).strip(" "))
    # print(right / len(test_data_no))
def hidden_information(sen):
####i find some emo char in tweets , it has strong connection with sentiment, I want to save it.
    sen = re.sub(r'(:\'\)|:-\)|\(-:|\(\s?:|:\s?\))', ' pos ', sen)
    sen = re.sub(r'(:\s?D|X-?D|:-D|x-?D)', ' pos ', sen)
    sen = re.sub(r'(:\s?\(|:-\(|\)\s?:|\)-:)', ' neg ',sen)

    return sen

train_filename = sys.argv[1]
test_filename = sys.argv[2]
testset = pd.read_csv(test_filename,sep='\t',header=None)
trainset = pd.read_csv(train_filename,sep='\t',header=None)

test_data_no,test_data_sentence,test_data_class = np.array(testset).T[:1][0],np.array(testset).T[1:2][0],np.array(testset).T[2:3][0]
train_data_sentence,train_data_class = np.array(trainset).T[1:2][0],np.array(trainset).T[2:3][0]

train_sentence=[]
for sen in train_data_sentence:
    sentence = []
    sen = hidden_information(sen)
    sen = re.sub(r'((www\.[\S]+)|(https?://[\S]+))', ' ', sen)
    sen = re.sub("[^@#$%_0-9a-zA-Z]+", " ", sen)
    sen = re.sub(" u[0-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z]", ' ', sen)
    for word in sen.split(" "):
        # word = word.lower()
        word = word.strip('\'"?!,.():;/')
        word = re.sub(r'(.)\1+', r'\1', word)
        word = re.sub(r'^w$', 'with', word)
        sentence.append(word)
    if "" in sentence:
        sentence.remove("")
    data_sentenec=" ".join(sentence)
    train_sentence.append(data_sentenec)
test_sentence=[]
for sen in test_data_sentence:
    sentence = []
    sen = hidden_information(sen)
    sen = re.sub(r'((www\.[\S]+)|(https?://[\S]+))', ' ', sen)
    sen = re.sub("[^@#$%_0-9a-zA-Z]+", " ", sen)
    sen = re.sub(" u[0-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z]",' ',sen)
    for word in sen.split(" "):
        # word = word.lower()
        word = word.strip('\'"?!,.():;/')
        word = re.sub(r'(.)\1+', r'\1', word)
        word = re.sub(r'^w$', 'with', word)
        sentence.append(word)
    if "" in sentence:
        sentence.remove("")
    data_sentenec=" ".join(sentence)
    test_sentence.append(data_sentenec)
X_train = train_sentence
X_test = test_sentence

y_train = train_data_class
y_test = test_data_class
# for i in range(0,len(X_test)):
#     print(test_data_no[i],X_test[i])
# n=len(X_train)
# count = CountVectorizer(token_pattern=r"(?u)\b\w\w+\b|@\w+|#\w+|\$\w+|\w+\$|\d\d\%",max_features=1000)
# X_train_bag_of_words = count.fit_transform(X_train)
# X_test_bag_of_words = count.transform(X_test)
#
# clf = tree.DecisionTreeClassifier(criterion='entropy',random_state=0,min_samples_leaf=int(n*0.01),max_features=1000)
# model = clf.fit(X_train_bag_of_words, y_train)


vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w\w+\b|@\w+|#\w+|\$\w+|\w+\$|\d\d\%")
vectorizer.fit(X_train)
# cls = MultinomialNB()
cls = svm.SVC(kernel='linear',C=1.0)
cls.fit(vectorizer.transform(X_train),y_train)
y_pred = cls.predict(vectorizer.transform(X_test))
print(accuracy_score(y_test,y_pred))
# print(classification_report(y_test,y_pred))
for i in range(0, len(y_pred)):
    print(str(test_data_no[i]).strip(" ") + ' ' + str(y_pred[i]).strip(" "))
