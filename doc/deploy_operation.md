server:ubuntu 14
connect server:

```
ssh username@address
```
```
/etc/init.d/sshd start
```

check sshd is run:
```
ps －e|grep ssh
```

update apt-get if not found 404 when install:
```
apt-get update
```
install sth you need

```
sudo apt-get install nginx supervisor python3 mysql-server
```

install easy install:
```
sudo apt-get install python-setuptools
```

copy file to server
```
scp [-r] filename[dir] username@address:/dir/
```


select python2.7

```
fab build
fab deploy
```






