# HOW TO SETUP A SHIBBOLETH SP WITH NGINX

#### Author: Marco Cappellacci - Università degli Studi di Urbino Carlo Bo

## TABLE OF CONTENTS

1. [PREREQUISITES](#prerequisites)
2. [INTRODUCTION](#introduction)
3. [INSTALLATION OF THE NECESSARY SOFTWARE](#installation-of-the-necessary-software)
4. [CONFIGURATIONS](#configurations)
  1. [SUPERVISOR CONFIGURATION](#supervisor-configuration)
  2. [NGINX CONFIGURATION](#nginx-configuration)
  3. [PHP5-FPM CONFIGURATION](#php5-fpm-configuration)
  4. [SHIBBOLETH CONFIGURATION](#shibboleth-configuration)
5. [AUTHORS](#authors)
5. [CREDITS](#credits)


## PREREQUISITES

* Debian 8
* Valid https certificates emitted by an approved CA
* File ```/etc/hosts``` with the ip and the hostname of your SP


## INTRODUCTION

This guide aims to setup a functional shibboleth SP with Nginx on Debian 8.
The example SP hostname is sp.example.it, you need to change it with your real SP hostname.

**BONUS:** Through this guide you will be able to get A+ on https://www.ssllabs.com

## INSTALLATION OF THE NECESSARY SOFTWARE

Install all the necessary packets to make shibboleth, nginx and supervisor work.
```bash
apt-get update && \
    apt-get install -y  opensaml2-schemas xmltooling-schemas libshibsp6 \
        libshibsp-plugins shibboleth-sp2-common shibboleth-sp2-utils supervisor procps curl git && \
    apt-get install -y build-essential libpcre3 libpcre3-dev libpcrecpp0 libssl-dev zlib1g-dev php5-fpm
```

Install nginx stable version with all the necessary modules.
To do this you can install the packet compiled by me (point A) or if you have particular needs or you wonder about it, we can develop it together (point B).

* A.Ready packet:
```bash
cd /tmp
wget -O nginx_1.10.1-1~jessie_amd64.deb http://goo.gl/NVqfw3
dpkg -i nginx_1.10.1-1~jessie_amd64.deb  
```
You can jump right to chapter 4 [CONFIGURATIONS](#configurations)

* B.Creation of your customised packet

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
dpkg-buildpackage -b
```
Install the generated packet:
```
dpkg -i nginx_1.10.1-1~jessie_amd64.deb  
```
All the necessary packets have been installed, now proceed with configurations.

## CONFIGURATIONS

### SUPERVISOR CONFIGURATION 

Create shibboleth.conf in /etc/supervisor/conf.d/:
```
nano /etc/supervisor/conf.d/shibboleth.conf
```
Copy this code:
```bash
[fcgi-program:shibauthorizer]
command=/usr/lib/x86_64-linux-gnu/shibboleth/shibauthorizer
socket=tcp://localhost:9002
user=_shibd
stdout_logfile=/var/log/supervisor/shibauthorizer.log
stderr_logfile=/var/log/supervisor/shibauthorizer.error.log

[fcgi-program:shibresponder]
command=/usr/lib/x86_64-linux-gnu/shibboleth/shibresponder
socket=tcp://localhost:9003
user=_shibd
stdout_logfile=/var/log/supervisor/shibresponder.log
stderr_logfile=/var/log/supervisor/shibresponder.error.log
```
#### NGINX CONFIGURATION

Now configure nginx default host.
```
nano /etc/nginx/conf.d/default.conf
```
And insert:
```bash
server {
    	listen 80;

    	server_name www.sp.example.it sp.example.it;

    	rewrite ^(.*) https://sp.example.it$1 permanent;
}

server {
    listen 443 ssl;
    server_name sp.example.it;
    root   /var/www/;
    ssl_certificate     /etc/nginx/ssl/bundle.crt;
    ssl_certificate_key /etc/nginx/ssl/sp_example_it.key;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
    ssl_dhparam /etc/nginx/ssl/dhparam.pem;
    add_header Strict-Transport-Security "max-age=31536000";
    ssl_session_cache shared:ssl_session_cache:10m;
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;


    #FastCGI authorizer for Auth Request module
    location = /shibauthorizer {
        internal;
        include fastcgi_params;
        fastcgi_pass 127.0.0.1:9002;
    }

    #FastCGI responder
    location /Shibboleth.sso {
        include fastcgi_params;
        fastcgi_pass 127.0.0.1:9003;
    }

    #Resources for the Shibboleth error pages.
    location /shibboleth-sp {
        alias /usr/share/shibboleth/;
    }

    #A secured location.  
    location ^~ /secure {
         include shib_clear_headers;
         #Add your attributes here: 
         more_clear_input_headers 'displayName' 'mail' 'persistent-id';
         shib_request /shibauthorizer;
         shib_request_use_headers on;
         fastcgi_pass unix:/var/run/php5-fpm.sock;
    	  fastcgi_index index.php;
    	  fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
    	  include fastcgi_params;
     }

}
```
Create www and secure directory:
```bash
mkdir /var/www
mkdir /var/www/secure
```
Create ssl directory:
```bash
mkdir /etc/nginx/ssl
cd /etc/nginx/ssl
```


Copy your certificates, adapting the filename:
```
cat sp_example_it.crt DigiCertCA.crt >> bundle.crt
```
In the same folder /etc/nginx/ssl run the following command:
```
openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048
```
More info https://www.openssl.org/docs/manmaster/apps/dhparam.html

**WARNING** when the SP goes into production, the attribute list after “more_clear_input_headers” will be updated.

### PHP5-FPM CONFIGURATION

Create a group and add a new user:
```bash
groupadd www
useradd -g www www 
```
Change /etc/php5/fpm/pool.d/www.conf 
```
nano  /etc/php5/fpm/pool.d/www.conf
```
As follows:
```bash
user = www
group = www
listen = /var/run/php5-fpm.sock
listen.owner = nginx
listen.group = nginx
```
And the rest remains unchanged.

Edit /etc/php5/fpm/php.ini
```
nano  /etc/php5/fpm/php.ini
```
Change the following value:
```
cgi.fix_pathinfo=0
```
Restart php5-fpm
```
/etc/init.d/php5-fpm restart
```

### SHIBBOLETH CONFIGURATION

First, generate certificates:
```
shib-keygen -f
```
Uncomment example attribute in attribute-map.xml.
In production environment select only needed attribute.
```
nano /etc/shibboleth/attribute-map-xml
```
Uncomment the block under this line
```
<!--Examples of LDAP-based attributes, uncomment to use these... -->
```
Edit shibboleth2.xml
```
nano /etc/shibboleth/shibboleth2.xml
```
Before “ApplicationDefaults” add:
```bash
<RequestMapper type="XML">
	<RequestMap >
    	<Host name="sp.example.it"
            	authType="shibboleth"
            	requireSession="true"
            	redirectToSSL="443">
        	<Path name="/secure" />
    	</Host>
	</RequestMap>
</RequestMapper>
```
Modify your SP hostname in “ApplicationDefaults” 
```bash
<ApplicationDefaults entityID="https://sp.example.it/shibboleth"
                     	REMOTE_USER="eppn persistent-id targeted-id">
```
Insert idem test wayf:
```bash
<SSO discoveryProtocol="SAMLDS"discoveryURL="https://wayf.idem-test.garr.it/WAYF">
     SAML2
</SSO>
```
Add metadataprovider:
```bash
<MetadataProvider type="XML" uri="http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml" backingFilePath="idem-test-metadata-sha256.xml" reloadInterval="7200">
   <MetadataFilter type="Signature" certificate="federation-cert.pem"/>
   <MetadataFilter type="RequireValidUntil" maxValidityInterval="864000" />
   <MetadataFilter type="EntityRoleWhiteList">
      <RetainedRole>md:IDPSSODescriptor</RetainedRole>
      <RetainedRole>md:AttributeAuthorityDescriptor</RetainedRole>
   </MetadataFilter>
</MetadataProvider>
```
Change Sessions in this way:
```bash
<Sessions lifetime="28800" timeout="3600" relayState="ss:mem"
              	checkAddress="true" handlerSSL="true" cookieProps="https">
```
Download idem signer and change permission:
```bash
wget https://md.idem.garr.it/certs/idem-signer-20220121.pem -O /etc/shibboleth/federation-cert.pem

chmod 444 /etc/shibboleth/federation-cert.pem
```
Restart all services using the following script:
```
nano /root/restart.sh
```
Copy the following lines
```bash
#!/bin/bash
#

/etc/init.d/shibd restart
sleep 1
/etc/init.d/supervisor restart
sleep 1
/etc/init.d/nginx restart
```
Make the script executable:
```
chmod +x /root/restart.sh
```
And run it
```
/root/restart.sh
```
Test your work, registering metadata on IDEM test federation.
You can download metadata from https://sp.example.it/Shibboleth.sso/Metadata

**BONUS:** test your SP on ssl labs: https://www.ssllabs.com/ssltest/


### AUTHORS

#### ORIGINAL AUTHORS

 * Marco Cappellacci - Università degli Studi di Urbino Carlo Bo (marco.cappellacci@uniurb.it)

## CREDITS

* https://shibboleth.net/
* https://github.com/nginx-shib/nginx-http-shibboleth
* http://supervisord.org/
* http://nginx.org/en/
