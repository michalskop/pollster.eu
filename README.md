# Pollster.eu
Polls and bets from Europe

## Setup
Python3
```
git clone git@github.com:michalskop/pollster.eu.git
cd pollster.eu
cp server_settings-example.json server_settings.json
cp server_settings-example.py server_settings.py
sudo chmod a+x app.wsgi
```
setup server_settings.json

setup server_settings.py


```
sudo pip3 install Flask
# should install into /usr/local/lib/python3.5/dist-packages/ !!!s
sudo apt-get install libapache2-mod-wsgi-py3
```

```
sudo -i
cp pollster.eu-example.conf /etc/apache2/sites-available/pollster.eu.conf
exit
```
setup /etc/apache2/sites-available/pollster.eu.conf
