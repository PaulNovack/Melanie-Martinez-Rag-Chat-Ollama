import asyncio
import json

import websockets
import time

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, Filter, FieldCondition, MatchValue, MatchText
import ollama, sys
from utilities import getconfig
starttime = time.time()
collectionname = getconfig()["collectionname"]
embedmodel = getconfig()["embedmodel"]
mainmodel = getconfig()["mainmodel"]
client = QdrantClient('http://localhost:6333')

# List of stop words
stop_words = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves", "Melanie","Martinez's","Martinez"
]

def remove_stop_words(text, stop_words):
    # Split the text into words
    words = text.split()

    # Remove stop words
    filtered_words = [word for word in words if word.lower() not in stop_words]

    # Join the filtered words back into a string
    filtered_text = ' '.join(filtered_words)

    return filtered_text

vector_size = 768  # Adjust based on your embedding size
distance = Distance.COSINE  # Or other distance m


async def echo(websocket, path):
    async for query in websocket:
        queryembed = ollama.embeddings(model=embedmodel, prompt=query)['embedding']
        relevantdocs = client.search(
            collection_name=collectionname,
            query_vector=queryembed,
            limit=50  # Number of results to retrieve
        )
        context = ''
        answers = []
        docnumber = 1
        for doc in relevantdocs:
            answer = doc.payload.get('text') + '\n'
            if answer not in answers:
                context += answer
                docnumber += 1
            answers.append(answer)
            if docnumber >= 15:
                break
        print(context)
        prompt = f"""
                    Heres context: {context}
                    Using the relevant information from the context
                    provide an answer as an assistant to the question: {query}.
                    If the context does not contain the knowledge reply only with \"I don't have that information\"
                    """

        stream = ollama.generate(model=mainmodel, prompt=prompt, stream=True)

        is_opening = True
        for chunk in stream:
            if chunk["response"]:
                result = []
                i = 0
                response_text = chunk['response']
                while i < len(response_text):
                    if response_text[i:i + 2] == '**':
                        if is_opening:
                            result.append('<strong>')
                        else:
                            result.append('</strong>')
                        is_opening = not is_opening
                        i += 2  # Skip the '**'
                    else:
                        result.append(response_text[i])
                        i += 1
                simple_string = ''.join(result)
                #print(simple_string, end='', flush=True)
                await websocket.send(f"{simple_string}")
        await websocket.send(f"~END~")

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
