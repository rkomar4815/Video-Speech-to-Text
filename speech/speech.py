import speechfuncs
import config


config.URL = 'https://www.youtube.com/watch?v=CFZETWI6cno'

speechfuncs.yt_downloader(config.URL)

config.outputfilename = speechfuncs.stereo_to_mono(config.outputfilename)

silence_bool = 'No'

if silence_bool == 'Yes':
    print('Deleting silent Audio!')
    config.outputfilename = speechfuncs.silence_trim(config.outputfilename)
elif silence_bool != 'Yes':
    pass

config.gcs_uri = speechfuncs.gcloud_uploader(
    config.gcred, config.project,
    config.bucket, config.outputfilename
    )

speechfuncs.file_remover(config.outputfilename)

print('AI is conducting analysis!')
config.words = speechfuncs.videotranscribe(config.gcs_uri, 1)

print(config.words)

speechfuncs.transcript_maker(config.words)

speechfuncs.delete_blob(
    config.gcred, config.project,
    config.bucket, config.outputfilename
    )

print('Blob deleted!')
