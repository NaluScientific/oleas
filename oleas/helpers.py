import pickle


def save_pickle(obj, path):
    try:
        with open(path, 'wb') as f:
            pickle.dump(obj, f)
    except:
        raise
