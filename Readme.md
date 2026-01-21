## INSTALLATION

## Deactivate
deactivate

###### WINDOWS

## Create virtual envirenment
python -m venv venv

## Activate virtual environment
.\venv\Scripts\Activate.ps1

## Install / update dependencies
pip install -r requirements.txt

## Run the project
uvicorn app.main:app --reload

###### MAC

## Create virtual envirenment
python3 -m venv venv

## Activate virtual environment 
source venv/bin/activate

## Install / update dependencies
pip install -r requirements.txt

## Run the project
uvicorn app.main:app --reload


sudo docker rm rag_multimodel

//sudo docker run -d -p 3000:3000  -v $(pwd)/chroma_db:/app/chroma_db  --name rag_multimodel  rag_multimodel:latest
sudo docker run -d -p 3001:3000 -v $(pwd)/chroma_db:/app/chroma_db --name rag_multimodel rag_multimodel:latest

sudo docker stop rag_multimodel


sudo docker run -d -p 3001:3000 -v $(pwd)/chroma_db:/app/chroma_db --env-file .env --name rag_multimodel rag_multimodel:latest

sudo docker ps

sudo docker logs rag_multimodel
