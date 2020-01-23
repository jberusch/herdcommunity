# library imports
from bs4 import BeautifulSoup
import requests

# local imports
from app import db
from app.models import Destination


BASE_URL = 'https://www.yelp.com/'
NASHVILLE_SEARCH_TERM = 'search?find_desc=&find_near=vanderbilt-university-nashville-4&start=' # needs multiple of 10 (starting at 0) added to end
CLEVELAND_SHAKER_SEARCH_TERM = 'search?find_desc=restaurants&find_loc=Shaker%20Heights%2C%20OH&ns=1&start='
CLEVELAND_DOWNTOWN_SEARCH_TERM = 'search?find_desc=Restaurants&find_loc=Cleveland%2C%20OH&ns=1&start='
LONDON_COVENT_GARDEN_SEARCH_TERM= 'search?find_desc=Restaurants&find_loc=Covent%20Garden%2C%20London%2C%20United%20Kingdom&start='
LONDON_ALL_SEARCH_TERM = 'search?cflt=restaurants&find_loc=London&start='

# scrape one page of results (they're paginated)
def scrape_one_page(page_content, region):
    # get all list items, where restaurants are stored
    list_items = page_content.find_all('li')
    for li in list_items:
        imgs = li.find_all('img')
        if len(imgs) < 1:
            # this list item must not be a restaurant
            continue

        # first get link to img
        img_src = imgs[0]['src']

        # next, get all anchor tags
        a_tags = li.find_all('a')
        name = ''

        for a in a_tags:
            if a['name']:
                # get name of restaurant
                name = a['name']
                # get link to yelp page about restaurant
                yelp_link = BASE_URL[:21] + a['href']
                break

        # only add if entry doesn't exist
        if Destination.query.filter_by(name=name).first() is not None:
            print('Restaurant {} already exists. Not adding to DB.'.format(name))
            continue
        # only add if restaurant has a name
        if len(name) < 1:
            continue

        # package all info into database entry
        new_dest = Destination(
            name=name,
            img_src=img_src,
            yelp_link=yelp_link if len(yelp_link) < 150 else BASE_URL,
            region=region,
            num_visits=0,
            users=[]
        )
        print(new_dest)
        db.session.add(new_dest)

def scrape_n_pages(search_term, region, n, step):
    for i in range(n):
        print('\n\n------------- scraping restaurants for page {} ------------'.format(i+1))
        try:
            resp = requests.get(BASE_URL + search_term + str(i * step), timeout=10)
        except requests.exceptions.ReadTimeout:
            print("\n\n<<<<<<<<<<<<<< timeout occured on page i = {} >>>>>>>>>>>>>>>>>", i)
        content = BeautifulSoup(resp.content, "html.parser")
        scrape_one_page(content, region)
    db.session.commit()

# print('======== Scraping restaurants for Nashville ========')
# scrape_n_pages(NASHVILLE_SEARCH_TERM, 'Nashville', 138, 10)
# print('\n\n======== Scraping restaurants for Cleveland (starting from Shaker Heights) ========')
# scrape_n_pages(CLEVELAND_SHAKER_SEARCH_TERM, 'Cleveland', 10, 30)
# print('\n\n======== Scraping more restaurants for Cleveland (starting from downtown) ========')
# scrape_n_pages(CLEVELAND_DOWNTOWN_SEARCH_TERM, 'Cleveland', 60, 30)
# print('\n\n======== Scraping restaurants for London (starting from Covent Garden) ========')
# scrape_n_pages(LONDON_COVENT_GARDEN_SEARCH_TERM, 'London', 98, 30)
print('\n\n======== Scraping restaurants for London (starting from total London link) ========')
scrape_n_pages(LONDON_ALL_SEARCH_TERM, 'London', 33, 30)