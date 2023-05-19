import requests


class YandexDiscUpload:
    def __init__(self, filepath: str, yd_token: str) -> None:
        self._file_path = filepath
        self._headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {yd_token}'
        }

    def create_new_folder(self) -> None:
        """Create a new folder"""
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': self._file_path}
        requests.put(url, params=params, headers=self._headers)

    def _get_link_to_upload(self, file_path: str) -> str:
        """Get link for upload files"""
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self._headers
        params = {'path': file_path, 'overwrite': True}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json().get('href', '')

    def upload_file(self, filename: str, new_filename, file, folder: str) -> None:
        """Upload new file to Yandex Disk"""
        href = self._get_link_to_upload(self._file_path + new_filename)
        requests.put(href, data=file)