import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
# import requests
from tqdm.auto import tqdm


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

    def perform_full_take(self, deep_lookup=False,
                          to_txt=False, progress_off=False):
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

        to_txt : bool, optional
            toggles whether track ids should be saved to .txt file in ./data

        progress_off: bool, optional
            if False, shows tqdm progress bar in jupyter notebook or console output

        """

        # check for sane credentials
        self.check_authmanager()

        # get all available category id's
        sp_cats = self.sp.categories()
        for cat in tqdm(sp_cats['categories']['items'], disable=progress_off):
            self.category_ids.append(cat['id'])

        # now get & save all playlist id's from those categories
        for cat_id in self.category_ids:
            # catch HTTP error for some categories
            try:
                pl_per_category_json = self.sp.category_playlists(cat_id)[
                    'playlists']['items']
            except spotipy.client.SpotifyException:
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

        if to_txt and not deep_lookup:
            print("Saving track ids")
            self.save_to_txt(self.track_ids, "track_ids_small.txt")

        # if deep_lookup
        if deep_lookup:
            print("starting deep lookup...")
            print("now getting all album ids for every song")
            for track_id in tqdm(self.track_ids, disable=progress_off):
                self.album_uris.append(self.sp.track(track_id)['album']['uri'])

            self.album_uris = list(set(self.album_uris))
            print(f"{len(self.album_uris)} unique album uris found")
            print("----")
            print("Getting all the songs from those uris")

            self.track_ids_for_all_albums_found = list(
                set(self.get_track_ids_from_album_uris(self.album_uris, progress_off=progress_off)))

            print("After deep lookup: "
                  f"{len(self.track_ids_for_all_albums_found)} unique"
                  " track ids found"
                  )
            if to_txt:
                print("Saving track ids")
                self.save_to_txt(self.track_ids, "track_ids_big.txt")

    def get_track_ids_from_album_uris(self, album_uris, progress_off=False):
        """Returns a list of track ids for every album uri provided as an input
         list

        Parameters
        ----------
        album_uris : list
            A list of Spotify album URIs

        progress_off: bool, optional
            if False, shows tqdm progress bar in jupyter notebook or console output

        Returns
        ----------
        track_ids : list
            A list of spotify track ids

        """

        track_ids = []
        for album_uri in tqdm(album_uris, disable=progress_off):
            tracks = self.sp.album_tracks(album_uri)
            for track in tracks['items']:
                track_ids.append(track['id'])
        return track_ids

    def get_track_ids_from_playlist_id(self, playlist_id):
        """
        Returns the track ids from one playlist_id
        """

        results = self.sp.playlist_items(playlist_id)
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
        return bool(self.get_id(track))

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
