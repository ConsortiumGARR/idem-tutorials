# HOWTO Install and Configure a Shibboleth SP v3.x on CentOS 7 (x86_64)

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements Hardware](#requirements-hardware)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Other Requirements](#other-requirements)
4. [Installation Instructions](#installation-instructions)
   1. [Install software requirements](#install-software-requirements)
   2. [Install Shibboleth Service Provider](#install-shibboleth-service-provider)
5. [Configuration Instructions](#configuration-instructions)
   1. [Configure the environment](#configure-the-environment)
   2. [Configure SSL on Apache2](#configure-ssl-on-apache2)
   3. [Configure Shibboleth SP](#configure-shibboleth-sp)
   4. [Configure an example federated resource "secure"](#configure-an-example-federated-resource-secure)
   5. [Enable Attribute Support on Shibboleth SP](#enable-attribute-support-on-shibboleth-sp)
   6. [Enable Attribute Checker Support on Shibboleth SP](#enable-attribute-checker-support-on-shibboleth-sp)
   7. [SE Linux](#se-linux)
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
 * httpd.x86_64 (Apache >= 2.4)
 * php
 * openssl
 * shibboleth.x86_64

## Other Requirements

 * Place the SSL Credentials into the right place:
   1. SSL Certificate: "```/etc/pki/tls/certs/ssl-sp.crt```"
   2. SSL Key: "```/etc/pki/tls/private/ssl-sp.key```"
   3. SSL CA: "```/etc/pki/ca-trust/source/anchors/ssl-ca.crt```"
   4. Run the command: "```update-ca-trust extract```"

## Installation Instructions

### Install software requirements

1. Become ROOT:
   * ```sudo su -```
  
2. Install the packages required: 
   * ```yum install ca-certificates vim openssl```

### Install Apache2 Web Server
1. Become ROOT: 
   * ```sudo su -```

2. Create the Shibboleth Repository:
   * ```yum install httpd.x86_64```

3. Remove the pre-set Apache welcome page
   * ```sed -i 's/^/#&/g' /etc/httpd/conf.d/welcome.conf```
   
4. Prevent Apache from listing web directory files to visitors:
   * ```sed -i "s/Options Indexes FollowSymLinks/Options FollowSymLinks/" /etc/httpd/conf/httpd.conf```
   
5. Start the Apache service and enable it to auto-start on boot:
   * ```systemctl start httpd.service```
   * ```systemctl enable httpd.service```

### Install Shibboleth Service Provider

1. Become ROOT: 
   * ```sudo su -```

2. Create the Shibboleth Repository:
   * ```vim /etc/yum.repos.d/shibboleth.repo```
   
     ```bash
     [shibboleth]
     name=Shibboleth (CentOS_7)
     # Please report any problems to https://issues.shibboleth.net
     type=rpm-md
     mirrorlist=https://shibboleth.net/cgi-bin/mirrorlist.cgi/CentOS_7
     gpgcheck=1
     gpgkey=https://download.opensuse.org/repositories/security:/shibboleth/CentOS_7/repodata/repomd.xml.key
     enabled=1
     ```

   * Save changes by clicking on the ```Esc``` button and by digiting ```:wq```

3. Update the repositories with:

   * ```yum update -y```

4. Discover what architecture do you have with:

   * ```echo "I am running: `cat /etc/redhat-release` (`arch`)"```
   
5. Install Shibboleth Service Provider:

   * ```yum install shibboleth.x86_64 -y```
   
   From this point the location of the SP directory will be: ```/etc/shibboleth```

## Configuration Instructions

### Configure the environment

1. Modify your ```/etc/hosts```:
   * ```vim /etc/hosts```
  
     ```bash
     192.168.XX.YY sp.example.org sp
     ```
   (*Replace ```sp.example.org``` with your SP Full Qualified Domain Name*)
   (*Replace ```192.168.XX.YY``` with your SP's private IP*)

2. Be sure that your firewall **doesn't block** the traffic on port **443** (or you can't access to your SP)
  
   (OPTIONAL) Create a Certificate and a Key self-signed for HTTPS if you don't have yet the official ones provided by the Certificate Authority:
   * ```bash
     openssl req -x509 -newkey rsa:4096 -keyout /etc/pki/tls/private/ssl-sp.key -out /etc/pki/tls/certs/ssl-sp.crt -nodes -days 1095
     ```

### Configure SSL on Apache2

1. Install "mod_ssl" to enable HTTPS configuration:
   * ```yum install mod_ssl -y```

2. Modify the file ```/etc/httpd/conf.d/ssl.conf``` as follows:

   ```apache
   ...
   SSLStaplingCache shmcb:/var/run/ocsp(128000)
   <VirtualHost _default_:443>
   DocumentRoot /var/www/html
   ServerName sp.example.org:443
   ServerAdmin admin@example.org
   ...
   SSLEngine On
   ...
   SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
   ...
   SSLCipherSuite "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH"
   SSLHonorCipherOrder on
   ...
   SSLCertificateFile /etc/pki/tls/certs/ssl-sp.crt
   ...
   SSLCertificateKeyFile /etc/pki/tls/private/ssl-sp.key
   ...
   SSLCACertificateFile /etc/pki/tls/certs/ca-bundle.crt
   ...
   # Disable SSL Compression
   SSLCompression Off
        
   # OCSP Stapling, only in httpd/apache >= 2.3.3
   SSLUseStapling On
   SSLStaplingResponderTimeout 5
   SSLStaplingReturnResponderErrors off
        
   # Enable HTTP Strict Transport Security with a 2 year duration
   Header always set Strict-Transport-Security "max-age=63072000;includeSubDomains;preload"
   </VirtualHost>
   ```

2. Reload Apache2 web server:
   * ```systemctl restart httpd.service```

3. Configure Apache2 to open port **80** only for localhost:
   * ```vim /etc/httpd/conf/httpd.conf```

     ```apache
     ...
     # Listen 12.34.56.78:80
     Listen 127.0.0.1:80
     ```
5. Configure Apache2 to redirect all on HTTPS:
   * ```vim /etc/httpd/conf.d/000-default.conf```
   
     ```apache
     <VirtualHost *:80>
        ServerName "sp.example.org"
        Redirect permanent "/" "https://sp.example.org/"
        RedirectMatch permanent ^/(.*)$ https://sp.example.org/$1
     </VirtualHost>
     ```

   * ```systemctl restart httpd.service```
  
6. Verify the strength of your SP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

### Configure Shibboleth SP

1. Become ROOT: 
   * ```sudo su -```

2. Retrieve the Federation Certificate used to verify its signed metadata:
   * ```cd /etc/shibboleth/```
   * ```bash
     curl https://md.idem.garr.it/certs/idem-signer-20220121.pem -o federation-cert.pem
     ```

    * Check the validity:
      *  ```cd /etc/shibboleth```
      *  ```openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout```
       
         (sha1: D1:68:6C:32:A4:E3:D4:FE:47:17:58:E7:15:FC:77:A8:44:D8:40:4D)
      *  ```openssl x509 -in federation-cert.pem -fingerprint -md5 -noout```

         (md5: 48:3B:EE:27:0C:88:5D:A3:E7:0B:7C:74:9D:24:24:E0)

3. Edit ```shibboleth2.xml``` opportunely:
   * ```vim /etc/shibboleth/shibboleth2.xml```

     ```bash
     ...
     <ApplicationDefaults entityID="https://sp.example.org/shibboleth"
          REMOTE_USER="eppn subject-id pairwise-id persistent-id"
          cipherSuites="DEFAULT:!EXP:!LOW:!aNULL:!eNULL:!DES:!IDEA:!SEED:!RC4:!3DES:!kRSA:!SSLv2:!SSLv3:!TLSv1:!TLSv1.1">
     ...
     <Sessions lifetime="28800" timeout="3600" relayState="ss:mem"
               checkAddress="false" handlerSSL="true" cookieProps="https">
     ...
     <!-- To install and Configure the Shibboleth Embedded Discovery Service follow: http://tiny.cc/howto-idem-shib-eds -->
     <SSO discoveryProtocol="SAMLDS" discoveryURL="https://wayf.idem-test.garr.it/WAYF">
        SAML2
     </SSO>
     ...
     <Errors supportContact="support@example.org"
            helpLocation="/about.html"
            styleSheet="/shibboleth-sp/main.css"/>
     ...
     <MetadataProvider type="XML" url="http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml"
                       legacyOrgName="true" backingFilePath="idem-test-metadata-sha256.xml" maxRefreshDelay="7200">
           <MetadataFilter type="Signature" certificate="federation-cert.pem"/>
           <MetadataFilter type="RequireValidUntil" maxValidityInterval="864000" />
     </MetadataProvider>
     
     <!-- Map to extract attributes from SAML assertions. -->
     <AttributeExtractor type="XML" validate="true" reloadChanges="true" path="attribute-map.xml"/>
     ```

4. Create SP metadata Signing and Encryption credentials:
   ```bash
   cd /etc/shibboleth
        
   ./keygen.sh -u shibd -g shibd -h $(hostname -f) -y 30 -e https://$(hostname -f)/shibboleth -n sp-signing -f
        
   ./keygen.sh -u shibd -g shibd -h $(hostname -f) -y 30 -e https://$(hostname -f)/shibboleth -n sp-encrypt -f
        
   LD_LIBRARY_PATH=/opt/shibboleth/lib64 /usr/sbin/shibd -t
   
   systemctl restart shibd.service
  
   systemctl restart httpd.service
   ```

5. Now you are able to reach your Shibboleth SP Metadata on:
   * ```https://sp.example.org/Shibboleth.sso/Metadata```
   (change ```sp.example.org``` to you SP full qualified domain name)

6. Register you SP on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
   * Go to ```https://registry.idem.garr.it``` and follow "Insert a New Service Provider into the IDEM Test Federation"


### Configure an example federated resource "secure"

1. Check to have the Apache configuration for the "secure" application on:
   * ```vim /etc/httpd/conf.d/shib.conf```
  
     ```bash
     ...
     <Location /secure>
       AuthType shibboleth
       ShibRequestSetting requireSession 1
       require shib-session
     </Location>
     ```

2. Create the "```secure```" application into the DocumentRoot:
   * ```mkdir /var/www/html/secure```

   * ```vim /var/www/html/secure/index.php```

     ```php
     <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
      <html>
       <head>
        <title>Example PHP Federated Application</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
       </head>
       <body>
        <p>
         <a href="https://sp.example.org/privacy.html">Privacy Policy</a>
        </p>
        <?php
         //The REMOTE_USER variable holds the name of the user authenticated by the web server.
         $name = getName();
         print "<h1>Ciao " . $name . "!!!</h1>";

         print "<p>Let see all other attributes:</p>";
         print "<p>Your REMOTE_USER is <strong>" . $_SERVER["REMOTE_USER"] . "</strong></p>";
         print "<p>Your email is <strong>" . $_SERVER['mail'] . "</strong></p>";
         print "<p>Your eduPersonPrincipalName is <strong>" . $_SERVER["eppn"] . "</strong></p>";
         print "<p>Your schacHomeOrganization is <strong>" . $_SERVER["schacHomeOrganization"] . "</strong></p>";
         print "<p>Your schacHomeOrganizationType is <strong>" . $_SERVER["schacHomeOrganizationType"] . "</strong></p>";

        ?>
       </body>
      </html>

      <?php
      function getName() {
       if (array_key_exists("displayName", $_SERVER)) {
       return implode(" ", explode(";", $_SERVER["displayName"]));
       } else if (array_key_exists("cn", $_SERVER)) {
       return implode(" ", explode(";", $_SERVER["cn"]));
       } else if (array_key_exists("givenName", $_SERVER) && array_key_exists("sn", $_SERVER)) {
       return implode(" ", explode(";", $_SERVER["givenName"])) . " " .
       implode(" ", explode(";", $_SERVER["sn"]));
       }
       return "Unknown";
      }
     ?>
     ```

3. Install PHP 7.x:
   1. Enable Remi and EPEL yum repositories on your system:
      * ```yum install epel-release```
      * ```rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-7.rpm```

   2. Install PHP 7.x:
      * 7.1: ```yum --enablerepo=remi-php71 install php```
      * 7.2: ```yum --enablerepo=remi-php72 install php```
   
   3. Verify:
      * ```php -v```

   4. Enable PHP:
      * ```systemctl restart httpd.service```

### Enable Attribute Support on Shibboleth SP
1. Enable attribute support by removing comment from the related content into "```/etc/shibboleth/attribute-map.xml```"

### Enable Attribute Checker Support on Shibboleth SP
1. Add a sessionHook for attribute checker: `sessionHook="/Shibboleth.sso/AttrChecker"` and the `metadataAttributePrefix="Meta-"` to `ApplicationDefaults`:
   * ```vim /etc/shibboleth/shibboleth2.xml```

     ```bash
     <ApplicationDefaults entityID="https://<HOST>/shibboleth"
                          REMOTE_USER="eppn subject-id pairwise-id persistent-id"
                          cipherSuites="DEFAULT:!EXP:!LOW:!aNULL:!eNULL:!DES:!IDEA:!SEED:!RC4:!3DES:!kRSA:!SSLv2:!SSLv3:!TLSv1:!TLSv1.1"
                          sessionHook="/Shibboleth.sso/AttrChecker"
                          metadataAttributePrefix="Meta-">
     ```
2. Add the attribute checker handler with the list of required attributes to Sessions (in the example below: `displayName`, `givenName`, `mail`, `cn`, `sn`, `eppn`, `schacHomeOrganization`, `schacHomeOrganizationType`). The attributes' names HAVE TO MATCH with those are defined on `attribute-map.xml`:
   * ```vim /etc/shibboleth/shibboleth2.xml```

     ```bash
     <!-- Attribute Checker -->
     <Handler type="AttributeChecker" Location="/AttrChecker" template="attrChecker.html" attributes="displayName givenName mail cn sn eppn schacHomeOrganization schacHomeOrganizationType" flushSession="true"/>
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

3. Add the following `<AttributeExtractor>` element under `<AttributeExtractor type="XML" validate="true" reloadChanges="false" path="attribute-map.xml"/>`
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
   * ```systemctl restart shibd.service```
   
5. Customize Attribute Checker template:
   * `cd /etc/shibboleth`
   * `cp attrChecker.html attrChecker.html.orig`
   * `curl https://raw.githubusercontent.com/CSCfi/shibboleth-attrchecker/master/attrChecker.html -o attrChecker.html`
   * `sed -i 's/SHIB_//g' /etc/shibboleth/attrChecker.html`
   * `sed -i 's/eduPersonPrincipalName/eppn/g' /etc/shibboleth/attrChecker.html`
   * `sed -i 's/Meta-Support-Contact/Meta-Technical-Contact/g' /etc/shibboleth/attrChecker.html`
   * `sed -i 's/supportContact/technicalContact/g' /etc/shibboleth/attrChecker.html`
   * `sed -i 's/support/technical/g' /etc/shibboleth/attrChecker.html`

   There are three locations needing modifications to do on `attrChecker.html`:

   1. The pixel tracking link after the comment "PixelTracking". 
      The Image tag and all required attributes after the variable must be configured here. 
      After "`miss=`" define all required attributes you updated in `shibboleth2.xml` using shibboleth tagging. 
      
      Eg `<shibmlpifnot $attribute>-$attribute</shibmlpifnot>` (this echoes $attribute if it's not received by shibboleth).
      The attributes' names HAVE TO MATCH with those are defined on `attribute-map.xml`.
      
      This example uses "`-`" as a delimiter.
      
   2. The table showing missing attributes between the tags "`<!--TableStart-->`" and "`<!--TableEnd-->`". 
      You have to insert again all the same attributes as above.

      Define row for each required attribute (eg: `displayName` below)

      ```html
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
   * Create your ```track.png``` with into your DocumentRoot:
   
     ```bash
     echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" | base64 -d > /var/www/html/track.png
     ```

   * Result into `/var/log/httpd/access.log`:
     ```bash
     ./httpd/access.log:193.206.129.66 - - [20/Sep/2018:15:05:07 +0000] "GET /track.png?idp=https://garr-idp-test.irccs.garr.it/idp/shibboleth&miss=-SHIB_givenName-SHIB_cn-SHIB_sn-SHIB_eppn-SHIB_schacHomeOrganization-SHIB_schacHomeOrganizationType HTTP/1.1" 404 637 "https://sp.example.org/Shibboleth.sso/AttrChecker?return=https%3A%2F%2Fsp.example.org%2FShibboleth.sso%2FSAML2%2FPOST%3Fhook%3D1%26target%3Dss%253Amem%253A43af2031f33c3f4b1d61019471537e5bc3fde8431992247b3b6fd93a14e9802d&target=https%3A%2F%2Fsp.example.org%2Fsecure%2F"
     ```

### SE Linux
If you'll met problem, probably they are related to SE Linux.

If you want to disable it until the next server reboot, doing this:

* ```sudo setenforce 0```

If you want to disable it forever do this:

* ```sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config ; setenforce permissive```

The SE Linux is disabled if you will find ```Current mode: permissive``` from the command ```sestatus```.

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
 * Barbara Monticini (barbara.monticini@garr.it)
 
### Thanks

 * eduGAIN Wiki: For the original [How to configure Shibboleth SP attribute checker](https://wiki.geant.org/display/eduGAIN/How+to+configure+Shibboleth+SP+attribute+checker)
