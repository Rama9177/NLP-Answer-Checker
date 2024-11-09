from sentence_transformers import SentenceTransformer, util
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from itertools import chain

# Load the pre-trained model
model = SentenceTransformer('bert-base-nli-mean-tokens')

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def get_synonyms(word):
    synonyms = wordnet.synsets(word)
    lemmas = set(chain.from_iterable([word.lemma_names() for word in synonyms]))
    return lemmas

def keyword_match_score(ideal_answer, user_answer):
    stop_words = set(stopwords.words('english'))
    ideal_tokens = [word for word in word_tokenize(ideal_answer.lower()) if word.isalnum() and word not in stop_words]
    user_tokens = [word for word in word_tokenize(user_answer.lower()) if word.isalnum() and word not in stop_words]

    ideal_keywords = set(ideal_tokens)
    user_keywords = set(user_tokens)
    
    synonym_matched_keywords = set()
    for word in user_keywords:
        synonyms = get_synonyms(word)
        if ideal_keywords.intersection(synonyms):
            synonym_matched_keywords.add(word)

    match_count = len(ideal_keywords & user_keywords) + len(synonym_matched_keywords)
    keyword_match_percentage = match_count / len(ideal_keywords) if ideal_keywords else 0

    return keyword_match_percentage

def semantic_similarity_score(ideal_answer, user_answer):
    embeddings1 = model.encode(ideal_answer, convert_to_tensor=True)
    embeddings2 = model.encode(user_answer, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(embeddings1, embeddings2)
    return similarity.item()

def evaluate_answer(ideal_answer, user_answer):
    keyword_score = keyword_match_score(ideal_answer, user_answer)
    semantic_score = semantic_similarity_score(ideal_answer, user_answer)

    # Adjusted heuristic to combine keyword score and semantic score
    if keyword_score == 0:
        final_score = 0.5 * semantic_score
    else:
        final_score = 0.4 * keyword_score + 0.6 * semantic_score

    # Ensure the final score does not exceed 100 and round appropriately
    final_score = min(final_score * 100, 100)
    final_score = round(final_score, 2)

    return final_score, keyword_score * 100, semantic_score * 100
