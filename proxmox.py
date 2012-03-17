import requests, json, sys, urllib, time

# Config ################################################################

API_URL = 'https://octopus.plebia.org:8006/api2/json/'
USERNAME = 'api@pve'


# Auth ##################################################################

with open('password.secret') as f:
    password = f.read()[:-1]
r = requests.post(API_URL+'access/ticket', verify=False, data={'username': USERNAME,
                                                               'password': password})
auth = json.loads(r.text)['data']


# Functions #############################################################

def api(method, path, data={}):
    if method == 'GET':
        method = requests.get
    elif method == 'POST':
        method = requests.post
        
    r = method(API_URL+path, 
               verify=False, 
               headers={'CSRFPreventionToken': auth['CSRFPreventionToken']},
               cookies={'PVEAuthCookie': urllib.quote_plus(auth['ticket'])},
               data=data)
    return r.text


