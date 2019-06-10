from google.cloud import speech_v1p1beta1 as speech
from google.protobuf.json_format import MessageToDict


def videotranscribe(gcs_uri, speakercount):
    client = speech.SpeechClient()
    audio = speech.types.RecognitionAudio(uri=gcs_uri)

    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.FLAC,
        language_code='en-US',
        enable_word_time_offsets=True,
        model='video',
        enable_speaker_diarization=True,
        diarization_speaker_count=speakercount,
        enable_automatic_punctuation=True,
        speech_contexts=[
            speech.types.SpeechContext(
                phrases=["JCPOA", "Mueller", "Ivanka", "emoulments", "foreign policy", "Iran Deal", "TPP"]
            )],
        enable_separate_recognition_per_channel=True,
        metadata={
            "InteractionType": "DISCUSSION",
            "OriginalMediaType": "VIDEO",
            "RecordingDeviceType": "OTHER_INDOOR_DEVICE",

            })

    operation = client.long_running_recognize(config, audio)

    response = operation.result(timeout=30000)
    words = MessageToDict(response)

    print(words)

    words = words.get('results')
    words = words.pop()
    words = words.get('alternatives')
    words = words.pop()
    words = words.get('words')

    return(words)
