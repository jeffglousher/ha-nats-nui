"""Isolated image-build checks. Runs only with disposable /db."""
import json, os, signal, socket, subprocess, tempfile, time, urllib.request, urllib.error
from pathlib import Path
Path('/db').mkdir(exist_ok=True)
Path('/db/options.json').write_text('{"log_level":"warn"}')
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
p=start()
try:
    try: urllib.request.urlopen('http://127.0.0.1:8099/',timeout=2)
    except urllib.error.HTTPError as e: assert e.code==403
    else: raise AssertionError('gateway bypass allowed')
    for path in ('/api/connection', '/health', '/ws/sub', '/api/proto/%2e%2e%2foutside'):
        req = urllib.request.Request('http://127.0.0.1:8099'+path, headers={'X-Forwarded-For':'172.30.32.2','X-Real-IP':'172.30.32.2'})
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
p=start()
try:
    assert any(c['name']=='Release persistence test' for c in json.loads(get('/api/connection')))
    os.kill(int(Path('/run/nginx/nginx.pid').read_text()),signal.SIGTERM)
    assert p.wait(timeout=10)!=0,'gateway failure did not stop app'
finally:stop(p)
log.seek(0);logs=log.read()
assert b'Incoming request' not in logs
assert b'error importing cli contexts' not in logs
assert b'Ingress gateway exited unexpectedly' in logs
print('PASS: gateway denies bypass; backend loopback-only; saved connection persists; service failure stops app; quiet startup')
Path('/test-passed').write_text('NUI isolated runtime checks passed\n')
