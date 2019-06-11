from bs4 import BeautifulSoup
import urllib.parse as urlparse
import datetime
import requests

def get_id(url,parameter):
        parsed_url = urlparse.urlparse(url)
        try:
            id_parse = urlparse.parse_qs(parsed_url.query)[parameter][0]
            ID = id_parse.split('.')[0]
        except KeyError:
            ID = None
        return ID

def processNumber(n_str,to_remove,type): 
    for t in to_remove:
        n_str = n_str.replace(t,'')
    if type == 'int':
        n = int(n_str)
    else:
        n = float(n_str)
    return n

def processDate(format,date):
    try:
        formatted_date = datetime.datetime.strptime(date,format).strftime("%Y-%m-%d")
    except ValueError:
        formatted_date = date
    return formatted_date

def convert_runtime(runtime_str):
        runtime_split = runtime_str.split()
        hours = int(runtime_split[0])
        minutes = int(runtime_split[2])
        runtime_mins = (hours * 60) + minutes
        return runtime_mins

def download(url):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    try:
        request = requests.get(url,headers={'User-Agent':user_agent})
        page = request.content
        soup = BeautifulSoup(page, 'lxml')
    except Exception as e: # couldn't download page
        print("DOWNLOAD ERROR: ",e)
        soup = None
    return soup