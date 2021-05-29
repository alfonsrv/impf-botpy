import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from impf.browser import Browser
# TODO: Make this an actual test – this is literally horrible af

def test_monolith():
	x = Browser(
		location='71636',
		code='Q29X-AX2F-TPC7',
		location_full='71636 Ludwigsburg, Impfzentrum Ludwigsburg'
	)
	x.driver.get('http://127.0.0.1:5000/impftermine/suche/Q29X-AX2F-TPC7/71636')
	x.book_appointment(2)

test_monolith()