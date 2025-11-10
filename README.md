how to start application:

step 1:
make sure docker desktop is running.

step 2:
in the console, navigate to the root folder of this project.

step 3:
run the command `docker compose up --build -d`

the application should be running now

in the database/model is a file with an example query. run this file, and a new user should be inserted in the database.

in order to see the data in the database (and execute queries directly to it), run the command `docker exec -it postgres psql -U user -d database`