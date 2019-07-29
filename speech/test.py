import speech
from multiprocessing.dummy import Pool as ThreadPool


urls = ['https://www.youtube.com/watch?v=Eyvw3fVWMk8',
        'https://www.youtube.com/watch?v=RQIG7XYqkK8']


def thread_downloader(urls):

    pool = ThreadPool(4)

    URIs = pool.map(speech.main, urls)

    pool.close()
    pool.join()

    results = zip(urls, URIs)

    return results


if __name__ == "__main__":

    thread_downloader(urls)
