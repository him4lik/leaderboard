# Leaderboard Service Submodule
## Description

This submodule is part of the larger project and provides the leaderboard functionality. It is built using Django and integrates with PostgreSQL for data storage, Redis for caching and task queuing, and Celery for asynchronous task processing. The service is containerized using Docker and managed via Docker Compose.

Parent module link to test with above mentioned services - [https://github.com/him4lik/leaderboard-deploy](https://github.com/him4lik/leaderboard-deploy)

## Installation
### Prerequisites
  - Docker and Docker Compose installed on your machine.
### Steps
  - Clone the super repository:
    ```bash
    git clone git@github.com:him4lik/leaderboard-deploy.git
    ```
  - Navigate to the leaderboard service directory:
    ```bash
    cd leaderboard-deploy/leaderboard
    ```
  - Build and start the services using Docker Compose:
    Go to the super project directory and run following commands
    ```bash
    source .bash_aliases
    dcrestart
    ```
    
## Usage
### Running the Services
  - Access the Django application at: [http://localhost:8001/web/dashboard](http://localhost:8001/web/dashboard)

### This service integrates with the following components:
  - PostgreSQL: For persistent data storage.
  - Redis: For task queuing and caching.
  - Celery Worker: For asynchronous task processing.
  - Celery Beat: For scheduled tasks
