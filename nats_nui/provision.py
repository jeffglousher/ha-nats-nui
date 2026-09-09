"""At-most-once import into an untouched NUI database."""
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

BROKER = 'b19429c2_pbscar_nats'
MARKER = Path('/db/.local-provisioned')

def request(url, body=None, supervisor=False):
    headers = {'Content-Type': 'application/json'}
    if supervisor:
        headers['Authorization'] = 'Bearer ' + os.environ['SUPERVISOR_TOKEN']
    req = urllib.request.Request(url, headers=headers,
        data=None if body is None else json.dumps(body).encode())
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.load(response)

def finish():
    # Exclusive, durable completion claim precedes insertion: after a crash or
    # ambiguous HTTP response, never recreate a connection somebody deleted.
    try:
        with MARKER.open('x') as stream:
            stream.write('Connection setup belongs to NUI.\n')
            stream.flush()
            os.fsync(stream.fileno())
        return True
    except FileExistsError:
        return False

def attempt():
    if MARKER.exists():
        return True
    connections = request('http://127.0.0.1:31311/api/connection')
    if connections:
        finish()
        return True
    metadata = request('http://supervisor/addons/' + BROKER + '/info', supervisor=True)
    if metadata.get('result') != 'ok' or metadata['data'].get('state') != 'started':
        return False
    hostname = metadata['data']['hostname']
    # The host is the companion's Supervisor-generated internal DNS name.
    if hostname != BROKER.replace('_', '-'):
        raise ValueError('Unexpected companion hostname')
    try:
        value = request('http://' + hostname + ':8098/connection')
    except urllib.error.HTTPError as error:
        if error.code == 409:
            finish()
            print('Local NATS uses custom authentication or TLS. Add its connection in NUI.', flush=True)
            return True
        raise
    if value.get('hosts') != ['nats://' + hostname + ':4222']:
        raise ValueError('Unexpected broker address')
    # Recheck after discovery so an operator-created connection takes precedence.
    if request('http://127.0.0.1:31311/api/connection'):
        finish()
        return True
    if not finish():
        return True
    request('http://127.0.0.1:31311/api/connection', value)
    print('Local NATS connection imported. Future connection changes belong to NUI.', flush=True)
    return True

def main():
    if MARKER.exists() or not os.environ.get('SUPERVISOR_TOKEN'):
        return
    print('Checking for the companion NATS app; existing connections will be preserved.', flush=True)
    while True:
        try:
            if attempt():
                return
        except Exception:
            # Never print HTTP responses, exception details or credentials.
            if MARKER.exists():
                print('Automatic setup was attempted. Check Connections in NUI; automatic retries are disabled to preserve user changes.', flush=True)
                return
        time.sleep(15)

if __name__ == '__main__':
    main()
