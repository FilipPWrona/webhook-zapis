from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import logging
from typing import List, Optional
from datetime import datetime

from app.database.session import SessionLocal
from app.models.models import FormSubmission, Notification

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])

# Szablony
templates = Jinja2Templates(directory="app/templates")

# Zależność dla sesji bazy danych
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Panel administracyjny z listą zgłoszeń formularzy.
    """
    submissions = db.query(FormSubmission).order_by(FormSubmission.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "submissions": submissions,
            "title": "Panel administratora"
        }
    )

@router.get("/submissions/{submission_id}", response_class=HTMLResponse)
async def submission_details(
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Szczegóły zgłoszenia formularza.
    """
    submission = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Zgłoszenie nie zostało znalezione")
    
    notifications = db.query(Notification).filter(
        Notification.submission_id == submission_id
    ).order_by(Notification.created_at.desc()).all()
    
    return templates.TemplateResponse(
        "admin/submission_details.html",
        {
            "request": request,
            "submission": submission,
            "notifications": notifications,
            "title": f"Szczegóły zgłoszenia #{submission.id}"
        }
    )

@router.post("/submissions/{submission_id}/delete")
async def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db)
):
    """
    Usuwa zgłoszenie formularza i powiązane powiadomienia.
    """
    submission = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Zgłoszenie nie zostało znalezione")
    
    # Usuń powiązane powiadomienia
    db.query(Notification).filter(Notification.submission_id == submission_id).delete()
    
    # Usuń zgłoszenie
    db.delete(submission)
    db.commit()
    
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/notifications", response_class=HTMLResponse)
async def notifications_list(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Lista wszystkich powiadomień.
    """
    notifications = db.query(Notification).order_by(Notification.created_at.desc()).all()
    
    return templates.TemplateResponse(
        "admin/notifications.html",
        {
            "request": request,
            "notifications": notifications,
            "title": "Lista powiadomień"
        }
    )

@router.get("/api/submissions", response_model=List[dict])
async def api_submissions(db: Session = Depends(get_db)):
    """
    API do pobierania listy zgłoszeń w formacie JSON.
    """
    submissions = db.query(FormSubmission).order_by(FormSubmission.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "created_at": s.created_at.isoformat(),
            "form_id": s.form_id,
            "form_name": s.form_name,
            "form_data": s.form_data,
            "notified": s.notified,
            "notification_sent_at": s.notification_sent_at.isoformat() if s.notification_sent_at else None
        }
        for s in submissions
    ] 