from __future__ import unicode_literals
from google.cloud import storage
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types
from google.protobuf.json_format import MessageToDict
import youtube_dl
import config
import os
import ffmpeg
import pandas as pd





class transcript:

    def ___init___(url, speakernum):
        self.url = url
        self.speakernum = speakernum

class youtube



def my_hook(d):  # changes filename string from .webm to .flac
    if d['status'] == 'finished':
        filename = str(d['filename'])
        if '.webm' in str(filename):
            config.outputfilename = str(filename).replace('.webm', '.flac')
        elif '.m4a' in str(filename):
            config.outputfilename = str(filename).replace('.m4a', '.flac')
        else:
            print('Filename conversion error.')


def yt_downloader(URL):
    ydl_opts = {
        'format': 'bestaudio/best',
        'restrictfilenames': 'true',
        'forcefilename': 'true',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'flac',  # AI needs FLAC
            'preferredquality': '0'
            }],
        'progress_hooks': [my_hook]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([URL])

#  Converts flac file from stereo to mono


def stereo_to_mono(outputfilename):
    newfilename = str(outputfilename).replace(
        '.flac', '_mono.flac')
    ffmpeg.input(outputfilename).output(newfilename, ac=1).run()
    os.remove(outputfilename)
    return newfilename

#  The section below uses PyDub to remove silent chunks from the .mp3 file
#  Note that this only removes silent chunks from the start and end of the .mp3


def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10000):
    trim_ms = 0  # ms
    assert chunk_size > 0  # to avoid infinite loops
    while sound[
                trim_ms:trim_ms+chunk_size
                ].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size
    return trim_ms


def silence_trim(outputfilename):
    sound = AudioSegment.from_file(str(outputfilename), format='flac')
    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())
    duration = len(sound)
    trimmed_sound = sound[start_trim:duration-end_trim]
    trimmed_sound.export(
        str(outputfilename), format='flac'
        )
    return outputfilename


#  The section below uploads the audio file to Google Cloud

def gcloud_uploader(gcred, project, bucketname, outputfilename):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcred

    storage_client = storage.Client(project=project)

    bucket = storage_client.get_bucket(bucketname)  # your bucket name

    blob = bucket.blob(outputfilename)  # your blob name
    blob.upload_from_filename(outputfilename)

    gcs_uri = os.path.join('gs://', bucketname, outputfilename)

    return gcs_uri


#  AI Speech to text


def videotranscribe(gcs_uri, speakercount):

    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        language_code='en-US',
        enable_speaker_diarization=True,
        diarization_speaker_count=speakercount,
        enable_word_time_offsets=True,
        model='video',
        enable_automatic_punctuation=True
        )

    operation = client.long_running_recognize(config, audio)

    response = operation.result(timeout=30000)

    words = MessageToDict(response)

    words = words.get('results')
    words = words.pop()
    words = words.get('alternatives')
    words = words.pop()
    words = words.get('words')

    return words


def transcript_maker(words):
    words_df = pd.DataFrame(words)

    if 'speakerTag' in words_df:

        words_df['current_speaker'] = (
            words_df.speakerTag.shift() != words_df.speakerTag).cumsum()

        transcript_df = words_df.groupby('current_speaker').agg({
            'startTime': min,
            'speakerTag': min,
            'word': lambda x: ' '.join(x),
            'endTime': max
        }).rename(columns={'word': 'transcript'})

        transcript_df[['speakerTag', 'transcript']].to_json(orient='records')

        pd.set_option('display.max_colwidth', -1)

        print(transcript_df)

        transcriptfile = open('transcript.txt', 'a')
        transcriptfile.write(transcript_df.to_string(
            index=False,
            columns=['startTime', 'speakerTag', 'transcript'],
            header=False, formatters=(
                {'startTime': '\n StartTime: {:} \n'.format,
                    'speakerTag': '\n Speaker {:}: \n'.format,
                    'transcript': '\n {:} \n'.format})))
        transcriptfile.close()

    else:

        transcript_df = words_df.agg({
            'startTime': min,
            'word': lambda x: ' '.join(x),
            'endTime': max
        }).rename(columns={'word': 'transcript'})

        transcript_df[['transcript']].to_json(orient='records')

        pd.set_option('display.max_colwidth', -1)

        print(transcript_df)

        transcriptfile = open('transcript.txt', 'a')
        transcriptfile.write(transcript_df.to_string(
            index=False,
            columns=['startTime', 'transcript'],
            header=False, formatters=(
                {'startTime': '\n StartTime: {:} \n'.format,
                    'transcript': '\n {:} \n'.format})))
        transcriptfile.close()

        

#  Removes flac files from your local drive

def file_remover(outputfilename):
    os.remove(outputfilename)


#  Deletes blob from Google Cloud

def delete_blob(gcred, project, bucket, outputfilename):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcred

    storage_client = storage.Client(project=project)
    bucket = storage_client.get_bucket(bucket)  # your bucket name
    blob = bucket.blob(outputfilename)

    blob.delete()


if __name__ == "__main__":

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config.gcred

    config.words = no_diarize_videotranscribe('gs://hearingtotext/I_m_so_angry_about_this_-_Authoritarian_visits_Trump_in_the_White_House_Pod_Save_the_World-BmwINhnxgb8_mono.flac')

    print(config.words)
