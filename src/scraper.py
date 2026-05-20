import csv
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

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

def get_channel_vid(channel_id):
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]    

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

def get_video_inf(video_id, channel_n):
    rows = []
    for i in range(0, len(video_id), 50):
        request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_id[i:i+50])
        )
        response = request.execute()
        for item in response["items"]:
            row = {
                "video_id": item["id"],
                "channel_name": channel_n,
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
                "view_count": item["statistics"].get("viewCount", 0),
                "like_count": item["statistics"].get("likeCount", 0),
                "comment_count": item["statistics"].get("commentCount", 0)
            }
            rows.append(row)
    return rows 

def save_to_csv(rows, filename):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["video_id", "channel_name", "title", "published_at", "view_count", "like_count", "comment_count"]
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
    all_inf = []
    
    os.makedirs("data/raw", exist_ok=True)

    for channel_name, channel_id in kanaly.items():
        filename = f"data/raw/{channel_name}_videos_info.csv"
        
        if os.path.exists(filename):
            print(f"Plik dla kanału {channel_name} już istnieje ({filename}). Pomijam pobieranie.")
            continue
            
        print(f"Pobieranie danych dla kanału: {channel_name}...")
        uploads_list_id = get_channel_vid(channel_id)
        video_ids = get_videos_id(uploads_list_id)
        videos_info = get_video_inf(video_ids, channel_name)
        
        save_to_csv(videos_info, filename)
        all_inf.extend(videos_info)

    print("Zakończono sprawdzanie i pobieranie danych w folderze data/raw/.")

if __name__ == "__main__":
    main()