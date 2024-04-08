import uvicorn
from currencyexplorer.main import app
from currencyexplorer import config


if __name__ == "__main__":
    uvicorn.run(
        "currencyexplorer.main:app",
        host="0.0.0.0",
        port=5000,
        reload=config.DEBUG
    )