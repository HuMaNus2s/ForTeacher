import logging
import uvicorn
from fastapi import FastAPI

from src.controllers.books import router as books_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Book API",
    description="API для книжного магазина",
    version="1.0.0",
)

app.include_router(books_router)

@app.get("/")
async def root():
    return {
        "message": "Это API книжного магазина",
    }

def main():
    logger.info('Started')
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

if __name__ == "__main__":
    main()