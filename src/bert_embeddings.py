#pip install torch, transformers, numpy
#in mac os there seems to be a problem with the tokenizers while installing transformers:
#https://github.com/huggingface/transformers/issues/2831

from transformers import BertTokenizer, BertModel, BertConfig
import torch
import numpy as np


tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
config = BertConfig.from_pretrained('bert-base-uncased', output_hidden_states=True)
model = BertModel.from_pretrained('bert-base-uncased', config=config)
# Put the model in "evaluation" mode, meaning feed-forward operation.
model.eval()
    

def get_bert_embeddings(input_sentence, layer_num):
    """
    Function to get a fixed dimensional (768) vector for a single sentence at a time. 

    Inputs:
        input_sentence : str of sentence for which embedding is required
        layer_num : int between 0 and 12, 12 = final output layer embedding, 0-11 are hidden layer outputs

    Returns:
        an embedding array of dimension (768,)
    """
    
    text = input_sentence
    # Add the special tokens.
    marked_text = "[CLS] " + text + " [SEP]"

    # Split the sentence into tokens.
    tokenized_text = tokenizer.tokenize(marked_text)

    # Map the token strings to their vocabulary indeces.
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)

    # Mark each of the tokens as belonging to sentence "1".
    segments_ids = [1] * len(tokenized_text)
    # Convert inputs to PyTorch tensors
    tokens_tensor = torch.tensor([indexed_tokens])
    segments_tensors = torch.tensor([segments_ids])
    
    # Predict hidden states features for each layer
    with torch.no_grad():
        outputs = model(tokens_tensor, segments_tensors)
        
#     if (np.array(outputs[0]).all() == np.array(outputs[2][12]).all()):
#         print("last_hidden_state = output embeddings")
    
    token_embeddings = np.array(torch.squeeze(outputs[2][layer_num], dim=0))  

    sentence_embeddings = np.sum(token_embeddings, axis=0)/token_embeddings.shape[0]
   
    return(sentence_embeddings)

    
if __name__ == "__main__": 
    
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    config = BertConfig.from_pretrained('bert-base-uncased', output_hidden_states=True)
    model = BertModel.from_pretrained('bert-base-uncased', config=config)
    # Put the model in "evaluation" mode, meaning feed-forward operation.
    model.eval()
    
    sentence_embedding = get_bert_embeddings("this is my test sentence", 12)
    
    print(sentence_embedding.shape)
