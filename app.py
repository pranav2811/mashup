from flask import Flask, render_template, request, redirect, url_for, flash
from youtube_search import YoutubeSearch
from pytube import YouTube
from moviepy.editor import AudioFileClip, concatenate_audioclips
from flask_mail import Mail, Message
import os

app = Flask(__name__)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'powar.pranav29@gmail.com'
app.config['MAIL_PASSWORD'] = 'xjgv elfe dsen uxgx'
app.config['MAIL_DEFAULT_SENDER'] = 'powar.pranav29@gmail.com'

mail = Mail(app)

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

def send_email(receiver_email, output_file):
    msg = Message(subject='Merged Audio File',
                  recipients=[receiver_email],
                  body='Please find the merged audio file attached.')
    with app.open_resource(output_file) as fp:
        msg.attach(output_file, 'audio/mp3', fp.read())
    mail.send(msg)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        singer_name = request.form['singer_name']
        num_videos = int(request.form['num_videos'])
        duration_per_video = float(request.form['duration_per_video'])
        receiver_email = request.form['email']

        download_videos(singer_name, num_videos)
        convert_to_audio(num_videos)
        cut_audio(num_videos, duration_per_video)
        merge_audios(num_videos, 'merged_audio.mp3')
        send_email(receiver_email, 'merged_audio.mp3')

        flash('Merged audio file has been sent to your email.')
        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
