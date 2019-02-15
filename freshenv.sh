#!/usr/bin/zsh
rmvirtualenv temp
mkvirtualenv -p /usr/bin/python3 temp
workon temp
pip install flask

