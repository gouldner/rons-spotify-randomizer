#!/usr/bin/bash
. /home/gouldner/.bashrc
cd /home/gouldner/rons-spotify-randomizer
source venv/bin/activate
python3 MakeRandomLists.py > MakeRandomLists.out 2> MakeRandomLists.err
DATE=`date "+%m/%d/%Y"`
/usr/bin/mail -r ubuntu@rgps.com -a "Content-type: text/html"  -s "New Playlists ${DATE}" gouldner@hawaii.edu < MakeRandomLists.out
