# project-software-construction-leerjaar2


In order to run the dockerfile, go to the folder that contains the docker compose (./api) and run the following command:

docker compose up --build

Then, go to http://localhost:8000/test to access the api.

http://localhost:8000/crash simulates a crash. The api should restart automatically.