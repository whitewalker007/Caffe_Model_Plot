'''
Title           :Generate_lmdb_32.py
Description     :It divides the training images into 2 sets and stores them in lmdb databases for training and validation.
Author          :Nitin Shukla
Date Created    :20170703
'''
import os
import glob
import random
import numpy as np

import sys
sys.path.append('/home/ubuntu/src/caffe')
import cv2

import caffe
from caffe.proto import caffe_pb2
import lmdb

#Image Size
IMG_WIDTH = 224
IMG_HEIGHT = 224

def transform_img(img, img_width=IMG_WIDTH, img_height=IMG_HEIGHT):

    # Performing histogram equalization
    img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
    img[:, :, 1] = cv2.equalizeHist(img[:, :, 1])
    img[:, :, 2] = cv2.equalizeHist(img[:, :, 2])

    #Performing image resizing
    img = cv2.resize(img, (img_width, img_height), interpolation = cv2.INTER_CUBIC)

    return img


def make_datum(img, label):
    return caffe_pb2.Datum(
        channels=3,
        width=IMG_WIDTH,
        height=IMG_HEIGHT,
        label=label,
        data=np.rollaxis(img, 2).tostring())

train_lmdb = '/home/ubuntu/DeepLearning_crop_classification/input/PLOT/train_lmdb'
validation_lmdb = '/home/ubuntu/DeepLearning_crop_classification/input/PLOT/validation_lmdb'

os.system('rm -rf  ' + train_lmdb)
os.system('rm -rf  ' + validation_lmdb)


df_train = [img for img in glob.glob("/home/ubuntu/DeepLearning_crop_classification/input/PLOT/train/*jpg")]
df_test = [img for img in glob.glob("/home/ubuntu/DeepLearning_crop_classification/input/PLOT/test/*jpg")]

#We should shuffle df_train
random.shuffle(df_train)

print 'Generating train_lmdb'

in_db = lmdb.open(train_lmdb, map_size=int(1e12))
with in_db.begin(write=True) as in_txn:
    for in_idx, img_path in enumerate(df_train):
        if in_idx %  6 == 0:
            continue
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = transform_img(img, img_width=IMG_WIDTH, img_height=IMG_HEIGHT)
        if 'sugarcane' in img_path:
            label=0
        elif 'soybean' in img_path:
            label=1
        elif 'rice' in img_path:
            label=2
        elif 'maize' in img_path:
            label=3
        else:
            label=4   #groundnut
        datum = make_datum(img, label)
        in_txn.put('{:0>5d}'.format(in_idx), datum.SerializeToString())
        print '{:0>5d}'.format(in_idx) + ':' + img_path
in_db.close()


print '\nGenerating validation_lmdb'

in_db = lmdb.open(validation_lmdb, map_size=int(1e12))
with in_db.begin(write=True) as in_txn:
    for in_idx, img_path in enumerate(df_train):
        if in_idx % 6 != 0:
            continue
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = transform_img(img, img_width=IMG_WIDTH, img_height=IMG_HEIGHT)
        if 'sugarcane' in img_path:
            label=0
        elif 'soybean' in img_path:
            label=1
        elif 'rice' in img_path:
            label=2
        elif 'maize' in img_path:
            label=3
        else:
            label=4   #groundnut
        datum = make_datum(img, label)
        in_txn.put('{:0>5d}'.format(in_idx), datum.SerializeToString())
        print '{:0>5d}'.format(in_idx) + ':' + img_path
in_db.close()

print '\nCompleted processing all images'
