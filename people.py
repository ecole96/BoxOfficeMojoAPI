from bs4 import BeautifulSoup
import utils

def scrape_person_chart(soup):
    results = {}
    keys = ["title","studio","domestic_gross","lifetime_theaters","ow_gross","ow_theaters","date"]
    h1 = soup.find("h1")
    if h1:
        name = h1.text.strip()
        results[name] = {}
        navtabs = soup.select("ul.nav_tabs li")
        for i,li in enumerate(navtabs):
            role = li.text.lower()
            results[name][role] = []
            if i > 0:
                role_url = "https://www.boxofficemojo.com" + li.find("a")['href']
                soup = utils.download(role_url)
                navtabs = soup.select("ul.nav_tabs li")
                li = navtabs[i]
            table = li.find_next("table")
            rows = table.find_all("tr",{"bgcolor":["#ffffff","#f4f4ff"]})
            for r in rows:
                row_dict = {}
                cols = r.select("td")[1:]
                for j,c in enumerate(cols):
                    key = keys[j]
                    data = c.text.strip()
                    if key == 'title':
                        row_dict["movie"] = {}
                        row_dict["movie"]["id"] = utils.get_id(c.find("a")['href'],'id')
                        row_dict["movie"]["title"] = data
                    elif key == 'studio':
                        row_dict["studio"] = {}
                        row_dict["studio"]["id"] = utils.get_id(c.find("a")['href'],'studio')
                        row_dict["studio"]["name"] = data
                    else:
                        if data in ["-","n/a"]:
                            data = None
                        else:
                            if 'gross' in key:
                                data = float(data[1:].replace(',',''))
                            elif 'theaters' in key:
                                data = int(data.replace(',',''))
                            else:
                                data = utils.processDate("%m/%d/%y",data)
                        row_dict[key] = data
                results[name][role].append(row_dict)
    return results