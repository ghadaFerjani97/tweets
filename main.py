from function.graph import * # fichier qui regroupe les fonctions pour faire les graphes
from function.follow import *  # fichier qui regroupe les fonctions sur les follows
from function.hashtags import * # fichier qui regoupe les fonctions pour analyser les hashtags
from function.figure import *
from function.recover import get_dataframe_from_table
import community
import networkx as nx

# sélectionner les parties de l'analyse que l'on veut effectuer

part_retweets = True
part_figure = True
part_hashtags = True
part_hashtags2 = True

# définition à la main du dictionnaire pour rassembler les hashtags sur un hashtag commun
dict_candidat = {'macron': ['macron', 'EnMarche', 'MacronBercy', 'JeVoteMacron', 'Macron2017'],
                 'fillon': ['fillon', 'Fillon2017', 'JeVoteFillon', 'FillonPresident'],
                 'jlm': ['JLM2017', 'Mélenchon', 'LaForcedupeuple', 'JLMToulouse', 'AuNomDuPeuple', 'FranceInsoumise'],
                 'lepen': ['Marine2017', 'LePen', 'MarineLePen', 'MarineÀParis'],
                 'hamon': ['Hamon2017', 'Hamon']}
index_cand = np.concatenate(list(dict_candidat.values()))
data_cand = ['macron']*5 + ['fillon']*4 + ['jlm']*6 + ['lepen']*4 + ['hamon']*2

# recover data
users = get_dataframe_from_table("users_0415_0423")

# compute number of tweet per user
tweets = get_dataframe_from_table("tweets_0415_0423",columns = ['tweet_id','user_id'])
tweets['nb_tweets'] = pd.Series(np.ones(tweets.shape[0])).values
tweets_count = tweets[['user_id', 'nb_tweets']].groupby('user_id').count()
users['nb_tweets'] = users.user_id.map(pd.Series(index=tweets_count.index, data=tweets_count.nb_tweets))

# select users with more than 100 tweets
users_reduced = users[users.nb_tweets > 100]

# recover data about media
media = get_dataframe_from_table("medias_0415_0423")

if part_hashtags:
    # recover tweets and hashtags data
    hashs = get_dataframe_from_table("hashs_0415_0423")
    hash_tweets = get_dataframe_from_table("tweet_hash_0415_0423")
    tweets = get_dataframe_from_table("tweets_0415_0423",columns = ['tweet_id','user_id'])

    # add column containing hashtag content in hash_tweets
    hashs['hash_id'] = hashs['hash_id'].apply(int)
    hash_tweets['hash'] = hash_tweets.hash_id.map(pd.Series(index=hashs.hash_id.values, data=hashs.hash.values))

    # on garde les hashtags qui sont dans le dictionnaire défini au début
    hash_tweets = hash_tweets[hash_tweets.hash.isin(np.concatenate(list(dict_candidat.values())))]
    # ajout d'une colonne pour le user qui a écrit le hashtag
    hash_tweets['user_id'] = hash_tweets.tweet_id.map(pd.Series(index = tweets.tweet_id.values, data = tweets.user_id.values))

    # on regroupe les hashtags ( jlm,jlm2017,jlmToulouse ---> jlm)
    hash_tweets['hash_simplified'] = hash_tweets.hash.map(pd.Series(index=index_cand, data=data_cand))

    #on sélectionne les hashtags des users qui ont au moins 100 tweets
    hash_tweets = hash_tweets[hash_tweets.user_id.isin(users_reduced.user_id.values)]
    tmp = hash_tweets[['user_id','hash_simplified']].groupby('user_id').hash_simplified.apply(list)

    #on ajoute une colonne dans la table des users, contenant les hashtags qu'ils ont écrit
    users_reduced['hashtags'] = users_reduced.user_id.map(tmp)
    # calcul de l'entropie
    users_reduced = entropy_hashtags(users_reduced)
    # définition de l'affinité politique
    users_reduced = politic_affinity((users_reduced))


