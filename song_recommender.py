import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from tqdm.auto import tqdm

class SongRecommender:

    def __init__(self):
        self.df = pd.DataFrame()
        self.track_ids = []
        self.sp = spotipy.Spotify()
        self.feats_lst = []

    def read_track_ids(self, filepath):
        with open(filepath) as f:
            content = f.readlines()
        self.track_ids = [x.strip() for x in content]

    def setup_credentials(self, c_id, c_se):
        self.c_id = c_id
        self.c_se = c_se

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(client_id=c_id,
                                                  client_secret=c_se))

    def audio_features_from_track_id(self, track_id):
        return self.sp.audio_features(track_id)[0]

    def feature_df_from_track_ids(self, progress_off=False):
        self.feats_lst = [self.audio_features_from_track_id(id_) for id_ in
                     tqdm(self.track_ids, disable=progress_off)]

    def df_from_feats_lst(self):
        self.df = pd.DataFrame(feats_lst)

    def create_df(self, filepath, to_pkl=False):
        self.read_track_ids(filepath)
        self.feature_df_from_track_ids()
        self.df_from_feats_lst()
        if to_pkl:
            pd.to_pickle("data/full_df.pkl")