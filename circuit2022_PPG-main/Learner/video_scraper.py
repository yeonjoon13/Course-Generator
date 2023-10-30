# import required packages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from Learner import models
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import inflect

video_table_index = 0

# url of site to search
urls = [
    'https://www.youtube.com/results?search_query='
]


def any_keywords_in_line(keywords, line):
    for keyword in keywords:
        if keyword in line:
            return True

    return False


def start_scraper(keywords):
    """
	
	scrapes specifically for videos on video-specific websites (YouTube, Vimeo)

	@param keywords: word to search for on video page
	"""

    keyword_list = []
    p = inflect.engine()

    #try:
        #if p.singular_noun(keywords):
           # keywords = p.singular_noun(keywords)
    #except:
        #print('')

    #keyword_list.append(keywords)

    #try:
       # if p.plural_noun(keywords):
          #  keyword_list.append(p.plural_noun(keywords))
    #except:
       # print('')

    global video_table_index

    try:
        video_table_index = models.video.objects.latest('video_id').video_id + 1
    except:
        video_table_index = 0

    og_index = video_table_index

    options = Options()
    options.headless = True
    driver = webdriver.Chrome("Learner/chromedriver", options=options)
    driver.implicitly_wait(30)

    for url in urls:
        # driver.get('{}{}'.format(url, keywords))
        url_to_get = url + keywords + '+educational'
        driver.get(url_to_get)
        try:
            elem = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "video-title"))  # This is a dummy element
            )
        finally:
            time.sleep(3)
            print('')
        # driver.quit()

        content = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, 'lxml')
        titles = soup.findAll('a', id='video-title')
        # video_urls = soup.findAll('a', id='video-title')

        # print(titles)
        # for t in titles[:10]:
        for t in titles[:10]:
            link = 'https://www.youtube.com' + t.get('href')
            print(t.get('href'))

            try:
                driver.get(link)
                time.sleep(1)
                content = driver.page_source.encode('utf-8').strip()
                soup = BeautifulSoup(content, 'lxml')
                pattern = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
                description = pattern.findall(str(soup))[0].replace('\\n', '\n')
                new_desc = ''
                lines = description.split('\n')
                for line in lines:
                    if 'http' not in line and len(line) > 20 and any_keywords_in_line(keyword_list, line):
                        new_desc += line
            except:
                new_desc = t.text

            # print(description)

            print(new_desc)

            tester = models.video.objects.create(keywords=keywords, title=t.text, URL=link, video_id=video_table_index,
                                                 description=new_desc)
            tester.save()
            video_table_index += 1

    return [og_index, video_table_index]

# start_scraper("apple")
