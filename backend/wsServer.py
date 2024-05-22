import asyncio
import websockets
import time
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, Filter, FieldCondition, MatchValue, MatchText
import ollama
from utilities import getconfig

starttime = time.time()

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
    "yourselves", "Melanie", "Martinez's", "Martinez"
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
distance = Distance.COSINE  # Or other distance measures

async def send_keep_alive_ping(websocket, interval=60):
    while True:
        try:
            await websocket.ping()
            await asyncio.sleep(interval)
        except websockets.ConnectionClosed:
            break

async def echo(websocket, path):
    keep_alive_task = asyncio.create_task(send_keep_alive_ping(websocket))
    try:
        async for query in websocket:
            goturl = False
            queryNew = query.split('|')
            collectionname = queryNew[0]
            query = queryNew[1]
            print(query + '\n')
            queryembed = ollama.embeddings(model=embedmodel, prompt=query)['embedding']
            relevantdocs = client.search(
                collection_name=collectionname,
                query_vector=queryembed,
                limit=35  # Number of results to retrieve
            )
            context = ''
            answers = []
            urls = []
            docnumber = 1
            for doc in relevantdocs:
                url = doc.payload.get('url', None)
                if url is not None:
                    goturl = True;
                if url not in urls:
                    urls.append(url)
                answer = doc.payload.get('text') + '\n'
                if answer not in answers:
                    context += answer
                    docnumber += 1
                answers.append(answer)
                if docnumber >= 20:
                    break
                #context += '\n\n\n'
            print(context)
            prompt = f"""
                        Heres context: {context}
                        Using the relevant information from the context
                        provide an answer as an assistant to the question: {query}.
                        If the context does not contain the knowledge reply only with \"I don't have that information or you can ask me a specific question about an album etc.\"
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
                    print(simple_string, end='', flush=True)
                    await websocket.send(f"{simple_string}")
            ur = '['
            urlNum = 0
            for url in urls:
              ur += '"' + url + '",'
              urlNum += 1
              if urlNum == 5:
                  break
            ur = ur.rstrip(',')
            ur = ur + ']'
            if goturl:
                await websocket.send("\n\nHere are some helpful links:\n")
                await websocket.send(f"~URLS~{ur}")
            await websocket.send(f"~END~")
            print('\n')
    except websockets.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        keep_alive_task.cancel()
        await websocket.close()

async def main():
    async with websockets.serve(echo, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
