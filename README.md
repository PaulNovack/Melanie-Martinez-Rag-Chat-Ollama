You must have pip and python 3 installed.

python 3 should be executable as python3

pip should be executable as "pip"

Requires docker installed

Requires nodejs and npm installed

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

Depending on your system it may take a while for response.

On my system with no GPU it takes about 3 to 8 seconds for a response.

![chat image](https://github.com/PaulNovack/Melanie-Martinez-Rag-Chat-Ollama/blob/main/img.png?raw=true)
