#projekt analiza danych w Pythonie- web scraping 
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import csv
import os

API_KEY = "AIzaSyACS_VxoOuQPG2WYwg27CTkrlQ11EcCQDo"

youtube = build("youtube", "v3", developerKey=API_KEY)

kanaly={
    "KanalZeroPL":"UClhEl4bMD8_escGCCTmRAYg",
    "ImponderabiliaTV": "UCoXxgqIOTa8qCM7Hd7RiURw"
}

def get_channel_vid(channel_id):
    
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()

        
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]    
def get_videos_id(list_id):
    video_ids=[]
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

def get_video_inf(video_id,channel_n):
    rows=[]
    for i in range(0,len(video_id),50):
        request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_id[i:i+50])
        )
        response = request.execute()
        for item in response["items"]:
            row={
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



def save_to_csv(rows, filename="yt_kanaly_inf.csv"):

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["video_id","channel_name","title","published_at","view_count","like_count","comment_count"]
        )
        writer.writeheader()

        for row in rows:
            writer.writerow(row)



def main():

    all_inf = []

    for channel_name,channel_id in kanaly.items():
        uploads_list_id = get_channel_vid(channel_id)
        video_ids = get_videos_id(uploads_list_id)
        videos_info = get_video_inf(video_ids, channel_name)
        all_inf.extend(videos_info)

    print("Pobrano:", len(all_inf))

    save_to_csv(all_inf)


if __name__ == "__main__":
    main()