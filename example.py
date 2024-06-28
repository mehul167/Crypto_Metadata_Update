# temp_mail = geropew265@gawte.com
import requests
from datetime import datetime
import os
import time
import random
from pymongo import MongoClient
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

ok_tag_api = os.getenv("ok_tag_api")
collection = None
client = None

def generate_random_ips(num_ips=1):
    octet_ranges = [
        (1, 254),  # First octet (avoid reserved ranges)
        (1, 255),  # Second octet
        (1, 255),  # Third octet
        (1, 255),  # Fourth octet
    ]
    ips = []
    for _ in range(num_ips):
        ip_parts = []
        for range_start, range_end in octet_ranges:
            ip_parts.append(str(random.randint(range_start, range_end)))
        ips.append(".".join(ip_parts))
    return ips

def oklink(target_collection, addr_list, chain="eth"):
    header_pair = {"Ok-Access-Key": ok_tag_api, "X-Forwarded-For": generate_random_ips()[0]}
    param_pair = {'chainShortName': chain, 'address': ",".join(addr_list)}
    try:
        tagged_addresses = []
        untagged_addresses = []
        count = 0
        while True:
            x = requests.get('https://www.oklink.com/api/v5/explorer/address/entity-label?', headers=header_pair, params=param_pair)
            if x.status_code == 200:
                data = x.json()
                # print(data)
                if len(data["data"]) > 0:
                    for row in data["data"]:
                        doc = {"address": row["address"], "name": row["label"], "tag": "exchange", "source": "oklink", "confidence": 80, "timestamp": int(datetime.now().timestamp())}
                        target_collection.insert_one(doc)
                        tagged_addresses.append(row['address'])
                        untagged_addresses = [element for element in addr_list if element not in tagged_addresses]
                else:
                    untagged_addresses.extend(addr_list)
                time.sleep(0.5)
                break
            else:
                count += 1
                time.sleep(1.3)
                if count > 5:
                    print(f"[x]response code: {x.status_code}")
                    break
    except requests.exceptions.RequestException as e:
        print(f"Error making API call: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return tagged_addresses,untagged_addresses

def find_addresses_not_in_second_collection(result_collection):
    pipeline = [
        {
            '$lookup': {
                'from': result_collection,
                'localField': 'address',
                'foreignField': 'address',
                'as': 'matched_docs'
            }
        },
        {
            '$match': {
                'matched_docs': []
            }
        },
        {
            '$project': {
                'address': 1
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    addresses = [doc['address'] for doc in result]
    return addresses

def connect_mongodb(collection_name=""):
    global collection, client
    client = MongoClient('mongodb://localhost:27017/')
    db = client['crypto_forensics']
    if collection_name:
        global result_collection
        collection = db[collection_name]
        result_collection = db[collection_name + "_result"]
    else:
        collection = None

def etherscan(target_collection, address):
    url = f"https://etherscan.io/address/{address}"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    headers = {'User-Agent': user_agent,"X-Forwarded-For": generate_random_ips()[0]}
    response = requests.get(url, headers=headers)
    print(response)
    if response.status_code ==200:
        soup = BeautifulSoup(response.text, 'html.parser')

        span_tag = soup.find('span', class_='hash-tag text-truncate lh-sm my-n1')
        if span_tag:
            tag = span_tag.text.strip()
            existing_doc = target_collection.find_one({"address": address})
            if not existing_doc :
                doc = {
                    "address": address,
                    "name": tag,
                    "tag": "exchange",
                    "source": "etherscan",
                    "confidence": 80,
                    "timestamp": int(datetime.now().timestamp())
                }
                target_collection.insert_one(doc)
                time.sleep(0.2)
            else:
                time.sleep(0.2)
                return address
    else:
        time.sleep(0.5)
        return address
    

def scrape_ethtective(address,target_collection):
    driver = webdriver.Chrome()
    url = f"https://canary.ethtective.com/address/{address}"
    driver.get(url)
    
    # Adjust the sleep time based on how long the page takes to load
    time.sleep(15)

    html = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    address_div = soup.find('div', class_='address')
    tag_div = soup.find('div', class_='toolbar')
    
    if address_div:
        name_span = address_div.find('span', class_='name')
        name_value = name_span.text.strip() if name_span else None
        # print("Address Name:", name_value)
        if len(name_value)>2:
            exchange_p = tag_div.find('p', class_='tag', title="Address belongs to a known exchange")
            exchange_text = exchange_p.text.strip() if exchange_p else None
            # print("Exchange Text:", exchange_text)
            existing_doc = target_collection.find_one({"address": address})
            if not existing_doc:
                doc = {
                    "address": address,
                    "name": name_value,
                    "tag": exchange_text,
                    "source": "ethtective",
                    "confidence": 80,
                    "timestamp": int(datetime.now().timestamp())
                }
                target_collection.insert_one(doc)
    else:
        # print("No tag found")
        return address

def bloxy(address,target_collection):
    url = f"https://bloxy.info/address/{address}"
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    }
    response = requests.get(url,headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    span_tag=soup.find("span", class_="name-annotated subject-annotation")
    if span_tag:
        tag = span_tag.text.strip()
        if len(tag)>3:
            existing_doc = target_collection.find_one({"address": address})
            if not existing_doc:
                doc = {
                    "address": address,
                    "name": tag,
                    "tag": "exchange",
                    "source": "bloxy",
                    "confidence": 80,
                    "timestamp": int(datetime.now().timestamp())
                }
                target_collection.insert_one(doc)
                print("Added successfully")
            else:
                pass
        else:
            print("len not sufficient")
    else:
        return address

def main():
    connect_mongodb('ethereum_metadata_update')
    addresses = find_addresses_not_in_second_collection('ethereum_metadata_update_result')
    ether_not_tagged=[]
    oklink_not_tagged=[]
    ethtective_not_tagged=[]
    bloxy_not_tagged = []
    for address in addresses[0:1000]:
        not_found_add=etherscan(result_collection,address)
        if not_found_add:
            if len(ether_not_tagged) <20:
                ether_not_tagged.append(not_found_add)
            else:
                tagged,untagged=oklink(result_collection,not_found_add,chain="eth")
                ether_not_tagged=[]
                oklink_not_tagged.append(untagged)
                if oklink_not_tagged:
                    ethtective_untagged = scrape_ethtective(address,result_collection)
                    ethtective_not_tagged.append(ethtective_untagged)
                    oklink_not_tagged=[]
                    if ethtective_not_tagged:
                        bloxy_untagged = bloxy(ethtective_not_tagged,result_collection)
                        bloxy_not_tagged.append(bloxy_untagged)
                    
    print(f"COMPLETE NOT TAGGED:\n{ethtective_not_tagged}")

if __name__ == "__main__":
    main()
    