import os
import re
import requests
from bs4 import BeautifulSoup

def download_images(search_query, num_images=50, min_width=512, min_height=512, save_folder='downloaded_images'):
    # 이미지 검색어를 Google 이미지 검색 URL로 변환합니다.
    search_query = search_query.replace(' ', '+')
    search_url = f'https://www.google.com/search?q={search_query}&source=lnms&tbm=isch'

    # 이미지를 다운로드할 폴더를 생성합니다.
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # 검색어 리스트를 파일에서 읽어옵니다.
    with open('search_list.txt', 'r') as f:
        search_list = f.readlines()

    for search in search_list:
        # 검색어와 이미지 개수를 구분합니다.
        search, num_images_str = search.strip().split(',')
        num_images = int(num_images_str)

        print(f"Scraping images for '{search}'...")

        # 스크랩할 이미지 수를 페이지 당 100개로 제한합니다. 더 많은 이미지가 필요한 경우 페이지 수를 늘려주세요.
        num_pages = (num_images - 1) // 100 + 1

        for page in range(num_pages):
            # 각 페이지에 대해 이미지 검색을 수행합니다.
            start_index = page * 100
            page_url = f'{search_url}&q={search}&start={start_index}'
            response = requests.get(page_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            images = soup.find_all('img', {'src': re.compile(r'https://.*\.(?:jpg|png|gif)')})

            for i, img_tag in enumerate(images):
                # 이미지의 URL과 크기를 가져옵니다.
                img_url = img_tag['src']
                img_request = requests.get(img_url, stream=True)
                img_width, img_height = 0, 0
                try:
                    img_width, img_height = int(img_tag['width']), int(img_tag['height'])
                except KeyError:
                    pass

                # 이미지 크기가 조건을 만족하는 경우 다운로드합니다.
                if img_width >= min_width and img_height >= min_height:
                    file_extension = img_url.split('.')[-1]
                    save_path = os.path.join(save_folder, f'{search}_{start_index + i}.{file_extension}')

                    with open(save_path, 'wb') as f:
                        for chunk in img_request.iter_content(8192):
                            f.write(chunk)

                    print(f'Downloaded: {save_path}')

                # 이미지 다운로드 개수가 목표치에 도달하면 종료합니다.
                if start_index + i + 1 >= num_images:
                    break

if __name__ == "__main__":
    download_images("사과", 50, 512, 512, "downloaded_images")
