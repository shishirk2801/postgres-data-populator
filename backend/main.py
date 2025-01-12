from fastapi import FastAPI
from fastapi.responses import FileResponse
from views import generate_xlsx

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/download-xlsx/")
async def download_xlsx():
    file_path = generate_xlsx()
    if file_path:
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="file.xlsx")
    return {"error": "File not found"}
