import datetime
import sqlite3

import ffn
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# python3 databaseName.db databaseTableName
database = sys.argv[1]
databaseTable = sys.argv[2]

# Reading to the database
conn = sqlite3.connect(database)

cur = conn.cursor()
cur.execute("SELECT * FROM " + databaseTable)

rows = cur.fetchall()

for row in rows:
    print(row)

# Converting to Dataframe
df = pd.DataFrame(rows, columns=["id", "title", "url", "date", "flair"])
print(df)

conn.close()

data = {}
ids = []
titles = []
urls = []
dates = []
flairs = []
for stat in subStats:
    for items in subStats[stat]:
        ids.append(items[0])
        titles.append(items[1])
        urls.append(items[2])
        dates.append(items[5])
        flairs.append(items[8])

data["id"] = ids
data["title"] = titles
data["url"] = urls
data["date"] = dates
data["flair"] = flairs
dataFrame = pd.DataFrame(data)
# dataFrame=dataFrame[dataFrame['flair']=='BTC']
# need to look at this https://towardsdatascience.com/scraping-reddit-data-1c0af3040768 properly
analyser = SentimentIntensityAnalyzer()

scores = []
# print(data['title'])
# print(data['date'])

for title in data["title"]:
    sentiment_score = 0
    try:
        for word in title:
            sentiment_score = (sentiment_score +
                               analyser.polarity_scores(word)["compound"])
    except TypeError:
        print("Error")
        sentiment_score = 0

    scores.append(sentiment_score)
print((scores))

dataFrame["sentiment score"] = scores

dataFrame.index = dataFrame["date"]
# dataFrame=dataFrame.set_index('date', inplace=True)
dataFrame = dataFrame.resample("D").mean()

btc_data = pdr.get_data_yahoo(
    ["BTC-USD"],
    start=datetime.datetime(2020, 1, 1),
    end=datetime.datetime(2020, 12, 29),
)["Close"]

print(btc_data["BTC-USD"])
x = dataFrame.index
y = dataFrame["sentiment score"]
print(x)
print(y)

plt.subplots(figsize=(30, 6))  # changing this helped with visualising

plt.plot(x, y)
# could pass these as parameters to help with the graphing not sure if this is the right approach.
plt.xlabel("Date")
plt.ylabel("Sentiment Score")  # same with this as well.
# plt.set_xlabel('date')
ax2 = plt.twinx()  # instantiate a second axes that shares the same x-axis
ax2.set_ylabel("Price")
ax2.set_xlabel("Date")
ax2.plot(btc_data, color="orange")
