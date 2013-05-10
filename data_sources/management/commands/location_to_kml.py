import arff
import datetime
import json
import random

from lxml import etree
from pykml.factory import KML_ElementMaker as KML

import dionysus
import numpy as np
import scipy

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from data_sources.models import DataSource, DataReport

EPS = 0.0005
MIN_SAMPLES = 20
RAND_SELECTION = 0.025

class Command(BaseCommand):
    def handle(self, *args, **options):
        source_name = args[0]
        
        past = datetime.datetime(datetime.MINYEAR, 1, 1)
        future = datetime.datetime(datetime.MAXYEAR, 12, 31)

        for ds in DataSource.objects.filter(name__contains=source_name):
            lat_points = ds.fetch_data('LocationProbe', 'LATITUDE', past, future)
            lon_points = ds.fetch_data('LocationProbe', 'LONGITUDE', past, future)
            
            pairs = []
            
            if len(lat_points) == len(lon_points):
                for i in range(0, len(lat_points)):
                    if random.random() < RAND_SELECTION:
                        lat_point = lat_points[i]
                        lon_point = lon_points[i]
                    
                        pairs.append([lat_point[1], lon_point[1]])
        
            doc = KML.kml()
            
            root = KML.Document()
            
#            for i in range(0, len(pairs)):
#                pair = pairs[i]
#
#                pm = KML.Placemark(KML.name('Point ' + str(i)))
#                point =  KML.Point(KML.coordinates(str(pair[1]) + ',' + str(pair[0])))
#                pm.append(point)
#                
#                root.append(pm)
                
            doc.append(root)
#            print('PAIRS LENGTH: ' + str(len(pairs)))

            db = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES).fit(scipy.array(pairs))
            core_samples = db.core_sample_indices_
            labels = db.labels_
            
            n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
            
#            print('LABELS: ' + str(labels))

            clusters = {}
            
            for i in range(0, len(labels)):
                if i >= 0:
                    label = labels[i]
                
                    cluster = []
                
                    try:
                        cluster = clusters[str(label)]
                    except KeyError:
                        clusters[str(label)] = cluster
                    
                    pair = pairs[i]
                
                    cluster.append(pair)

#            print('Estimated number of clusters: %d' % n_clusters_)
#            print('Found number of clusters: %d' % len(clusters.keys()))
            
            for k, points in clusters.iteritems():
                pm = KML.Placemark(KML.name('Cluster ' + k))
                
                complex = dionysus.Filtration()
                dionysus.fill_alpha2D_complex(points, complex)
                
                shape = [s for s in complex if s.data[0] <= 0.5]

                mgeom = KML.MultiGeometry()
                
                for simplex in shape:
                    if simplex.dimension() == 2:
                        coords_string = ''
                        
                        vertices = list(simplex.vertices)
                        
                        one_x = points[vertices[0]][1]
                        one_y = points[vertices[0]][0]

                        two_x = points[vertices[1]][1]
                        two_y = points[vertices[1]][0]

                        three_x = points[vertices[2]][1]
                        three_y = points[vertices[2]][0]
                        
                        go_on = True
                        
                        go_on = (abs(one_x - two_x) < EPS) and (abs(one_x - three_x) < EPS) and (abs(two_x - three_x) < EPS)
                         
                        if go_on:
                            go_on = (abs(one_y - two_y) < EPS) and (abs(one_y - three_y) < EPS) and (abs(two_y - three_y) < EPS)
                                               
                        if go_on:
                            coords_string += (str(one_x) + ',' + str(one_y) + ',0\n')
                            coords_string += (str(two_x) + ',' + str(two_y) + ',0\n')
                            coords_string += (str(three_x) + ',' + str(three_y) + ',0\n')
                            coords_string += (str(one_x) + ',' + str(one_y) + ',0')

                            poly = KML.Polygon(KML.outerBoundaryIs(KML.LinearRing(KML.coordinates(coords_string))))

                            mgeom.append(poly)
                        
                pm.append(mgeom)
                root.append(pm)

            print(etree.tostring(doc, pretty_print=True))

#                print(k + ': ' + str(shape))

                
#            print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
#            print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
#            print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
#            print("Adjusted Rand Index: %0.3f" % metrics.adjusted_rand_score(labels_true, labels))
#            print("Adjusted Mutual Information: %0.3f" % metrics.adjusted_mutual_info_score(labels_true, labels))
#            print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels))




