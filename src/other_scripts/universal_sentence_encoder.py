"""
We don't use this script anymore. We use sentence_embeddings.py instead, which uses tensorflow 2.

4 requirements for this script:

    Please install Tensforlow version 1.13 or above (but not Tensorflow 2) and Tensorflow-hub.
    One way to install those packages are using Conda. Download and install Anaconda. Activate the tensorflow environment.
    Then use the following commands to install tensorflow & tensorflow-hub.

    1. Tensorflow : conda install -c conda-forge tensorflow (This installs version 1.13.1 but a higher version (1.14) is even better)
    2. Tensorflow-hub : conda install -c conda-forge tensorflow-hub
    3. Python 3
    4. Numpy

"""
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/3"
embed = hub.Module(module_url)


""" This function takes as input a list of sentences/one sentence at a time and returns a 512 length embedding from
    Google's Universal Sentence Encoder pretrained module.

    Input parameter: Un-processed string sentences in a list/one at a time.
    For example inputs can be one of the following 2 types:
    Type 1: List of string type sentences ->  sentences_ = ["I am a sentence for which I would like to get its embedding.",
                        "Universal Sentence Encoder embeddings also support short paragraphs. ",
                        "There is no hard limit on how long the paragraph is. Roughly, the longer ",
                        "the more 'diluted' the embedding will be."]
    Type 2: one string sentence at a time -> sentences_ = "This is a single sentence input."

    Returns : Numpy array of dimension (n,512) where n is the number of sentences in input, and 512 is the embedding dimension
"""
def get_sentence_embedding(sentences):
    if not isinstance(sentences,(list,)):
        sentences = [sentences]
    tf.logging.set_verbosity(tf.logging.ERROR)
    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        sentence_embedding = session.run(embed(sentences))
        return np.array(sentence_embedding)

sentences_ = ["I am a sentence for which I would like to get its embedding.",
            "Universal Sentence Encoder embeddings also support short paragraphs. ",
            "There is no hard limit on how long the paragraph is. Roughly, the longer ",
            "the more 'diluted' the embedding will be." ]

# Can also try this as input -> Uncomment next line
#sentences_ = "I am a sentence for which I would like to get its embedding."

# function call
embeddings = get_sentence_embedding(sentences_)

print("Shape of output/embeddings array", embeddings.shape)
for sent_emb in embeddings:
    print (sent_emb)


