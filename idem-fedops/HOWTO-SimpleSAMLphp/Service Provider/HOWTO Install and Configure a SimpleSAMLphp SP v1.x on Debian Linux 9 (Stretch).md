# HOWTO Install and Configure a SimpleSAMLphp SP v1.x on Debian Linux 9 (Stretch) 

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements Hardware](#requirements-hardware)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Other Requirements](#other-requirements)
4. [Installation Instructions](#installation-instructions)
   1. [Install software requirements](#install-software-requirements)
   2. [Configure the environment](#configure-the-environment)
   3. [Install SimpleSAMLphp Service Provider](#install-simplesamlphp-service-provider)
5. [Configuration Instructions](#configuration-instructions)
   1. [Configure SSL on Apache2](#configure-ssl-on-apache2)
   2. [Configure SimpleSAMLphp SP](#configure-simplesamlphp-sp)
   3. [Configure an example federated resouce "secure"](#configure-an-example-federated-resouce-secure)
6. [Utility](#utility)
7. [Authors](#authors)


## Requirements Hardware

 * CPU: 2 Core
 * RAM: 4 GB
 * HDD: 20 GB

## Software that will be installed

 * ca-certificates
 * ntp
 * vim
 * libapache2-mod-php, php, php7.0-mcrypt, php-dom, php-curl, php-mbstring, apache2 (>= 2.4)
 * openssl
 * cron
 * curl

## Other Requirements

 * Place the SSL Credentials into the right place:
   * SSL Certificate: "`/etc/ssl/certs/ssl-sp.crt`"
   * SSL Key: "`/etc/ssl/private/ssl-sp.key`"
   * SSL CA: "`/usr/local/share/ca-certificates/ssl-ca.crt`"
   * Run the command: "`update-ca-certificates`"

## Installation Instructions

### Install software requirements

1. Become ROOT:
   * `sudo su -`

2. Change the default mirror with the GARR ones:
   * `sed -i 's/deb.debian.org/debian.mirror.garr.it/g' /etc/apt/sources.list`
   * `apt update && apt upgrade`
  
3. Install the packages required:
   * `apt install ca-certificates vim openssl`

### Configure the environment

1. Modify your `/etc/hosts`:
   * `vim /etc/hosts```
  
     ```bash
     127.0.1.1 sp.example.org sp
     ```
   (*Replace `sp.example.org` with your SP Full Qualified Domain Name*)

2. Be sure that your firewall **doesn't block** the traffic on port **443** (or you can't access to your SP)

### Install SimpleSAMLphp Service Provider

1. Become ROOT: 
   * `sudo su -`

2. Install required packages SP:
   * ```bash
     apt install apache2 openssl ntp vim php php-curl php-dom php7.0-mcrypt php-mbstring curl cron --no-install-recommends
     ```

3. Install the SimpleSAMLphp SP:
   * `cd /opt/`
   * `wget https://github.com/simplesamlphp/simplesamlphp/releases/download/v1.19.1/simplesamlphp-1.19.1.tar.gz`
   * `tar xzf simplesamlphp-1.19.1.tar.gz`
   * `mv simplesamlphp-1.19.1 simplesamlphp`

## Configuration Instructions

### Configure SSL on Apache2

1. Complete the file `/etc/apache2/sites-available/default-ssl.conf` as follows:

   ```apache
   <IfModule mod_ssl.c>
      SSLStaplingCache        shmcb:/var/run/ocsp(128000)
      <VirtualHost _default_:443>
        ServerName sp.example.org:443
        ServerAdmin admin@example.org
        DocumentRoot /var/www/html
        
        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
	
        #LogLevel info ssl:warn
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
        
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
        
        SSLCertificateFile /etc/ssl/certs/ssl-sp.crt
        SSLCertificateKeyFile /etc/ssl/private/ssl-sp.key
	
        SSLCertificateChainFile /etc/ssl/certs/ssl-ca.pem
        
      </VirtualHost>
   </IfModule>
   ```

2. Enable **proxy_http**, **SSL** and **headers** Apache2 modules:
   * `a2enmod ssl headers alias include negotiation`
   * `a2ensite default-ssl.conf`
   * `systemctl restart apache2`

3. Configure Apache2 to open port **80** only for localhost:
   * `vim /etc/apache2/ports.conf`

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
   * `vim /etc/apache2/sites-enabled/000-default.conf`
   
     ```apache
     <VirtualHost *:80>
        ServerName "sp.example.org"
        Redirect permanent "/" "https://sp.example.org/"
        RedirectMatch permanent ^/(.*)$ https://sp.example.org/$1
     </VirtualHost>
     ```

6. Verify the strength of your SP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

### Configure SimpleSAMLphp SP

1. Become ROOT: 
   * `sudo su -`

2. Create the Apache2 configuration for the application: 

   * `vim /etc/apache2/conf-available/simplesaml.conf`
  
     ```bash
     Alias /simplesaml /opt/simplesamlphp/www

     RedirectMatch    ^/$  /simplesaml

     <Location /simplesaml>
       Require all granted
     </Location>
     ```

3. Enable the simplesaml Apache2 configuration:

   * ```a2enconf simplesaml.conf`

   * `systemctl reload apache2.service```

4. Change the permission for SimpleSAMLphp logs:

   * `chown www-data /opt/simplesamlphp/log`

5. Configure the SimpleSAMLphp SP:

   * Generate some useful opaque strings:
      * User Admin Password (`auth.adminpassword`):
        `php /opt/simplesamlphp/bin/pwgen.php`
        
      * Secret Salt (`secretsalt`):
        `tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo`
        
      * Cron Key (`key`):
        `tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo`

   * Change SimpleSAMLphp configuration:
      `vim /opt/simplesamlphp/config/config.php`
   
      ```bash
      ...
      'technicalcontact_name' => 'Technical Contact',
      'technicalcontact_email' => 'service.support@example.com',
      ...
      'secretsalt' => '#_YOUR_SECRET_SALT_HERE_#',
      ...
      'auth.adminpassword' => '#_YOUR_USER_ADMIN_PASSWORD_#',
      ...
      'admin.protectindexpage' => true,
      ...
      'logging.handler' => 'file',
      ```

6. Generate SAML Credentials:

   * Move on the SAML credentials directory:
     * `cd /opt/simplesamlphp/cert`

   * Follow [Appendix A: Sample SAML2 Metadata embedded certificate](https://www.switch.ch/aai/support/certificates/embeddedcerts-requirements-appendix-a/) and generate the right SAML Credentials.

7. Configure automatic download of Federation Metadata:

   * Enable CRON module:

     ```bash
     cd /opt/simplesamlphp/

     touch modules/cron/enable

     cp modules/cron/config-templates/module_cron.php config/
     ```

   * Enable METAREFRESH module:
   
     ```bash
     cd /opt/simplesamlphp/

     touch modules/metarefresh/enable

     cp modules/metarefresh/config-templates/config-metarefresh.php config/
     ```

     Test if it works:

     ```bash
     cd /opt/simplesamlphp/modules/metarefresh/bin

     ./metarefresh.php -s http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml > metarefresh-test.txt
     ```

   * Change the CRON configuration file:

     `vim /opt/simplesamlphp/config/module_cron.php`

     ```php
     <?php
     /*
      * Configuration for the Cron module.
      */

     $config = array (

             'key' => '#_YOUR_CRON_KEY_#',
             'allowed_tags' => array('daily', 'hourly', 'frequent'),
             'debug_message' => TRUE,
             'sendemail' => TRUE,

     );
     ?>
     ```

   * Insert the following Cron job to the crontab file (`crontab -e`):
   
     ```bash
     # Run cron: [hourly]
     01 * * * *  root  curl --silent "https://sp.example.org/simplesaml/module.php/cron/cron.php?key=<SECRET>&tag=hourly" > /dev/null 2>&1
     ```

   * Configure METAREFRESH:

     `vim /opt/simplesamlphp/config/config-metarefresh.php`

     ```bash
     <?php

     $config = array(

        /*
         * Global blacklist: entityIDs that should be excluded from ALL sets.
        */
        #'blacklist' = array(
        #       'http://my.own.uni/idp'
        #),

        /*
         * Conditional GET requests
         * Efficient downloading so polling can be done more frequently.
         * Works for sources that send 'Last-Modified' or 'Etag' headers.
         * Note that the 'data' directory needs to be writable for this to work.
         */
        #'conditionalGET'       => TRUE,

        'sets' => array(

           'idem' => array(
              'cron'    => array('hourly'),
              'sources' => array(
                              array(
                                 /*
                                  * entityIDs that should be excluded from this src.
                                  */
                                 #'blacklist' => array(
                                 #       'http://some.other.uni/idp',
                                 #),

                                 /*
                                  * Whitelist: only keep these EntityIDs.
                                  */
                                 #'whitelist' => array(
                                 #       'http://some.uni/idp',
                                 #       'http://some.other.uni/idp',
                                 #),

                                 #'conditionalGET' => TRUE,
                                 'src' => 'http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml',
                                 'certificates' => array(
                                    '/opt/simplesamlphp/cert/federation-cert.pem',
                                 ),
                                 'template' => array(
                                    'tags'  => array('idem'),
                                    'authproc' => array(
                                       51 => array('class' => 'core:AttributeMap', 'oid2name'),
                                    ),
                                 ),

                                 /*
                                  * The sets of entities to load, any combination of:
                                  *  - 'saml20-idp-remote'
                                  *  - 'saml20-sp-remote'
                                  *  - 'shib13-idp-remote'
                                  *  - 'shib13-sp-remote'
                                  *  - 'attributeauthority-remote'
                                  *
                                  * All of them will be used by default.
                                  *
                                  * This option takes precedence over the same option per metadata set.
                                  */
                                //'types' => array(),
                              ),
                           ),
              'expireAfter' => 60*60*24*10, // Maximum 10 days cache time
              'outputDir'   => 'metadata/idem-federation/',

              /*
               * Which output format the metadata should be saved as.
               * Can be 'flatfile' or 'serialize'. 'flatfile' is the default.
              */
              'outputFormat' => 'flatfile',


              /*
               * The sets of entities to load, any combination of:
               *  - 'saml20-idp-remote'
               *  - 'saml20-sp-remote'
               *  - 'shib13-idp-remote'
               *  - 'shib13-sp-remote'
               *  - 'attributeauthority-remote'
               *
               * All of them will be used by default.
              */
              //'types' => array(),
           ),
        ),
     );

     ```

   * `mkdir /opt/simplesamlphp/metadata/idem-federation ; chown www-data /opt/simplesamlphp/metadata/idem-federation`

   * Change the SimpleSAMLphp configuration file:

     `vim /opt/simplesamlphp/config/config.php`

     ```bash
     ...
     'metadata.sources' => array(
        array('type' => 'flatfile'),
        array(
           'type' => 'flatfile', 
           'directory' => 'metadata/idem-federation'
        ),
     ),
     ```

   * Remove/Rename all PHP files under:
   
     `cd /opt/simplesamlphp/metadata ; rm *.php`

     ```
     adfs-idp-hosted.php
     adfs-sp-remote.php
     saml20-idp-hosted.php
     saml20-idp-remote.php
     saml20-sp-remote.php
     shib13-idp-hosted.php
     shib13-idp-remote.php
     shib13-sp-hosted.php
     shib13-sp-remote.php
     wsfed-idp-remote.php
     wsfed-sp-hosted.php
     ```

   * Download the Federation signing certificate:

     `wget https://md.idem.garr.it/certs/idem-signer-20241118.pem -O /opt/simplesamlphp/cert/federation-cert.pem`

   * Check the validity:
     * `cd /opt/simplesamlphp/cert/`
     * `openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout`
       
       (sha1: D1:68:6C:32:A4:E3:D4:FE:47:17:58:E7:15:FC:77:A8:44:D8:40:4D)
     * `openssl x509 -in federation-cert.pem -fingerprint -md5 -noout`

       (md5: 48:3B:EE:27:0C:88:5D:A3:E7:0B:7C:74:9D:24:24:E0)

   * Go to 'https://sp.example.org/simplesaml/module.php/core/frontpage_federation.php' and forcing download of the Federation metadata by pressing on `Metarefresh: fetch metadata` or wait 1 day

8. Set PHP 'memory_limit' to '1024M' or more to allow the download of huge metadata files (like eduGAIN):

   * `vim /etc/php/7.0/apache2/php.ini`

     ```bash
     memory_limit = 1024M
     ```

9. Choose and modify your authsources:

   * `vim /opt/simplesamlphp/config/authsources.php`

     ```bash
     <?php

     $config = array(

         // This is a authentication source which handles admin authentication.
         'admin' => array(
             // The default is to use core:AdminPassword, but it can be replaced with
             // any authentication source.

             'core:AdminPassword',
         ),


         // An authentication source which can authenticate against both SAML 2.0
         // and Shibboleth 1.3 IdPs.
         'default-sp' => array(
             'saml:SP',
	     
	     'privatekey' => 'ssp-sp.key',
	     'certificate' => 'ssp-sp.crt',

             // The entity ID of this SP.
             // Can be NULL/unset, in which case an entity ID is generated based on the metadata URL.
             'entityID' => null,

             // The entity ID of the IdP this should SP should contact.
             // Can be NULL/unset, in which case the user will be shown a list of available IdPs.
             'idp' => null,

             // The URL to the discovery service.
             // Can be NULL/unset, in which case a builtin discovery service will be used.
             'discoURL' => null,

             /*
              * The attributes parameter must contain an array of desired attributes by the SP.
              * The attributes can be expressed as an array of names or as an associative array
              * in the form of 'friendlyName' => 'name'. This feature requires 'name' to be set.
              * The metadata will then be created as follows:
              * <md:RequestedAttribute FriendlyName="friendlyName" Name="name" />
              */
             'name' => array(
                'en' => 'IDEM Test SP ENG',
                'it' => 'IDEM Test SP ITA',
             ),

             'attributes' => array(
                'eduPersonPrincipalName' => 'urn:oid:1.3.6.1.4.1.5923.1.1.1.6',
                'mail' => 'urn:oid:0.9.2342.19200300.100.1.3',
                'cn' => 'urn:oid:2.5.4.3',
             ),

             'attributes.required' => array (
                'urn:oid:0.9.2342.19200300.100.1.3',
             ),
	     
             'attributes.NameFormat' => 'urn:oasis:names:tc:SAML:2.0:attrname-format:uri',

             'description' => array(
                'en' => 'Service Description',
                'it' => 'Descrizione del Servizio offerto',
             ),

             'OrganizationName' => array(
               'en' => 'Your Organization Name',
               'it' => 'Il nome della tua organizzazione',
             ),

             'OrganizationDisplayName' => array(
               'en' => 'Your Organization Display Name',
               'it' => 'Il Display Name della tua Organizzazione',
             ),

             'OrganizationURL' => array(
               'en' => 'https://www.your.organization.it/en',
               'it' => 'https://www.your.organization.it/it',
             ),

             'UIInfo' => array(
                'DisplayName' => array(
                   'en' => 'English SP Display Name',
                   'it' => 'SP Display Name in Italiano',
                ),
                'Description' => array(
                   'en' => 'Service Description',
                   'it' => 'Descrizione del Servizio offerto',
                ),
                'PrivacyStatementURL' => array(
                   'en' => 'https://www.your.organization.it/en/privacy',
                   'it' => 'https://www.your.organization.it/it/privacy',
                ),
                'Logo' => array(
                   array(
                     'url'    => 'https://www.your.organization.it/en/logo80x60.png',
                     'height' => 60,
                     'width'  => 80,
                   ),
                   array(
                     'url'    => 'https://www.your.organization.it/logo16x16.png',
                     'height' => 16,
                     'width'  => 16,
                   ),
                ),
             ),
         ),
     );

     ```

10. OPTIONAL: Enable UTF-8 for SP metadata:

   * `vim /opt/simplesamlphp/vendor/simplesamlphp/saml2/src/SAML2/DOMDocumentFactory.php`

     ```bash
     ...
        public static function create()
        {
          return new \DOMDocument('1.0','utf-8');
        }
     }
     ```

11. Now you are able to reach your Shibboleth SP Metadata on:

   * `https://sp.example.org/simplesaml/module.php/saml/sp/metadata.php/default-sp`

   (change ```sp.example.org``` to you SP full qualified domain name)

12. Register you SP on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
   * Go to `https://registry.idem.garr.it/` and follow "**Insert a New Service Provider into the IDEM Test Federation**"


### Configure an example federated resouce "secure"

1. Create the "`secure`" application into the DocumentRoot:
   * `mkdir /var/www/html/secure`

   * `vim /var/www/html/secure/index.php`

     ```html
     <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
     <html>
        <head>
           <title>SSP-SP Example Page</title>
        </head>

        <body>
          <p>This is an Example Page that show the behaviour of a SimpleSAMLphp Service Provider</p>
          <p>These are attributes released from the IdP to this <strong>secure</strong> application:</p>
     <?php
        require_once('/opt/simplesamlphp/lib/_autoload.php');

        $as = new \SimpleSAML\Auth\Simple('default-sp');
        $as->requireAuth();
        $attributes = $as->getAttributes();
 
        echo "<ul>";
        foreach ($attributes as $name => $values) {
           echo "<li><strong>$name:</strong>\n";
           foreach ($values as $value) {
              echo "\t$value\n";
           }
           echo "</li>";
           echo "<br\>";
        }
     ?>
        </body>
     </html>
     ```

### Utility

* [The Mozilla Observatory](https://observatory.mozilla.org/):
  The Mozilla Observatory has helped over 240,000 websites by teaching developers, system administrators, and security professionals how to configure their sites safely and securely.

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
