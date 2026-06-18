import sys
import os

from flask import Flask, request, redirect, session, url_for

with open('credentials.txt', 'r') as file:
    lines = file.readlines()
    flask_host = lines[3].strip()
    code_path = lines[4].strip()

sys.path.append(os.path.abspath(code_path))
from common import *

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64);

#with open(commonCodePath, "rb") as source_file:
#    code = compile(source_file.read(), filename, "exec")
#exec(code)

#cache_handler = FlaskSessionCacheHandler(session)

def get_menu_html():
    html = "<h1>"
    html += "<ol>"
    html += "<li><a href=" + url_for("get_playlists") + ">Get Playlists</a></li>"
    html += "<li><a href=" + url_for("get_liked_songs") + ">Get Liked Songs</a></li>"
    html += "<li><a href=" + url_for("get_liked_artists") + ">Get Liked Artists</a></li>"
    html += "<li><a href=" + url_for("make_liked_list") + ">Make (" + my_random_playlist_name + ") playlists</a></li>"
    html += "<li><a href=" + url_for("display_my_random") + ">Display (" + my_random_playlist_name + ") playlists</a></li>"
    html += "</ol>"
    html += "</h1>"
    html += "<br><br>"
    return html

def get_front_page_html():
    return get_menu_html()

@app.route('/')
def home():
    return get_front_page_html()

@app.route('/callback')
def callback():
    return redirect(url_for('home'))

@app.route('/get_playlists')
def get_playlists():
    result=get_menu_html()
    result+= getPlaylistsHTML()
    return result 

@app.route('/display_my_random')
def display_my_random():
    result=get_menu_html()
    result+=my_random_lists_html()
    return result

@app.route('/make_liked_list')
def make_liked_list():
    make_random_lists()
    result = get_menu_html()
    result += my_random_lists_html()
    return result
    

@app.route('/get_liked_songs')
def get_liked_songs():
    liked_songs = getLikedSongs()
    return get_menu_html() + "<h2>All Liked Songs ("+ str(len(liked_songs)) +")</h2>" + make_song_list_html(liked_songs)

@app.route('/get_liked_artists')
def get_liked_artists():
    liked_songs = getLikedArtists()
    return get_menu_html() + "<h2>All Liked Songs by Artist ("+ str(len(liked_songs)) +")</h2>" + make_song_list_html(liked_songs)


if __name__ == '__main__':
    app.run(host=flask_host,port=5000, debug=True)

