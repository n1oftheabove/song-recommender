import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

class SongCollector:
    def __init__(self):
        self.playlist_ids = []
        self.categories = []
        self.category_ids = []
        self.c_id = ""
        self.c_se = ""
        self.sp = spotipy.Spotify()
        self.tracks = []
        self.track_ids = []
        self.album_uris = []
        self.track_ids_for_all_albums_found = []

    def setup_credentials(self, c_id, c_se):
        self.c_id = c_id
        self.c_se = c_se

        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=c_id, client_secret=c_se))

    def load_playlist_ids(self, playlist_ids):
        self.playlists = playlist_ids

    def perform_full_take(self, deep_lookup=False, to_pkl=False):
        """Performs a 'full take' of as many songs that can be found via the
         spotify API.

        Starting from Spotify's categories, all category ids are collected. For
         those, all associated playlist ids are collected and ultimately in each
          of those playlists all unique track ids are collected.

        If the argument `deep_lookup` is set to True, in a next step for every
        found track id the associated album id is searched and the track ids of
         those are also added.

        Parameters
        ----------
        deep_lookup : bool, optional
            toggles whether deep lookup should be performed

        to_pkl : bool, optional
            toggles whether track ids should be saved to .pkl file in ./data

        """

        # check for sane credentials
        self.check_authmanager()

        # get all available category id's
        self.category_ids = [cat['id']
                             for cat in self.sp.categories()['categories']['items']]

        # now get & save all playlist id's from those categories
        for cat_id in self.category_ids:
            # catch HTTP error for some categories
            try:
                pl_per_category_json = self.sp.category_playlists(cat_id)[
                    'playlists']['items']
            except spotipy.client.SpotifyException as e:
                continue

            for pl in pl_per_category_json:
                try:
                    id_ = pl['id']
                except TypeError:
                    continue
                self.playlist_ids.append(f"spotify:playlist:{id_}")

        # populating the track_id's with the tracks found in the playlist_ids
        for playlist_id in self.playlist_ids:
            self.track_ids.extend(
                self.get_track_ids_from_playlist_id(playlist_id))

        self.track_ids = list(set(self.track_ids))
        print(f"{len(self.track_ids)} unique track ids found")

        # if deep_lookup
        if deep_lookup:
            print("starting deep lookup...")
            print("now getting all album ids for every song")
            for track_id in tqdm(self.track_ids):
                self.album_uris.append(sp.track(track_id)['album']['uri'])

            self.album_uris = list(set(self.album_uris))
            print(f"{len(self.album_uris)} unique album uris found")
            print("----")
            print("Getting all the songs from those uris")

            self.track_ids_for_all_albums_found = list(
                set(get_track_ids_from_album_uris(self.album_uris)))

            print("After deep lookup: "
                  f"{len(self.track_ids_for_all_albums_found)} unique"
                  " track ids found"
                )

    def get_track_ids_from_album_uris(self, album_uris):
        """Returns a list of track ids for every album uri provided as an input
         list

        Parameters
        ----------
        album_uris : list
            A list of Spotify album URIs

        to_pkl : bool, optional
            toggles whether track ids should be saved to .pkl file in ./data

        Returns
        ----------
        track_ids : list
            A list of spotify track ids

        """

        track_ids = []
        for album_uri in tqdm(album_uris, disable=False):
            tracks = self.sp.album_tracks(album_uri)
            for track in tracks['items']:
                track_ids.append(track['id'])
        return track_ids

    def get_track_ids_from_playlist_id(self, playlist_id):
        """
        Returns the track ids from one playlist_id
        """

        results = self.sp.user_playlist_tracks("spotify", playlist_id)
        tracks = results['items']
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])

        # keep only those tracks with ids
        tracks = [track for track in tracks if self.track_exists(
            track) and self.id_exists(track)]

        return [track['track']['id'] for track in tracks]

    def get_id(self, track):
        return track['track']['id']

    def id_exists(self, track):
        return bool(get_id(track))

    def track_exists(self, track):
        return track['track']

    def save_to_txt(self, lst, filename):
        with open('data/'+filename, 'w') as file_handler:
            for item in lst:
                file_handler.write("{}\n".format(item))

    def check_authmanager(self):
        if not self.sp.auth_manager:
            print("spotipy.Spotify().auth_manager not set up."
            " Run setup_credentials()?")
