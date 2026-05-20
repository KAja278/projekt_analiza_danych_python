# Analiza Clickbaitu na Polskim YouTube

Projekt bada i porównuje stopień manipulacji w tytułach filmów (Kanał Zero, ORB, Konopskyy) przy użyciu **YouTube Data API v3**.

---

## Skala Punktacji (0-22 pkt)
*   **0 – 2 pkt:** 1. Rzetelny / Neutralny
*   **3 – 5 pkt:** 2. Lekki marketing newsowy
*   **6 – 9 pkt:** 3. Wysoka manipulacja algorytmiczna
*   **10+ pkt:**  4. Skrajny clickbait sensacyjny

Algorytm premiuje: CAPS LOCK, pytajniki, wykrzykniki, presję czasu, nawiasy SEO oraz słowa-triggery (*AFERA, SKANDAL, WOJNA, PILNE*). Oblicza też stosunek lajków do wyświetleń (`engagement_rate_%`).

---

## Struktura i uruchomienie

1. **Instalacja bibliotek:**
   ```bash
   pip install -r requirements.txt

2. **Uruchomienie potoku danych:**
   ```bash
   python src/scraper.py     # Pobieranie -> data/raw/ -> JAK NIE ZMIENIAMY KANALOW TO NIE URUCHAMIAC BO JEST LIMIT NA KLUCZ KAJI
   python src/analyzer.py    # Analiza -> data/processed/
   python src/visualizer.py  # Wykresy -> plots/