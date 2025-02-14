#!/usr/bin/bash
. /home/gouldner/.bashrc
cd /home/gouldner/rons-spotify-randomizer
source venv/bin/activate
python3 MakeRandomLists.py > MakeRandomLists.out 2> MakeRandomLists.err
