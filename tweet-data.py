import tweepy
from wordcloud import WordCloud
import re
import matplotlib.pyplot as plt
import emoji
import click

# generate word cloud 
def wc(s) : 
    wordcloud = WordCloud().generate(s)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

def extract_emojis(str):
  return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)

def remove_urls(r : tweepy.cursor.ItemIterator):
    return " ".join([re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", tweet.full_text) 
                 for tweet in r
                    if "RT @" not in tweet.full_text])

@click.command(context_settings={'help_option_names':['-h','--help']})
@click.argument('username')
@click.argument('tweet_count')

def data_viz(username, tweet_count) :
    try :
        count = int(tweet_count)
    except ValueError :
        print("Invalid tweet count: {}".format(tweet_count))
        return

    client_id = "ZqT9qiED8ogLYdVLpK2nxVoCW"
    client_secret = "3skyBKuf9RJndvfcszRmKWZaRuNsxHAxpDQeKws4a2Il9B1w3S"
    access_key= '3343168235-39yNUvXmStC59DxI1rDXUGYvukbnX3xV9qYiB5p'
    access_secret = '3ynInkKMBBbaBatHyq5UgqQEwfbq1jPZh2xUMpvxFC7Ar'

    auth = tweepy.OAuthHandler(client_id, client_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    r = tweepy.Cursor(api.user_timeline, id=username, tweet_mode='extended').items(count)
    cloud_string = remove_urls(r)

    wc(cloud_string)

if __name__ == '__main__' :
    data_viz()