**Chatbot using qdrant vector DB and ollama to run llm**

![chat image](https://github.com/PaulNovack/Melanie-Martinez-Rag-Chat-Ollama/blob/main/img.png?raw=true)

*llama3 LLM Model*

*nomic-embed-text Embedding Model*

Models can be configured in config.ini but they must be added with: docker exec ollama2 ollama pull llama3

You must have pip and python 3 installed.

python 3 should be executable as python3

pip should be executable as "pip"

Requires docker installed

Requires nodejs and npm installed

**The start script will run Docker prune and stop all containers**

If you have other docker containers you do not want stopped edit the

./startAll.sh 

script first!

run ./startAll.sh

This will install ollama and download llama3 model and the nomic-embed-text embedding model

It will take a while couple gigs of data

Then qdrant will be installed in a docker container and started

Then the json melanie martinez data will be imported

Then the wsServer.py with be started

Finally a Browser window will open which you can ask questions like:

What songs are on the album portals?

What songs are on the album Cry Baby?

When was Melanie Martinez born?

How old is Melanie Martinez?

What is Melanie Martinez Middle name?

Depending on your system it may take a while for response.

On my system with no GPU it takes about 3 to 8 seconds for a response.

You could edit questions and answers to answer questions and answers for whatever topic you prefer.

Just need to follow format in /backend/Melanie.json or change filename in the code


