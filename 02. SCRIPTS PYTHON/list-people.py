import requests
import json

from config import ACCESS_TOKEN, PERSON_EMAIL

url = 'https://webexapis.com/v1/people'
headers = {
    'Authorization': 'Bearer {}'.format(ACCESS_TOKEN),
    'Content-Type': 'application/json'
}
params = {
    'email': PERSON_EMAIL
}
res = requests.get(url, headers=headers, params=params)
print(json.dumps(res.json(), indent=4))
