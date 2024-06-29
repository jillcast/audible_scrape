#### Scraping Audible Books ####

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Headless mode
options = Options()  # Initialize an instance of the Options class
options.add_argument('--headless')  # Activate headless mode
options.add_argument('window-size=1920x1080')  # optional; big window size ensures all data will be displayed

web = "https://www.audible.com/search"
path = '/Users/jillcastellano/Documents/Coding/chromedriver-mac-arm64/chromedriver'

# Create a service object
service = Service(path)

# Initialize the Chrome driver with the service object and options
driver = webdriver.Chrome(service=service, options=options)

driver.get(web)
# driver.maximize_window() # We don't need because we set window size above

#### Pagination ####

# Locating the pagination bar
pagination = driver.find_element(By.XPATH, '//ul[contains(@class, "pagingElements")]')

# Locating each page displayed in the pagination bar
pages = pagination.find_elements(By.TAG_NAME, 'li')

# Getting the last page with negative indexing (everything before the right arrow element)
last_page = int(pages[-2].text) if len(pages) > 1 else 1  # Handle cases where there's no pagination

current_page = 1  # this is the page the bot starts scraping

#### Get Containers Ready ####

# Initializing storage in empty lists
book_title = []
book_author = []
book_length = []

# The while loop works until the the bot reaches the last page of the website, then it will break
while current_page <= last_page:

    # Incorporate Explicit Wait
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'adbl-impression-container')))
    products = WebDriverWait(container, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, './/li[contains(@class, "productListItem")]')))

    #### Scrape ####

    # Looping through the products list (each "product" is an audiobook)
    for product in products:
        # Find elements using updated syntax in Selenium 4
        book_title_elem = product.find_element(By.XPATH, './/h3[contains(@class, "bc-heading")]')
        book_author_elem = product.find_element(By.XPATH, './/li[contains(@class, "authorLabel")]')
        book_length_elem = product.find_element(By.XPATH, './/li[contains(@class, "runtimeLabel")]')

        # Watch code work
        print(book_title_elem.text)

        # Storing data in lists
        book_title.append(book_title_elem.text)
        book_author.append(book_author_elem.text)
        book_length.append(book_length_elem.text)

    # Moving on to next page in the while loop
    current_page = current_page + 1  # increment the current_page by 1 after the data is extracted

    # Locating the next_page button and clicking on it. If the element isn't on the website, pass to the next iteration
    try:
        next_page = driver.find_element(By.XPATH, './/span[contains(@class , "nextButton")]')
        next_page.click()
    except:
        pass

driver.quit()

#### Store and Export Data ####

# Storing the data into a DataFrame and exporting to a csv file
df_books = pd.DataFrame({'title': book_title, 'author': book_author, 'length': book_length})
df_books.to_csv('all_audible_books.csv', index=False)

