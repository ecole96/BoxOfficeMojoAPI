from bs4 import BeautifulSoup
import utils

def scrape_chart(soup,keys,cols_to_remove):
    results = []
    table = soup.find("table",{"border":"0","cellpadding":"5","cellspacing":"1"})
    if table:
        rows = table.find_all("tr",{"bgcolor":["#ffffff","#f4f4ff","#ffff99"]})
        for r in rows:
            cols = r.select("td")
            for i in cols_to_remove:
                del cols[i]
            row_dict = {"movie":{"id":None,"title":None}}
            for i,c in enumerate(cols):
                key = keys[i]
                data = c.text.strip()
                if key == 'title':
                    row_dict['movie'][key] = data
                    row_dict['movie']['id'] = utils.get_id(c.find("a")['href'],'id')
                elif key == 'studio':
                    row_dict[key] = {"id":None,"name":None}
                    row_dict[key]['name'] = data
                    row_dict[key]['id'] = utils.get_id(c.find("a")['href'],'studio')
                else:
                    if data in ['-','N']:
                        data = None
                    else:
                        if 'gross' in key:
                            data = float(data[1:].replace(',',''))
                        elif key in ['yd_change','lw_change']:
                            data = round(float(data[:-1].replace(',','')) / 100,3)
                        elif key == 'budget':
                            data = float(data[1:]) * 1000000
                        else:
                            data = int(data.replace(',',''))
                    row_dict[key] = data
            results.append(row_dict)
    return results

                






