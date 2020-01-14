import click
import collections
import itertools
import matplotlib.pyplot as plt
import re
import pandas as pd
import tweepy
import matplotlib.backends.backend_pdf

from decimal import Decimal
from textblob import TextBlob
from wordcloud import WordCloud
from nltk.corpus import stopwords

client_id = "ZqT9qiED8ogLYdVLpK2nxVoCW"
client_secret = "3skyBKuf9RJndvfcszRmKWZaRuNsxHAxpDQeKws4a2Il9B1w3S"
access_key = '3343168235-39yNUvXmStC59DxI1rDXUGYvukbnX3xV9qYiB5p'
access_secret = '3ynInkKMBBbaBatHyq5UgqQEwfbq1jPZh2xUMpvxFC7Ar'

stop_words = set(stopwords.words('english'))


# generate word cloud
def wc(s, username, count):
    wordcloud = WordCloud().generate(s)
    fig = plt.figure()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.suptitle("Word Cloud of @" + username + "'s " + count + " Most Recent Tweets", fontsize=16)
    return fig

# generate word frequency plot
def word_frequency(tweets, username, count):
    list_of_tweets = remove_urls_to_list(tweets)
    words_by_tweet = [tweet.lower().split() for tweet in list_of_tweets]

    words_by_tweet_cleaned = [[w for w in words if not w in stop_words]
                              for words in words_by_tweet]

    all_words = list(itertools.chain(*words_by_tweet_cleaned))

    counts = collections.Counter(all_words)
    clean_tweets = pd.DataFrame(counts.most_common(20), columns=['words', 'count'])
    fig, ax = plt.subplots(figsize=(8, 8))

    clean_tweets.sort_values(by='count').plot.barh(x='words', y='count', ax=ax, color="blue")
    ax.set_title("Top 20 Words Found in the Most Recent " + count + " Tweets for @" + username)

    return fig


def get_sentiment(tweets):
    list_of_tweets = remove_urls_to_list(tweets)

    sentiment_list = [TextBlob(tweet) for tweet in list_of_tweets]

    positive = []
    negative = []
    neutral = []
    for sentiment in sentiment_list:
        if sentiment.polarity > 0:
            positive.append(sentiment)
        elif sentiment.polarity == 0:
            neutral.append(sentiment)
        else:
            negative.append(sentiment)

    pos_pt = "Positive tweets percentage: {} %".format(round(Decimal((100 * len(positive) / len(sentiment_list))), 2))\
             + "\n\n"
    most_pos = "Most positive tweet:\n\"" + max(str(p) for p in positive) + "\"\n\n"
    neg_pt = "Negative tweets percentage: {} %".format(round(Decimal((100 * len(negative) / len(sentiment_list))), 2))\
             + "\n\n"
    neg_pos = "Most negative tweet:\n\"" + max(str(n) for n in negative) + "\"\n\n"
    neut_pt = "Neutral tweets percentage: {} %".format(round(Decimal((100 * len(neutral) / len(sentiment_list))), 2))
    output_txt = pos_pt + most_pos + neg_pt + neg_pos + neut_pt

    return create_fig(output_txt)


def top_performer(tweets):
    no_rts = tweets[(tweets.text.str[0] != "@") & (tweets.text.str[:4] != "RT @")]
    no_rts.reset_index()

    no_rts = pd.concat([no_rts, (no_rts[no_rts.columns[-2:]]
                                 .sum(axis=1)
                                 .rename("sum"))],
                       axis=1)

    top = no_rts.loc[no_rts['sum'].idxmax()]

    output_txt = "top performing tweet:" \
                 "\n\"{}\"\n" \
                 "with a combined {} engagements\n".format(top['text'], top['sum'])

    return create_fig(output_txt)


def create_fig(text):
    fig = plt.figure()
    plt.axis('off')
    plt.text(0.5, 0.5, text, horizontalalignment='center', verticalalignment='center', wrap=True)
    return fig


def remove_urls_to_list(tweets):
    return [" ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", tweet).split())
            for tweet in tweets["text"].tolist()
            if "RT @" not in tweet]


def remove_urls(r):
    return " ".join([re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", tweet)
                     for tweet in r
                     if "RT @" not in tweet])


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument('username')
@click.argument('tweet_count')
def data_viz(username, tweet_count):
    try:
        count = int(tweet_count)
    except ValueError:
        print("Invalid tweet count: {}".format(tweet_count))
        return

    auth = tweepy.OAuthHandler(client_id, client_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    r = tweepy.Cursor(api.user_timeline, id=username, tweet_mode='extended', ).items(count)

    tweets = pd.DataFrame(columns=["text", "created_at", "RTs", "favs"],
                          data=[(tweet.full_text, tweet.created_at,
                                 tweet.retweet_count, tweet.favorite_count)
                                for tweet in r])

    # top performing tweet (highest combined RTs and favs)
    tp_fig = top_performer(tweets)

    # display positive, negative and neutral percentage of tweets in dataset
    sent_fig = get_sentiment(tweets)

    # generate plot of top 20 words that are used more frequently in dataset
    wf_fig = word_frequency(tweets, username, tweet_count)

    # generate word cloud with larger words appearing more often in dataset
    cloud_string = remove_urls(tweets["text"])
    wc_fig = wc(cloud_string, username, tweet_count)

    # output data into output.pdf
    pdf = matplotlib.backends.backend_pdf.PdfPages("output.pdf")
    pdf.savefig(tp_fig)
    pdf.savefig(sent_fig)
    pdf.savefig(wc_fig)
    pdf.savefig(wf_fig)
    pdf.close()


if __name__ == '__main__':
    data_viz()
