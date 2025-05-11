import uvicorn
from fastapi import FastAPI, APIRouter

from arxiv import arxiv_router

APP_HOST = "localhost"
APP_PORT = 8080

app = FastAPI()
router = APIRouter()

app.include_router(arxiv_router)

if __name__ == "__main__":
    uvicorn.run("api:app", host=APP_HOST, port=APP_PORT, workers=1)