# identidock

`itentidock` example app from ![cover](http://akamaicovers.oreilly.com/images/0636920035671/bkt.gif) [Using Docker](http://shop.oreilly.com/product/0636920035671.do)

## Step 1

Using [boot2docker](https://docs.docker.com/installation/mac/) on mac.

- Example of code bundled inside the container

```
docker build -t identidock .
DID=$(docker run -d -p 5000:5000 identidock)
curl $(boot2docker ip):5000 # expect Hello World!
docker rm -f $DID
```

- Example with code referenced as volume mounted from outside the container 

```
DID=$(docker run -d -p 5000:5000 -v $(pwd)/app:/app identidock)
curl $(boot2docker ip):5000 # expect Hello World!
sed -i s/World/Docker/ app/identidock.py
curl $(boot2docker ip):5000 # expect Hello Docker!
docker rm -f $DID
```

