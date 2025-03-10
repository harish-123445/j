# -*- coding: utf-8 -*-
"""dm_prac_lab2 (1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16VtuZ-n3sH7ApCJeTtchxO9VxBChH0bb
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter,defaultdict
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,accuracy_score
from sklearn.ensemble import BaggingClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import pprint

train=pd.read_csv('/content/Data Mining Lab PS10 dataset2.csv')
test=pd.read_csv('/content/Data Mining Lab PS10 dataset1.csv')

"""# preprocessing"""

df=train

df['buying']=df['buying'].fillna(df['buying'].mode()[0])
df['maint']=df['maint'].fillna(df['maint'].mode()[0])
df['doors']=df['doors'].fillna(df['doors'].mode()[0])
df['safety']=df['safety'].fillna(df['safety'].mode()[0])
df['acceptance']=df['acceptance'].fillna(df['acceptance'].mode()[0])

df=df.dropna()

"""# decision tree"""

def entropy(y):
  class_counts=np.array(list(Counter(y).values()))
  probabilities=class_counts/len(y)
  entropies= -sum(probabilities*np.log2(probabilities))
  return entropies

def best_attribute_calc(df,attributes):
  parent_entropy=entropy(df.iloc[:,-1])

  info_gain={}
  for attribute in attributes:
    entropy_attribute=0
    for value in df[attribute].unique():
      sub_df=df[df[attribute]==value]
      sub_df_entropy_value=entropy(sub_df.iloc[:,-1])
      entropy_attribute+=(len(sub_df)/len(df))*sub_df_entropy_value

    info_gain[attribute]=(parent_entropy-entropy_attribute)

  return max(info_gain,key=info_gain.get)

def ID3(df,attributes):
  y=df.iloc[:,-1]

  if len(np.unique(y))==1:
    return y.values[0]

  if not attributes:
    return y.value_counts().idxmax()

  best_attribute=best_attribute_calc(df,attributes)

  tree={best_attribute:{}}
  remaining_attribute=attributes.copy()
  remaining_attribute.remove(best_attribute)

  for value in np.unique(df[best_attribute]):
    sub_df=df[df[best_attribute]==value].copy()
    tree[best_attribute][value]=ID3(sub_df,remaining_attribute)

  return tree

attributes=list(df.columns[:-1])
decision_tree=ID3(df,attributes)  # Hunt(df,attributes)
pprint.pprint(decision_tree)

"""# Hunts"""

def Hunts(df,attributes):
  y=df.iloc[:,-1]

  if len(np.unique(y))==1:
    return y.values[0]

  if not attributes:
    return y.value_counts().idxmax()

  best_attribute=attributes[0]
  tree={best_attribute:{}}
  remaining_attribute=attributes.copy()
  remaining_attribute.remove(best_attribute)

  for value in np.unique(df[best_attribute]):
    sub_df=df[df[best_attribute]==value].copy()
    tree[best_attribute][value]=Hunts(sub_df,remaining_attribute)

  return tree

attributes=list(df.columns[:-1])
decision_tree=Hunts(df,attributes)  # Hunt(df,attributes)
pprint.pprint(decision_tree)

"""# prediction"""

def predict(decision_tree,sample):

  for attribute in decision_tree:
    if sample[attribute] not in decision_tree[attribute]:
      return 0

    subtree=decision_tree[attribute][sample[attribute]]

    if(isinstance(subtree,dict)):
      return predict(subtree,sample)
    return subtree

""" in train and test are separate files"""

X_train = train.drop(columns=['acceptance'])
y_train = train['acceptance']

X_test = test.drop(columns=['acceptance'])
y_test = test['acceptance']

test['prediction']=test.apply(lambda x: predict(decision_tree,x[:-1]),axis=1)

report_dict=classification_report(test['prediction'],test['acceptance'],output_dict=True)
report_df=pd.DataFrame(report_dict).transpose()
print(report_df)

"""in case only a single file is given"""

X_train,X_test,y_train,y_test=train_test_split(df.iloc[:,:-1],df.iloc[:,-1],test_size=0.3)

y_pred=X_test.apply(lambda x: predict(decision_tree,x),axis=1)
y_pred

report_dict=classification_report(y_pred,y_test,output_dict=True)
report_df=pd.DataFrame(report_dict).transpose()
print(report_df)

"""# bagging and boosting"""

df_encoded=df.copy()
le=LabelEncoder()
for col in df_encoded.columns:
  df_encoded[col]=le.fit_transform(df_encoded[col])

X=df_encoded.iloc[:,:-1]
y=df_encoded.iloc[:,-1]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

bagging=BaggingClassifier(estimator=DecisionTreeClassifier(),n_estimators=50,random_state=42)
bagging.fit(X_train,y_train)
y_pred_bagging = bagging.predict(X_test)
print(accuracy_score(y_test,y_pred_bagging))

boosting=AdaBoostClassifier(estimator=DecisionTreeClassifier(),n_estimators=50,random_state=42)
boosting.fit(X_train,y_train)
y_pred_boosting = boosting.predict(X_test)
print(accuracy_score(y_test,y_pred_boosting))

"""# Plot"""

#same code as above
info_gain = {}
for attribute in attributes:
    parent_entropy = entropy(df.iloc[:, -1])
    entropy_of_attribute = 0

    for unique_value in df[attribute].unique():
        sub_df = df[df[attribute] == unique_value]
        entropy_sub_df = entropy(sub_df.iloc[:, -1])
        entropy_of_attribute += (len(sub_df) / len(df)) * entropy_sub_df

    info_gain[attribute] = parent_entropy - entropy_of_attribute

plt.bar(info_gain.keys(), info_gain.values(), color='skyblue')
plt.xlabel("Features")
plt.ylabel("Information Gain")
plt.show()

plt.pie(df['acceptance'].value_counts(), labels=df['acceptance'].unique())
plt.title("Class Distribution in acceptance")
plt.show()

df['safety'].value_counts().plot(kind='bar')
plt.xlabel("Outlook")
plt.ylabel("Frequency")
plt.title("Distribution of Outlook Feature")
plt.show()

sns.heatmap(df_encoded.corr(),annot=True,cmap="coolwarm",fmt='.2f')
plt.title("Feature Correlation Heatmap")
plt.show()

plt.scatter(df_encoded['buying'], df_encoded['maint'], c=df_encoded['acceptance'], cmap='coolwarm', edgecolors='k')
plt.xlabel("Temperature (Encoded)")
plt.ylabel("Humidity (Encoded)")
plt.title("Scatter Plot of Temperature vs Humidity")
plt.colorbar(label="PlayTennis (0: No, 1: Yes)")
plt.show()