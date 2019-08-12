# ProxyPool

## Installation 

Python: 3.5

## Redis

Open the Redis service after installation.

## Configuring a Proxy Pool

```
cd proxypool
```

Enter the proxypool directory and modify the [settings.py](./proxypool/setting.py) file.

PASSWORD is the Redis password, if it is empty, set to **None**.

## Installation Dependency

```
pip3 install -r requirements.txt
```

## Open the Proxy Pool and API

```
python3 run.py
```

## Get Proxy 


Use the requests to get the following methods:

```python
import requests

PROXY_POOL_URL = 'http://localhost:5555/random'

def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None
```
