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

## Step 3 Run uWSGI as someone other than root and auto-map ports

Using [this Dockerfile](https://github.com/dlbewley/identidock/blob/41f39ffbc2ea12c1357079d227b2a9fe0d003235/Dockerfile) run the container as `uwsgi` user and designate ports in Dockerfile instead of on the command line.

```bash
docker build -t identidock:user .
docker run identidock:uwsgi whoami
root
docker run identidock:user whoami
uwsgi
DID=$(docker run -d -P --name port-test identidock:user)
docker port port-test
9090/tcp -> 0.0.0.0:32768
9191/tcp -> 0.0.0.0:32769
curl $(boot2docker ip):32768
Hello World!
```

## Step 4 Delegate app start to cmd shell script which determines environment first

Using [this Dockerfile](https://github.com/dlbewley/identidock/blob/d0040c2a26d9a6a2c5c90d3510c55c4bddc336f8/Dockerfile) build and run a dev instance of identidock.

```bash
docker build -t identidock:cmd .
DID=$(docker run -e "ENV=DEV" -d -P identidock:cmd)
docker port $DID
5000/tcp -> 0.0.0.0:32782
9090/tcp -> 0.0.0.0:32783
9191/tcp -> 0.0.0.0:32784
# curl port 5000 in the container
curl $(boot2docker ip):32782
Hello World!
# there is nothing listening on 9090 in this container
curl $(boot2docker ip):32783
curl: (7) Failed to connect to 192.168.59.103 port 32783: Connection refused
```

Now stop that container and run a production instance.

```bash
docker rm -f $DID
DID=$(docker run -e "ENV=PROD" -d -P identidock:cmd)
docker port $DID
9191/tcp -> 0.0.0.0:32787
5000/tcp -> 0.0.0.0:32785
9090/tcp -> 0.0.0.0:32786
# there is nothing listening on 5000 in this container
curl $(boot2docker ip):32785
curl: (7) Failed to connect to 192.168.59.103 port 32785: Connection refused
# curl port 9090 in the container
curl $(boot2docker ip):32786
Hello World!
```