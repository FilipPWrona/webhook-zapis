# Webhook z Formularza Online - Zapis do Bazy i Powiadomienie

Automatyzacja odbierająca dane z formularza online, zapisująca je do bazy danych i wysyłająca powiadomienia na Discord.

## Funkcje

- Odbieranie danych z formularza Google Sheets poprzez webhook
- Zapis danych do bazy SQLite
- Wysyłanie powiadomień na Discord
- Prosty panel administratora

## Wymagania

- Python 3.8+
- Pakiety z `requirements.txt`
- Dostęp do Google Sheets API (opcjonalnie)
- Webhook URL z serwera Discord

## Instalacja

1. Klonuj repozytorium
2. Zainstaluj zależności: `pip install -r requirements.txt`
3. Skopiuj `.env.example` do `.env` i uzupełnij dane konfiguracyjne
4. Uruchom aplikację: `python -m uvicorn app.main:app --reload`

## Konfiguracja Discord

1. Otwórz Discord i przejdź do serwera, gdzie chcesz otrzymywać powiadomienia
2. Kliknij prawym przyciskiem myszy na wybrany kanał → Edytuj kanał → Integracje → Webhook
3. Kliknij "Nowy webhook" → ustaw nazwę i awatar → "Kopiuj adres URL webhooks"
4. Wklej skopiowany URL do pliku .env jako DISCORD_WEBHOOK_URL

## Konfiguracja Google Sheets (opcjonalnie)

1. Utwórz projekt w Google Cloud Console
2. Włącz Google Sheets API
3. Utwórz poświadczenia i pobierz plik credentials.json
4. Umieść plik credentials.json w katalogu głównym projektu

## Struktura projektu

- `app/` - Główny katalog aplikacji
  - `main.py` - Punkt wejściowy aplikacji
  - `models/` - Modele danych
  - `database/` - Konfiguracja bazy danych
  - `services/` - Usługi aplikacji
  - `api/` - Endpointy API
  - `templates/` - Szablony HTML
  - `static/` - Pliki statyczne
- `.env` - Zmienne środowiskowe
- `requirements.txt` - Zależności projektu 