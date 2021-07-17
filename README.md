# song-recommender

A song recommender trained on spotify song data using their audio features


## Database Generator

Module containing `class SongCollector`, which allows to create a database of
Spotify track ids (to be able to use these track ids to create audio features
  for classification / clustering purposes). The module uses the popular
   `spotipy` API wrapper to obtain the data.

**Usage**
```python
# import the module
from database_generator import SongCollector

# create a song collector instance
my_songcollector = SongCollector()

# provide your credentials for your Spotify app
my_songcollector.setup_credentials(<spotify_client_id>, <spotify_client_secret>)

# get all spotify categories, look into their playlists, and in each playlist,
# find and store the track id
# deep lookup: For every track id found, look up their album and also store the
# track ids from there.
# to_txt: Choose to save the track ids to a txt file in folder .data
my_songcollector.perform_full_take(deep_lookup=True, to_txt=True)

# return a list of all found track ids for non deep lookup
my_songcollector.track_ids

# return a list of all found track ids after deep lookup was performed
my_songcollector.track_ids_for_all_albums_found

# save any list - in this case found track ids - to txt in folder .data
my_songcollector.save_to_txt(my_songcollector.track_ids, "trackids.txt")

```
