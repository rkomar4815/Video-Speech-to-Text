import speech
import concurrent.futures


def thread_downloader(urls):

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL

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

    test = thread_downloader(URLS)

    print(test)
