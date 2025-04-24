from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from typing import Dict, Any

from app.database.session import SessionLocal
from app.models.models import FormSubmission, Notification
from app.services.notification import send_notification_email

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhook"])

# Zależność dla sesji bazy danych
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def process_form_submission(form_id: str, form_name: str, form_data: Dict[str, Any], db: Session):
    """
    Funkcja przetwarzająca dane formularza w tle:
    1. Zapisuje dane do bazy
    2. Wysyła powiadomienie
    3. Aktualizuje status powiadomienia
    """
    # Zapisz dane formularza do bazy
    submission = FormSubmission(
        form_id=form_id,
        form_name=form_name,
        form_data=form_data
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Wyślij powiadomienie
    subject = f"Nowe zgłoszenie z formularza: {form_name}"
    notification_result = await send_notification_email(subject, form_data)
    
    # Zapisz informacje o powiadomieniu
    notification = Notification(
        submission_id=submission.id,
        recipient=notification_result.get("webhook_url", "Discord webhook"),
        subject=subject,
        message=str(form_data),
        status=notification_result.get("status", "unknown"),
        error_message=notification_result.get("error")
    )
    db.add(notification)
    
    # Aktualizuj status powiadomienia w zgłoszeniu
    if notification_result.get("status") == "sent":
        submission.notified = True
        submission.notification_sent_at = datetime.utcnow()
    
    db.commit()

@router.post("/webhook")
async def webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Endpoint webhook do przyjmowania danych z formularzy.
    Dane są zapisywane do bazy i wysyłane jest powiadomienie.
    """
    try:
        # Pobierz dane JSON z żądania
        form_data = await request.json()
        
        # Pobierz informacje o formularzu z nagłówków lub domyślne wartości
        form_id = request.headers.get("X-Form-ID", "unknown")
        form_name = request.headers.get("X-Form-Name", "Formularz online")
        
        # Dodaj zadanie przetwarzania w tle
        background_tasks.add_task(
            process_form_submission,
            form_id=form_id,
            form_name=form_name,
            form_data=form_data,
            db=db
        )
        
        logger.info(f"Przyjęto dane z formularza {form_id}: {form_name}")
        return {
            "status": "success",
            "message": "Dane formularza zostały przyjęte i są przetwarzane."
        }
        
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Wystąpił błąd podczas przetwarzania danych: {str(e)}"
        )

@router.get("/webhook/test")
async def webhook_test(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Endpoint testowy do sprawdzenia działania webhook'a.
    """
    # Przykładowe dane testowe
    test_data = {
        "imie": "Jan",
        "nazwisko": "Kowalski",
        "email": "jan.kowalski@example.com",
        "telefon": "123456789",
        "wiadomosc": "To jest testowa wiadomość z formularza."
    }
    
    # Przetwórz dane testowe
    background_tasks.add_task(
        process_form_submission,
        form_id="test-form",
        form_name="Formularz testowy",
        form_data=test_data,
        db=db
    )
    
    return {
        "status": "success",
        "message": "Test webhook wykonany. Sprawdź powiadomienia i bazę danych.",
        "test_data": test_data
    } 