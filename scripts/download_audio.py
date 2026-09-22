import yt_dlp
import os

def download_audio(youtube_url, output_folder="data"):
    # yt-dlp options: we want audio only, converted to WAV, 16kHz mono
    ydl_opts = {
        'format': 'bestaudio/best',          # grab the best available audio track
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',  # where/how to name the file
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',     # tells yt-dlp to use ffmpeg after download
            'preferredcodec': 'wav',         # convert to WAV format
        }],
        'postprocessor_args': [
            '-ar', '16000',                  # set sample rate to 16kHz
            '-ac', '1',                      # set to 1 channel (mono)
        ],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

if __name__ == "__main__":
    url = input("Paste a YouTube URL: ")
    download_audio(url)
    print("Done! Check your data/ folder.")