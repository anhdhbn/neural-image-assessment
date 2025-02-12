import numpy as np
import argparse
from path import Path
# from os import Path

from keras.models import Model
from keras.layers import Dense, Dropout
from keras.applications.inception_resnet_v2 import InceptionResNetV2
from keras.applications.inception_resnet_v2 import preprocess_input
from keras.preprocessing.image import load_img, img_to_array
import tensorflow as tf

from IPython.display import Image
import matplotlib.pyplot as plt
import cv2
import matplotlib.image as mpimg

# %matplotlib inline


from utils.score_utils import mean_score, std_score

parser = argparse.ArgumentParser(description='Evaluate NIMA(Inception ResNet v2)')
parser.add_argument('-dir', type=str, default=None,
                    help='Pass a directory to evaluate the images in it')

parser.add_argument('-img', type=str, default=[None], nargs='+',
                    help='Pass one or more image paths to evaluate them')

parser.add_argument('-resize', type=str, default='false',
                    help='Resize images to 224x224 before scoring')

parser.add_argument('-rank', type=str, default='true',
                    help='Whether to tank the images after they have been scored')

args = parser.parse_args()
resize_image = args.resize.lower() in ("true", "yes", "t", "1")
target_size = (224, 224) if resize_image else None
rank_images = args.rank.lower() in ("true", "yes", "t", "1")

# give priority to directory
if args.dir is not None:
    print("Loading images from directory : ", args.dir)
    imgs = Path(args.dir).files('*.png')
    imgs += Path(args.dir).files('*.jpg')
    imgs += Path(args.dir).files('*.jpeg')

elif args.img[0] is not None:
    print("Loading images from path(s) : ", args.img)
    imgs = args.img

else:
    raise RuntimeError('Either -dir or -img arguments must be passed as argument')

# with tf.device('/CPU:0'):
if True:
    base_model = InceptionResNetV2(input_shape=(None, None, 3), include_top=False, pooling='avg', weights=None)
    x = Dropout(0.75)(base_model.output)
    x = Dense(10, activation='softmax')(x)

    model = Model(base_model.input, x)
    model.load_weights('weights/inception_resnet_weights.h5')

    score_list = []

    fig = plt.figure()
    ncols = int(len(imgs)/3) + 1 
    # plt.subplots(ncols, 3, figsize = (15,12))
    fig,axes=plt.subplots(ncols=ncols, nrows = 3, figsize = (15,12))
    rows = 3
    for idx, img_path in enumerate(imgs):
        i = idx % 3 # Get subplot row
        j = idx // 3 # Get subplot column

        img = load_img(img_path, target_size=target_size)
        x = img_to_array(img)
        x = np.expand_dims(x, axis=0)

        x = preprocess_input(x)

        scores = model.predict(x, batch_size=1, verbose=0)[0]

        mean = mean_score(scores)
        std = std_score(scores)

        file_name = Path(img_path).name.lower()
        score_list.append((file_name, mean))

        print("Evaluating : ", img_path)
        print("NIMA Score : %0.3f +- (%0.3f)" % (mean, std))
        print()

        plt.subplot(rows,3,idx+1)
        plt.title("NIMA Score : %0.3f +- (%0.3f)" % (mean, std))
        plt.axis('off')
        plt.imshow(img)
        # img = cv2.imread(img_path)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # iar_shp = img.shape

        # axes[i] = fig.add_subplot(ncols * 100 + 30 + i) 
        # ax.set_title("NIMA Score : %0.3f +- (%0.3f)" % (mean, std))
        # # plt.subplots(2, 3, figsize = (15,12))
        # plt.imshow(img)
        
    
    plt.show()

    if rank_images:
        print("*" * 40, "Ranking Images", "*" * 40)
        score_list = sorted(score_list, key=lambda x: x[1], reverse=True)

        for i, (name, score) in enumerate(score_list):
            print("%d)" % (i + 1), "%s : Score = %0.5f" % (name, score))
    

