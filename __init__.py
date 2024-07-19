from time import time
from json import dumps, loads
from random import choices
from . import pcrdapi

_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Referer": "https://pcrdfans.com/",
    "Origin": "https://pcrdfans.com",
    "Accept": "*/*",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": "",
    "Host": "api.pcrdfans.com",
}

def _getNonce():
    return ''.join(choices("0123456789abcdefghijklmnopqrstuvwxyz", k=16))

def _getTs():
    return int(time())

def _dumps(x):
    return dumps(x, ensure_ascii=False).replace(' ', '')

def patch(module):
    old_post = module.post
    async def post(url, data=None, json=None, **kwargs):
        if url != 'https://api.pcrdfans.com/x/v1/search':
            return await old_post(url, data, json, **kwargs)
    
        if data is not None:
            if isinstance(data, bytes):
                json = loads(data.decode('utf8'))
            elif isinstance(data, str):
                json = loads(data)
        
        assert json is not None
        
        data = {
            "def": json['def'],
            "language": json.get('language', 0),
            "nonce": _getNonce(),
            "page": json['page'],
            "region": json['region'],
            "sort": json['sort'],
            "ts": _getTs()
        }
        data['_sign'] = pcrdapi.sign(_dumps(data), data['nonce'])
        kwargs['headers'] = _headers
        return await old_post(url, json=None, data=_dumps(data).encode('utf8'), **kwargs)
    module.post = post

try:
    from hoshino.modules.priconne.arena import arena
    arena.__get_auth_key = lambda: ''
except:
    pass

try:
    from hoshino import aiorequests
    patch(aiorequests)
except:
    pass

try:
    from hoshino.modules.autopcr.autopcr.util import aiorequests
    patch(aiorequests)
except:
    pass
