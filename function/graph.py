###### fichier qui regroupe les fonctions pour faire les graphes

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# def louvain_community():


def write_retweets_gml(tweets, users, affinity = True):
    # on réduit la table des tweets: on garde les users qui ont une affinité
    if affinity:
        users = users[~users.politic_affinity.isin(['None'])]
    # on nettoie les tweets, on ne garde que les tweets retweeters/retweeteurs par la table des users
    tweets = tweets[tweets.retweeted_user_id.isin(users.user_id.values)]
    tweets = tweets[tweets.user_id.isin(users.user_id.values)]
    tweets = tweets[~tweets.retweeted_user_id.isin([None])]
    retweets_unique = pd.DataFrame({'weight' : tweets[['user_id','retweeted_user_id','tweet_id']].groupby( ['user_id', 'retweeted_user_id'] ).size()}).reset_index()
    retweets_unique.drop_duplicates()
    users_unique = np.unique(
        np.concatenate((retweets_unique.user_id.unique(), retweets_unique.retweeted_user_id.unique())))
    users = users[users.user_id.isin(users_unique)]
    with open('./data/retweets1.gml', 'w') as f:
        f.write("graph\n[\nmultigraph 1\n")
        for user in users.itertuples():
            # on écrit les noeuds du graphe
            f.write("  node\n  [\n")
            f.write("   id %s\n" % user.user_id)
            # f.write("   category %s\n" %user.category)
            #f.write("   politic_affinity %s\n" % user.politic_affinity)
            #f.write("   louvain %s\n" % user.louvain)
            f.write("  ]\n")
        for retweet in retweets_unique.itertuples():
            # on écrit les liaisons
            f.write("  edge\n  [\n")
            f.write("   source %s\n" % retweet.retweeted_user_id)
            f.write("   target %s\n" % retweet.user_id)
            #f.write("   weight %s\n"% retweet.weight)
            f.write("  ]\n")
        f.write("]\n")
    return

#inutile pour le moment
def write_mentions_gml(tweets_mentions, users):
    users_unique = np.unique(
        np.concatenate((tweets_mentions.source_user_id.unique(), tweets_mentions.target_user_id.unique())))
    users = users[users.user_id.isin(users_unique)]

    with open('./data/retweets.gml', 'w') as f:
        f.write("Creator \"Retweets\"\n")
        f.write("graph\n[\n")
        for user in users.itertuples():
            f.write("  node\n  [\n")
            f.write("   id %s\n" % user.user_id)
            # f.write("   category %s\n" %user.category)
            # f.write("   politic_affinity %s\n" %user.affinity)
            f.write("  ]\n")
        for retweet in tweets_mentions.itertuples():
            f.write("  edge\n  [\n")
            f.write("   source %s\n" % retweet.source_user_id)
            f.write("   target %s\n" % retweet.target_user_id)
            f.write("   weight 1\n")
            f.write("  ]\n")
        f.write("]\n")

# fonctionnel, mais le contenu: la table de followers ne l'est pas
def write_followers_gml(followers, users):
    with open('./following3.gml', 'w') as f:
        f.write("Creator \"Following\"\n")
        f.write("graph\n[\n")
        for user in users:
            f.write("  node\n  [\n")
            f.write("   id %s\n" % user)
            f.write("  ]\n")
        for row in followers.itertuples():
            fols = row.following
            for fol in fols:
                f.write("  edge\n  [\n")
                f.write("   source %s\n" % row.screen_name)
                f.write("   target %s\n" % fol)
                f.write("   weight 1\n")




