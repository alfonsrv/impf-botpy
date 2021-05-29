#!/usr/bin/env python3
""" Impftermin Service Mock Backend """
from random import randint

from flask import Flask, Response, request, jsonify, make_response, render_template
from base64 import b64decode

# TODO: Clean-up
import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import settings

APPOINTMENTS = {
    "gesuchteLeistungsmerkmale": ["L920", "L921"],
    "termine": [
        [{
            "slotId": "slot-f4049ed1-6c2d-4c22-ad12-a91743a99b8d",
            "begin": 1621607701000,
            "bsnr": "005221261"
        }, {
            "slotId": "slot-fbe52874-0455-4c42-8e5b-c88dc4fd2085",
            "begin": 1625226601000,
            "bsnr": "005221261"
        }],
        [{
            "slotId": "slot-3a044cc0-1875-4f12-b4f0-05cd38d3400e",
            "begin": 1621687801000,
            "bsnr": "005221261"
        }, {
            "slotId": "slot-9342fe5c-444a-4c5f-b391-34b442fb7266",
            "begin": 1625296501000,
            "bsnr": "005221261"
        }],
        [{
            "slotId": "slot-5dde19a2-2e60-49d0-82c4-7f801fbac6a0",
            "begin": 1621867501000,
            "bsnr": "005221261"
        }, {
            "slotId": "slot-b6c789cb-60ae-40c7-ae50-546de60a0f11",
            "begin": 1625479201000,
            "bsnr": "005221261"
        }],
        [{
            "slotId": "slot-e04d7b41-2391-40d1-9210-5ceb8fb2c60c",
            "begin": 1621938901000,
            "bsnr": "005221261"
        }, {
            "slotId": "slot-6d31da09-4c37-43ba-8ced-b5ae980a8c8c",
            "begin": 1625589901000,
            "bsnr": "005221261"
        }],
        [{
            "slotId": "slot-bf5b4254-43f2-4f41-9ff9-98b090c7be0d",
            "begin": 1622130901000,
            "bsnr": "005221261"
        }, {
            "slotId": "slot-ae60e608-00ba-4d21-b0a0-8c3cfc4f969c",
            "begin": 1625730301000,
            "bsnr": "005221261"
        }]
    ],
    "termineTSS": [],
    "praxen": {
        "005221261": {
            "label": "Impfzentrum Ludwigsburg - 1",
            "kv": "kv.digital GmbH",
            "languages": None,
            "lat": 48.8926679,
            "lon": 9.1683451,
            "distance": 0.0,
            "street": "Grönerstraße 33",
            "plz": "71636",
            "city": "Ludwigsburg",
            "bf": [""],
            "web": "",
            "phone": "",
            "comment": ""
        }
    }
}

def chaos_monkey(f):
    """ 1:1 implementation of the original ImpfterminService API """
    def func(*args, **kwargs):
        if not randint(0,2):
            return Response({}, status=429)
        if 'termin_buchung' in f.__name__ and not randint(0,3):
            return Response({}, status=481)
        return f(*args, **kwargs)
    return func


app = Flask(__name__, template_folder='res')

# TODO: Mock HTML sites + mock cookies + mock workflow

@app.route('/impftermine/suche/<vermittlungscode>/<zip>')
def termin_suche(*args, **kwargs):
    return render_template('appointment_appointment_form.html')

@chaos_monkey
@app.route('/rest/suche/impfterminsuche', methods=['GET'])
def rest_termin_suche():
    assert request.headers.get('Referer')
    assert request.headers.get('Authorization')
    assert 'application/json' in request.headers.get('Content-Type')
    assert request.args.get('plz')
    *_, _code, _plz = request.headers.get('Referer').split('/')
    plz = request.args.get('plz')
    assert len(plz) == 5
    assert plz.isdigit()
    assert _plz == plz

    assert request.cookies.get('bm_sz') == '140EFSD342XOs8E139FEF9XASD2~YAAQV2ZWuGugTUZ5AQVVA7FCkwsD1DbT5fM7q0zs/uw9gmpbJwLKXLbs0a6QFVj6flaBovO577NTLMspOQNiTPnXXoCASD312VQrP/MhMwzOk8RbSD5nQavFzduYazPJLJxm34KePfrwjLA3+lNzODFds12MLcDu7QQDc6OGpJ27gw6jitsiL+JBL4QcvsmBL7RV6fX+vlu=='
    assert request.cookies.get('akavpau_User_allowed') == '1546795457~id=6255b1eh238943e08141b8fa231'

    auth = b64decode(request.headers.get('Authorization').replace('Basic ', '')).decode("utf-8")
    assert auth == f':{_code}'
    return jsonify(APPOINTMENTS)


@chaos_monkey
@app.route('/rest/buchung', methods=['POST'])
def rest_termin_buchung():
    assert request.headers.get('Referer')
    assert request.headers.get('Authorization')
    assert 'application/json' in request.headers.get('Content-Type')
    *_, _code, _zip = request.headers.get('Referer').split('/')
    auth = b64decode(request.headers.get('Authorization').replace('Basic ', '')).decode("utf-8")
    assert auth == f':{_code}'

    assert request.json
    print('Request:', request.json)

    data = request.json
    data_contact = data.get('contact')
    assert len(data.get('slots')) == 2
    assert isinstance(data.get('qualifikationen'), list)
    assert _zip == data.get('plz')
    assert data_contact.get('anrede') == settings.SALUTATION
    assert data_contact.get('vorname') == settings.FIRST_NAME
    assert data_contact.get('nachname') == settings.LAST_NAME
    assert data_contact.get('strasse') == settings.STREET_NAME
    assert data_contact.get('hausnummer') == settings.HOUSE_NUMBER
    assert data_contact.get('plz') == settings.ZIP_CODE
    assert data_contact.get('ort') == settings.CITY
    assert data_contact.get('notificationReceiver') == settings.MAIL
    assert data_contact.get('notificationChannel') == 'email'
    assert data_contact.get('phone') == f'+49 {settings.PHONE}'

    return Response('{}', status=201)

@app.route('/', methods=['GET'])
def landing():
    r = make_response('https://github.com/alfonsrv/impf-botpy')
    # TODO: Maybe do timestamp checking
    r.set_cookie('bm_sz', '140EFSD342XOs8E139FEF9XASD2~YAAQV2ZWuGugTUZ5AQVVA7FCkwsD1DbT5fM7q0zs/uw9gmpbJwLKXLbs0a6QFVj6flaBovO577NTLMspOQNiTPnXXoCASD312VQrP/MhMwzOk8RbSD5nQavFzduYazPJLJxm34KePfrwjLA3+lNzODFds12MLcDu7QQDc6OGpJ27gw6jitsiL+JBL4QcvsmBL7RV6fX+vlu==')
    r.set_cookie('akavpau_User_allowed', '1546795457~id=6255b1eh238943e08141b8fa231')
    return r

if __name__ == '__main__':
    app.run(debug=True)