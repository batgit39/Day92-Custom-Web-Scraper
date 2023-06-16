import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


headers = {
        'Accept-Language': "en-US,en;q=0.5",
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"
    }


def get_top250_titles():
    URL = "https://www.imdb.com/chart/top"

    response = requests.get(url=URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "lxml")

    all_list = soup.find(name="tbody", class_="lister-list")
    movies = all_list.find_all(name="tr")
    titles = [movie.find(name="td", class_="titleColumn").find(name="a").text for movie in movies]

    return titles


def get_movies_details(titles):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    URL = "https://www.boxofficemojo.com/date/2023-06-12/weekly/"
    driver.get(URL)
    movie_ranking = 0

    movie_details = []

    for title in titles:
        movie_ranking += 1
        search_box = driver.find_element(By.XPATH, '//*[@id="mojo-search-text-input"]')
        search_box.click()
        search_box.send_keys(title)
        search_box.send_keys(Keys.RETURN)

        movie = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div/div/div[1]/div/div[2]/a')
        movie.click()

        details = {
            "Rank on IMDB": movie_ranking,
            "Title": title,
            "Budget": None,
            "Gross Worldwide": None,
            "Genres": None,
            "Running Time": None
        }

        try:
            budget = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[3]/div[4]/div[3]/span[2]/span")
            details["Budget"] = budget.text
        except NoSuchElementException:
            pass

        try:
            gross_worldwide = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[3]/div[1]/div/div[3]/span[2]/span")
            details["Gross Worldwide"] = gross_worldwide.text
        except NoSuchElementException:
            pass

        try:
            genres = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[3]/div[4]/div[7]/span[2]")
            details["Genres"] = genres.text
        except NoSuchElementException:
            pass

        try:
            running_time = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[3]/div[4]/div[6]/span[2]")
            details["Running Time"] = running_time.text
        except NoSuchElementException:
            pass

        movie_details.append(details)

    driver.quit()

    return movie_details


def write_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
        print("Data written Successfully")


titles = get_top250_titles()

details = get_movies_details(titles[:100])

write_to_csv(details, 'movie_details.csv')
