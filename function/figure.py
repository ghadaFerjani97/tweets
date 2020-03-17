import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np
from sklearn.preprocessing import StandardScaler


def scatterplot(df, columns1, columns2, title=None, filename=None):
    df = df.astype(object).replace('None', 0)
    plt.scatter(df[columns1], df[columns2])
    plt.ylabel(columns2)
    plt.xlabel(columns1)
    #plt.legend()
    if title is not None:
        plt.title(title)
    if filename is not None:
        plt.savefig('./figures/%s.png' % filename)
    plt.show()

def scatterplot_cluster(df, columns1, columns2, title=None, filename=None):
    df = df.astype(object).replace('None', 0)
    for c_id in df.cluster_id.unique():
        plt.scatter(df[df.cluster_id == c_id][columns1], df[df.cluster_id == c_id][columns2])
    plt.ylabel(columns2)
    plt.xlabel(columns1)
    #plt.legend()
    if title is not None:
        plt.title(title)
    if filename is not None:
        plt.savefig('./figures/%s.pdf' % filename)
    plt.show()

# pareil que l'autre, mais pour toutes les donénes c'est trop long car il y a trop de bins sur l'histogramme
def hist_followers_tweet(users):
    text_box = []
    paliers = [0, 100, 500, 1000, 2000]
    for i in range(len(paliers) - 1):
        num_of_tweets = users[users.followers_count <= paliers[i + 1]]
        num_of_tweets = num_of_tweets[users.followers_count >= paliers[i]].shape[0]
        pc_of_tweets = 100.0 * num_of_tweets / users.shape[0]
        text_box.append(
            'Users with %d <= tweets <= %d: %d  (%f )' % (paliers[i], paliers[i + 1], num_of_tweets, pc_of_tweets))

    num_of_tweets = users[users.followers_count >= paliers[-1]].shape[0]
    pc_of_tweets = 100.0 * num_of_tweets / users.shape[0]
    text_box.append('Users with tweets >= %d: %d  (%f )' % (paliers[-1], num_of_tweets, pc_of_tweets))
    min_value = users.followers_count.values.min()
    max_value = users.followers_count.values.max()
    fig, ax = plt.subplots()
    bincuts = np.linspace(start=min_value - 0.5, stop=max_value + 0.5, num=(max_value - min_value + 2), endpoint=True)
    ax.grid()
    users['followers_count'] = users.followers_count.apply(lambda x: round(x, -4))
    print(users.followers_count.values)
    ax.hist(users.followers_count.values, bins=bincuts, edgecolor='black', linewidth=0.8, zorder=3)
    ax.set_xscale("log", nonposx='clip')
    ax.set_yscale("log", nonposy='clip')
    props = dict(boxstyle='round', facecolor='wheat', alpha=1.0)
    ax.text(0.35, 0.9, '\n'.join(text_box), transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    plt.xlabel('Number of Followers')
    plt.ylabel('Number of Users')
    plt.show()
    plt.savefig('./figures/hist_user_nb_followers.pdf')
    plt.clf()
    plt.close()


def hist_user_tweet(users):
    text_box = []
    paliers = [0, 10, 30, 50, 100, 200]
    # pour faire le résumé de l'histogramme: on compte le nb de user dans chaque tranche définie dans paliers
    for i in range(len(paliers) - 1):
        num_of_tweets = users[users.nb_tweets <= paliers[i + 1]]
        num_of_tweets = num_of_tweets[users.nb_tweets >= paliers[i]].shape[0]
        pc_of_tweets = 100.0 * num_of_tweets / users.shape[0]
        text_box.append(
            'Users with %d <= tweets <= %d: %d  (%f )' % (paliers[i], paliers[i + 1], num_of_tweets, pc_of_tweets))

    num_of_tweets = users[users.nb_tweets >= paliers[-1]].shape[0]
    pc_of_tweets = 100.0 * num_of_tweets / users.shape[0]
    text_box.append('Users with tweets >= %d: %d  (%f )' % (paliers[-1], num_of_tweets, pc_of_tweets))

    # mise en forme de l'histogramme
    min_value = users.nb_tweets.values.min()
    max_value = users.nb_tweets.values.max()
    fig, ax = plt.subplots()
    bincuts = np.linspace(start=min_value - 0.5, stop=max_value + 0.5, num=(max_value - min_value + 2), endpoint=True)
    ax.grid()
    ax.hist(users.nb_tweets.values, bins=bincuts, edgecolor='black', linewidth=0.8, zorder=3)
    ax.set_xscale("log", nonposx='clip')
    ax.set_yscale("log", nonposy='clip')
    props = dict(boxstyle='round', facecolor='wheat', alpha=1.0)
    ax.text(0.35, 0.9, '\n'.join(text_box), transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    plt.xlabel('Number of Tweets')
    plt.ylabel('Number of Users')
    plt.show()
    plt.savefig('./figures/hist_user_nb_tweets.pdf')
    plt.clf()
    plt.close()


def supervised(df, features, n_cluster=3, normalize=True):
    df = df.copy(deep=True)
    if normalize == True:
        normalized_ = [feature + '_normalized' for feature in features]
        df[normalized_] = normalization(df, features)
    kmeans = KMeans(n_clusters=n_cluster, random_state=0).fit(df[normalized_])
    df['supervised_cluster_id'] = kmeans.labels_

    return df['supervised_cluster_id']


def normalization(df, features):
    scaler = StandardScaler()
    df[features] = df[features].astype(np.float64)
    df[features] = scaler.fit_transform(df[features])
    return df[features];
