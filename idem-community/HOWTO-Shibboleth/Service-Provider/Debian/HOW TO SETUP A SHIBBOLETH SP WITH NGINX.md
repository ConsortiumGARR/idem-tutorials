#HOW TO SETUP A SHIBBOLETH SP WITH NGINX

##TABLE OF CONTENTS

1. PREREQUISITES
2. INTRODUCTION
3. INSTALLATION OF THE NECESSARY SOFTWARE
4. CONFIGURATIONS
  1. SUPERVISOR CONFIGURATION
  2. NGINX CONFIGURATION
  3. PHP5-FPM CONFIGURATION
  4. SHIBBOLETH CONFIGURATION
5. CREDITS


##PREREQUISITES

* Debian 8
* Valid https certificates emitted by an approved CA
* File ```/etc/hosts``` with the ip and the hostname of your SP


##INTRODUCTION

This guide aims to setup a functional shibboleth SP with Nginx on Debian 8.
The example SP hostname is sp.example.it, you need to change it with your real SP hostname.

**BONUS:** Throught this guide you will be able to get A+ on https://www.ssllabs.com

##INSTALLATION OF THE NECESSARY SOFTWARE

Install all the necessary packets to make shibboleth, nginx and supervisor work.
```bash
apt-get update && \
    apt-get install -y  opensaml2-schemas xmltooling-schemas libshibsp6 \
        libshibsp-plugins shibboleth-sp2-common shibboleth-sp2-utils supervisor procps curl git && \
    apt-get install -y build-essential libpcre3 libpcre3-dev libpcrecpp0 libssl-dev zlib1g-dev php5-fpm
```

Install nginx stable version with all the necessary modules.
To do this you can install the packet compiled by me (point A) or if you have particular needs or you wonder about it, we can develop it together (point B).

*A.Ready packet:
```bash
cd /tmp
wget -O nginx_1.10.1-1~jessie_amd64.deb http://goo.gl/NVqfw3
dpkg -i nginx_1.10.1-1~jessie_amd64.deb  
```
You can jump right to chapter 4 (CONFIGURATION)

*B.Creation of your customised packet

Change the following file:
```
nano /etc/apt/sources.list
```
And add nginx repository:
```bash
#nginx repository
deb http://nginx.org/packages/debian/ jessie nginx
deb-src http://nginx.org/packages/debian/ jessie nginx
```
Then get the key for the new repository:
```bash
cd /tmp
wget http://nginx.org/keys/nginx_signing.key
apt-key add nginx_signing.key
```
Now you can download nginx sources (stable version in this moment 1.10.1) and additional modules:
```bash
cd /opt
git clone https://github.com/openresty/headers-more-nginx-module.git
git clone https://github.com/nginx-shib/nginx-http-shibboleth.git
mkdir buildnginx
cd buildnginx 
apt-get source nginx
apt-get build-dep nginx
```
Change the configuration to create the packet:
```
nano nginx1.10.1/debian/rules
```
In the same line of --with-ld-opt="$(LDFLAGS)" add  \ and then:
```bash
--with-ld-opt="$(LDFLAGS)" \
--add-module=/opt/headers-more-nginx-module \
--add-module=/opt/nginx-http-shibboleth
```
Make the packet with:
```
sudo dpkg-buildpackage -b
```
Install the generated packet:
```
dpkg -i nginx_1.10.1-1~jessie_amd64.deb  
```
All the necessary packets has been installed, now proceed with configurations.
