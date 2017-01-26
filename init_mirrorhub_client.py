'''init script which prepares our docker container'''
#!/usr/bin/env python3
import os
import signal
import socket
import subprocess
from pathlib import Path
from jinja2 import Template

HOSTNAME = socket.gethostname()
LETSENCRYPT_ARGS = ' '.join(['-a webroot',
                             '--webroot-path=/tmp/letsencrypt',
                             '--rsa-key-size 4096',
                             '--non-interactive'])

def exec_cmd(cmd):
    '''executes a shell command
    args:
        cmd (str): shell command'''
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)


print(r'''
           _                     _           _      _
          (_)                   | |         | |    (_)
 _ __ ___  _ _ __ _ __ ___  _ __| |__  _   _| |__   _  ___
| '_ ` _ \| | '__| '__/ _ \| '__| '_ \| | | | '_ \ | |/ _ \
| | | | | | | |  | | | (_) | |  | | | | |_| | |_) || | (_) |
|_| |_| |_|_|_|  |_|  \___/|_|  |_| |_|\__,_|_.__(_)_|\___/
============================================================
''')
exit()
if not Path("/srv/nginx/dhparam.pem").is_file():
    print('[nginx] Did not found dhparams, generating. This may take a while..')
    exec_cmd('openssl dhparam -out /srv/nginx/dhparam.pem 2048')
    print('[nginx] Finished generating.')
else:
    print('[nginx] Using existing dhparams')


print('[nginx] Using %s as HOSTNAME' % HOSTNAME)

NGINX_CONF_TEMP = Template(open('/srv/internals/mirror_nonssl.j2').read())
with open('/etc/nginx/sites-available/mirror.conf', 'w+') as f:
    f.write(NGINX_CONF_TEMP.render(domain=HOSTNAME, mirror_name='test'))

os.symlink('/etc/nginx/sites-available/mirror.conf',
           '/etc/nginx/sites-enabled/mirror.conf')

NGINX = subprocess.Popen('/usr/sbin/nginx')

if os.path.exists('/etc/letsencrypt/live/' + HOSTNAME):
    exec_cmd('letsencrypt renew ' + LETSENCRYPT_ARGS)
else:
    exec_cmd('letsencrypt certonly %s --register-unsafely-without-email \
             --agree-tos -d %s' % (LETSENCRYPT_ARGS, HOSTNAME))

os.kill(NGINX.pid, signal.SIGTERM)

NGINX_CONF_TEMP = Template(open('/srv/internals/mirror.j2').read())
with open('/etc/nginx/sites-available/mirror.conf', 'w+') as f:
    f.write(NGINX_CONF_TEMP.render(domain=HOSTNAME, mirror_name='test'))

print('[mirror] Ready to serve!')
exec_cmd('/usr/bin/supervisord')
