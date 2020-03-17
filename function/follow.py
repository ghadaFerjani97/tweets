##### fichier qui regroupe les fonctions pour analyser les follows

import time
import twint
import numpy as np
import tqdm


def following_list(users):
    start_time = time.time()
    followings = []

    for i in tqdm.tqdm(range(len(users))):
        user = users.screen_name[i]
        c = twint.Config()
        c.Username = user
        c.Hide_output = True
        c.Pandas = True
        c.Limit = 500
        twint.run.Followers(c)
        try:
            followed = twint.storage.panda.Follow_df["followers"].tolist()[0]
            twint.storage.panda.Follow_df = None
        except:
            followed = []
        followings.append(followed)
    print('time : ', time.time() - start_time)
    users['following'] = followings
    return users


def clean_following(users, users_tot):
    """return the following which are in users_tot only"""
    users_tot_cleaned = np.array([])
    for row in users.itertuples():
        users['following'].at[row.Index] = np.array(np.intersect1d(row.following, users_tot))
        users_tot_cleaned = np.concatenate((users_tot_cleaned,np.array(np.intersect1d(row.following, users_tot))))
    users_tot_cleaned = np.unique(users_tot_cleaned)

    return users, users_tot_cleaned
