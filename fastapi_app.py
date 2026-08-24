from fastapi import FastAPI

from api.response_routes import router as response_router


app = FastAPI()

app.include_router(response_router)