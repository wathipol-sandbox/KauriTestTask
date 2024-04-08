# Kauri Test Task: Crypto Currency Explorer API
(My implementation of the service described [here](https://docs.google.com/document/d/1kUlZ7suZZPPEefWpu9WrdSJgBbVEutLtlXnRUehq4n8/edit?usp=sharing) (test task for Kauri))

> 8. The application should not rely on REST API or make real-time requests at the time of the API service call.

**Target:** Create a system that easily and quickly integrates with new exchanges without need to changing the flow of the application every time when we need add new exchanger as a data source.

<hr>

## Service design and structure

### Features:

- **Modular** design: Easy to add support for new exchanges.
- **Well-defined specifications:** System does not hardcode logic for data scraping. Instead of that app has defines a specification for implementing specific operators to retrieve data from the desired source.
- **Pluggable backends:** Support for different storage solutions.
- **Asyncio safe:** Safe to use in asynchronous applications.


### How to add new data sources?

1. Implement new child class of scraping operator with data scraping logic based on the specification for scraping operators (see. `./currencyexplorer/core`).
2. Import new scraper class to `./app/scrapers/__init__.py` file.
3. The system automatically registers the new operator and data from this source can be requested by API methods ! 


## Usage Guide

### API usage:

After successful launch of the application, interactive documentation will be available along the path: ```{host}/docs``` or ```{host}/redoc```

> The Swager documentation in the header also contains a description of how to work with the WebSocket interface for receiving API data.

## Local Build and Run:

1. Сlone this repository and go to it
2. Touch `.env` file and put inside basic config vars:
    ```sh
    ENVIRONMENT="DEV"
    PORT=<APP CONTAINER PORT FOR EXPOSE>
    API_AUTHENTICATION_TOKEN="<API BASIC AUTH TOKEN>"
    ```
3. Execute: (docker+docker-compose should be installed in your system)
    ```sh
    sudo docker-compose -f docker-compose.yml up -d --build
    ```
4. Now API and workers should launch successfully and be immediately accessible on the specified port in your local `.env` file

## Installing dependencies outside of docker container:

> Poetry must be installed in your python libary. Recommended version: poetry==1.4.2

**Install:**

```sh
poetry config virtualenvs.in-project true
poetry install
```

### Deploy

The application can be easily deployed in any cloud or VM where docker can be installed. For deployment you need to use the `Dockerfile.prod` Dockerfile.

**Deploy to Google Cloud Run & GAR:** for this you can use a template SH script in the project folder - `push_and_deploy_gcloud.sh`

> It can be launched without changing the script file, but for this you must specified env variables with project number and GAR region.
