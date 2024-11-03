import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Body, Header # type: ignore
from fastapi.responses import JSONResponse, StreamingResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from App.routes import openai_routes, api_key_routes
from App.data.settings import Settings

settings = Settings()

app = FastAPI()

app.openapi_schema = settings.schema

@app.get("/")
async def welcome():
    return {"message": "Welcome to Candebugger API"}

@app.get("/docs")
async def get_openapi_schema():
    return app.openapi_schema

app.include_router(openai_routes.router) 
app.include_router(api_key_routes.router)  

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "https://localhost",
        "https://edix.studio",
        "https://api.edix.studio",
        "https://jin.edix.studio"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if __name__ == "__main__":
    uvicorn.run("App.main:app", host="0.0.0.0", port=8000, workers=8)