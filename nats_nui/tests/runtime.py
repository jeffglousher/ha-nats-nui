"""Isolated image-build checks. Runs only with disposable /db."""
import http.client, json, os, signal, socket, subprocess, tempfile, time, urllib.request, urllib.error
from pathlib import Path
Path('/db').mkdir(exist_ok=True)
ADMIN_ID = 'a' * 32
Path('/db/options.json').write_text(json.dumps({'log_level': 'warn', 'console_admin_user_ids': [ADMIN_ID]}))
log=tempfile.TemporaryFile()
def get(path):
    with urllib.request.urlopen('http://127.0.0.1:31311'+path,timeout=2) as r: return r.read()
def start():
    p=subprocess.Popen(['/sbin/tini','-g','--','/run.sh'],stdout=log,stderr=log)
    for _ in range(100):
        assert p.poll() is None,'app exited before ready'
        try: get('/health');return p
        except OSError: time.sleep(.1)
    p.terminate();p.wait(timeout=10);raise AssertionError('not ready')
def stop(p):
    if p.poll() is None:p.terminate()
    p.wait(timeout=10)

def check_trusted_ingress(allowed):
    # Docker build cannot assign Supervisor's real IP. A second disposable
    # gateway changes only its trusted peer to loopback; the production gateway
    # remains unchanged and is separately tested against spoofed direct access.
    config = Path('/etc/nginx/nginx.conf').read_text()
    assert config.count('allow 172.30.32.2;') == 1
    config = config.replace('allow 172.30.32.2;', 'allow 127.0.0.1;')
    config = config.replace('listen 8099;', 'listen 8098;')
    config = config.replace('/run/nginx/nginx.pid', '/run/nginx/ingress-test.pid')
    Path('/tmp/ingress-test.conf').write_text(config)
    proxy = subprocess.Popen(['nginx', '-c', '/tmp/ingress-test.conf', '-g', 'daemon off;'], stdout=log, stderr=log)
    def request(path='/', headers=(), method='GET'):
        conn = http.client.HTTPConnection('127.0.0.1', 8098, timeout=2)
        conn.putrequest(method, path)
        for name, value in headers: conn.putheader(name, value)
        conn.endheaders()
        response = conn.getresponse()
        status, body = response.status, response.read()
        conn.close()
        return status, body
    try:
        for _ in range(50):
            try:
                assert request('/health') == (200, b'OK')
                break
            except OSError: time.sleep(.1)
        else: raise AssertionError('trusted ingress fixture did not start')
        assert request('/health', method='HEAD') == (200, b'')
        assert request('/health', method='POST')[0] == 403
        for path in ('/', '/api/connection', '/ws/sub', '/health/../api/connection'):
            for headers in ((), [('X-Remote-User-Id', 'b' * 32)],
                            [('X-Remote-User-Id', ADMIN_ID), ('X-Remote-User-Id', ADMIN_ID)],
                            [('X-Remote-User-Id', ADMIN_ID), ('Sec-Fetch-Site', 'cross-site')]):
                assert request(path, headers)[0] == 403, (path, headers)
        headers = [('X-Remote-User-Id', ADMIN_ID)]
        assert request('/', headers)[0] == (200 if allowed else 403)
        assert request('/api/connection', headers)[0] == (200 if allowed else 403)
        assert request('/ws/sub', headers)[0] == (426 if allowed else 403)
    finally:
        proxy.terminate()
        proxy.wait(timeout=10)

p=start()
try:
    check_trusted_ingress(True)
    try: urllib.request.urlopen('http://127.0.0.1:8099/',timeout=2)
    except urllib.error.HTTPError as e: assert e.code==403
    else: raise AssertionError('gateway bypass allowed')
    for path in ('/api/connection', '/health', '/ws/sub', '/api/proto/%2e%2e%2foutside'):
        req = urllib.request.Request('http://127.0.0.1:8099'+path, headers={'X-Forwarded-For':'172.30.32.2','X-Real-IP':'172.30.32.2','X-Remote-User-Id':ADMIN_ID})
        try: urllib.request.urlopen(req,timeout=2)
        except urllib.error.HTTPError as e: assert e.code==403
        else: raise AssertionError('spoofed proxy headers bypassed gateway')
    req = urllib.request.Request('http://127.0.0.1:8099/',headers={'Sec-Fetch-Site':'cross-site'})
    try: urllib.request.urlopen(req,timeout=2)
    except urllib.error.HTTPError as e: assert e.code==403
    else: raise AssertionError('cross-site request accepted')
    tcp=Path('/proc/net/tcp').read_text().splitlines()[1:]
    listeners=[x.split()[1] for x in tcp if x.split()[3]=='0A' and x.split()[1].endswith(':7A4F')]
    assert listeners==['0100007F:7A4F'],listeners # 31311, loopback only
    payload={'name':'Release persistence test','hosts':['nats://127.0.0.1:4222'],'auth':[{'mode':'auth_none','active':True}],'tls_auth':{'enabled':False},'metrics':{'httpSource':{'active':False},'natsSource':{'active':False}},'subscriptions':[]}
    req=urllib.request.Request('http://127.0.0.1:31311/api/connection',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=3) as r: assert r.status==200
finally:stop(p)
Path('/db/options.json').write_text('{"log_level":"warn","console_admin_user_ids":[]}')
p=start()
try:
    check_trusted_ingress(False)
    assert any(c['name']=='Release persistence test' for c in json.loads(get('/api/connection')))
    os.kill(int(Path('/run/nginx/nginx.pid').read_text()),signal.SIGTERM)
    assert p.wait(timeout=10)!=0,'gateway failure did not stop app'
finally:stop(p)
for bad_ids in (None, False, 'all', ['invalid;'], [1], [ADMIN_ID + '\n']):
    Path('/db/options.json').write_text(json.dumps({'console_admin_user_ids': bad_ids}))
    invalid = subprocess.Popen(['/run.sh'], stdout=log, stderr=log)
    assert invalid.wait(timeout=5) != 0, 'invalid administrator setting accepted'
log.seek(0);logs=log.read()
assert b'Incoming request' not in logs
assert b'error importing cli contexts' not in logs
assert b'Ingress gateway exited unexpectedly' in logs
print('PASS: ingress identity authorization and watchdog; gateway denies bypass; backend loopback-only; saved connection persists; service failure stops app; quiet startup')
Path('/test-passed').write_text('NUI isolated runtime checks passed\n')
