# -*- coding: utf-8 -*-
#tensorflow 1.2.0 is needed
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os,time,scipy.io
import tensorflow as tf
import numpy as np
import utils_up as utils
import scipy.misc as sic
import subprocess
import argparse
tf.compat.v1.disable_eager_execution()

parser = argparse.ArgumentParser()
parser.add_argument("--model", default='ckpt_woflow', type=str, help="Model Name")
parser.add_argument("--use_gpu", default=1, type=int, help="Use gpu or not")
parser.add_argument("--test_dir", default='test_sample0', type=str, help="Test dir path")
parser.add_argument("--test_img", default='', type=str, help="Test image path")
parser.add_argument("--out_dir", default='../data/VFI_input/', type=str, help="Path to save output")


ARGS = parser.parse_args()
test_dir = ARGS.test_dir
test_img = ARGS.test_img
model=ARGS.model
result_path=ARGS.out_dir
print(ARGS)

if not ARGS.use_gpu:
    os.environ["CUDA_VISIBLE_DEVICES"]=''  
else:
    os.environ["CUDA_VISIBLE_DEVICES"]=str(np.argmax( [int(x.split()[2]) for x in subprocess.Popen("nvidia-smi -q -d Memory | grep -A4 GPU | grep Free", shell=True, stdout=subprocess.PIPE).stdout.readlines()]))

def identity_initializer():
    def _initializer(shape, dtype=tf.float32, partition_info=None):
        array = np.zeros(shape, dtype=float)
        cx, cy = shape[0]//2, shape[1]//2
        for i in range(np.minimum(shape[2],shape[3])):
            array[cx, cy, i, i] = 1
        return tf.constant(array, dtype=dtype)
    return _initializer

def lrelu(x):
    return tf.maximum(x*0.2,x)

