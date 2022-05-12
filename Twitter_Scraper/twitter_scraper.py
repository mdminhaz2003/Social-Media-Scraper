import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

load_dotenv(dotenv_path="./.env")

df = pd.read_csv(filepath_or_buffer=os.getenv("CSV_FILE_PATH"))

twitter_username = df['Twitter_User'].dropna()

options = Options()
driver = webdriver.Chrome(executable_path=os.getenv("DRIVER_PATH"), options=options)
driver.get("https://www.twitter.com")
driver.implicitly_wait(time_to_wait=5)
driver.execute_script("window.open('');")


def scraper(index: int, single_twitter_username: str) -> dict:
    driver.switch_to.window(driver.window_handles[index])
    driver.get(f'https://www.twitter.com/{single_twitter_username}')
    driver.implicitly_wait(5)
    data = {}
    try:
        total_tweets_count = driver.find_element(
            by=By.XPATH,
            value='/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div[2]/div/div'
        )
        data["tweets_count"] = total_tweets_count.text
    except Exception as e:
        print(e)
        data["tweets_count"] = "Not Found"

    try:
        total_followings_count = driver.find_element(
            by=By.CSS_SELECTOR,
            value='a[href$="/following"]'
        )
        data["following_count"] = total_followings_count.text
    except Exception as e:
        print(e)
        data["following_count"] = "Not Found"

    try:
        total_followers_count = driver.find_element(
            by=By.CSS_SELECTOR,
            value='a[href$="/followers"]'
        )
        data["followers_count"] = total_followers_count.text
    except Exception as e:
        print(e)
        data["followers_count"] = "Not Found"
    return data


all_data = np.array(["Name", "Web", "Twitter Username", "Total Tweets", "Total Followers", "Total Following"], ndmin=2)
index_number = 1
for username in twitter_username:
    if username != "":
        df_index_number = df[df['Twitter_User'] == username].index[0]
        single_data = np.empty(shape=[1, 6], dtype='<U100')
        single_data[0, 0] = df['Name'][df_index_number]
        single_data[0, 1] = df['Web'][df_index_number]
        single_data[0, 2] = df['Twitter_User'][df_index_number]

        if index_number % 2 == 1:
            single_data_set = scraper(index=0, single_twitter_username=username)
            single_data[0, 3] = single_data_set["tweets_count"]
            single_data[0, 4] = single_data_set["followers_count"]
            single_data[0, 5] = single_data_set["following_count"]
        elif index_number % 2 == 0:
            single_data_set = scraper(index=1, single_twitter_username=username)
            single_data[0, 3] = single_data_set["tweets_count"]
            single_data[0, 4] = single_data_set["followers_count"]
            single_data[0, 5] = single_data_set["following_count"]
        else:
            pass
        all_data = np.append(all_data, single_data, axis=0)
    else:
        pass
    index_number += 1
print(all_data)
new_dataframe = pd.DataFrame(data=all_data[1:], columns=all_data[0])
new_dataframe.to_csv("twitter_result.csv", index=False)
driver.quit()
