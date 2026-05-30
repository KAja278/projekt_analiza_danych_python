import csv
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# dodałam duration i category)id - czas trwania oraz jakiej kategori według yt jest to filmik

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("Brak klucza API w pliku .env! Sprawdź konfigurację.")

youtube = build("youtube", "v3", developerKey=API_KEY)

kanaly = {
    "KanalZero": "UClhEl4bMD8_escGCCTmRAYg",
    "ORB": "UCW5bKAEBFWz1yHKUEw3VLFg",
    "Konopskyy": "UCR7uLtPuXsDpN8N6ocFQyeg"
}

def load_existing_csv(filename):
    rows = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    return rows

def fetch_missing_details(video_ids):
    details_map = {}
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails",
            id=",".join(video_ids[i:i+50])
        )
        response = request.execute()
        for item in response.get("items", []):
            v_id = item["id"]
            snippet = item.get("snippet", {})
            content_details = item.get("contentDetails", {})
            
            details_map[v_id] = {
                "duration": content_details.get("duration", ""),
                "category_id": snippet.get("categoryId", "")
            }
    return details_map

def save_updated_csv(rows, filename):
    fieldnames = [
        "video_id", "channel_name", "title", "published_at", 
        "view_count", "like_count", "comment_count", 
        "duration", "category_id"
    ]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            filtered_row = {k: row.get(k, "") for k in fieldnames}
            writer.writerow(filtered_row)

def main():
    for channel_name in kanaly.keys():
        filename = f"data/raw/{channel_name}_videos_info.csv"
        
        if not os.path.exists(filename):
            print(f"Plik dla kanału {channel_name} nie istnieje w data/raw/.")
            continue
            
        print(f"Aktualizacja danych dla kanału: {channel_name}...")
        existing_rows = load_existing_csv(filename)
        
        videos_to_update = [
            row["video_id"] for row in existing_rows 
            if "duration" not in row or "category_id" not in row or not row["duration"]
        ]
        
        if not videos_to_update:
            print(f"Wszystkie filmy w pliku {channel_name} posiadają już komplet danych.")
            continue
            
        print(f"Znaleziono {len(videos_to_update)} filmów wymagających uzupełnienia danych. Pobieranie z API...")
        missing_data_map = fetch_missing_details(videos_to_update)
        
        for row in existing_rows:
            v_id = row["video_id"]
            if v_id in missing_data_map:
                row["duration"] = missing_data_map[v_id]["duration"]
                row["category_id"] = missing_data_map[v_id]["category_id"]
            else:
                row.setdefault("duration", "")
                row.setdefault("category_id", "")
                
        save_updated_csv(existing_rows, filename)
        print(f"Zakończono aktualizację pliku: {filename}")

if __name__ == "__main__":
    main()