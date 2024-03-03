import os
import sys
from youtube_search import YoutubeSearch
from pytube import YouTube
from moviepy.editor import AudioFileClip, concatenate_audioclips

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_videos(artist, num_videos):
    results = YoutubeSearch(artist, max_results=num_videos).to_dict()
    create_directory('downloaded')

    for i in range(min(num_videos, len(results))):
        video_url = "https://www.youtube.com" + results[i]['url_suffix']
        try:
            yt = YouTube(video_url)
            stream = yt.streams.filter(only_audio=True).first()
            stream.download(output_path='downloaded', filename=f'video_{i}.mp4')
        except Exception as e:
            print(f"Error downloading video from {video_url}: {str(e)}")

def convert_to_audio(num_videos):
    create_directory('audios')
    for i in range(num_videos):
        video_path = f'downloaded/video_{i}.mp4'
        audio_path = f'audios/audio_{i}.mp3'
        video_clip = AudioFileClip(video_path)
        video_clip.write_audiofile(audio_path)
        video_clip.close()

def cut_audio(num_videos, cut_duration):
    for i in range(num_videos):
        audio_path = f'audios/audio_{i}.mp3'
        output_path = f'audios/audio_{i}_cut.mp3'
        audio_clip = AudioFileClip(audio_path)
        cut_audio_clip = audio_clip.subclip(cut_duration, None)
        cut_audio_clip.write_audiofile(output_path)
        audio_clip.close()

def merge_audios(num_videos, output_file):
    audio_clips = []
    for i in range(num_videos):
        audio_clip = AudioFileClip(f'audios/audio_{i}_cut.mp3')
        audio_clips.append(audio_clip)

    final_clip = concatenate_audioclips(audio_clips)
    final_clip.write_audiofile(output_file)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    artist = sys.argv[1]
    num_videos = int(sys.argv[2])
    cut_duration = float(sys.argv[3])
    output_file = sys.argv[4]

    download_videos(artist, num_videos)
    convert_to_audio(num_videos)
    cut_audio(num_videos, cut_duration)
    merge_audios(num_videos, output_file)
