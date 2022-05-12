import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

load_dotenv(dotenv_path="./.env")

df = pd.read_csv(filepath_or_buffer=os.getenv("CSV_FILE_PATH"))
linkedin_usernames = df['Linkedin_Company'].dropna()

options = Options()
driver = webdriver.Chrome(executable_path=os.getenv("DRIVER_PATH"), options=options)

driver.set_window_size(width=600, height=750)

driver.get("https://www.linkedin.com/")
driver.implicitly_wait(time_to_wait=5)
driver.find_element(
    by=By.ID,
    value="session_key"
).send_keys(os.getenv("LINKEDIN_USERNAME"))

driver.find_element(
    by=By.ID,
    value="session_password"
).send_keys(os.getenv("LINKEDIN_PASSWORD"))

driver.find_element(
    by=By.CSS_SELECTOR,
    value="button[type='submit']"
).click()
driver.implicitly_wait(5)

driver.execute_script("window.open('https://www.linkedin.com/');")


def scraper(index: int, linkedin_username) -> dict:
    driver.switch_to.window(driver.window_handles[index])
    driver.get(f'https://www.linkedin.com/company/{linkedin_username}')
    data = {}

    try:
        total_followers_count = driver.find_element(
            by=By.XPATH,
            value='/html/body/div[5]/div[3]/div/div[2]/div/div[2]/main/div[1]/section/div/div[2]/div[1]/div[1]/div[2]/div/div/div[2]/div[2]'
        )
        print(f"{linkedin_username} followers == {total_followers_count.text[:-10]}")
        data["followers_count"] = total_followers_count.text[:-10]
    except NoSuchElementException:
        data["followers_count"] = "Check Manually"

    try:
        total_followings_count = driver.find_element(
            by=By.ID,
            value='ember35'
        )
        following_text = total_followings_count.text
        following_text = following_text[8:]
        following_text = following_text[:-22]
        print(f"{linkedin_username} following == {following_text}")
        data["following_count"] = following_text
    except NoSuchElementException:
        data["following_count"] = "Check Manually"
    return data


all_data = np.array(["Name", "Web", "Linkedin Username", "Total Followers", "Total Following"], ndmin=2)
index_number = 1
for username in linkedin_usernames:
    if username != "":
        df_index_number = df[df['Linkedin_Company'] == username].index[0]
        single_data = np.empty(shape=[1, 5], dtype='<U100')
        single_data[0, 0] = df['Name'][df_index_number]
        single_data[0, 1] = df['Web'][df_index_number]
        single_data[0, 2] = df['Linkedin_Company'][df_index_number]

        if index_number % 2 == 1:
            single_data_set = scraper(index=0, linkedin_username=username)
            single_data[0, 3] = single_data_set["followers_count"]
            single_data[0, 4] = single_data_set["following_count"]
        elif index_number % 2 == 0:
            single_data_set = scraper(index=1, linkedin_username=username)
            single_data[0, 3] = single_data_set["followers_count"]
            single_data[0, 4] = single_data_set["following_count"]
        else:
            pass
        all_data = np.append(all_data, single_data, axis=0)
    else:
        pass
    index_number += 1
print(all_data)
new_dataframe = pd.DataFrame(data=all_data[1:], columns=all_data[0])
new_dataframe.to_csv("linkedin_result.csv", index=False)
driver.quit()
