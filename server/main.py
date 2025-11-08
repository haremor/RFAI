import uvicorn
sample = [[20, 20, 10, 3, 20, 1, 100]]
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
    else:
        # Try to extract named fields from JSON (flexible keys)
        def _get(keys):
            for k in keys:
                if k in payload:
                    return payload[k]
            return None

        N = _get(["nitrogen", "n", "N", "nitro"])
        P = _get(["phosphorus", "p", "P"])
        K = _get(["potassium", "k", "K"])
        temp = _get(["temperature", "temp"])
        humid = _get(["humidity", "humid"])
        phv = _get(["ph"]) or _get(["pH", "PH"]) 
        rain = _get(["rainfall", "rain"])

        missing = [name for name, val in [("nitrogen", N), ("phosphorus", P), ("potassium", K), ("temperature", temp), ("humidity", humid), ("ph", phv), ("rainfall", rain)] if val is None]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing fields: {', '.join(missing)}")

        try:
            sample = [float(N), float(P), float(K), float(temp), float(humid), float(phv), float(rain)]
        except Exception:
            raise HTTPException(status_code=400, detail="Unable to convert one or more fields to numeric values")

    try:
        result = top_crops([sample])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)