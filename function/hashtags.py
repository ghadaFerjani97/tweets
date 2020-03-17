##### fichier qui regroupe les fonctions sur l'analyse des hashtags

import numpy as np
from collections import Counter
import pandas as pd


def entropy_hashtags(users):
    # calcul de l'entropie
    users['hashtag_entropy'] = users.hashtags.apply(lambda x: np.array(x))
    users['hashtag_entropy'] = users.hashtags.apply(
        lambda x: (np.unique(x, return_counts=True)[1]) / (np.unique(x, return_counts=True)[1]).sum())
    users['hashtag_entropy'] = users.hashtag_entropy.apply(lambda x: -np.sum(x * np.log2(x)))
    print(users.hashtag_entropy)
    return users


def most_frequent(List):
    # fonction que sélectionne l'élement le plus fréquent d'une liste
    if List is np.nan:
        return None
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]


def politic_affinity(users, entropy_limit=1):
    # en fonction de la limite de l'entropie, on affecte une affinité politique
    affinity = users[users.hashtag_entropy < 1]
    affinity['politic_affinity'] = affinity.hashtags.apply(most_frequent)
    users['politic_affinity'] = users.user_id.map(
        pd.Series(index=affinity.user_id, data=affinity.politic_affinity.values))
    users = users.astype(object).replace(np.nan, 'None')
    return users
