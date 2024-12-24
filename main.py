import os
#import logging
import random
from flask import Flask, request, redirect, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
#from spotipy.cache_handler import FlaskSessionCacheHandler

my_random_playlist_name = "Ron's Random Playlist"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64);

#logger = getLogger(__liked_randomizer__)
#logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

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

def get_front_page_html():
    return get_menu_html()

def get_menu_html():
    html = "<h1>"
    html += "<ol>"
    html += "<li><a href=" + url_for("get_playlists") + ">Get Playlists</a></li>"
    html += "<li><a href=" + url_for("get_liked_songs") + ">Get Liked Songs</a></li>"
    html += "<li><a href=" + url_for("make_liked_list") + ">Make (" + my_random_playlist_name + ") playlists</a></li>"
    html += "</ol>"
    html += "</h1>"
    html += "<br><br>"
    return html


@app.route('/')
def home():
    return get_front_page_html()

@app.route('/callback')
def callback():
    return redirect(url_for('home'))

@app.route('/get_playlists')
def get_playlists():
    playlists = sp.current_user_playlists()
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])

    return get_menu_html() + "<h2>Current Playlists</h2>" + playlists_html

def byName(track):
    return track['track']['name'].upper()

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

def make_song_list_html(songs):
   songs_html = '<table>'
   for song in songs:
        #print('Song:')
        #print(song)
        track_id=song['track']['id']
        track_name=song['track']['name']
        track_artist=song['track']['artists'][0]['name']
        songs_html += '<tr><td>'
        songs_html += track_name
        songs_html += '</td><td>'
        songs_html += track_artist
        songs_html += '</td></tr>'
   songs_html += '</table>'
   return songs_html

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
    return "<h2>" + playlist_name + "</h2>" + make_song_list_html(sublist) + "<br><br>"
 

@app.route('/make_liked_list')
def make_liked_list():
    result = get_menu_html()
    #print("authenticated, making the new list")
    liked_songs = getLikedSongs()
    random.shuffle(liked_songs)
    user_id = sp.me()['id']
    # Make first 50 playlist
    result += makePlaylist(user_id,liked_songs,1,50)
    # Make second 50 playlist
    result += makePlaylist(user_id,liked_songs,51,100)
    # Make third 50 playlist
    result += makePlaylist(user_id,liked_songs,101,151)
    return result
    

@app.route('/get_liked_songs')
def get_liked_songs():
    liked_songs = getLikedSongs()
    return get_menu_html() + "<h2>All Liked Songs</h2>" + make_song_list_html(liked_songs)

if __name__ == '__main__':
    app.run(debug=True)

