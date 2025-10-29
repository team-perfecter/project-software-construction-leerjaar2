# project-software-construction-leerjaar2

In order to run FastAPI, navigate to the file that contains FastAPI code and execute the following command:
uvicorn {filename}:app --reload
for now, the filename is profile, so go to api/profile and execute: uvicorn profile:app --reload



In order to run the dockerfile, go to the folder that contains the docker compose (./api) and run the following command:

docker compose up --build

Then, go to http://localhost:8000/test to access the api.

http://localhost:8000/crash simulates a crash. The api should restart automatically.