from bs4 import BeautifulSoup
import re
import utils

def scrape_weeks(soup,parameter):
    results = {}
    keys = ["date","rank","gross","lw_change","theaters","theaters_change","gross_to_date","week_#"]
    junk = soup.find_all("table",{"style":"padding-top: 5px;"})
    for j in junk:
        j.decompose()
    container = soup.select_one("center")
    if container.text.strip() != "No weekend data available.":
        years = soup.select("center > b")
        for y in years:
            year = y.text
            results[year] = {}
            table = y.find_next("table")
            rows = table.find_all("tr",{"bgcolor":["#ffffff","#f4f4ff"]})
            for r in rows:
                cols = r.select("td")
                del cols[6]
                datekey = None
                for i,c in enumerate(cols):
                    key = keys[i]
                    data = c.text.replace('\x96','-').strip()
                    if key == 'date':
                        datekey = data
                        results[year][datekey] = {'id':None,'week_#':None}
                        url = c.select_one("a")['href']
                        weekend_id = utils.get_id(url,parameter)
                        results[year][datekey]['id'] = weekend_id
                    else:
                        if data == '-':
                            data = None
                        else:
                            if key  == 'lw_change':
                                data = round(float(data[:-1].replace(',','')) / 100,3)
                            elif key in ['gross','gross_to_date']:
                                data = float(data[1:].replace(',',''))
                            else:
                                data = int(data.replace(',',''))
                        results[year][datekey][key] = data
    return results

def scrape_daily(soup):
    results = {}
    keys = ["date","rank","gross","yd_change","lw_change","theaters","gross_to_date"]
    container = soup.select_one('table[width="95%"] center')
    if container.text.strip() != "NO DAILY DATA AVAILABLE":
        rows = container.find_all("tr",{"bgcolor":["#ffffff","#f4f4ff"]})
        for r in rows:
            all_cols = r.find_all("td")
            cols = []
            for i in range(len(all_cols)):
                if 1 <= i <= 6 or i == 8:
                    cols.append(all_cols[i])
            datekey = None
            for i,c in enumerate(cols):
                key = keys[i]
                data = c.text.strip()
                if key == 'date':
                    datekey = utils.processDate("%b %d, %Y",data.replace('.',''))
                    results[datekey] = {}
                else:
                    if data == '-':
                        data = None
                    else:
                        if key in ['yd_change','lw_change']:
                            data = round(float(data[:-1].replace(',','')) / 100,3)
                        elif key in ['gross','gross_to_date']:
                            data = float(data[1:].replace(',',''))
                        else:
                            data = int(data.replace(',',''))
                results[datekey][key] = data
    return results


def get_metadata(soup,results):
    results["title"] = None
    results["metadata"] = {}
    keys = ["title","studio","release_date","genre","runtime_mins","mpaa_rating","budget"]
    table = soup.find("table",{"border":"0","cellpadding":"0","cellspacing":"0","width":"100%","style":"padding-top: 5px;"})
    if table:
        extra = table.find("td",{"align":"center","colspan":"2"})
        if extra:
            extra.decompose()
        metadata_bold = table.find_all("b")
        for i, key in enumerate(keys):
            m = metadata_bold[i]
            metadata = m.text.strip()
            if metadata.lower() in ['n/a','tbd']: 
                metadata = None
            if key == 'studio':
                url = m.select_one("a")['href']
                studio_id = utils.get_id(url,"studio")
                metadata = {"id":studio_id,"name":metadata}
            elif key == 'budget' and metadata is not None:
                metadata = metadata.replace(' million','000000')
                metadata = utils.processNumber(metadata,["$",","],'float')
            elif key == 'runtime_mins' and metadata is not None:
                metadata = utils.convert_runtime(metadata)
            elif key == 'release_date' and metadata is not None:
                metadata = utils.processDate("%B %d, %Y",metadata)
            if key == 'title':
                results[key] = metadata
            else:
                results['metadata'][key] = metadata
    return results

def get_table_data(soup,results):
    results['box_office'] = {}
    boxes = soup.select("div.mp_box")
    for b in boxes:
        header = b.select_one("div.mp_box_tab").text
        tables = b.find_all("table",{"border":"0","cellspacing":"0","cellpadding":"0"})
        if header == 'Total Lifetime Grosses':
            results['box_office']['lifetime_grosses'] = lifetime_grosses(tables)
        elif header == 'Domestic Summary':
            results['box_office']['domestic_summary'] = domestic_summary(tables)
        elif header == 'The Players':
            results['cast_and_crew'] = the_players(b)
    return results

def lifetime_grosses(soup):
    results = {}
    for s in soup:
        rows = s.select("tr")
        for r in rows:
            cols = r.select("td")
            label = cols[0].text.strip().replace('\xa0',' ')
            if label in ['Domestic:','+ Foreign:']:
                data = cols[1].text.strip()
                if data.lower() == 'n/a':
                    data = None
                else:
                    data = utils.processNumber(data,['$',','],'float')
                if label == "Domestic:":
                    key = 'domestic_gross'
                else:
                    key = 'foreign_gross'
                results[key] = data
    return results

def domestic_summary(soup): #separate by table
    results = {}
    for s in soup:
        subtables = s.select("td")
        header = subtables[0]
        label = header.text[:-1].replace('\xa0',' ').strip()
        data = subtables[1].text.replace('\xa0',' ').strip()
        if label == 'Release Dates':
            data = re.findall(r"[a-zA-Z]* \d{1,2}, \d{4}", data)
            results['limited_release_date'] = utils.processDate("%B %d, %Y",data[0].strip())
            results['wide_release_date']  = utils.processDate("%B %d, %Y",data[1].strip())
        elif label in ['Limited Opening Weekend','Wide Opening Weekend','Opening Weekend']:
            keys = {'Limited Opening Weekend':'ow_limited','Wide Opening Weekend':'ow_wide','Opening Weekend':'ow'}
            key = keys[label]
            results[key] = {}
            results[key]['id'] = {'year':None,'weekend_number':None}
            weekend_url = header.find("a")
            if weekend_url:
                results[key]['id']['year'] = utils.get_id(weekend_url['href'],'yr')
                results[key]['id']['weekend_number'] = utils.get_id(weekend_url['href'],'wknd')
            results[key]['gross'] = utils.processNumber(data,['$',','],'float')
            data = subtables[2].text.replace(',','').strip()
            data = re.findall(r"\d+", data)
            results[key]['rank'] = int(data[0])
            results[key]['theaters'] = int(data[1])
        elif label in ['Widest Release','In Release']:
            keys = {'Widest Release':'widest_release','In Release':'days_in_release'}
            key = keys[label]
            data = data.split()[0]
            results[key] = utils.processNumber(data,[','],'int')
        elif label == 'Close Date':
            results['close_date'] = utils.processDate("%B %d, %Y",data)
    return results

def the_players(soup):
    results = {}
    for br in soup.find_all("br"): br.replace_with('\n')
    rows = soup.select("tr")
    for r in rows:
        cols = r.select("td")
        category = cols[0].text[:-1].strip().lower()
        data = cols[1:]
        if len(category.split()) == 1:
            if category[-1] != 's': category += 's'
            results[category] = []
            for section in data: 
                section = str(section).split('\n')
                people = [BeautifulSoup(s,"lxml") for s in section]
                for p in people:
                    person = {"id":None}
                    person_url = p.find("a")
                    if person_url: person['id'] = utils.get_id(person_url['href'],'id')
                    person['name'] = re.sub(r"(\*| \(.+\))",'',p.text.strip())
                    results[category].append(person)
    return results