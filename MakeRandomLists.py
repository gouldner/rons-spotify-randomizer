import os
import random
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
#from spotipy.cache_handler import FlaskSessionCacheHandler

my_random_playlist_name = "Ron's Random Playlist"

with open('credentials.txt', 'r') as file:
    lines = file.readlines()
    client_id = lines[0].strip()
    client_secret = lines[1].strip()
    redirect_uri = lines[2].strip()

scope = 'playlist-modify-public user-library-read user-read-recently-played'

#cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    show_dialog=True
)

sp = Spotify(auth_manager=sp_oauth)

def getLikedSongs():
    offset=0
    liked_songs = []
    # Get all liked songs
    # Since max returned from /me/tracks = 50 (default is 20) we have to get all tracks using batches
    while True:
        batch = sp.current_user_saved_tracks(50,offset=offset)
        liked_songs += batch['items']
        if batch['next'] is None:
            break
        offset += len(batch['items'])
    return liked_songs

def getMyPlaylist(playlist_name):
    while True:
        offset = 0
        batch = sp.current_user_playlists(50,offset=offset)
        for playlist in batch['items']:
            #print("Playlist Name:" + playlist['name'])
            if playlist['name'] == playlist_name:
                #print('Found playlist')
                return playlist
        if batch['next'] is None:
            break
        offset += len(batch['items'])
    # Playlist not found so create it
    #print('Playlist not Found creating new playlist')
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user_id, playlist_name, public=True, description="This week's random songs")
    return playlist
    
def makePlaylist(user_id,liked_list,from_index,to_index):
    sublist=liked_list[from_index:to_index]
    playlist_name = my_random_playlist_name + " " + str(from_index) + "-" + str(to_index)
    playlist = getMyPlaylist(playlist_name)
    # Add selected tracks to the new playlist
    track_id_list = [(song['track']['id']) for song in sublist]
    sp.user_playlist_replace_tracks(user_id, playlist['id'], track_id_list)

liked_songs = getLikedSongs()
random.shuffle(liked_songs)
user_id = sp.me()['id']
# Make first 50 playlist
makePlaylist(user_id,liked_songs,1,50)
# Make second 50 playlist
makePlaylist(user_id,liked_songs,51,100)
# Make third 50 playlist
makePlaylist(user_id,liked_songs,101,151)
print("Done")
