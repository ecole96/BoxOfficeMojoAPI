import math
from bs4 import BeautifulSoup
import utils

def movie_search(q,soup):
    movie_results = []
    page_count = get_movie_page_count(soup)
    if page_count:
        movie_rows = get_movie_rows(soup,page_count,q)
        for m in movie_rows:
            movie_details = scrape_movie_search_data(m)
            movie_results.append(movie_details)
    return movie_results

def trim_search_page(soup):
    soup = soup.find("table",{"border":"0","cellpadding":"0","cellspacing":"0","width":"100%"}).decode_contents()
    soup = BeautifulSoup(soup,"lxml")
    junk = soup.find_all("table",{"border":"0","cellpadding":"0","cellspacing":"0"}) + soup.find_all("table",{"border":"0","cellpadding":"5","cellspacing":"0","align":"right"})
    for j in junk:
        j.decompose()
    return soup
    
def get_movie_page_count(soup):
    page_count = 0
    count_str = soup.select_one("td > b")
    if count_str:
        match_count = count_str.text.strip().split()[0]
        if match_count.isnumeric():
            match_count = int(match_count)
            per_page = 51
            page_count = math.ceil(match_count / per_page)
    return page_count

def get_movie_rows(soup,page_count,q):
    movie_rows = []
    for i in range(1,page_count+1):
        if i > 1:
            url = "https://www.boxofficemojo.com/search/?q=" + q + "&showpage=" + str(i) + "&p=.htm"
            soup = utils.download(url)
        table = soup.find("table",{"border":"0","cellpadding":"5","cellspacing":"0"})
        rows = table.find_all("tr")[1:]
        for r in rows:
            movie_rows.append(r)
    return movie_rows

def scrape_movie_search_data(movie_row):
    keys = ["title","studio","domestic_gross","max_theaters","ow_gross","ow_theaters","release_date"]
    details = {}
    cols = movie_row.find_all("td")
    for i,k in enumerate(keys):
        col = cols[i].text.strip()
        if col.lower() == 'n/a':
            col = None
        if k == "title":
            url = cols[i].select_one("a")['href']
            movie_id = utils.get_id(url,'id')
            details["id"] = movie_id
        elif k == 'release_date' and col.lower() not in ['multiple','tbd']:
            col = utils.processDate("%m/%d/%Y",col)
        elif k in ['domestic_gross','ow_gross'] and col is not None:
            col = utils.processNumber(col,[",","$"],'float')
        elif k in ['max_theaters','ow_theaters'] and col is not None:
            col = utils.processNumber(col,[","],'int')
        details[k] = col
    return details

def people_search(soup):
    people_results = []
    table = soup.find("table",{"border":"0","cellpadding":"5","cellspacing":"1"})
    if table:
        rows = table.find_all("tr")[1:]
        for r in rows:
            details = {}
            url = r.select_one("a")['href']
            person_id = get_id(url,'id')
            details["name"] = r.text
            people_results.append(details)
    return people_results