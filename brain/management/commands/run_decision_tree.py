import arff
import datetime
import json
import numpy
import sys
import tempfile
import uuid
import urllib
import urllib2
import subprocess

from sklearn import svm
from sklearn import tree
from sklearn import naive_bayes
from sklearn import neighbors

from sklearn.metrics import classification_report, confusion_matrix
from sklearn.cross_validation import cross_val_score
from sklearn.feature_extraction import DictVectorizer

from xml.dom.minidom import *

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from brain.models import *
from data_sources.models import DataSource, DataReport

def tree_to_javascript(tree, indent=0):
    return ''

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        
        job = ReportJob.objects.get(pk=int(args[0]))
        
        arff_file = arff.load(job.result_file)
        
        label_indices = {}
        labels = []
        data = []
        
        print('building data')
        
        attributes = arff_file['attributes']
        
        for attribute in attributes:
            label_indices[attribute[0]] = []
        
        for row in arff_file['data']:
            label_index = -1
            
            if True: # row[0] == 'work' or row[0] == 'home' or row[0] == 'restaurant':
                try:
                    label_index = label_indices[attributes[0][0]].index(row[0])
                except ValueError:
                    label_indices[attributes[0][0]].append(row[0])
                    label_index = label_indices[attributes[0][0]].index(row[0])
                    
                labels.append(label_index)
                
                row_data = []
                for i in range(1, len(row)):
                    col_name = attributes[i][0]
    
                    if attributes[i][1][0] == 'REAL':
                        if row[i] != None:
                            row_data.append(float(row[i]))
                        else:
                            row_data.append(0 - sys.maxint)
                    else:
                        field_index = -1
    
                        try:
                            field_index = label_indices[col_name].index(row[i])
                        except ValueError:
                            label_indices[col_name].append(row[i])
                            field_index = label_indices[col_name].index(row[i])
                            
                        row_data.append(field_index)
    
                data.append(row_data)

        test_data = data[0::2]
        test_labels = labels[0::2]

        train_data = data[1::2]
        train_labels = labels[1::2]
        
        classifiers = [tree.DecisionTreeClassifier(), svm.SVC(), naive_bayes.GaussianNB(), neighbors.KNeighborsClassifier()]
        
        for clf in classifiers:
            # clf = tree.DecisionTreeClassifier()
            # clf = svm.SVC()
            # clf = naive_bayes.GaussianNB()
            # clf = neighbors.KNeighborsClassifier()

            print('training ' + str(clf))

            clf.fit(train_data, train_labels)

            test_pred = clf.predict(test_data)

            # print(str(test_pred))
            # print(str(test_labels))
            print(classification_report(test_labels, test_pred, target_names=label_indices['location_feature_value']))
         
