import os
from datetime import datetime
from tempfile import NamedTemporaryFile
from tqdm import tqdm

import requests

from class_YandexDiskUpload import YandexDiscUpload
from class_GoogleDiskUpload import GoogleDiskUpload


class VkApiBackup:
    def __init__(self, owner_id: str, vk_token: str, yd_token: str, version: str = '5.131', disk: str = 'Yandex') -> None:
        self.id = owner_id
        self._names = []
        self.photos_info = []
        self._file_path = f'profile_photos_id{self.id}/'
        self._disk = YandexDiscUpload(self._file_path, yd_token) if disk == 'Yandex' \
            else GoogleDiskUpload(self._file_path.strip('/'))
        self._params = {
            'access_token': vk_token,
            'v': version
        }

    def get_user_photo(self, album_id: str = 'profile', count: int = 5) -> dict:
        """
        Get a list of user photos.
        album_id should be 'profile' (default), 'wall' or 'saved'.
        Saved photos are only returned with the user's access key.
        Also, you can specify other a specific album_id.
        """
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': self.id,
            'album_id': album_id,
            'extended': '1',
            'photo_sizes': '1',
            'count': count,
            **self._params
        }
        try:
            response = requests.get(url, params=params)
            photos = response.json()
            return photos['response']
        except KeyError:
            print("Error: can't download photo from private profile/album")

    def _get_filename(self, item: dict) -> str:
        name = str(item['likes']['count'])
        x = 1
        if name in self._names:
            upload_date = datetime.fromtimestamp(item['date']).strftime("%d.%m.%Y")
            name = f'{name}_{upload_date}'
        while name in self._names:
            name += f'_{str(x)}'
            x += 1
        self._names.append(name)
        return name + '.png'

    @staticmethod
    def _get_max_size(item: dict) -> dict:
        max_size = max(item['sizes'], key=lambda x: x['height'] * x['width'])
        if max_size['height'] * max_size['width'] == 0:
            max_size = item['sizes'][-1]
        return max_size

    def upload_file_to_disk(self, id_data: dict) -> None:
        """Method uploads photos to Yandex disk"""
        try:
            photos = id_data['items']
            folder = self._disk.create_new_folder()

            for item in tqdm(photos):
                filename = self._get_filename(item)
                max_size = self._get_max_size(item)
                self.photos_info.append({
                    "file_name": filename,
                    "size": max_size['type']
                })
                photo = requests.get(max_size['url'])
                with NamedTemporaryFile(mode='wb', delete=False) as file:
                    file.write(photo.content)
                    name = file.name
                    with open(name, 'rb') as new_file:
                        self._disk.upload_file(name, filename, new_file, folder)
            # print('Successful upload for all photos')
        except Exception as e:
            print(f"Error: {e}")
