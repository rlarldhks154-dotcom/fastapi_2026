import math
import requests
import pandas as pd

service_key = "APUHM9SL-APUH-APUH-APUH-APUHM9SL3F"

base_url = "https://www.safemap.go.kr/openapi2/IF_0039"

page = 1
rows = 1000

params = {
    "serviceKey": service_key,
    "pageNo": page,
    "numOfRows": rows,
    "returnType": "json"
}

r = requests.get(base_url, params=params)
data = r.json()

# 응답 구조에 맞게 수정이 필요할 수 있음
total = data["body"]["totalCount"]
last_page = math.ceil(total / rows)

all_data = []

for page in range(1, last_page + 1):
    params["pageNo"] = page
    r = requests.get(base_url, params=params)
    data = r.json()

    items = data["body"]["items"]["item"]
    all_data.extend(items)

df = pd.DataFrame(all_data)
df.to_csv("IF0039.csv", index=False, encoding="utf-8-sig")

print("완료 :", len(df), "건 저장")