def bilinear_up_and_concat(x1, x2, output_channels, in_channels, scope):
    with tf.compat.v1.variable_scope(scope):
        upconv = tf.image.resize(x1, [tf.shape(input=x1)[1]*2, tf.shape(input=x1)[2]*2] )
        upconv.set_shape([None, None, None, in_channels])
        upconv = tf.compat.v1.layers.conv2d(upconv,output_channels,[3,3],  padding='same',activation=None,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"), name='up_conv1')
        upconv_output =  tf.concat([upconv, x2], axis=3)
        upconv_output.set_shape([None, None, None, output_channels*2])
    return upconv_output

def VCN(input, channel=32, output_channel=3,reuse=False,ext=""):
    if reuse:
        tf.compat.v1.get_variable_scope().reuse_variables()
    conv1=tf.compat.v1.layers.conv2d(input, channel, [1,1], padding='same',activation=lrelu, kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"), name=ext+'g_conv1_1')
    conv1=tf.compat.v1.layers.conv2d(conv1, channel, [3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),name=ext+'g_conv1_2')
    pool1=tf.compat.v1.layers.max_pooling2d(conv1, [2, 2],2, padding='same')
    conv2=tf.compat.v1.layers.conv2d(pool1,channel*2,[3,3],  padding='same',activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),name=ext+'g_conv2_1')
    conv2=tf.compat.v1.layers.conv2d(conv2,channel*2,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"), name=ext+'g_conv2_2')
    pool2=tf.compat.v1.layers.max_pooling2d(conv2, [2, 2], 2, padding='same')
    conv3=tf.compat.v1.layers.conv2d(pool2,channel*4,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"), name=ext+'g_conv3_1')
    conv3=tf.compat.v1.layers.conv2d(conv3,channel*4,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"), name=ext+'g_conv3_2')
    pool3=tf.compat.v1.layers.max_pooling2d(conv3, [2, 2], 2, padding='same')
    conv4=tf.compat.v1.layers.conv2d(pool3,channel*8,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"), name=ext+'g_conv4_1')
    conv4=tf.compat.v1.layers.conv2d(conv4,channel*8,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv4_2')
    pool4=tf.compat.v1.layers.max_pooling2d(conv4, [2, 2], 2, padding='same')
    conv5=tf.compat.v1.layers.conv2d(pool4,channel*16,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv5_1')
    conv5=tf.compat.v1.layers.conv2d(conv5,channel*16,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv5_2')
    up6 =  bilinear_up_and_concat( conv5, conv4, channel*8, channel*16, scope=ext+"g_up_1" )
    conv6=tf.compat.v1.layers.conv2d(up6,  channel*8,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv6_1')
    conv6=tf.compat.v1.layers.conv2d(conv6,channel*8,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv6_2')
    up7 =  bilinear_up_and_concat( conv6, conv3, channel*4, channel*8, scope=ext+"g_up_2" )
    conv7=tf.compat.v1.layers.conv2d(up7,  channel*4,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv7_1')
    conv7=tf.compat.v1.layers.conv2d(conv7,channel*4,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv7_2')
    up8 =  bilinear_up_and_concat( conv7, conv2, channel*2, channel*4, scope=ext+"g_up_3" )
    conv8=tf.compat.v1.layers.conv2d(up8,  channel*2,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv8_1')
    conv8=tf.compat.v1.layers.conv2d(conv8,channel*2,[3,3], padding='same', activation=lrelu,kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv8_2')
    up9 =  bilinear_up_and_concat( conv8, conv1, channel, channel*2, scope=ext+"g_up_4" )
    conv9=tf.compat.v1.layers.conv2d(up9,  channel,[3,3], padding='same', activation=lrelu, kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv9_1')
    conv9=tf.compat.v1.layers.conv2d(conv9, output_channel*4 , [3,3], padding='same', activation=None, kernel_initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform"),  name=ext+'g_conv9_2')
    return conv9


config=tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth=True
sess=tf.compat.v1.Session(config=config)
input_i=tf.compat.v1.placeholder(tf.float32,shape=[1,None,None,2])
input_target=tf.compat.v1.placeholder(tf.float32,shape=[1,None,None,6])

with tf.compat.v1.variable_scope(tf.compat.v1.get_variable_scope()):
    with tf.compat.v1.variable_scope('individual'):
        g0=VCN(utils.build(tf.tile(input_i[:,:,:,0:1],[1,1,1,3])), reuse=False)
        g1=VCN(utils.build(tf.tile(input_i[:,:,:,1:2],[1,1,1,3])), reuse=True)

saver=tf.compat.v1.train.Saver(max_to_keep=1000)


# +
sess.run([tf.compat.v1.global_variables_initializer()])

var_restore = [v for v in tf.compat.v1.trainable_variables()]
saver_restore=tf.compat.v1.train.Saver(var_restore)
ckpt=tf.train.get_checkpoint_state(model)
saver_restore.restore(sess,ckpt.model_checkpoint_path)
# -

if not len(test_img):
    img_names = utils.get_names(test_dir)
    ind=0
    for img_name in img_names:
        im=np.float32(scipy.misc.imread(img_name, 'L'))/255.0
        h=im.shape[0]//32*32
        w=im.shape[1]//32*32
        im=im[np.newaxis,:h,:w,np.newaxis]
        st=time.time()
        output=sess.run(g0,feed_dict={input_i:np.concatenate((im,im),axis=3)})
        print("test time for %s --> %.3f"%(ind, time.time()-st))
        # 이름 추출
        base = os.path.basename(img_name)
        img_name = os.path.splitext(base)[0]
        if not os.path.exists(result_path):
            os.makedirs(result_path)
#         out_all = np.concatenate([output[:,:,:,3*i:3*i+3] for i in range(1)],axis=2)
        print('image name', img_name)
        sic.imsave("%s%s.png"%(result_path, img_name),np.uint8(np.maximum(np.minimum(output[0,:,:,:3] * 255.0,255.0),0.0)))
#         sic.imsave("%s%05d.png"%(result_path,ind),np.uint8(np.maximum(np.minimum(out_all[0,:,:,:] * 255.0,255.0),0.0)))        
        
        ind+=1

else:
    im=np.float32(scipy.misc.imread(test_img, 'L'))/255.0
    h=im.shape[0]//32*32
    w=im.shape[1]//32*32
    im=im[np.newaxis,:h,:w,np.newaxis]
    st=time.time()
    output=sess.run(g0,feed_dict={input_i:np.concatenate((im,im),axis=3)})
    print("test time for %s --> %.3f"%(test_img, time.time()-st))
    folder = test_dir.split('/')[-1]
    out_all = np.concatenate([output[:,:,:,3*i:3*i+3] for i in range(4)],axis=2)
    for idx in range(4):
        sic.imsave("%s/%s_result%d.png"%(result_path,test_img.split('/')[-1][:-4],idx+1),np.uint8(np.maximum(np.minimum(output[0,:,:,3*idx:3*idx+3] * 255.0,255.0),0.0)))
    sic.imsave("%s/%s_result.png"%(result_path,test_img.split('/')[-1][:-4]),np.uint8(np.maximum(np.minimum(out_all[0,:,:,:] * 255.0,255.0),0.0)))    
    sic.imsave("%s/%s_input.png"%(result_path,test_img.split('/')[-1][:-4]),np.uint8(np.maximum(np.minimum(im[0,:,:,0] * 255.0,255.0),0.0)))    
