import os
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from typing import Dict, Any

from app.database.session import SessionLocal, engine
from app.models import models
from app.api import webhook, admin
from app.services.notification import send_notification_email

# Załaduj zmienne środowiskowe
load_dotenv()

# Inicjalizacja bazy danych
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Webhook - Zapis do Bazy i Powiadomienie",
    description="Automatyzacja odbierająca dane z formularza online, zapisująca je do bazy danych i wysyłająca powiadomienia",
    version="1.0.0"
)

# Statyczne pliki
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Szablony
templates = Jinja2Templates(directory="app/templates")

# Zależność dla sesji bazy danych
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dołącz routery API
app.include_router(webhook.router, prefix="/api")
app.include_router(admin.router, prefix="/admin")

# Strona główna
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Webhook - Zapis do Bazy i Powiadomienie"}
    )

# Obsługa błędów
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 