import time
import helper
import argparse
import numpy as np
import pandas as pd
import tensorflow as tf
from BILSTM_CRF_tf import BILSTM_CRF

# python test.py model test.in test.out

#arg
parser = argparse.ArgumentParser()
parser.add_argument("model_path", help="the path of model file")
parser.add_argument("test_path", help="the path of test file")
parser.add_argument("output_path", help="the path of output file")
parser.add_argument("-c", "--char_emb", help="the char embedding file", default=None)
parser.add_argument("-g", "--gpu", help="the id of gpu, the default is 0", default=0, type=int)
args = parser.parse_args()

model_path = args.model_path
test_path = args.test_path
output_path = args.output_path
gpu_config = "/gpu:"+str(args.gpu)
# gpu_config = "/cpu:0"
emb_path = args.char_emb
num_steps = 200  # it must consist with the train

start_time = time.time()

#get testData
print "preparing test data"
X_test, X_left_test, X_right_test, X_pos_test, X_lpos_test, X_rpos_test, X_rel_test, X_dis_test = helper.getTest(test_path=test_path, seq_max_len=num_steps)

#feature of testData
test_data = {}
test_data['char'] = X_test
test_data['left'] = X_left_test
test_data['right'] = X_right_test
test_data['pos'] = X_pos_test
test_data['lpos'] = X_lpos_test
test_data['rpos'] = X_rpos_test
test_data['rel'] = X_rel_test
test_data['dis'] = X_dis_test

#dictionary
char2id, id2char = helper.loadMap("char2id")
pos2id, id2pos = helper.loadMap("pos2id")
label2id, id2label = helper.loadMap("label2id")

num_chars = len(id2char.keys())
num_poses = len(id2pos.keys())
num_classes = len(id2label.keys())
num_dises = 250

embedding_matrix = None

print "building model"
config = tf.ConfigProto(allow_soft_placement=True)
with tf.Session(config=config) as sess:
    with tf.device(gpu_config):
        #init model_path
        initializer = tf.random_uniform_initializer(-0.1, 0.1)
        with tf.variable_scope("model", reuse=None, initializer=initializer):
            model = BILSTM_CRF(num_chars=num_chars, num_poses=num_poses, num_dises=num_dises, num_classes=num_classes, num_steps=num_steps,
                               embedding_matrix=embedding_matrix, is_training=False)
        #load model
        print "loading model parameter"
        saver = tf.train.Saver()
        saver.restore(sess, model_path)
        #test
        print "testing"
        results = model.test(sess, test_data, output_path)

        outputFile = open(output_path, 'w')
        for line in results:
            outputFile.write(' '.join(line) + '\n')
        outputFile.close()

        end_time = time.time()
        print "time used %f(hour)" % ((end_time - start_time) / 3600)
