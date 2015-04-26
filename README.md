# identidock

`itentidock` example app from 

![cover](http://akamaicovers.oreilly.com/images/0636920035671/bkt.gif) [Using Docker](http://shop.oreilly.com/product/0636920035671.do) by [Adrian Mouat](https://github.com/amouat)

Examples below are using [boot2docker](https://docs.docker.com/installation/mac/) on Mac running OS X 10.10.3.

It might be helpful to refer to these Docker User Guide docs once you get stuck:

- [Hello World][1]
- [Working with Containers][2]

[1]: https://docs.docker.com/userguide/dockerizing/ "Docker User Guide: Hello World"
[2]: https://docs.docker.com/userguide/usingdocker/ "Docker User Guide: Working With Containers"
[3]: https://docs.docker.com/userguide/dockerimages/ "Docker User Guide: Working with Docker Images"
[4]: http://docs.docker.com/compose/install/ "Docker Compose Install"

## Step 1. Simple Hello World
_[Ref][1]_

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

**BTW** Here are [the images][3] we have made at this point. Not that `lastest` is from step 1 and `uwsgi` is from step 2:

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
_[Ref][2]_

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
# shortcut
curl $(boot2docker ip):$(docker port $DID 9090 | cut -d: -f2)
Hello World!
```

The `cut` in the shortcut above is needed since docker port returns something like `0.0.0.0:9999`. I there a better way to do that?

## Step 5 Use docker-compose to launch container

[Install docker-compose][4] before continuing.

```bash
curl -o docker-compose -L https://github.com/docker/compose/releases/download/1.2.0/docker-compose-`uname -s`-`uname -m`
chmod 755 docker-compose
sudo mv docker-compose /usr/local/bin
docker-compose --help
Illegal instruction: 4
```
**Oh no!** It didn't work!

[It turns out](https://github.com/docker/compose/issues/271) that you can `pip install` docker-compose to work around this.

```bash
brew update
brew install python
pip install docker-compose
```

Create a [docker-compose.yml](https://github.com/dlbewley/identidock/blob/8fc9164bdf074c8e9ffd1c49452a7738ff92b0aa/docker-compose.yml) which looks like this.

```yaml
---
identidock:
  build: .
  ports:
    - "5000:5000"
  environment:
    ENV: DEV
  volumes:
    - ./app:/app
```

Now, start up the container.

```bash
docker-compose up
```

Using `docker-compose` [v1.2.0](https://github.com/docker/compose/releases/tag/1.2.0), I got a python traceback:

```
Successfully built bb9620f3a5b1
Attaching to identidock_identidock_1
Exception in thread Thread-1:
Traceback (most recent call last):
  File "/usr/local/Cellar/python/2.7.6_1/Frameworks/Python.framework/Versions/2.7/lib/python2.7/threading.py", line 810, in __bootstrap_inner
    self.run()
  File "/usr/local/Cellar/python/2.7.6_1/Frameworks/Python.framework/Versions/2.7/lib/python2.7/threading.py", line 763, in run
    self.__target(*self.__args, **self.__kwargs)
  File "/usr/local/lib/python2.7/site-packages/compose/cli/multiplexer.py", line 41, in _enqueue_output
    for item in generator:
  File "/usr/local/lib/python2.7/site-packages/compose/cli/log_printer.py", line 59, in _make_log_generator
    for line in line_generator:
  File "/usr/local/lib/python2.7/site-packages/compose/cli/utils.py", line 77, in split_buffer
    for data in reader:
  File "/usr/local/lib/python2.7/site-packages/docker/client.py", line 225, in _multiplexed_response_stream_helper
    socket = self._get_raw_response_socket(response)
  File "/usr/local/lib/python2.7/site-packages/docker/client.py", line 167, in _get_raw_response_socket
    self._raise_for_status(response)
  File "/usr/local/lib/python2.7/site-packages/docker/client.py", line 119, in _raise_for_status
    raise errors.APIError(e, response, explanation=explanation)
APIError: 500 Server Error: Internal Server Error ("http: Hijack is incompatible with use of CloseNotifier")
```

I'm not sure what that is from, but everything is working.
A new image was built and a development version of the identidock app is up and running. Let's look around.

```
docker images
REPOSITORY              TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
identidock_identidock   latest              bb9620f3a5b1        42 seconds ago      767.5 MB

docker ps -l
CONTAINER ID        IMAGE                          COMMAND             CREATED             STATUS              PORTS                                        NAMES
9113a34dcce9        identidock_identidock:latest   "/cmd.sh"           5 minutes ago       Up 5 minutes        9090/tcp, 0.0.0.0:5000->5000/tcp, 9191/tcp   identidock_identidock_1

curl $(boot2docker ip):5000
Hello World!

docker-compose logs
Attaching to identidock_identidock_1
identidock_1 | Running Development Server
identidock_1 |  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
identidock_1 |  * Restarting with stat
identidock_1 | 192.168.59.3 - - [26/Apr/2015 22:13:14] "GET / HTTP/1.1" 200 -
identidock_1 |  * Detected change in '/app/identidock.py', reloading
identidock_1 |  * Restarting with stat
identidock_1 | 192.168.59.3 - - [26/Apr/2015 22:14:46] "GET / HTTP/1.1" 200 -
```

Since we mapped our app directory as a volume in the container, we can make changes to [identidock.py](app/identidock.py) which will be picked up immediately. Try it.
