'''
Taken from:
    https://github.com/saranya132/pretrained_sent_embeddings
'''

import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

#dictionary to store URLs of pre-trained modules
models_dict = {
    'embed_20_model_url' : "https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim-with-oov/1",
    'embed_50_model_url' : "https://tfhub.dev/google/tf2-preview/nnlm-en-dim50-with-normalization/1",
    'embed_128_model_url' : "https://tfhub.dev/google/tf2-preview/nnlm-en-dim128-with-normalization/1",
    'embed_250_model_url' : "https://tfhub.dev/google/Wiki-words-250/2",
    'embed_512_model_url' : "https://tfhub.dev/google/universal-sentence-encoder/4", #trained with Deep Averaging Network (DAN)
    'embed_512t_model_url' : "https://tfhub.dev/google/universal-sentence-encoder-large/5" #trained with transformerhttps://tfhub.dev/google/universal-sentence-encoder/4
    }


def load_embeddings_model(embed_size=128):
    '''Fetches an embedding model from tensorflow hub, where the type of model is given by the embed_size
    Args:
        embed_size: dimensionality of the pretrained model, it can be a string, specially for 512t
    Returns:
        model object
        
    In order to get embeddings:  embs= np.array(embed([Sentence1, Sentence2,...])), or use method below
    '''
    #get URL according to embedding size
    model_url = 'embed_{}_model_url'.format(embed_size)
    #load model
    embed = hub.load(models_dict[model_url])
    return embed


def get_sentence_embeddings(sentences,embedding_model):
    """ Fetches n-dimensional embedding per input sentence from pretrained sentence embedding module.
    Args:
        sentences: Python List of String/sequence of Strings.
        embedding_model: pretrained model fetched from tensorflow hub
    Returns:
        Numpy array of dimension (m,n) where m is the number of sentences in input, and n is the embedding dimension.
 
    """
    return np.array(embedding_model(sentences))


if __name__ == "__main__":

    #set embedding size(20/50/128/250/512/512t) 
    EMBEDDING_SIZE ="512t"
    
    #get input sentences/read from file into list
    sentences_= ["Universal Sentence Encoder embeddings also support short paragraphs.",
                 "There is no hard limit on how long the paragraph is.", 
                 "Roughly, the longer the more 'diluted' the embedding will be."]
    import os
    os.environ['TFHUB_CACHE_DIR']='tf_cache'
    
    emb_model=load_embeddings_model(EMBEDDING_SIZE)
    #get embeddings from loaded model
    embeddings = np.array(emb_model(sentences_))
    
    print("Shape of output/embeddings array", embeddings.shape)
    for sent_emb in embeddings:
        print(sent_emb)