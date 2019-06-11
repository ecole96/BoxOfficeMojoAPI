import urllib.parse as urlparse
import search
import utils
import filmPage
import charts
import people

class BoxOfficeMojo:
    baseURL = "https://www.boxofficemojo.com"

    def search(self,q): 
        results = {"movies":[],"people":[]}
        q = urlparse.quote(q.encode('utf8'))
        url = self.baseURL + "/search/?q=" + q + "&p=.htm"
        soup = utils.download(url)
        soup = search.trim_search_page(soup)
        results["movies"] = search.movie_search(q,soup)
        results["people"] = search.people_search(soup)
        return results

    def get_film_data(self,movie_id):
        results = {"id":movie_id}
        url = self.baseURL + "/movies/?id=" + movie_id + ".htm"
        soup = utils.download(url)
        results = filmPage.get_metadata(soup,results)
        results = filmPage.get_table_data(soup,results)
        return results
    
    def get_film_daily(self,movie_id):
        results = {"id":movie_id,"daily":{}}
        url = self.baseURL + "/movies/?page=daily&view=chart&id=" + movie_id + ".htm"
        soup = utils.download(url)
        results['daily'] = filmPage.scrape_daily(soup)
        return results
    
    def get_film_weekend(self,movie_id):
        results = {"id":movie_id,"weekend":{}}
        url = self.baseURL + "/movies/?page=weekend&id=" + movie_id + ".htm"
        soup = utils.download(url)
        results['weekend'] = filmPage.scrape_weeks(soup,'wknd')
        return results

    def get_film_weekly(self,movie_id):
        results = {"id":movie_id,"weekly":{}}
        url = self.baseURL + "/movies/?page=weekly&id=" + movie_id + ".htm"
        soup = utils.download(url)
        results['weekly'] = filmPage.scrape_weeks(soup,'wk')
        return results
    
    def get_weekend(self,yr,wknd_id):
        results = {"id":{"year":yr, "wknd":wknd_id},"weekend":[]}
        keys = ["tw_rank","lw_rank","title","studio","gross","lw_change","theaters","theaters_change","total_gross","budget","week_#"]
        url = self.baseURL + "/weekend/chart/?yr=" + yr + "&wknd=" + wknd_id + "&p=.htm"
        soup = utils.download(url)
        results['weekend'] = charts.scrape_chart(soup,keys,[8])
        print(results)
        return results
        
    def get_day(self,date):
        results = {date:[]}
        keys = ["td_rank","yd_rank","title","studio","gross","yd_change","lw_change","theaters","gross_to_date","day_#"]
        url = self.baseURL + "/daily/chart/?view=1day&sortdate=" + date + "&p=.htm"
        soup = utils.download(url)
        results[date] = charts.scrape_chart(soup,keys,[8])
        print(results)
        return results
    
    #def get_year(self,yr):
    
    def get_week(self,yr,wk):
        key = wk + "-" + yr
        results = {key:[]}
        keys = ["tw_rank","lw_rank","title","studio","gross","lw_change","theaters","theaters_change","gross_to_date","budget","week_#"]
        url = self.baseURL + "/weekly/chart/?yr=" + yr + "&wk=" + wk + "&p=.htm"
        soup = utils.download(url)
        results[key] = charts.scrape_chart(soup,keys,[8])
        print(results)
        return results

    def get_person(self,person_id):
        url = self.baseURL + "/people/chart/?id=" + person_id + ".htm&sort=rank&order=ASC&p=.htm"
        soup = utils.download(url)
        results = people.scrape_person_chart(soup)
        return results

    #def get_all_films(self):
    
    #def get_all_studios(self):
    
    #def get_all_people(self):

                
def main():
    bomo = BoxOfficeMojo()
    p = bomo.get_person("georgeclooney")
    #wknd = bomo.get_week("2019","22")
    
    
main()