import csv
import glob
import os
import re

def calculate_clickbait_score(title, views, likes):
    score = 0
    title_upper = title.upper()

    # 1. FORMATOWANIE I KRZYK (Max 5 pkt)
    if title.endswith("?"):
        score += 1
    if "!" in title:
        score += 1

    # Analiza Caps Locka (min. 2 litery, odrzucamy skróty typu USA, PiS, PO, TVN, ORB)
    clean_title = re.sub(r'\b(USA|PIS|PO|TVN|ORB|NBP|UE|UK|KO|FAME|MMA|VIP)\b', '', title)
    words = re.findall(r"\b[A-ZŚĆŹŻÓŁĘĄŃ]{2,}\b", clean_title)
    if words:
        total_words = len(re.findall(r"\b\w+\b", clean_title))
        if total_words > 0 and (len(words) / total_words) > 0.6:
            score += 2  # Drastyczny krzyk (większość tytułu)
        else:
            score += 1  # Pojedyncze słowa-wykrzykniki

    # 2. LICZBY, CZAS I SEKCJA SEO (Max 5 pkt)
    if re.search(r"\b\d{4,}\b", title) or "ZŁ" in title_upper:
        score += 1  # Epatowanie kwotami/rokiem katastrofy
    if any(x in title_upper for x in ["MINUT", "GODZIN", "DNI", "TYDZIEŃ", "MIESIĄC"]):
        score += 1  # Presja czasu
    if "(" in title and ")" in title:
        score += 2  # "Nawias SEO" - upychanie nazwisk pod wyszukiwarkę (znak rozpoznawczy Konopskiego)
    if "WSZYSTKO" in title_upper or "CAŁY" in title_upper:
        score += 1

    # 3. PROFILOWANE SŁOWA KLUCZOWE (Max 10 pkt)
    # Profil A: Sensacja YT / Commentary (Typowy Konopskyy)
    sensacja_yt = ["AFERA", "SKANDAL", "DOWODY", "KŁAMSTWO", "OSZUSTWO", "PRAWDA O", "PORAŻAJĄCE", "SHOCKS", "WORLD", "KATASTROFA"]
    # Profil B: Dramaturgia Publicystyczna / Polityczna (Kanał Zero / ORB)
    publicystyka = ["WOJNA", "KONIEC", "UPADNIE", "UPADEK", "ZAGROŻENIE", "SOUSZ", "ZDRADA", "SPISEK", "ODCHODZI", "PILNE", "ROZPAD"]
    # Profil C: Wyolbrzymianie / Atak / Memy
    agresja_memy = ["DOJEŻDŻA", "ZAORAŁ", "MOCNE", "HIT", "ZEMSTA", "NIGDY", "XD", "DYMY", "GRILLOWANIE", "MASAKRA"]

    if any(w in title_upper for w in sensacja_yt):
        score += 3  # Wyższa waga za typowo plotkarski/dramowy clickbait
    if any(w in title_upper for w in publicystyka):
        score += 2  # Średnia waga za pompę polityczną/newsową
    if any(w in title_upper for w in agresja_memy):
        score += 2  # Waga za zwroty nacechowane emocjonalnie/memicznie

    # 4. OBLICZANIE WSKAŹNIKA AKTYWNOŚCI
    try:
        views = int(views)
        likes = int(likes)
    except ValueError:
        views, likes = 0, 0

    if views > 0:
        engagement_rate = round((likes / views) * 100, 2)
    else:
        engagement_rate = 0.0

    # 5. INTERPRETACJA WYNIKÓW
    if score <= 2:
        level = "1. Rzetelny / Neutralny"
    elif score <= 5:
        level = "2. Lekki marketing newsowy"
    elif score <= 9:
        level = "3. Wysoka manipulacja algorytmiczna"
    else:
        level = "4. Skrajny clickbait sensacyjny"

    return score, level, engagement_rate

def main():
    raw_data_path = os.path.join("data", "raw", "*_videos_info.csv")
    csv_files = glob.glob(raw_data_path)

    if not csv_files:
        print("Błąd: Nie znaleziono plików CSV w katalogu data/raw/. Uruchom najpierw src/scraper.py")
        return

    os.makedirs("data/processed", exist_ok=True)
    all_analyzed_rows = []

    for file_path in csv_files:
        print(f"Analiza pliku: {file_path}...")
        channel_analyzed_rows = []
        base_name = os.path.basename(file_path)
        
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("title", "")
                views = row.get("view_count", 0)
                likes = row.get("like_count", 0)

                score, level, eng_rate = calculate_clickbait_score(title, views, likes)

                row["clickbait_score"] = score
                row["clickbait_level"] = level
                row["engagement_rate_%"] = eng_rate

                channel_analyzed_rows.append(row)
                all_analyzed_rows.append(row)
        
        if channel_analyzed_rows:
            channel_output_filename = os.path.join("data", "processed", f"processed_{base_name}")
            with open(channel_output_filename, "w", newline="", encoding="utf-8-sig") as f:
                fieldnames = list(channel_analyzed_rows[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in channel_analyzed_rows:
                    writer.writerow(row)
            print(f"-> Zapisano raport indywidualny: {channel_output_filename}")

    if all_analyzed_rows:
        total_output_filename = os.path.join("data", "processed", "ZBIORCZY_raport_clickbaitu.csv")
        with open(total_output_filename, "w", newline="", encoding="utf-8-sig") as f:
            fieldnames = list(all_analyzed_rows[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in all_analyzed_rows:
                writer.writerow(row)
        
        print("-" * 50)
        print(f"Analiza zakończona! Przetworzono łącznie {len(all_analyzed_rows)} filmów.")
        print(f"Gotowy raport zbiorczy znajdziesz w: {total_output_filename}")

if __name__ == "__main__":
    main()