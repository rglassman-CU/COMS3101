import tweepy
from wordcloud import WordCloud
import re
import matplotlib.pyplot as plt

# generate word cloud 
def wc(s) : 
    wordcloud = WordCloud().generate(s)
    # Display the generated image:
    # the matplotlib way:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    # plt.figure()
    plt.show()

def remove_urls(r : tweepy.cursor.ItemIterator):
    return " ".join([re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", tweet.full_text) 
                 for tweet in r
                    if "RT @" not in tweet.full_text])

client_id = "ZqT9qiED8ogLYdVLpK2nxVoCW"
client_secret = "3skyBKuf9RJndvfcszRmKWZaRuNsxHAxpDQeKws4a2Il9B1w3S"
access_key= '3343168235-39yNUvXmStC59DxI1rDXUGYvukbnX3xV9qYiB5p'
access_secret = '3ynInkKMBBbaBatHyq5UgqQEwfbq1jPZh2xUMpvxFC7Ar'

auth = tweepy.OAuthHandler(client_id, client_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

r = tweepy.Cursor(api.user_timeline, id='realdonaldtrump', tweet_mode='extended').items(500)
cloud_string = remove_urls(r)

wc(cloud_string)