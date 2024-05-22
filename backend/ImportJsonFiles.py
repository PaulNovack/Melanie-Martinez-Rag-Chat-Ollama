import json
import os
import ollama
from langchain_text_splitters import nltk
from qdrant_client import QdrantClient, models
from qdrant_openapi_client.models import models
from qdrant_client.http.models import PointStruct, Distance
from utilities import getconfig

#nltk.download('punkt')
client = QdrantClient('http://localhost:6333')

files = os.listdir('../topic_data')
for file in files:
    collectionname = file.replace('.json', '')
    collections = client.get_collections()
    for collection in collections.collections:
        if collection.name == collectionname:
            client.delete_collection(collectionname)
    client.create_collection(
        collection_name=collectionname,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    )

    embedmodel = getconfig()["embedmodel"]

    newData = ''
    with open('../topic_data/' + file, 'r') as file:
        data = file.read()
    dataJson = json.loads(data)
    key = 1
    answers = []
    questions = []
    for qa in dataJson:
        question = qa.get("question", None)
        answer = qa.get("answer", None)
        url = qa.get("url", None)
        if qa['question'] not in questions:
            try:
                embed = ollama.embeddings(model=embedmodel, prompt=question)['embedding']
                points = [
                    PointStruct(
                        id=key,
                        vector=embed,
                        payload={
                            "text": answer,
                            "question": question,
                            "url": url,
                            "topic": collectionname,
                            "metadata": {"source": "JSON"}
                        }
                    )
                ]
                client.upsert(
                    collection_name=collectionname,
                    points=points
                )
                key = key + 1
                print(collectionname + ' ' + str(key))
                embed = ollama.embeddings(model=embedmodel, prompt=answer)['embedding']
                points = [
                    PointStruct(
                        id=key,
                        vector=embed,
                        payload={
                            "text": answer,
                            "question": answer,
                            "url": url,
                            "topic": collectionname,
                            "metadata": {"source": "JSON"}
                        }
                    )
                ]
                client.upsert(
                    collection_name=collectionname,
                    points=points
                )
                key = key + 1
                print(collectionname + ' ' + str(key))
            except Exception as e:
                print(f"Error processing chunk {question}: {answer} {e}")
        answers.append(qa['answer'])
        questions.append(qa["question"])