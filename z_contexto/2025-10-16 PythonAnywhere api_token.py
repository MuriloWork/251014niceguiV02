# Use this token for our API by setting a request header called Authorization, followed by Token <token>, eg:

import requests
username = 'muWork01'
token = 'bce4f33d9e4aab365006bbb6c12bcbedc0a90f56'

response = requests.get(
    'https://www.pythonanywhere.com/api/v0/user/{username}/cpu/'.format(
        username=username
    ),
    headers={'Authorization': 'Token {token}'.format(token=token)}
)
if response.status_code == 200:
    print('CPU quota info:')
    print(response.content)
else:
    print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))