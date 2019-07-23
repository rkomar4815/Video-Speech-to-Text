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

'''
This module converts any youtube or soundcloud video/audio file into a text file transcript with unique speakers identified.

The GCP Speech to Text AI used in this module is diarization enabled meaning it will identify unique speakers in audio.
However, GCP's diarized Speech to Text AI is in beta, so there may be some bugs when long videos are analyzed.
'''


def main(url, speakernum):

    yt_downloader(url)

    config.filename = stereo_to_mono(config.filename)

    config.gcs_uri = gcloud_uploader(
        config.gcred, config.project,
        config.bucket, config.filename
    )

    os.remove(config.filename)

    config.words = videotranscribe(config.gcs_uri, speakernum)

    words = videotranscribe(config.gcs_uri, speakernum)

    _transcript_maker(words, config.filename)

    delete_blob(
        config.gcred, config.project,
        config.bucket, config.filename
    )


# Hooks for Youtube-dl
# Youtube videos are either downloaded as .webm files or .m4a files

def _my_hook(d):  # changes filename string from .webm to .flac
    if d['status'] == 'finished':
        filename = str(d['filename'])
        if '.webm' in str(filename):
            config.filename = str(filename).replace('.webm', '.flac')
        elif '.m4a' in str(filename):
            config.filename = str(filename).replace('.m4a', '.flac')
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
        'progress_hooks': [_my_hook]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([URL])

#  Converts flac file from stereo to mono
#  Google Cloud Speech to Text AI only works with mono audio
#  This returns the updated filename after the FLAC file is converted to mono


def stereo_to_mono(filename):
    newfilename = str(filename).replace(
        '.flac', '_mono.flac'
    )

    ffmpeg.input(filename).output(newfilename, ac=1).run()

    os.remove(filename)

    return newfilename

#  The function below uses PyDub to remove silent chunks from the audio file
#  Note that this only removes silent chunks from the start and end of audio file


def silence_trim(outputfilename):
    sound = AudioSegment.from_file(str(outputfilename), format='flac')
    start_trim = _detect_leading_silence(sound)
    end_trim = _detect_leading_silence(sound.reverse())
    duration = len(sound)
    trimmed_sound = sound[start_trim:duration-end_trim]
    trimmed_sound.export(
        str(outputfilename), format='flac'
    )

    return outputfilename


def _detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10000):
    trim_ms = 0  # ms
    assert chunk_size > 0  # to avoid infinite loops
    while sound[
        trim_ms:trim_ms+chunk_size
    ].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


#  Uploads files to Google Cloud blob storage

def gcloud_uploader(gcred, project, bucketname, outputfilename):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcred

    storage_client = storage.Client(project=project)

    bucket = storage_client.get_bucket(bucketname)  # your bucket name

    blob = bucket.blob(outputfilename)  # your blob name
    blob.upload_from_filename(outputfilename)

    gcs_uri = os.path.join('gs://', bucketname, outputfilename)

    return gcs_uri


#  Transcribes an audio file based on a passed through speakercount and GCS URI


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


def _transcript_maker(words, filename):
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

        textfilename = filename.replace('_mono.flac', '.txt')

        transcriptfile = open(textfilename, 'a')

        transcriptfile.write(transcript_df.to_string(
            index=False,
            columns=['startTime', 'speakerTag', 'transcript'],
            header=False, formatters=(
                {'startTime': '\n StartTime: {:} \n'.format,
                    'speakerTag': '\n Speaker {:}: \n'.format,
                    'transcript': '\n {:} \n'.format})))

        transcriptfile.close()


#  Deletes a file in Google Cloud blob storage

def delete_blob(gcred, project, bucket, outputfilename):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcred

    storage_client = storage.Client(project=project)
    bucket = storage_client.get_bucket(bucket)  # your bucket name
    blob = bucket.blob(outputfilename)

    blob.delete()


if __name__ == "__main__":

    main()
