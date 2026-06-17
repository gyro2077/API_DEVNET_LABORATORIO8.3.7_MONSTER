import requests
import json

from config import ACCESS_TOKEN, ROOM_ID

url = 'https://webexapis.com/v1/memberships'
headers = {
    'Authorization': 'Bearer {}'.format(ACCESS_TOKEN),
    'Content-Type': 'application/json'
}
params = {'roomId': ROOM_ID}
res = requests.get(url, headers=headers, params=params)
print(res.json())
