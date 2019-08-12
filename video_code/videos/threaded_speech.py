import speech
import concurrent.futures


'''
Multithreaded version of speech.main with 5 workers and no diarization

Returns a dict of Youtube URLs and GCP URIs for the according transcript
'''


def speech_daemon(urls):

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start daemons and mark each URL with its future GCP URI

        data = {}

        URI_to_URL = {executor.submit(
            speech.main, url, 1): url for url in urls}

        for future in concurrent.futures.as_completed(URI_to_URL):

            url = URI_to_URL[future]

            try:
                uri = future.result()

                data.update({url: uri})  # adds url and GCP uri pair to dict

            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))

        return data


if __name__ == "__main__":

    URLS = ['https://www.youtube.com/watch?v=4ZLndu5pUuQ',
            'https://www.youtube.com/watch?v=CFZETWI6cno',
            'https://www.youtube.com/watch?v=ut9-xKN0ZXE']

    test = speech_daemon(URLS)

    print(test)
