from fastapi import FastAPI, UploadFile, File
import shutil

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    with open(file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}
