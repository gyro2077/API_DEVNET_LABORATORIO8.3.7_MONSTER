import requests
import json

from config import ACCESS_TOKEN

url = 'https://webexapis.com/v1/people/me'
headers = {
    'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)
}
res = requests.get(url, headers=headers)
print(json.dumps(res.json(), indent=4))
