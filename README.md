# Kauri Test Task: Crypto Currency Explorer API
(My implementation of the service described [here](https://docs.google.com/document/d/1kUlZ7suZZPPEefWpu9WrdSJgBbVEutLtlXnRUehq4n8/edit?usp=sharing) (test task for Kauri))

> 8. The application should not rely on REST API or make real-time requests at the time of the API service call.
**Target:** Create a system that easily and quickly integrates with new exchanges without need to changing the flow of the application every time when we need add new exchanger as a data source.

<hr>


##№ Service design and structure

## Features:

- **Modular** design: Easy to add support for new exchanges.
- **Well-defined specifications:** System does not hardcode logic for data scraping. Instead of that app has defines a specification for implementing specific operators to retrieve data from the desired source.
- **Pluggable backends:** Support for different storage solutions.
- **Asyncio safe:** Safe to use in asynchronous applications.

