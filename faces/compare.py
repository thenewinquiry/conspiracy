import os
import numpy as np
import tensorflow as tf
from PIL import Image
from scipy import misc
from faces import facenet

MODEL = 'assets/models/facenet/ms_celeb_1m/20170512-110547.pb'


def compare_faces(paths, size=160):
    """calculates L2 distance between the embeddings of face images"""
    images = load_and_align_data(paths, size)
    with tf.Graph().as_default():
        with tf.Session() as sess:

            # Load the model
            facenet.load_model(MODEL)

            # Get input and output tensors
            images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

            # Run forward pass to calculate embeddings
            feed_dict = { images_placeholder: images, phase_train_placeholder:False }
            emb = sess.run(embeddings, feed_dict=feed_dict)

            nrof_images = len(images)

            dists = np.zeros((nrof_images, nrof_images))
            for i in range(nrof_images):
                for j in range(nrof_images):
                    dists[i,j] = np.sqrt(np.sum(np.square(np.subtract(emb[i,:], emb[j,:]))))
            return dists


def load_and_align_data(image_paths, image_size):
    nrof_samples = len(image_paths)
    img_list = [None] * nrof_samples
    for i in range(nrof_samples):
        img = Image.open(os.path.expanduser(image_paths[i])).convert('RGB')
        aligned = misc.imresize(np.array(img), (image_size, image_size), interp='bilinear')
        prewhitened = facenet.prewhiten(aligned)
        img_list[i] = prewhitened
    images = np.stack(img_list)
    return images
