# Analiza wybranego kanału na YouTube

## Struktura i uruchomienie

1. **Instalacja bibliotek:**
   ```bash
   pip install -r requirements.txt

2. **Uruchomienie potoku danych:**
   ```bash
   python src/scraper.py  # Scraper do pobierania danych
   python src/analyzer_token.py    # Wyliczenie metryk (clickbait score / engagement rate)
   ```
   Wizualizacja i szczegółowa analiza danych znajdują się w pliku:

   notebooks/analiza_wybranego_kanalu.ipynb
