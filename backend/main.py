from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def root():
    return {"message": "欢迎来到知遇Link API"}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}