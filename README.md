[![Docker Repository on Quay](https://quay.io/repository/mirrorhub/client/status "Docker Repository on Quay")](https://quay.io/repository/mirrorhub/client)

Build with

```
docker build -t quay.io/mirrorhub/client .
```

Start with

```
docker run \
  -p 80:80 -p 443:443 \
  -v "`pwd`/volumes/internals":/srv/internals \
  -v "`pwd`/volumes/letsencrypt":/etc/letsencrypt/live \
  -v "`pwd`/volumes/archive":/etc/letsencrypt/archive \
  -i -t -h vnode-hetzner.my-node.de \
  quay.io/mirrorhub/client
```
