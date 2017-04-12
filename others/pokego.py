#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests

POKEURL = 'http://cmmcd.com/PokemonGo/'
STATUSES = {
	'Online!'  : 0,
	'Unstable!': 1,
	'Offline!' : 2,
}

r = requests.get(POKEURL)
try:
	import lxml
	soup = BeautifulSoup(r.text, 'lxml')
except ImportError:
	soup = BeautifulSoup(r.text, 'html.parser')

status = STATUSES[soup.body.header.h2.font.text]

if __name__ == '__main__':
	if status == 1:
		u = '  PKGO Shaky!'
		print(u)
	elif status == 2:
		d = '  PKGO Down!'
		print(d)
	else:
		up = ' PKGO UP!'
		print(up)
		exit(0)
