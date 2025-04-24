import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe, jeśli jeszcze nie załadowane
load_dotenv()

# Pobierz adres URL bazy danych z zmiennych środowiskowych lub użyj domyślnego
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Dla SQLite dodaj check_same_thread=False
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# Utwórz fabrykę sesji
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baza dla modeli deklaratywnych
Base = declarative_base() 