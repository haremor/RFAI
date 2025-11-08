import uvicorn
from pathlib import Path
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from model import top_crops


BASE_DIR = Path(__file__).resolve().parent.parent
CLIENT_DIR = BASE_DIR / "client"

app = FastAPI(title="RFAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not CLIENT_DIR.exists():
    raise RuntimeError(f"Client directory not found: {CLIENT_DIR}")

# Serve files from the client directory at /static
app.mount("/static", StaticFiles(directory=str(CLIENT_DIR)), name="static")


@app.get("/", response_class=FileResponse)
def read_index():
    return FileResponse(str(CLIENT_DIR / "index.html"))


@app.get("/es", response_class=FileResponse)
def read_index_es():
    return FileResponse(str(CLIENT_DIR / "index.es.html"))

@app.post("/predict")
def predict(payload: dict = Body(...)):
    sample = None

    # If client sent a 'sample' list, accept it (must have at least 7 values)
    if "sample" in payload:
        s = payload.get("sample")
        if not isinstance(s, list) or len(s) < 7:
            raise HTTPException(status_code=400, detail="'sample' must be a list with at least 7 numeric values")
        try:
            sample = [float(x) for x in s[:7]]
        except Exception:
            raise HTTPException(status_code=400, detail="Unable to convert sample values to numbers")
        
    try:
        result = top_crops([sample])
        # Optionally translate crop names based on payload 'lang'
        lang = str(payload.get("lang", "en")).lower()

        if lang.startswith("es"):
            # mapping of English crop keys (as used in model) to Spanish names
            es_map = {
                'rice': 'arroz',
                'maize': 'maíz',
                'chickpea': 'garbanzo',
                'kidneybeans': 'frijol riñón',
                'pigeonpeas': 'guandú',
                'mothbeans': 'vigna moth',
                'mungbean': 'frijol mungo',
                'blackgram': 'frijol negro',
                'lentil': 'lenteja',
                'pomegranate': 'granada',
                'banana': 'plátano',
                'mango': 'mango',
                'grapes': 'uvas',
                'watermelon': 'sandía',
                'muskmelon': 'melón',
                'apple': 'manzana',
                'orange': 'naranja',
                'papaya': 'papaya',
                'coconut': 'coco',
                'cotton': 'algodón',
                'jute': 'yute',
                'coffee': 'café'
            }

            translated = {}
            for k, v in result.items():
                key_lower = k.lower()
                translated_name = es_map.get(key_lower, k)
                translated[translated_name] = v

            return translated

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)