import http.client
import mimetypes
import json
import os
key = os.getenv('zomato_api')
conn = http.client.HTTPSConnection("developers.zomato.com")
payload = ''
headers = {
    'user-key': key,
}

city = input("enter city:")
link="/api/v2.1/cities?q="
citylink = link + city
conn.request("GET", citylink , payload, headers)
res = conn.getresponse()
data = res.read()
data = json.loads(data.decode("utf-8"))

print(data['location_suggestions'][0]['id'])
