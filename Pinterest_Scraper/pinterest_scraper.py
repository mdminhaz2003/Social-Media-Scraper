import os
import numpy
import asyncio
import aiohttp
import pandas
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv(dotenv_path="./.env")
df = pandas.read_csv(os.getenv(key="CSV_FILE_PATH"))
pinterest_usernames = df['Pinterest_User'].dropna()
new_data_set = numpy.array(["Name", "Web", "Pinterest Username", "Pinterest Followers", "Pinterest Following"], ndmin=2)


async def make_request(session: aiohttp.ClientSession, username: str) -> None:
    global new_data_set
    async with session.get(url=f"https://www.pinterest.com/{username}") as response:
        response_text = await response.read()

    try:
        soup = BeautifulSoup(response_text.decode('utf-8'), 'html.parser')
        followers_tag = soup.find(name='meta', property="pinterestapp:followers")["content"]
        following_tag = soup.find(name='meta', property="pinterestapp:following")["content"]
    except TypeError as unresolved_username:
        following_tag = "Not Found"
        followers_tag = "Not Found"
        print(unresolved_username)

    df_index_number = df[df['Pinterest_User'] == username].index[0]
    single_data = numpy.array([
        df['Name'][df_index_number],
        df['Web'][df_index_number],
        df['Pinterest_User'][df_index_number],
        followers_tag,
        following_tag
    ], ndmin=2)
    new_data_set = numpy.append(new_data_set, single_data, axis=0)


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session=session, username=username) for username in pinterest_usernames]
        await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
new_dataframe = pandas.DataFrame(data=new_data_set[1:], columns=new_data_set[0])
new_dataframe.to_csv("pinterest_result.csv", index=False)
