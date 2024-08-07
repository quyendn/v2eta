from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # CORS
import gzip
from models import info
from io import BytesIO
from fastapi.responses import StreamingResponse
app = FastAPI()

@app.get('/')
async def index():
    return await info()