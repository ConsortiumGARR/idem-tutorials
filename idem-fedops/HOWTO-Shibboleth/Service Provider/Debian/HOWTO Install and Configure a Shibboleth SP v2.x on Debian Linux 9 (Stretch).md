# HOWTO Install and Configure a Shibboleth SP v2.x on Debian Linux 9 (Stretch) 

<img width="120px" src="https://wiki.idem.garrservices.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements Hardware](#requirements-hardware)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Other Requirements](#other-requirements)
4. [Installation Instructions](#installation-instructions)
   1. [Install software requirements](#install-software-requirements)
   2. [Configure the environment](#configure-the-environment)
   3. [Install Shibboleth Service Provider](#install-shibboleth-service-provider)
5. [Configuration Instructions](#configuration-instructions)
   1. [Configure SSL on Apache2](#configure-ssl-on-apache2)
   2. [Configure Shibboleth SP](#configure-shibboleth-sp)
   3. [Configure an example federated resouce "secure"](#configure-an-example-federated-resouce-secure)
   4. [OPTIONAL - Maintain 'shibd' working](#optional---maintain-shibd-working)
   5. [Enable Attribute Support on Shibboleth SP](#enable-attribute-support-on-shibboleth-sp)
   6. [Enable Attribute Checker Support on Shibboleth SP](#enable-attribute-checker-support-on-shibboleth-sp)
6. [Authors](#authors)
7. [Thanks](#thanks)


## Requirements Hardware

 * CPU: 2 Core
 * RAM: 4 GB
 * HDD: 20 GB

## Software that will be installed

 * ca-certificates
 * ntp
 * vim
 * libapache2-mod-php, libapache2-mod-shib2, apache2 (>= 2.4)
 * openssl

## Other Requirements

 * Place the SSL Credentials into the right place:
   1. SSL Certificate: "```/etc/ssl/certs/ssl-sp.crt```"
   2. SSL Key: "```/etc/ssl/private/ssl-sp.key```"
   3. SSL CA: "```/usr/local/share/ca-certificates/ssl-ca.crt```"
   4. Run the command: "```update-ca-certificates```"

## Installation Instructions

### Install software requirements

1. Become ROOT:
   * ```sudo su -```

2. Change the default mirror with the GARR ones:
   * ```sed -i 's/deb.debian.org/mi.mirror.garr.it\/mirrors/g' /etc/apt/sources.list```
   * ```apt update && apt upgrade```
  
3. Install the packages required: 
   * ```apt install ca-certificates vim openssl```

### Configure the environment

1. Modify your ```/etc/hosts```:
   * ```vim /etc/hosts```
  
     ```bash
     127.0.1.1 sp.example.org sp
     ```
   (*Replace ```sp.example.org``` with your SP Full Qualified Domain Name*)

2. Be sure that your firewall **doesn't block** the traffic on port **443** (or you can't access to your SP)

3. ***Define the costant ```APACHE_LOG```, ```SHIB_SP``` and ```SHIBD_LOG``` inside ```/etc/environment```:
   * ```vim /etc/environment```

     ```bash
     APACHE_LOG=/var/log/apache2
     SHIB_SP=/etc/shibboleth
     SHIBD_LOG=/var/log/shibboleth
     ```

   * ```source /etc/environment```
  
   (OPTIONAL) Create a Certificate and a Key self-signed for HTTPS if you don't have yet the official ones provided by the Certificate Authority(DigicertCA):
   * ```openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/ssl-sp.key -out /etc/ssl/certs/ssl-sp.crt -nodes -days 1095```

### Install Shibboleth Service Provider

1. Become ROOT: 
   * ```sudo su -```

2. Install Shibboleth SP:
   * ```bash
     apt install apache2 libapache2-mod-shib2 libapache2-mod-php ntp --no-install-recommends
     ```

   From this point the location of the SP directory is: ```/etc/shibboleth```

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
        ...
        SSLCertificateFile /etc/ssl/certs/ssl-sp.crt
        SSLCertificateKeyFile /etc/ssl/private/ssl-sp.key
        ...
        SSLCertificateChainFile /root/certificates/ssl-ca.pem
        ...
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
      </VirtualHost>
   </IfModule>
   ```

2. Enable **proxy_http**, **SSL** and **headers** Apache2 modules:
   * ```a2enmod proxy_http ssl headers alias include negotiation```
   * ```a2ensite default-ssl.conf```
   * ```systemctl restart apache2.service```

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

   * ```systemctl reload apache2.service```
  
6. Verify the strength of your SP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

### Configure Shibboleth SP

1. Become ROOT: 
   * ```sudo su -```

2. Download Federation Metadata Signing Certificate:
   * ```cd /etc/shibboleth/```
   * ```wget https://www.idem.garr.it/documenti/doc_download/321-idem-metadata-signer-2019 -O idem_signer.pem```

   * Check the validity:
     *  ```openssl x509 -in idem_signer.pem -fingerprint -sha1 -noout```
       
        (sha1: 2F:F8:24:78:6A:A9:2D:91:29:19:2F:7B:33:33:FF:59:45:C1:7C:C8)
     *  ```openssl x509 -in federation-cert.pem -fingerprint -md5 -noout```

        (md5: AA:A7:CD:41:2D:3E:B7:F6:02:8A:D3:62:CD:21:F7:DE)

3. Edit ```shibboleth2.xml``` opportunely:
   * ```vim /etc/shibboleth/shibboleth2.xml```

     ```bash
     ...
     <ApplicationDefaults entityID="https://sp.example.org/shibboleth"
          REMOTE_USER="eppn persistent-id targeted-id"
          cipherSuites="ECDHE+AESGCM:ECDHE:!aNULL:!eNULL:!LOW:!EXPORT:!RC4:!SHA:!SSLv2">
     ...
     <Sessions lifetime="28800" timeout="3600" checkAddress="false" handlerSSL="true" cookieProps="https">
     ...
     <!-- To install and Configure the Shibboleth Embedded Discovery Service follow: http://tiny.cc/howto-idem-shib-eds -->
     <SSO discoveryProtocol="SAMLDS" discoveryURL="https://wayf.idem-test.garr.it/WAYF">
        SAML2
     </SSO>
     ...
     <MetadataProvider type="XML" uri="http://www.garr.it/idem-metadata/idem-test-metadata-sha256.xml" legacyOrgName="true" backingFilePath="idem-test-metadata-sha256.xml" reloadInterval="600">
           <MetadataFilter type="Signature" certificate="idem_signer.pem"/>
           <MetadataFilter type="RequireValidUntil" maxValidityInterval="864000" />
     </MetadataProvider>
     ```
4. Create SP metadata credentials:
   * ```/usr/sbin/shib-keygen```
   * ```shibd -t /etc/shibboleth/shibboleth2.xml``` (Check Shibboleth configuration)
   * ```systemctl restart shibd.service```

5. Enable Shibboleth Apache2 configuration:
   * ```a2enmod shib2```
   * ```systemctl reload apache2.service```

5. Now you are able to reach your Shibboleth SP Metadata on:
   * ```https://sp.example.org/Shibboleth.sso/Metadata```
   (change ```sp.example.org``` to you SP full qualified domain name)

7. Register you SP on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
   * Go to ```https://registry.idem.garr.it/``` and follow "Insert a New Service Provider into the IDEM Test Federation"


### Configure an example federated resouce "secure"

1. Create the Apache2 configuration for the application: 
   * ```sudo su -```

   * ```vim /etc/apache2/conf-available/secure.conf```
  
     ```bash
     RedirectMatch    ^/$  /secure

     <Location /secure>
       Authtype shibboleth
       ShibRequireSession On
       require valid-user
     </Location>
     ```
   * ```a2enconf secure```

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
   * ```apt install libapache2-mod-php```

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
     STOPPED_MESSAGE="failed"

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
1. Enable attribute by remove comment from the related content into "```/etc/shibboleth/attribute-map.xml```"
2. Disable First deprecated/incorrect version of ```persistent-id``` from ```attribute-map.xml```

### Enable Attribute Checker Support on Shibboleth SP
1. Add a sessionHook for attribute checker: `sessionHook="/Shibboleth.sso/AttrChecker"` and the `metadataAttributePrefix="Meta-"` to `ApplicationDefaults`:
   * ```vim /etc/shibboleth/shibboleth2.xml```

     ```bash
     <ApplicationDefaults entityID="https://<HOST>/shibboleth"
                          REMOTE_USER="eppn persistent-id targeted-id"
                          cipherSuites="ECDHE+AESGCM:ECDHE:!aNULL:!eNULL:!LOW:!EXPORT:!RC4:!SHA:!SSLv2"
                          sessionHook="/Shibboleth.sso/AttrChecker"
                          metadataAttributePrefix="Meta-" >
     ```
2. Add the attribute checker handler with the list of required attributes to Sessions (in the example below: `eppn`, `displayName`). The attributes' names HAVE TO MATCH with those are defined on `attribute-map.xml`:
   * ```vim /etc/shibboleth/shibboleth2.xml```

     ```bash
     <!-- Attribute Checker -->
     <Handler type="AttributeChecker" Location="/AttrChecker" template="attrChecker.html" attributes="eppn displayName" flushSession="true"/>
     ```
     
     If you want to describe more complex scenarios with required attributes, operators such as "AND" and "OR" are available.
     ```bash
     <Handler type="AttributeChecker" Location="/AttrChecker" template="attrChecker.html" flushSession="true">
        <OR>
           <Rule require="displayName"/>
           <AND>
              <Rule require="givenName"/>
              <Rule require="surname"/>
           </AND>
        </OR>
      </Handler>
      ```

3. Add the <AttributeExtractor> element of the type="Metadata" next to the already existing type="XML": (```<AttributeExtractor type="XML" validate="true" path="attribute-map.xml"/>```)
   * ```vim /etc/shibboleth/shibboleth2.xml```

     ```bash
     <!-- Extracts support information for IdP from its metadata. -->
     <AttributeExtractor type="Metadata" errorURL="errorURL" DisplayName="displayName"
                         InformationURL="informationURL" PrivacyStatementURL="privacyStatementURL"
                         OrganizationURL="organizationURL">
        <ContactPerson id="Technical-Contact"  contactType="technical" formatter="$EmailAddress" />
        <Logo id="Small-Logo" height="16" width="16" formatter="$_string"/>
     </AttributeExtractor>
     ```

4. Save and restart "shibd" service:
   * ```systemctl restart shibd.restart```
   
5. Customize Attribute Checker template:
   * ```cd /etc/shibboleth```
   * ```cp attrChecker.html attrChecker.html.orig```
   * ```wget https://raw.githubusercontent.com/CSCfi/shibboleth-attrchecker/master/attrChecker.html -O attrChecker.html```
   * ```sed -i 's/SHIB_//g' /etc/shibboleth/attrChecker.html```
   * ```sed -i 's/eduPersonPrincipalName/eppn/g' /etc/shibboleth/attrChecker.html```
   * ```sed -i 's/Meta-Support-Contact/Meta-Technical-Contact/g' /etc/shibboleth/attrChecker.html```
   * ```sed -i 's/supportContact/technicalContact/g' /etc/shibboleth/attrChecker.html```
   * ```sed -i 's/support/technical/g' /etc/shibboleth/attrChecker.html```

   There are three locations needing modifications:

   1. The pixel tracking link after the comment "PixelTracking". 
      The Image tag and all required attributes after the variable must be configured here. 
      After "`miss=`" define all required attributes you updated in `shibboleth2.xml` using shibboleth tagging. 
      
      Eg `<shibmlpifnot $attribute>-$attribute</shibmlpifnot>` (this echoes $attribute if it's not received by shibboleth).
      The attributes' names HAVE TO MATCH with those are defined on `attribute-map.xml`.
      
      This example uses "`-`" as a delimiter.
      
   2. The table showing missing attributes between the tags "`<!--TableStart-->`" and "`<!--TableEnd-->`". 
      You have to insert again all the same attributes as above.

      Define row for each required attribute (eg: `displayName` below)

      ```bash
      <tr <shibmlpifnot displayName> class='warning text-danger'</shibmlpifnot>>
        <td>displayName</td>
        <td><shibmlp displayName /></td>
      </tr>
      ```

   3. The email template between the tags "<textarea>" and "</textarea>". After "The attributes that were not released to the service are:". 

      Again define all required attributes using shibboleth tagging like in section 1 ( eg: `<shibmlpifnot $attribute> * $attribute</shibmlpifnot>`).
      The attributes' names HAVE TO MATCH with those are defined on `attribute-map.xml`.
      Note that for SP identifier target URL is used instead of entityID. 
      There arent yet any tag for SP entityID so you can replace this target URL manually.

6. Enable Logging:
   * Download an image 1x1 px from 'http://png-pixel.com/' and put it under /var/www/html/track.png (your DocumentRoot)

   * Result into /var/log/apache2/access.log:
   
   ```bash
   ./apache2/access.log:193.206.129.66 - - [20/Sep/2018:15:05:07 +0000] "GET /track.png?idp=https://garr-idp-test.irccs.garr.it/idp/shibboleth&miss=-SHIB_givenName-SHIB_cn-SHIB_sn-SHIB_eppn-SHIB_schacHomeOrganization-SHIB_schacHomeOrganizationType HTTP/1.1" 404 637 "https://sp.example.org/Shibboleth.sso/AttrChecker?return=https%3A%2F%2Fsp.example.org%2FShibboleth.sso%2FSAML2%2FPOST%3Fhook%3D1%26target%3Dss%253Amem%253A43af2031f33c3f4b1d61019471537e5bc3fde8431992247b3b6fd93a14e9802d&target=https%3A%2F%2Fsp.example.org%2Fsecure%2F"
   ```
   
### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
 
### Thanks

 * eduGAIN Wiki: For [How to configure Shibboleth SP attribute checker](https://wiki.geant.org/display/eduGAIN/How+to+configure+Shibboleth+SP+attribute+checker)
