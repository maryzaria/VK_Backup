import os
import json
from dotenv import load_dotenv

from VK_backup import VkApiBackup


if __name__ == '__main__':
    load_dotenv()
    my_vk_token = os.getenv('VK_API_TOKEN')
    # my_id = '55242725'
    user_id = str(input('Введите id пользователя: '))
    your_yd_token = str(input('Введите токен Яндекс диска или пустую строку, если загружаете на Google диск: '))
    vk = VkApiBackup(user_id, my_vk_token, your_yd_token, disk='google')  # disk='google'
    data = vk.get_user_photo()  # album_id='wall', count=10
    if isinstance(data, dict):
        vk.upload_file_to_disk(data)
        with open('photos_info.json', 'w', encoding='utf-8') as output_file:
            json.dump(vk.photos_info, output_file, indent=2)
