# utils/encoding_utils.py
import pickle

ENCODINGS_PATH = 'encodings.pkl'

def load_encodings():
    try:
        with open(ENCODINGS_PATH, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

def save_encodings(encodings):
    with open(ENCODINGS_PATH, 'wb') as f:
        pickle.dump(encodings, f)
