from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import time

tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-distilroberta-v1') # you can change the model here
model = AutoModel.from_pretrained('sentence-transformers/all-distilroberta-v1')

def convert_to_embedding(query):
    tokens = {'input_ids': [], 'attention_mask': []}
    new_tokens = tokenizer.encode_plus(query, max_length=512,
                                       truncation=True, padding='max_length',
                                       return_tensors='pt')
    tokens['input_ids'].append(new_tokens['input_ids'][0])
    tokens['attention_mask'].append(new_tokens['attention_mask'][0])
    tokens['input_ids'] = torch.stack(tokens['input_ids'])
    tokens['attention_mask'] = torch.stack(tokens['attention_mask'])
    with torch.no_grad():
        outputs = model(**tokens)
    embeddings = outputs.last_hidden_state
    attention_mask = tokens['attention_mask']
    mask = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
    masked_embeddings = embeddings * mask
    summed = torch.sum(masked_embeddings, 1)
    summed_mask = torch.clamp(mask.sum(1), min=1e-9)
    mean_pooled = summed / summed_mask
    
    return mean_pooled[0] # assuming query is a single sentence

def query_index(query):
	query_embedding = convert_to_embedding(query)
	cos = torch.nn.CosineSimilarity()
	# sim = cos(query_embedding, mean_pooled)

	index_loaded = faiss.read_index("bert_index.index")
	D, I = index_loaded.search(query_embedding[None, :], 10)
	return (I[0], D[0])

def index_sentences(index, sentences):
	if(len(sentences) > 0):
		batch_size = 500
		start = 0
		values = []
		while start <= len(sentences):
			print("running "+ str(start)+" to "+ str(batch_size+start))
			values.append(bert_index(sentences[start: start + batch_size]))
			start += batch_size
			if(start >= len(sentences)):
				break
		return values
	else:
		print("indexing skipped since len is 0")
		return None


def bert_index(sentences):
	if(len(sentences) > 0):
		print(str(len(sentences))+ " is passed to bert_index")
		# initialize dictionary to store tokenized sentences
		tokens = {'input_ids': [], 'attention_mask': []}

		for sentence in sentences:
		    # encode each sentence and append to dictionary
		    new_tokens = tokenizer.encode_plus(sentence, max_length=512,
		                                       truncation=True, padding='max_length',
		                                       return_tensors='pt')
		    tokens['input_ids'].append(new_tokens['input_ids'][0])
		    tokens['attention_mask'].append(new_tokens['attention_mask'][0])
		# reformat list of tensors into single tensor
		tokens['input_ids'] = torch.stack(tokens['input_ids'])
		tokens['attention_mask'] = torch.stack(tokens['attention_mask'])
		
		with torch.no_grad():
			t = time.time()
			print("start model")
			outputs = model(**tokens)
			print("time taken for model to run :: " + str(time.time() - t))

		embeddings = outputs.last_hidden_state
		attention_mask = tokens['attention_mask']
		mask = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
		masked_embeddings = embeddings * mask
		summed = torch.sum(masked_embeddings, 1)
		summed_mask = torch.clamp(mask.sum(1), min=1e-9)
		mean_pooled = summed / summed_mask

		# index = faiss.IndexFlatIP(768)# build the index
		
		# D, I = index.search(query_embedding[None, :], 1) # None dimension is added because we only have one query against 4 documents
		# index.add(mean_pooled)
		return mean_pooled
	else:
		return None


	
