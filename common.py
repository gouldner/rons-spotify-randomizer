import random
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
#from spotipy.cache_handler import FlaskSessionCacheHandler

my_random_playlist_name = "My Random"

scope = 'playlist-modify-public user-library-read user-read-recently-played'

with open('credentials.txt', 'r') as file:
    lines = file.readlines()
    client_id = lines[0].strip()
    client_secret = lines[1].strip()
    redirect_uri = lines[2].strip()

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    show_dialog=True
)

sp = Spotify(auth_manager=sp_oauth)

def byName(track):
    return track['track']['name'].upper()

def byArtist(track):
    return track['track']['artists'][0]['name'].upper()

def byPlayListName(pl):
    return pl['name'].upper()

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
    liked_songs.sort(key=byName)
    return liked_songs

def getLikedArtists():
    offset=0
    liked_art = []
    # Get all liked artists
    # Since max returned from /me/tracks = 50 (default is 20) we have to get all tracks using batches
    while True:
        batch = sp.current_user_saved_tracks(50,offset=offset)
        liked_art += batch['items']
        if batch['next'] is None:
            break
        offset += len(batch['items'])
    liked_art.sort(key=byArtist)
    return liked_art

def getPlaylistsHTML():
    playlists = sp.current_user_playlists()
    sortedList = playlists['items']
    sortedList.sort(key=byPlayListName)
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in sortedList]
    playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])

    return "<h2>Current Playlists</h2>" + playlists_html

# Print to STDERR
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def make_song_list_html(songs):
   songs_html = '<table>'
   last_artist = " "
   last_song = " "
   for song in songs:
        #eprint('Song:')
        #eprint(song)
        track_id=song['track']['id']
        track_name=song['track']['name']
        track_artist=song['track']['artists'][0]['name']
        if track_name == last_song and track_artist == last_artist:
            songs_html += '<tr><td style="color:red;">'
        else:
            songs_html += '<tr><td>'
        songs_html += track_name
        if track_name == last_song and track_artist == last_artist:
            songs_html += '</td><td style="color:red;">'
        else:
            songs_html += '</td><td>'
        songs_html += track_artist
        songs_html += '</td></tr>'
        last_artist = track_artist
        last_song = track_name
   songs_html += '</table>'
   return songs_html

def getMyPlaylist(playlist_name):
    while True:
        offset = 0
        batch = sp.current_user_playlists(50,offset=offset)
        for playlist in batch['items']:
            #eprint("Playlist Name:" + playlist['name'])
            if playlist['name'] == playlist_name:
                #eprint('Found playlist')
                return playlist
        if batch['next'] is None:
            break
        offset += len(batch['items'])
    # Playlist not found so create it
    #eprint('Playlist not Found creating new playlist')
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user_id, playlist_name, public=True, description="This week's random songs")
    return playlist

def makePlaylist(user_id,liked_list,from_index,to_index):
    sublist=liked_list[from_index:to_index]
    playlist_name = my_random_playlist_name + " " + str(from_index).rjust(3,'0') + "-" + str(to_index).rjust(3,'0')
    playlist = getMyPlaylist(playlist_name)
    # Add selected tracks to the new playlist
    track_id_list = [(song['track']['id']) for song in sublist]
    sp.user_playlist_replace_tracks(user_id, playlist['id'], track_id_list)

def getPlaylistSongs(playlist_name):
    playlists = sp.current_user_playlists()
    #eprint(playlists)
    for pl in playlists['items']:
        if pl['name'] == playlist_name:
            return sp.playlist_items(pl['uri'])['items']
    # if list not found just return empty list
    return []

def my_random_lists_html():
    rand1_name = my_random_playlist_name + " 001-050"
    rand2_name = my_random_playlist_name + " 051-100"
    rand3_name = my_random_playlist_name + " 101-150"
    rand1 = getPlaylistSongs(rand1_name);
    rand2 = getPlaylistSongs(rand2_name);
    rand3 = getPlaylistSongs(rand3_name);
    return "<h2>My Rand 001-050</h2>" + make_song_list_html(rand1) + "<h2>My Rand 051-100</h2>" + make_song_list_html(rand2) + "<h2>My Rand 101-150</h2>" + make_song_list_html(rand3)

def make_random_lists():
    #eprint("authenticated, making the new list")
    liked_songs = getLikedSongs()
    random.shuffle(liked_songs)
    user_id = sp.me()['id']
    # Make third 50 playlist
    makePlaylist(user_id,liked_songs,101,150)
    # Make second 50 playlist
    makePlaylist(user_id,liked_songs,51,100)
    # Make first 50 playlist
    makePlaylist(user_id,liked_songs,1,50)
