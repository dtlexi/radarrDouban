import requests

url="https://pt.btschool.club/torrents.php?search=&incldead=0&spstate=0&search_area=0&search_mode=0&sort=4&type=desc"

kv = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
      'referer': 'https://www.mzitu.com/'}

resp= requests.post(url=url,timeout=10,cookies={
    "cf_clearance":"hfS3Dt0vZzNV2rEMZkqn3feRjgOfPyA.IsdR5LzDrZA-1646018437-0-150",
    "c_secure_uid":"OTM4MDY%3D",
    "c_secure_pass":"f2e2ca161bfdfc9568cc4abd7b67bc25",
    "c_secure_ssl":"eWVhaA%3D%3D",
    "c_secure_tracker_ssl":"eWVhaA%3D%3D",
    "c_secure_login":"bm9wZQ%3D%3D",
    "cf_ob_info":"502:6ea8d8caba6dd447:HAM",
    "cf_use_ob":"0"
},headers=kv)
print(resp.content)