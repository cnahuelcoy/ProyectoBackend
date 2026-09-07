from fastapi import FastAPI

app = FastAPI(
    title="API Taller Mecánico",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"mensage": "API Taller Mecánico funcionanda"}