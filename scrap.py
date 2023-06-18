import requests
from time import time
import os
import math


def timed(func):
    def wrapper(*args, **kwargs):
        start = time()
        try:
            return func(*args, **kwargs)
        finally:
            total = time() - start
            print(f'"{func.__name__}" completed in {total:.2f} seconds')
    return wrapper


def download_file(urls: list, dir_name: str):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    for url in urls:
        response = requests.get(url)
        assert response.status_code == 200

        file_name = url.split('-')[-1]
        with open(f'./{dir_name}/{file_name}', 'wb') as file:
            file.write(response.content)

@timed
def scrap_pixels(query: str):
    headers = {'Authorization': f'{os.getenv("PIXELS_API_KEY")}'}

    # The number of results you are requesting per page. Default: 15 Max: 80
    per_page = 80
    query_str = f'https://api.pexels.com/v1/search?query={query}&per_page={per_page}'

    resp = requests.get(headers=headers, url=query_str)
    assert resp.status_code == 200

    json_data = resp.json()
    total_results = json_data.get('total_results')

    print(f'The total number of images - {total_results}')

    urls_photos = [url.get('src').get('original') for url in json_data.get('photos')]

    if json_data.get('next_page'):
        for page in range(2, math.ceil(total_results / per_page)+1):
            resonse = requests.get(f'{query_str}&page={page}', headers=headers)
            assert resonse.status_code == 200
            data = resonse.json()
            urls_photos.extend([url.get('src').get('original') for url in data.get('photos')])

    download_file(urls_photos, query)


@timed
def main():
    query = input('Enter a keyword to search : ')
    query = '_'.join(s for s in query.split(' ') if s.isalnum())
    if query:
        scrap_pixels(query)
    

if __name__ == '__main__':
    main()
