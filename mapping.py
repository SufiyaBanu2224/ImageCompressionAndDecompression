# from __future__ import division
# import os
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# plt.style.use('ggplot')

# from util import load_single_image, normalize
# import pandas as pd
# import numpy as np
# from model import CNN
# from params import HyperParams
# import skimage.io
# import tensorflow as tf
# def MAP(image_path):

#     # Check if the image file exists
#     if os.path.exists(image_path):
#         image = load_single_image(image_path)
#     else:
#         raise Exception("Image file " + image_path + " does not exist")

#     # Initialize hyperparameters and placeholders
#     hyper = HyperParams(verbose=False)
#     images_tf = tf.placeholder(tf.float32, [None, hyper.image_h, hyper.image_w, hyper.image_c], name="images")
#     class_tf = tf.placeholder(tf.int64, [None], name='class')

#     # Initialize CNN model
#     cnn = CNN()
#     if hyper.fine_tuning:
#         cnn.load_vgg_weights()

#     # Build the CNN model
#     conv_last, gap, class_prob = cnn.build(images_tf)
#     classmap = cnn.get_classmap(class_tf, conv_last)

#     # Start TensorFlow session
#     with tf.Session() as sess:
#         tf.train.Saver().restore(sess, hyper.model_path)
#         conv_last_val, class_prob_val = sess.run([conv_last, class_prob], feed_dict={images_tf: image})

#         # Get all class predictions
#         class_predictions_all = class_prob_val.argsort(axis=1)

#         roi_map = None
#         for i in range(-1 * hyper.top_k, 0):
#             current_class = class_predictions_all[:, i]
#             classmap_vals = sess.run(classmap, feed_dict={class_tf: current_class, conv_last: conv_last_val})
#             normalized_classmap = normalize(classmap_vals[0])

#             if roi_map is None:
#                 roi_map = 1.2 * normalized_classmap
#             else:
#                 # Simple exponential ranking
#                 roi_map = (roi_map + normalized_classmap) / 2
#         roi_map = normalize(roi_map)

#     # Plot the heatmap on top of the image
#     fig, ax = plt.subplots(1, 1, figsize=(12, 9))
#     ax.margins(0)
#     plt.axis('off')
#     plt.imshow(roi_map, cmap=plt.cm.jet, interpolation='nearest')
#     plt.imshow(image[0], alpha=0.4)

#     roi_map_uint8 = skimage.img_as_ubyte(roi_map)

#     # Save the plot and the map
#     if not os.path.exists('static/output'):
#         os.makedirs('static/output')
#     plt.savefig('static/output/overlayed_heatmap.png')
#     skimage.io.imsave('static/output/msroi_map.jpg', roi_map_uint8)

#     ### Save the plot and the map
#     ##if not os.path.exists('output'):
#     ##    os.makedirs('output')
#     ##plt.savefig('output/overlayed_heatmap.png')
#     ##skimage.io.imsave('output/msroi_map.jpg', roi_map)
from __future__ import division
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('ggplot')

from util import load_single_image, normalize
import pandas as pd
import numpy as np
from model import CNN
from params import HyperParams
import skimage.io
import tensorflow as tf
def MAP(image_path):

    # Check if the image file exists
    if os.path.exists(image_path):
        image = load_single_image(image_path)
    else:
        raise Exception("Image file " + image_path + " does not exist")

    # Initialize hyperparameters and placeholders
    hyper = HyperParams(verbose=False)
    images_tf = tf.placeholder(tf.float32, [None, hyper.image_h, hyper.image_w, hyper.image_c], name="images")
    class_tf = tf.placeholder(tf.int64, [None], name='class')

    # Initialize CNN model
    cnn = CNN()
    if hyper.fine_tuning:
        cnn.load_vgg_weights()

    # Build the CNN model
    conv_last, gap, class_prob = cnn.build(images_tf)
    classmap = cnn.get_classmap(class_tf, conv_last)

    # Start TensorFlow session
    with tf.Session() as sess:
        tf.train.Saver().restore(sess, hyper.model_path)
        conv_last_val, class_prob_val = sess.run([conv_last, class_prob], feed_dict={images_tf: image})

        # Get all class predictions
        class_predictions_all = class_prob_val.argsort(axis=1)

        # --- MODIFIED: Direct calculation for the single top class for speed ---
        current_class = class_predictions_all[:, -1]
        classmap_vals = sess.run(classmap, feed_dict={class_tf: current_class, conv_last: conv_last_val})
        roi_map = normalize(classmap_vals[0])
        # --------------------------------------------------------------------

    # Plot the heatmap on top of the image
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    ax.margins(0)
    plt.axis('off')
    plt.imshow(roi_map, cmap=plt.cm.jet, interpolation='nearest')
    plt.imshow(image[0], alpha=0.4)

    roi_map_uint8 = skimage.img_as_ubyte(roi_map)

    # Save the plot and the map
    if not os.path.exists('static/output'):
        os.makedirs('static/output')
    plt.savefig('static/output/overlayed_heatmap.png')
    skimage.io.imsave('static/output/msroi_map.jpg', roi_map_uint8)