import requests
import json

from config import ACCESS_TOKEN, ROOM_TITLE

url = 'https://webexapis.com/v1/rooms'
headers = {
    'Authorization': 'Bearer {}'.format(ACCESS_TOKEN),
    'Content-Type': 'application/json'
}
params = {'title': ROOM_TITLE}
res = requests.post(url, headers=headers, json=params)
print(res.json())
