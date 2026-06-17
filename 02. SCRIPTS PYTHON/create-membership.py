import requests
import json

from config import ACCESS_TOKEN, ROOM_ID, PERSON_EMAIL

url = 'https://webexapis.com/v1/memberships'
headers = {
    'Authorization': 'Bearer {}'.format(ACCESS_TOKEN),
    'Content-Type': 'application/json'
}
params = {'roomId': ROOM_ID, 'personEmail': PERSON_EMAIL}
res = requests.post(url, headers=headers, json=params)
print(res.json())
