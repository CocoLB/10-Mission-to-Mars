# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


def scrape_all():
   # Initiate headless driver for deployment
   browser = Browser("chrome", executable_path="chromedriver.exe", headless=True)

   # set news title and paragraph variables
   news_title, news_paragraph = mars_news(browser)
   # Run all scraping functions and store results in dictionary
   hemispheres = mars_4_hemispheres()
   data = {
       "news_title": news_title,
       "news_paragraph": news_paragraph,
       "featured_image": featured_image(browser),
       "facts": mars_facts(),
       "last_modified": dt.datetime.now(),
       "hem_0_url": hemispheres[0]['img_url'],
       "hem_0_title":hemispheres[0]['title'],
       "hem_1_url": hemispheres[1]['img_url'],
       "hem_1_title":hemispheres[1]['title'],
       "hem_2_url": hemispheres[2]['img_url'],
       "hem_2_title":hemispheres[2]['title'],
       "hem_3_url": hemispheres[3]['img_url'],
       "hem_3_title":hemispheres[3]['title'],    
       }
   browser.quit()
  

   return data   

# Set the executable path and initialize the chrome browser in splinter
#executable_path = {'executable_path': 'chromedriver'}
#browser = Browser('chrome', **executable_path)


### Article
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # add try/except for handling errors
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        slide_elem.find("div", class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


### Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)


    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()


    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()


    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')


    # Find the relative image url
    img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    try:
        # Use the base URL to create an absolute URL
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    
    except AttributeError:
        return None    

    return img_url


### Getting facts/table

def mars_facts():        
    try:
    #use pandas 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    
    #Assign columns and set index of dataframe 
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)
    
    # do the same for earth, get the table facts with same index, 
    # add the earth column to the Mars facts table, and drop the 2 bottom rows
    try:
        df_earth = pd.read_html('https://space-facts.com/earth/')[0] 
    except BaseException:
        return None    
    df_earth.columns=['description', 'Earth']
    df_earth.set_index('description', inplace=True)
    
    df["Earth"] = df_earth["Earth"]
    df=df.drop(index =['First Record:', 'Recorded By:'])
  
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


### CHALLENGE getting the 4 Mars hemispheres images

def mars_4_hemispheres():
    hemispheres = []
    
    def Mars_hemisphere(i):
        browser = Browser("chrome", executable_path="chromedriver.exe", headless=True)
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)
    
        links_found = browser.links.find_by_partial_text('Enhanced')
        links_found[i].click()
    
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
    
        info = soup.find('div', class_='downloads').find('a')
        link = info.get('href')
        title = soup.find('h2', class_='title').get_text()

        browser.quit()
    
        return ({"img_url": link, "title": title})

    hem0 = Mars_hemisphere(0)
    hem1 = Mars_hemisphere(1)
    hem2 = Mars_hemisphere(2)   
    hem3 = Mars_hemisphere(3)
    
    hemispheres.append(hem0)
    hemispheres.append(hem1)
    hemispheres.append(hem2)
    hemispheres.append(hem3)

    return hemispheres
   


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())