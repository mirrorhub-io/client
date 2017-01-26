#!/usr/bin/env python3
'''init script which prepares our docker container'''
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

def gen_ngx_conf(template_name):
    NGINX_CONF_TEMP = Template(open('/srv/internals/%s.j2' % template_name).read())
    with open('/etc/nginx/sites-available/mirror.conf', 'w+') as f:
        f.write(NGINX_CONF_TEMP.render(domain=HOSTNAME, mirror_name='test'))

    if Path("/etc/nginx/sites-enabled/mirror.conf").is_file():
        os.unlink('/etc/nginx/sites-enabled/mirror.conf')

    os.symlink('/etc/nginx/sites-available/mirror.conf',
               '/etc/nginx/sites-enabled/mirror.conf')



print(r'''
           _                     _           _      _
          (_)                   | |         | |    (_)
 _ __ ___  _ _ __ _ __ ___  _ __| |__  _   _| |__   _  ___
| '_ ` _ \| | '__| '__/ _ \| '__| '_ \| | | | '_ \ | |/ _ \
| | | | | | | |  | | | (_) | |  | | | | |_| | |_) || | (_) |
|_| |_| |_|_|_|  |_|  \___/|_|  |_| |_|\__,_|_.__(_)_|\___/
============================================================
''')

if not Path("/srv/nginx/dhparam.pem").is_file():
    print('[nginx] Did not found dhparams, generating. This may take a while..')
    exec_cmd('openssl dhparam -out /srv/nginx/dhparam.pem 2048')
    print('[nginx] Finished generating.')
else:
    print('[nginx] Using existing dhparams')


print('[nginx] Using %s as HOSTNAME' % HOSTNAME)


if os.path.exists('/etc/letsencrypt/live/' + HOSTNAME):
    print('[cert] Found certificate for domain. Attempt renew..')
    exec_cmd('letsencrypt renew ' + LETSENCRYPT_ARGS)
else:
    print('[nginx] Applying temporary site configuration..')
    gen_ngx_conf('mirror_nonssl')
    NGINX = subprocess.Popen('/usr/sbin/nginx')

    print('[cert] Missing certificate for domain. Request new one..')
    exec_cmd('letsencrypt certonly %s --register-unsafely-without-email \
             --agree-tos -d %s' % (LETSENCRYPT_ARGS, HOSTNAME))

    os.kill(NGINX.pid, signal.SIGTERM)


print('[nginx] Applying final site configuration..')
gen_ngx_conf('mirror')

print('[mirror] Ready to serve!')
exec_cmd('/usr/bin/supervisord')
