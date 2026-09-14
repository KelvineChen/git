from fastapi import FastAPI
from pydantic import BaseModel

from ai_service import parse_project_requirement, parse_user_profile

app = FastAPI()

@app.get("/")
def root():
    return {"message": "欢迎来到知遇Link API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

class ProfileRequest(BaseModel):
    raw_text: str

@app.post("/api/parse_profile")
def parse_profile(request: ProfileRequest):
    try:
        result = parse_user_profile(request.raw_text)
        return {"success": True, "data": result}
    except Exception:
        return {"success": False, "message": "解析失败，请重试"}


@app.post("/api/parse_project")
def parse_project(request: ProfileRequest):
    try:
        result = parse_project_requirement(request.raw_text)
        return {"success": True, "data": result}
    except Exception:
        return {"success": False, "message": "解析失败，请重试"}
