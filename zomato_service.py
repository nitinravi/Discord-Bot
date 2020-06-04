import http.client
import mimetypes
import json
import os
key = os.getenv('zomato_api')
conn = http.client.HTTPSConnection("developers.zomato.com")


def city_id(city):
    payload = ''
    headers = {
        'user-key': key,
    }

    link = "/api/v2.1/cities?q="
    citylink = link + city
    conn.request("GET", citylink, payload, headers)
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data.decode("utf-8"))
    return (data["location_suggestions"][0]["id"])

