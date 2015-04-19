# identidock

`itentidock` example app from 

![cover](http://akamaicovers.oreilly.com/images/0636920035671/bkt.gif) [Using Docker](http://shop.oreilly.com/product/0636920035671.do)

Examples below are using [boot2docker](https://docs.docker.com/installation/mac/) on Mac running OS X 10.10.3.

## Step 1. Simple Hello World

Using [this Dockerfile](https://github.com/dlbewley/identidock/blob/b8994922451700e83c50afa79f9749216165d810/Dockerfile).

- Example of using the code bundled inside the _identidock_ image within the container.

```bash
docker build -t identidock .
DID=$(docker run -d -p 5000:5000 identidock)
curl $(boot2docker ip):5000 # expect Hello World!
docker rm -f $DID
```

- Example of using the code in our current directory referenced as volume bind mounted in _identidock_ container, occluding the code bundled inside the image.

```bash
DID=$(docker run -d -p 5000:5000 -v $(pwd)/app:/app identidock)
curl $(boot2docker ip):5000 # expect Hello World!
sed -i s/World/Docker/ app/identidock.py # undo this change after the test
curl $(boot2docker ip):5000 # expect Hello Docker!
docker rm -f $DID
```

## Step 2 add uWSGI

Using [this Dockerfile](https://github.com/dlbewley/identidock/blob/5b589a2c8e6d579a1c3f57e50f1daf7f57639b8c/Dockerfile).

- Start new _uwsgi_ tagged instance of _identidock_ docker image.

```bash
docker build -t identidock:uwsgi .
DID=$(docker run -d -p 9090:9090 -p 9191:9191 identidock:uwsgi)
curl $(boot2docker ip):9090          # expect Hello World!
curl $(boot2docker ip):9191          # expect JSON block of stats
docker logs $DID 2>&1 | grep WARNING # expect to get yelled at for using root
docker rm -f $DID
```

**BTW** Here are the images we have made at this point. Not that `lastest` is from step 1 and `uwsgi` is from step 2:

```
$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
identidock          uwsgi               cf36ee739e9c        12 minutes ago      767.2 MB
identidock          latest              fd04dbc88df1        43 minutes ago      765.1 MB
```

## Step 3 Run uWSGI as someone other than root

Using [this Dockerfile](https://github.com/dlbewley/identidock/blob/x/Dockerfile).

...

