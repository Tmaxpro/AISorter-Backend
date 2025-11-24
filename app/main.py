from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from .database import collection
from ml.model.predictor import predict_from_file
import dotenv
import os

dotenv.load_dotenv()

app = FastAPI()

# Pour autoriser l'appel depuis un frontend (Streamlit, React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        report = predict_from_file(file)
        report['fileName'] = file.filename
        result = collection.insert_one(report)  # Enregistrer le rapport dans MongoDB
        report['_id'] = str(result.inserted_id)
        return report  # Le report est déjà un JSON
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/history")
async def get_history():
    try:
        history = list(collection.find({}, {"_id": 1, "fileName": 1, "timestamp": 1, "summary": 1}))
        # Convertir _id en string
        for item in history:
            item['_id'] = str(item['_id'])
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{report_id}")
async def get_report(report_id: str):
    try:
        report = collection.find_one({"_id": ObjectId(report_id)})
        if report:
            report['_id'] = str(report['_id'])
            return report
        raise HTTPException(status_code=404, detail="Report not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