if part_retweets:
    # on récupere la table des tweets avec les informations sur les retweets
    tweets = get_dataframe_from_table("tweets_0415_0423",
                                    columns=['tweet_id', 'user_id', 'retweeted_status_id', 'retweeted_user_id'])
    #calcul de nombre de fois qu'une personne est retweetée
    retweeted_count = tweets[['user_id','retweeted_user_id']].groupby('retweeted_user_id').count()
    users_reduced['retweeted_count'] = users_reduced.user_id.map(pd.Series(index=retweeted_count.index, data=retweeted_count.user_id.values))

    #calcul du nombre de fois qu'un user retweet
    retweeter_count = tweets[~tweets.retweeted_user_id.isin([None])][['user_id','retweeted_user_id']].groupby('user_id').count()
    users_reduced['retweeter_count'] = users_reduced.user_id.map(pd.Series(index=retweeter_count.index, data=retweeter_count.retweeted_user_id.values))

    users_reduced = users_reduced.astype(object).replace('None',0) # on remplace les np.nan par des None
    users_reduced = users_reduced.astype(object).replace(np.nan,0) # on remplace les np.nan par des None

    # partitionnement par rapport aux nb tweets, retweeted/retweeter count en utilisant KMeans
    users_reduced['cluster_id'] = supervised(users_reduced,['nb_tweets','retweeter_count','retweeted_count'])


if part_figure:
    hist_user_tweet(users)
    scatterplot(users_reduced,'followers_count','nb_tweets',title='scatterplot',filename='nb_foll_nb_tweets_scatter')
    scatterplot_cluster(users_reduced,'nb_tweets','retweeted_count',title='scatterplot_cluster',filename='cluster_nb_tweets_retweeted_scatter')
    # on écrit le fichier de graphe des retweets
    write_retweets_gml(tweets, users_reduced)
    G = nx.read_gml('./data/retweets1.gml',label=None)
    partition = community.best_partition(G)
    users_reduced['louvain'] = users_reduced.user_id.map(pd.Series(index = list(partition.keys()),data = list(partition.values())))

users_final = users_reduced[~users_reduced.louvain.isin([np.nan])]



def hist_hashtags(df,filename = None):
    """calcule l'hist des hashtags pour une df"""
    flatten = lambda l: [item for sublist in l for item in sublist]
    hashtags = pd.Series(flatten(list(df.hashtag_origin.values)))
    hist = hashtags.value_counts()[:15].plot(kind='bar')
    hist.set_xticklabels(hist.get_xticklabels(), rotation=45, horizontalalignment='right')
    if filename is not None:
        plt.savefig('./figures/%s.pdf'%filename,bbox_inches='tight')

def moy_hashtag(df,hashtag):
    """calcule la fréquence d'apparation du hashtags dans les tweets pour chaque user"""
    bool_hash = df.hashtag_origin.apply(lambda x: hashtag in x)
    bool_hash = bool_hash[bool_hash == True]
    res = len(bool_hash)/len(df)
    return res

if part_hashtags2:
    # recover tweets and hashtags data
    hashs = get_dataframe_from_table("hashs_0415_0423")
    hash_tweets = get_dataframe_from_table("tweet_hash_0415_0423")
    tweets = get_dataframe_from_table("tweets_0415_0423",columns = ['tweet_id','user_id'])

    # add column containing hashtag content in hash_tweets
    hashs['hash_id'] = hashs['hash_id'].apply(int)
    hash_tweets['hash'] = hash_tweets.hash_id.map(pd.Series(index=hashs.hash_id.values, data=hashs.hash.values))

    # ajout d'une colonne pour le user qui a écrit le hashtag
    hash_tweets['user_id'] = hash_tweets.tweet_id.map(pd.Series(index = tweets.tweet_id.values, data = tweets.user_id.values))

    #on sélectionne les hashtags des users qui ont au moins 100 tweets
    hash_tweets = hash_tweets[hash_tweets.user_id.isin(users_final.user_id.values)]
    tmp = hash_tweets[['user_id','hash']].groupby('user_id').hash.apply(list)

    #on ajoute une colonne dans la table des users, contenant les hashtags qu'ils ont écrit
    users_final['hashtag_origin'] = users_reduced.user_id.map(tmp)


    contre_fillon = users_final[users_final.louvain == 0]
    pour_macron = users_final[users_final.louvain == 1]
    contre_macron = users_final[users_final.louvain == 4][users_final.politic_affinity== 'macron']
    pour_fillon = users_final[users_final.louvain == 4][users_final.politic_affinity== 'fillon']




