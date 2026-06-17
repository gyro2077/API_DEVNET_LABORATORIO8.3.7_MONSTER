import requests
import json

from config import ACCESS_TOKEN, ROOM_ID, MESSAGE

url = 'https://webexapis.com/v1/messages'
headers = {
    'Authorization': 'Bearer {}'.format(ACCESS_TOKEN),
    'Content-Type': 'application/json'
}
params = {'roomId': ROOM_ID, 'markdown': MESSAGE}
res = requests.post(url, headers=headers, json=params)
print(res.json())
