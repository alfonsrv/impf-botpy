from impf.browser import Browser

# TODO: Make clean and more modular - just testing the monolith rn
def test_monolith():
	x = Browser(
		location='71636',
		code='Q29X-AX2F-TPC7',
		location_full='71636 Ludwigsburg, Impfzentrum Ludwigsburg'
	)
	x.driver.get('http://127.0.0.1:5000')
	x.alert_appointment()

# https://003-iz.impfterminservice.de/impftermine/suche/Q29X-AX2F-TPC7/71636