import tweepy
from wordcloud import WordCloud
import re
import regex
import matplotlib.pyplot as plt
import emoji
import click
import pandas as pd

# generate word cloud 
def wc(s) : 
    wordcloud = WordCloud().generate(s)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

def fav_emoji(lst):
    emojis = [word for word in regex.findall(r'\X', " ".join(lst))
            if any(char in emoji.UNICODE_EMOJI for char in word)]
    fave = max(set(emojis), key=emojis.count)
    count = emojis.count(fave)
    return fave, count

def remove_urls(r):
    return " ".join([re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", tweet) 
                 for tweet in r
                    if "RT @" not in tweet])

def top_performer(tweets) :
    no_rts = tweets[(tweets.text.str[0] != "@") & (tweets.text.str[:4] != "RT @")]
    no_rts.reset_index()

    no_rts = pd.concat([no_rts, (no_rts[no_rts.columns[-2:]]
                    .sum(axis=1)
                    .rename("sum"))],
               axis=1)
    
    top = no_rts.loc[no_rts['sum'].idxmax()]
    return top['text'], top['sum']

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

    tweets = pd.DataFrame(columns=["text", "geo", "created_at", "RTs", "favs"],
                data=[(tweet.full_text, tweet.geo, tweet.created_at, 
                        tweet.retweet_count, tweet.favorite_count) 
                         for tweet in r])

    cloud_string = remove_urls(tweets["text"])

    wc(cloud_string)

    # most used emoji
    emoji, count = fav_emoji(tweets["text"])
    print("favorite emoji: {} \nused {} times\n".format(emoji, count))

    # top performing tweet (highest combined RTs and favs)
    top, engagements = top_performer(tweets)
    print("top performing tweet:"
            "\n\"{}\"\n"
            "with a combined {} engagements\n".format(top, engagements))

if __name__ == '__main__' :
    data_viz()