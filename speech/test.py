import speech
import concurrent.futures

def thread_downloader(urls):

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        URI_to_URL = {executor.submit(
            speech.main, url, 1): url for url in URLS}

        for future in concurrent.futures.as_completed(URI_to_URL):

            url = URI_to_URL[future]
            print(url)

            try:
                data = future.result()
                print(data)

            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))

        return data


if __name__ == "__main__":

    test = thread_downloader(URLS)

    print(test)
