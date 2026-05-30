import csv
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
import isodate

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
MAX_WARNING_VIDEOS = 10000
MIN_DURATION_SECONDS = 121
MAX_DURATION_SECONDS= 10800

if not API_KEY:
    raise ValueError("Brak klucza API w pliku .env! Sprawdź konfigurację.")

youtube = build("youtube", "v3", developerKey=API_KEY)

kanaly = {
    "KanalZero": "UClhEl4bMD8_escGCCTmRAYg",
    "ORB": "UCW5bKAEBFWz1yHKUEw3VLFg",
    "Konopskyy": "UCR7uLtPuXsDpN8N6ocFQyeg",
    "Imponderabilia": "UCoXxgqIOTa8qCM7Hd7RiURw"
}

def get_channel_info(channel_id):
    request = youtube.channels().list(
        part="contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()

    item = response["items"][0]

    uploads_playlist_id = item["contentDetails"]["relatedPlaylists"]["uploads"]
    video_count = int(item["statistics"].get("videoCount", 0))

    return uploads_playlist_id, video_count

def get_videos_id(list_id):
    video_ids = []
    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=list_id,
        maxResults=50
    )
    while request:
        response = request.execute()
        for item in response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])
        request = youtube.playlistItems().list_next(request, response)
    return video_ids

def ask_user_confirmation(channel_name, video_count):
    print(f"\nKanał {channel_name} ma około {video_count} filmów.")

    if video_count > MAX_WARNING_VIDEOS:
        print("UWAGA: Ten kanał ma ponad 10 000 filmów.")
        print("Pobieranie wszystkich danych może zająć dużo czasu.")

    answer = input("Czy chcesz pobrać wszystkie dane? [tak/nie]: ").strip().lower()

    if answer not in ["tak", "t", "yes", "y"]:
        print(f"Pomijam kanał: {channel_name}")
        return False

    return True
def get_video_inf(video_id, channel_n):
    rows = []
    for i in range(0, len(video_id), 50):
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_id[i:i+50])
        )
        response = request.execute()
        for item in response["items"]:
            duration_iso = item["contentDetails"]["duration"]
            duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())

            if duration_seconds < MIN_DURATION_SECONDS or duration_seconds > MAX_DURATION_SECONDS:
                continue
            row = {
                "video_id": item["id"],
                "channel_name": channel_n,
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
                "view_count": item["statistics"].get("viewCount", 0),
                "like_count": item["statistics"].get("likeCount", 0),
                "comment_count": item["statistics"].get("commentCount", 0),
                "duration": duration_iso,
                "duration_seconds": duration_seconds,
                "category_id": item["snippet"].get("categoryId", None)
            }
            rows.append(row)
    return rows 

def save_to_csv(rows, filename):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["video_id", "channel_name", "title", "published_at", "view_count", "like_count", "comment_count","duration","duration_seconds","category_id"]
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
    
    os.makedirs("data/raw", exist_ok=True)

    for channel_name, channel_id in kanaly.items():
        filename = f"data/raw/{channel_name}_videos_info.csv"
        
        if os.path.exists(filename):
            print(f"Plik dla kanału {channel_name} już istnieje ({filename}). Pomijam pobieranie.")
            continue
            
        print(f"\nSprawdzanie kanału: {channel_name}...")

        uploads_list_id, video_count = get_channel_info(channel_id)

        if not ask_user_confirmation(channel_name, video_count):
            continue

        print(f"Pobieranie ID filmów dla kanału: {channel_name}...")
        video_ids = get_videos_id(uploads_list_id)

        print(f"Pobieranie danych i filtrowanie Shorts dla kanału: {channel_name}...")
        videos_info = get_video_inf(video_ids, channel_name)

        save_to_csv(videos_info, filename)

        print(f"Zapisano {len(videos_info)} filmów do {filename}")

    print("\nZakończono sprawdzanie i pobieranie danych w folderze data/raw/.")

if __name__ == "__main__":
    main()