# HOWTO Install and Configure a Shibboleth SP v2.6.1(from source) on Debian Linux 9 (Stretch) 

<img width="120px" src="https://wiki.idem.garrservices.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements Hardware](#requirements-hardware)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Other Requirements](#other-requirements)
4. [Installation Instructions](#installation-instructions)
   1. [Install software requirements](#install-software-requirements)
   2. [Configure the environment](#configure-the-environment)
   3. [Install Shibboleth Service Provider v2.6.1](##install-shibboleth-service-provider-v261)
5. [Configuration Instructions](#configuration-instructions)
   1. [Configure SSL on Apache2](#configure-ssl-on-apache2)
   2. [Configure Shibboleth SP (with IDEM WAYF)](#configure-shibboleth-sp-with-idem-wayf)
   3. [Configure an example federated resouce "secure"](#configure-an-example-federated-resouce-secure)
   4. [OPTIONAL - Maintain 'shibd' working](#optional---maintain-shibd-working)
   5. [Enable Attribute Support on Shibboleth SP](#enable-attribute-support-on-shibboleth-sp)
10. [Authors](#authors)


## Requirements Hardware

 * CPU: 2 Core
 * RAM: 4 GB
 * HDD: 20 GB

## Software that will be installed

 * ca-certificates
 * ntp
 * vim
 * libapache2-mod-php, apache2-dev, apache2 (>= 2.4)
 * g++, gcc
 * openssl, libcurl4-openssl-dev, libssl-dev, libboost-dev
 * libxerces-c-dev, liblog4shib1v5, libxml-security-c17v5, libsaml2-dev
 * libxmltooling-dev, libxmltooling7, xmltooling-schema
 * opensaml2-schemas
 * shibboleth-sp-2.6.1.tar.gz

## Other Requirements

 * Place the SSL Credentials into the right place:
   1. SSL Certificate: "```/etc/ssl/certs/ssl-sp.crt```"
   2. SSL Key: "```/etc/ssl/private/ssl-sp.key```"
   3. SSL CA: "```/usr/share/local/ca-certificates/ssl-ca.crt```"
   4. Run the command: "```update-ca-certificates```"

## Installation Instructions

### Install software requirements

1. Become ROOT:
   * ```sudo su -```

2. Change the default mirror with the GARR ones:
   * ```sed -i 's/deb.debian.org/mi.mirror.garr.it\/mirrors/g' /etc/apt/sources.list```
   * ```apt update && apt upgrade```
  
3. Install the packages required: 
   * ```apt install apache2 openssl ntp g++ libcurl4-openssl-dev libxerces-c-dev liblog4shib1v5 libxml-security-c17v5 libxmltooling-dev libxmltooling7 opensaml2-schemas apache2-dev libssl-dev libboost-dev xmltooling-schemas libsaml2-dev vim ca-certificates```

### Configure the environment

1. Modify your ```/etc/hosts```:
   * ```vim /etc/hosts```
  
     ```bash
     127.0.1.1 sp.example.org sp
     ```
   (*Replace ```sp.example.org``` with your SP Full Qualified Domain Name*)

2. Be sure that your firewall **doesn't block** the traffic on port **443** (or you can't access to your SP)

3. Define the costant ```JAVA_HOME``` and ```IDP_SRC``` inside ```/etc/environment```:
   * ```vim /etc/environment```

     ```bash
     APACHE_LOG=/var/log/apache2
     SHIB_SP=/opt/shibboleth-sp/etc/shibboleth
     SHIBD-LOG=/opt/shibboleth-sp/var/log/shibboleth
     ```

   * ```source /etc/environment```
  
   (OPTIONAL) Create a Certificate and a Key self-signed for HTTPS if you don't have yet the official ones provided by the Certificate Authority(DigicertCA):
   * ```openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/ssl-sp.key -out /etc/ssl/certs/ssl-sp.crt -nodes -days 1095```

### Install Shibboleth Service Provider v2.6.1

1. Become ROOT: 
   * ```sudo su -```

2. Download the Shibboleth Service Provider v2.6.1:
   * ```cd /usr/local/src```
   * ```wget https://shibboleth.net/downloads/service-provider/latest/shibboleth-sp-2.6.1.tar.gz -O shibboleth-sp.tar.gz```
   * ```tar -xzvf shibboleth-sp.tar.gz```
   * ```cd shibboleth-sp```

3. Install Shibboleth SP:
   * ```bash
     ./configure --with-log4shib=/usr/bin/log4shib-config --with-log4cpp=/usr/include/log4cpp --with-xmltooling=/usr/include/xmltooling --enable-apache-24 --with-apxs24=/usr/bin/apxs -prefix=/opt/shibboleth-sp
     ```
   * ```bash
     make
     ```
   * ```bash
     make install
     ```
 
   From this point the location of the SP directory is: ```/opt/shibboleth-sp```

## Configuration Instructions

### Configure SSL on Apache2

1. Modify the file ```/etc/apache2/sites-available/default-ssl.conf``` as follows:

   ```apache
   <IfModule mod_ssl.c>
      SSLStaplingCache        shmcb:/var/run/ocsp(128000)
      <VirtualHost _default_:443>
        ServerName sp.example.org:443
        ServerAdmin admin@example.org
        DocumentRoot /var/www/html
        ...
        SSLEngine On
        
        SSLProtocol All -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
        SSLCipherSuite "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH"

        SSLHonorCipherOrder on

        # Disable SSL Compression
        SSLCompression Off
        
        # OCSP Stapling, only in httpd/apache >= 2.3.3
        SSLUseStapling          on
        SSLStaplingResponderTimeout 5
        SSLStaplingReturnResponderErrors off
        
        # Enable HTTP Strict Transport Security with a 2 year duration
        Header always set Strict-Transport-Security "max-age=63072000;includeSubDomains;preload"
        ...
        SSLCertificateFile /root/certificates/ssl-sp.crt
        SSLCertificateKeyFile /root/certificates/ssl-sp.key
        SSLCertificateChainFile /root/certificates/ssl-ca.pem
        ...
      </VirtualHost>
   </IfModule>
   ```

2. Enable **proxy_http**, **SSL** and **headers** Apache2 modules:
   * ```a2enmod proxy_http ssl headers alias include negotiation```
   * ```a2ensite default-ssl.conf```
   * ```service apache2 restart```

3. Configure Apache2 to open port **80** only for localhost:
   * ```vim /etc/apache2/ports.conf```

     ```apache
     # If you just change the port or add more ports here, you will likely also
     # have to change the VirtualHost statement in
     # /etc/apache2/sites-enabled/000-default.conf

     Listen 127.0.0.1:80
 
     <IfModule ssl_module>
       Listen 443
     </IfModule>
    
     <IfModule mod_gnutls.c>
       Listen 443
     </IfModule>
     ```
5. Configure Apache2 to redirect all on HTTPS:
   * ```vim /etc/apache2/sites-enabled/000-default.conf```
   
     ```apache
     <VirtualHost *:80>
        ServerName "sp.example.org"
        Redirect permanent "/" "https://sp.example.org/"
        RedirectMatch permanent ^/(.*)$ https://sp.example.org/$1
     </VirtualHost>
     ```
  
6. Verify the strength of your IdP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

### Configure Shibboleth SP (with IDEM WAYF)

1. Become ROOT: 
   * ```sudo su -```

2. Enable Shibboleth Apache2 configuration:
   * ```cp /opt/shibboleth-sp/etc/shibboleth/apache24.config /etc/apache2/conf-available/shib-sp.conf```
   * ```apache2ctl configtest```
   * ```a2enconf shib-sp.conf ```
   * ```systemctl reload apache2.service ```
  
3. Download Federation Metadata Signing Certificate:
   * ```cd /opt/shibboleth-sp/etc/shibboleth/```
   * ```wget https://www.idem.garr.it/documenti/doc_download/321-idem-metadata-signer-2019 -O idem_signer.pem```

   * Check the validity:
     *  ```openssl x509 -in idem_signer.pem -fingerprint -sha1 -noout```
       
        (sha1: 2F:F8:24:78:6A:A9:2D:91:29:19:2F:7B:33:33:FF:59:45:C1:7C:C8)
     *  ```openssl x509 -in federation-cert.pem -fingerprint -md5 -noout```

        (md5: AA:A7:CD:41:2D:3E:B7:F6:02:8A:D3:62:CD:21:F7:DE)

4. Edit ```shibboleth2.xml``` opportunely:
   * ```vim /opt/shibboleth-sp/etc/shibboleth/shibboleth2.xml```

     ```bash
     ...
     <ApplicationDefaults entityID="https://sp.example.org/shibboleth"
          REMOTE_USER="eppn persistent-id targeted-id">
     ...
     <Sessions lifetime="28800" timeout="3600" checkAddress="false" handlerSSL="true" cookieProps="https">
     ...
     <SSO discoveryProtocol="SAMLDS" discoveryURL="https://wayf.idem-test.garr.it/WAYF">
        SAML2
     </SSO>
     ...
     <MetadataProvider type="XML" uri="http://www.garr.it/idem-metadata/idem-test-metadata-sha256.xml" legacyOrgName="true" backingFilePath="idem-test-metadata-sha256.xml" reloadInterval="600">
           <MetadataFilter type="Signature" certificate="idem_signer.pem"/>
     </MetadataProvider>
     ```

5. Enable '```shibd```' deamon and restart it:
   * ```cp -v /opt/shibboleth-sp/etc/shibboleth/shibd-debian /etc/init.d/shibd```
   * ```sudo update-rc.d shibd enable```
   * ```sudo systemctl restart shibd```

6. Now you are able to reach your Shibboleth SP Metadata on:
   * ```https://sp.example.org/Shibboleth.sso/Metadata```
   (change ```sp.example.org``` to you SP full qualified domain name)

7. Register you SP on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
   * Go to ```https://registry.idem.garr.it/``` and follow "Insert a New Service Provider into the IDEM Test Federation"

### Configure an example federated resouce "secure"

1. Create the Apache2 configuration for the application: 
   * ```sudo su -```
   * ```vim /etc/apache2/site-available/secure.conf```
  
     ```bash
     RedirectMatch    ^/$  /secure

     <Location /secure>
       Authtype shibboleth
       ShibRequireSession On
       require valid-user
     </Location>
     ```

2. Create the "```secure```" application into the DocumentRoot:
   * ```mkdir /var/www/html/secure```
   * ```vim /var/www/html/secure/index.php```
     ```html
     <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
     <html>
       <head>
         <title></title>
         <meta name="GENERATOR" content="Quanta Plus">
         <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
       </head>
       <body>
         <p>
          <a href="https://sp.example.org/privacy.html">Privacy Policy</a>
         </p>
         <?php
         // Visualizza tutte le informazioni, default: INFO_ALL
         //phpinfo();
         foreach ($_SERVER as $key => $value){
            print $key." = ".$value."<br>";
         }
         /*foreach ($_ENV as $key => $value){
            print $key." = ".$value."<br>";
         }
         foreach ($_COOKIE as $key => $value){
            print $key." = ".$value."<br>";
         }*/
         ?>
       </body>
     </html>
     ```

3. Install needed packages:
   * ```apt istall libapache2-mod-php```
   * ```systemctl restart apache2.service```


### OPTIONAL - Maintain '```shibd```' working
1. Edit '```shibd```' init script:
   * ```vim /etc/init.d/shibd```

     ```bash
     #...other lines...
     ### END INIT INFO

     # Import useful functions like 'status_of_proc' needed to 'status'
     . /lib/lsb/init-functions
     #...other lines...
     # Add 'status' operation
     status)
       status_of_proc -p "$PIDFILE" "$DAEMON" "$NAME" && exit 0 || exit $?
       ;;
     *)
       echo "Usage: $SCRIPTNAME {start|stop|restart|force-reload|status}" >&2
       exit 1
       ;;

     esac
     exit 0
     ```
2. Create a new watchdog for '```shibd```':
   * ```vim /etc/cron.hourly/watch-shibd.sh```

     ```bash
     #! /bin/bash
     SERVICE=/etc/init.d/shibd
     STOPPED_MESSAGE="shibd is not running"

     if [[ "`$SERVICE status`" == *"$STOPPED_MESSAGE"* ]];
     then
       $SERVICE stop
       sleep 1
       $SERVICE start
     fi
     ```
3. Reload daemon:
   * ```systemctl daemon-reload```

### Enable Attribute Support on Shibboleth SP
1. Enable attribute by remove comment from the related content into "```/opt/shibboleth-idp/etc/shibboleth/attribute-map.xml```"
2. Disable First deprecated/incorrect version of ```persistent-id``` from ```attribute-map.xml```

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
