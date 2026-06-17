import requests
import json

from config import ACCESS_TOKEN

url = 'https://webexapis.com/v1/rooms'
headers = {
    'Authorization': 'Bearer {}'.format(ACCESS_TOKEN),
    'Content-Type': 'application/json'
}
params = {'max': '100'}
res = requests.get(url, headers=headers, params=params)
print(res.json())
