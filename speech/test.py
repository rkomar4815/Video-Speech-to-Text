import speech
from multiprocessing.dummy import Pool as ThreadPool
from timeit import default_timer as timer


urls = ['https://www.youtube.com/watch?v=Eyvw3fVWMk8',
        'https://www.youtube.com/watch?v=RQIG7XYqkK8',
        'https://www.youtube.com/watch?v=YAF9BWpzwvI']


def thread_downloader(urls):

    pool = ThreadPool(4)

    results = pool.map(speech.main, urls)

    pool.close()
    pool.join()

    print(results)


def normal_downloader(urls):

    for i in urls:
        speech.main(i)


if __name__ == "__main__":

    start = timer()

    thread_downloader(urls)

    end = timer()
    print(end - start)

    start = timer()

    normal_downloader(urls)

    end = timer()
    print(end - start)
