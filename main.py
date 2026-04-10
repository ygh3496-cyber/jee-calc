from fastapi import FastAPI, UploadFile, File, Form, Request,Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
import uuid
import marks_calculator
from pyrate_limiter import Duration, Limiter, Rate

from fastapi_limiter.depends import RateLimiter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return FileResponse("index.html")

@app.post("/analyze",dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 3))))])
async def analyze_pdf(
    file: UploadFile = File(...),
    shift: str = Form(...)
):

    try:
        print("Request received")

        unique_name = f"{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        contents = await file.read()
        if len(contents)>4*1024*1024:
            return{"error":"file too large"}
        # save file
        with open(file_path, "wb") as f:
            f.write(contents)
        print("Saved at:", file_path)

        # process
        result = marks_calculator.get_marks(file_path, shift)

        print("Processing done")
        print(result)
        os.remove(file_path)
        return {
                "status": "success",
                "result": result
            }

    except Exception as e:
        print("ERROR:", e)
        return {"error": "Error"}