import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

load_dotenv(dotenv_path="./.env")

df = pd.read_csv(filepath_or_buffer=os.getenv("CSV_FILE_PATH"))
facebook_page_usernames = df['Facebook_Page'].dropna()

chrome_options = uc.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
driver = uc.Chrome(executable_path=os.getenv("DRIVER_PATH"), options=chrome_options)

driver.set_window_size(width=600, height=750)

driver.get("https://www.facebook.com/login/")
email_input_field_finder = ec.presence_of_element_located(
    (By.ID, "email")
)

password_input_field_finder = ec.presence_of_element_located(
    (By.ID, "pass")
)

login_button_finder = ec.presence_of_element_located(
    (By.ID, "loginbutton")
)

email_input_field = WebDriverWait(driver=driver, timeout=10).until(method=email_input_field_finder)
password_input_field = WebDriverWait(driver=driver, timeout=10).until(method=password_input_field_finder)
login_button = WebDriverWait(driver=driver, timeout=10).until(method=login_button_finder)

email_input_field.send_keys(os.getenv("FACEBOOK_EMAIL"))
password_input_field.send_keys(os.getenv("FACEBOOK_PASSWORD"))

login_button.click()
driver.implicitly_wait(time_to_wait=5)
driver.execute_script("window.open('https://www.facebook.com/');")


def first_page_scraper(index: int, facebook_page_username: str) -> dict:
    driver.switch_to.window(driver.window_handles[index])
    driver.get(f'https://www.facebook.com/{facebook_page_username}')
    data = {
        "Page_Likes": "Manual Check",
        "Page_Followers": "Manual Check",
        "Page_Checked": "Manual Check"
    }

    try:
        all_tags = ec.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                'span.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.b0tq1wua.a8c37x1j.fe6kdd0r.mau55g9w.c8b282yb.keod5gw0'
                '.nxhoafnm.aigsh9s9.d9wwppkn.hrzyx87i.jq4qci2q.a3bd9o3v.b1v8xokw.oo9gr5id.hzawbc8m '
            )
        )
        all_tags_list = WebDriverWait(driver=driver, timeout=10).until(method=all_tags)
        for x in all_tags_list:
            if x is not None:
                if "people like this" in x.text:
                    print(f"{facebook_page_username} likes == {x.text[:-17]}")
                    data["Page_Likes"] = x.text[:-17]
                elif "people follow this" in x.text:
                    print(f"{facebook_page_username} followers == {x.text[:-19]}")
                    data["Page_Followers"] = x.text[:-19]
                elif "people checked in here" in x.text:
                    print(f"{facebook_page_username} checked == {x.text[:-23]}")
                    data["Page_Checked"] = x.text[:-23]
                else:
                    continue
            else:
                continue
    except TimeoutException as time_out_exception:
        print(time_out_exception)
    return data


def second_page_scraper(index: int, facebook_page_username: str) -> dict:
    driver.switch_to.window(driver.window_handles[index])
    driver.get(f'https://www.facebook.com/{facebook_page_username}')
    data = {
        "Page_Likes": "Manual Check",
        "Page_Followers": "Manual Check",
        "Following": "Manual Check"
    }

    try:
        all_tags = ec.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                'a.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5'
                '.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl'
                '.gpro0wi8.m9osqain.lrazzd5p '
            )
        )
        all_tags_list = WebDriverWait(driver=driver, timeout=10).until(method=all_tags)
        for x in all_tags_list:
            if x is not None:
                if "followers" in x.text:
                    print(f"{facebook_page_username} followers == {x.text}")
                    data["Page_Followers"] = x.text
                elif "following" in x.text:
                    print(f"{facebook_page_username} followers == {x.text}")
                    data["Following"] = x.text
                elif "likes" in x.text:
                    print(f"{facebook_page_username} likes == {x.text}")
                    data["Page_Likes"] = x.text
                else:
                    continue
            else:
                continue
    except TimeoutException as time_out_exception:
        print(time_out_exception)
    return data


all_data = np.array(["Name", "Web", "Facebook Page Username", "Page Followers", "Following", "Page Likes", "Page Checked"], ndmin=2)
index_number = 1
for username in facebook_page_usernames:
    if username != "":
        df_index_number = df[df['Facebook_Page'] == username].index[0]
        single_data = np.empty(shape=[1, 7], dtype='<U100')
        single_data[0, 0] = df['Name'][df_index_number]
        single_data[0, 1] = df['Web'][df_index_number]
        single_data[0, 2] = df['Facebook_Page'][df_index_number]

        if index_number % 2 == 1:
            single_data_set = first_page_scraper(index=0, facebook_page_username=username)
            single_data[0, 3] = single_data_set["Page_Followers"]
            single_data[0, 5] = single_data_set["Page_Likes"]
            single_data[0, 6] = single_data_set["Page_Checked"]
        elif index_number % 2 == 0:
            single_data_set = first_page_scraper(index=1, facebook_page_username=username)
            single_data[0, 3] = single_data_set["Page_Followers"]
            single_data[0, 5] = single_data_set["Page_Likes"]
            single_data[0, 6] = single_data_set["Page_Checked"]
        else:
            pass
        all_data = np.append(all_data, single_data, axis=0)
    else:
        pass
    index_number += 1
for skip_data in all_data:
    if skip_data[3] == "Manual Check":
        if index_number % 2 == 1:
            single_data_set = second_page_scraper(index=0, facebook_page_username=skip_data[2])
            skip_data[3] = single_data_set["Page_Followers"]
            skip_data[4] = single_data_set["Following"]
            skip_data[5] = single_data_set["Page_Likes"]
        elif index_number % 2 == 0:
            single_data_set = second_page_scraper(index=1, facebook_page_username=skip_data[2])
            skip_data[3] = single_data_set["Page_Followers"]
            skip_data[4] = single_data_set["Following"]
            skip_data[5] = single_data_set["Page_Likes"]
        else:
            pass
    else:
        pass
    index_number += 1

for skip_data in all_data:
    if skip_data[3] == "Manual Check":
        if index_number % 2 == 1:
            single_data_set = first_page_scraper(index=0, facebook_page_username=skip_data[2])
            skip_data[3] = single_data_set["Page_Followers"]
            skip_data[5] = single_data_set["Page_Likes"]
            skip_data[6] = single_data_set["Page_Checked"]
        elif index_number % 2 == 0:
            single_data_set = first_page_scraper(index=1, facebook_page_username=skip_data[2])
            skip_data[3] = single_data_set["Page_Followers"]
            skip_data[5] = single_data_set["Page_Likes"]
            skip_data[6] = single_data_set["Page_Checked"]
        else:
            pass
    else:
        pass
    index_number += 1

for skip_data in all_data:
    if skip_data[3] == "Manual Check":
        if index_number % 2 == 1:
            single_data_set = second_page_scraper(index=0, facebook_page_username=skip_data[2])
            skip_data[3] = single_data_set["Page_Followers"]
            skip_data[4] = single_data_set["Following"]
            skip_data[5] = single_data_set["Page_Likes"]
        elif index_number % 2 == 0:
            single_data_set = second_page_scraper(index=1, facebook_page_username=skip_data[2])
            skip_data[3] = single_data_set["Page_Followers"]
            skip_data[4] = single_data_set["Following"]
            skip_data[5] = single_data_set["Page_Likes"]
        else:
            pass
    else:
        pass
    index_number += 1

new_dataframe = pd.DataFrame(data=all_data[1:], columns=all_data[0])
new_dataframe.to_csv("facebook_page_result.csv", index=False)
driver.quit()
