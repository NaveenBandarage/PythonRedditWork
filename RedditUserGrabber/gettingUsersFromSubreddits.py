import csv
import time
from datetime import datetime
import pandas as pd
import sys
import sqlite3

import requests
#usage python3 gettingUsersFromSubreddits.py (subredditname) (#OfComments) (#dbName) (#dbTable)
sub = sys.argv[1]
SUBREDDITS = [sub]

HEADERS = {"User-Agent": "Comments Downloader v0.1"}
COMMENTS_LIST = list()

MAX_COMMENTS = sys.argv[2]


def init():

    for subreddit in SUBREDDITS:

        print("Downloading:", subreddit)
        load_comments(subreddit=subreddit)

        COMMENTS_LIST.clear()


dateList = []
usernameList = []
commentList = []


def load_comments(subreddit, latest_timestamp=None):

    base_url = "https://api.pushshift.io/reddit/comment/search/"

    params = {"subreddit": subreddit, "sort": "desc",
              "sort_type": "created_utc", "size": 500}

    # After the first call of this function we will use the 'before' parameter.
    if latest_timestamp != None:
        params["before"] = latest_timestamp

    with requests.get(base_url, params=params, headers=HEADERS) as response:
        try:
            json_data = response.json()
        except:
            print("json error")
        total_comments = len(json_data["data"])
        latest_timestamp = 0

        print("Downloading: {} comments".format(total_comments))

        for item in json_data["data"]:

            # We will only take 3 properties, the timestamp, author and body.

            latest_timestamp = item["created_utc"]

            iso_date = datetime.fromtimestamp(latest_timestamp)
            user = item["author"]
            comment = item["body"]
            dateList.append(iso_date)
            usernameList.append(user)
            commentList.append(comment)

            COMMENTS_LIST.append(
                [iso_date, item["author"], item["body"]])

        if len(COMMENTS_LIST) >= int(MAX_COMMENTS):
            print("Download complete.")
        else:
            time.sleep(1.2)
            load_comments(subreddit, latest_timestamp)


init()


data = {}
data['date'] = dateList
data['username'] = usernameList
data['comment'] = commentList
dfTest = pd.DataFrame(data)
print(dfTest)

dbName = sys.argv[3]
dbTableName = sys.argv[4]
try:
    sqliteConnection = sqlite3.connect(dbName)
    cursor = sqliteConnection.cursor()
    print("Successfully Connected to SQLite")
    dfTest.to_sql(dbTableName, sqliteConnection,
                  if_exists='replace', index=False)
    sqliteConnection.commit()
    print("Record inserted successfully into the database ", cursor.rowcount)
    rows = cursor.fetchall()

    for row in rows:
        print(row)
    cursor.close()

except sqlite3.Error as error:
    print("Failed to insert data into sqlite table", error)
finally:
    if (sqliteConnection):
        sqliteConnection.close()
        print("The SQLite connection is closed")
