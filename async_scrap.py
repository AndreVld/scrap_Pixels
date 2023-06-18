import os
import asyncio
from aiohttp import ClientSession
from asyncio import Queue
import math
from timer import async_timed


@async_timed
async def download_file(session: ClientSession, queue: Queue, dir_name: str):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    while not queue.empty():
        data_file = queue.get_nowait()
        url = data_file[1]
        file_name =  f"{data_file[0].replace(' ', '_')}_{url.split('-')[-1]}"

        async with session.get(url) as response:
            with open(f'./{dir_name}/{file_name}', 'wb') as file:
                async for chunk in response.content.iter_chunked(1024):
                    file.write(chunk)

        queue.task_done()

@async_timed
async def add_urls(session: ClientSession, queue: Queue, total_pages: int, query: str):

    for page in range(2, total_pages):
        query = f'{query}&page={page}'

        async with session.get(query) as response:
            json_data = await response.json()
            photos = json_data.get('photos')
            for photo in photos:
                url = photo.get('src').get('original')
                file_name= photo.get('alt')
                await queue.put((file_name, url))


@async_timed
async def main():
    query = input('Enter a keyword to search : ')
    query = '_'.join(s for s in query.split(' ') if s.isalnum())

    if query:
        headers = {'Authorization': f'{os.getenv("PIXELS_API_KEY")}'}
        # The number of results you are requesting per page. Default: 15 Max: 80
        per_page = 80
        count_downloader = math.ceil(per_page / 4)

        query_str = f'https://api.pexels.com/v1/search?query={query}&per_page={per_page}'

        urls_queue = Queue(maxsize=per_page)

        async with ClientSession(headers=headers) as session:
            async with session.get(query_str) as response:
                json_data = await response.json()

            total_results = json_data.get('total_results')
            print(f'The total number of images - {total_results}')

            photos = json_data.get('photos')
            [urls_queue.put_nowait((photo.get('alt'), photo.get('src').get('original'))) for photo in photos]

            tasks = [asyncio.create_task(download_file(session, urls_queue, query)) for _ in range(count_downloader)]

            if json_data.get('next_page'):
                pages = math.ceil(total_results / per_page) + 1
                queue_task = asyncio.create_task(add_urls(session, urls_queue, pages, query_str))
                tasks.append(queue_task)

            await asyncio.gather(urls_queue.join(), *tasks)


if __name__ == '__main__':
    asyncio.run(main())

