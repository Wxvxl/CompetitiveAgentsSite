# Project Description

This is the **back-end** system utilized in the "Competitive Agent Site" project undertaken by CITS5206 Students for the client **Daochang Liu**, the tutor of **CITS3011 : Intelligent Agents**. The purpose of this project is to facilitate the marking process for the project of the unit. This back-end server is an API endpoint for processing requests for the front-end while also storing the necessary data for running games within the project. 

---

## Getting Started

### 1. Environment Variables

The program need an .env folder placed in the root folder of "PythonWebserver" folder. Example of the content of the env folder is:

```env
POSTGRES_DB=database_name
POSTGRES_PASSWORD=password
SECRET_KEY=super-secret-key
DATABASE_URL=postgresql://postgres:password@db:5432/database_name
```

DATABASE_URL uses a postgresql URL. You should adjust the variable based off your own data. The database name is the name of the database, username is redundant here and should stay postgres, which is the default admin user. Replace the "password" with your own password when setting up the postgres database. 5432 is the default port which shouldn't be changed and lastly change the database_name to whatever testing name you desire.

---

### 2. Download Docker
This deployment uses Docker to create a Flask server and the Database PostgreSQL deployment. Therefore it is necessary to install a Docker Engine and make sure that it is running: `https://docs.docker.com/engine/install`. Once your docker is configured and running 

### 3. Running the Deployment
Docker-compose and Dockerfile is already provided in the PythonWebserver folder, so just navigate to that folder and run the following command:

```bash
docker compose up --build
```

### 4. Database Setup

There is a Python script that will setup the necessary table. Note that this also **delete all the data** in the table and should only be used for **testing** purposes or initial **setup**!

```bash
docker compose exec app python dbSetup.py
```

### 5. Testing the App
After running `dbSetup.py` it will create the database with all of the table, but however all of the table is empty! There is a Python script for testing all of the available endpoints in the app while also testing the integrity and function of the database: `appTesting.py` By running appTesting.py in the docker container:

```bash
docker compose exec app python appTesting.py
```

## Games Specification
Creating a new games requires the following set of specifications:
### 1. All games must be stored in the /games/ folder.
### 2. All games must have a game.py stored in the root folder.
### 2.1 The class for the game **must** be a class type of **Game**
### 2.2 The class must have an **__init__** that accepts a parameter of agents, which is a list of agents competing in the game.
### 2.3 The class must have a **play()** function that accepts no parameters
### 2.4 The **play()** function must return a list, which is the result of the game. Generally the 0th Index is the winner, while the 1st Index is the loser. But different games can handle this differently.
### 2.5 Inside there should be an /agents/ folder that contains two sub-folder to store agents: **students/** and **test/** The students folder contains user submitted agents while the test/ folder contains the agents that are used to test against the student's agent.