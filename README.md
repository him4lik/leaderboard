## Leaderboard Service Submodule
### Description

This submodule is part of the larger project and provides the leaderboard functionality. It is built using Django and integrates with PostgreSQL for data storage, Redis for caching and task queuing, and Celery for asynchronous task processing. The service is containerized using Docker and managed via Docker Compose.
### Installation
#### Prerequisites
  Docker and Docker Compose installed on your machine.
#### Steps
  Clone the super repository:
  ```bash
git clone https://github.com/username/super-repo.git
  ```
  Navigate to the leaderboard service directory:
    ```bash
    cd super-repo/leaderboard
    ```
  Build and start the services using Docker Compose:
    ```bash
    docker-compose up --build
    ```
### Configuration
### Environment Variables

#### Create a .env file in the leaderboard directory with the following variables:
```bash
DEBUG=TRUE
PATH_SPEC=test
DB_NAME=leaderboard
DB_USER=ubuntu
DB_PASSWORD=forgot123
DB_HOST=postgres
```

### Usage
#### Running the Services
  Access the Django application at: 
    [http://localhost:8000](http://localhost:8000)

### This service integrates with the following components:
#### PostgreSQL: For persistent data storage.
#### Redis: For task queuing and caching.
#### Celery Worker: For asynchronous task processing.
#### Celery Beat: For scheduled tasks

Super module link to test with above mentioned services - [https://github.com/him4lik/leaderboard-deploy](https://github.com/him4lik/leaderboard-deploy)
