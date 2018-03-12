# HOWTO Install and Configure a SimpleSAMLphp SP v1.x on Debian Linux 9 (Stretch) 

<img width="120px" src="https://wiki.idem.garrservices.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements Hardware](#requirements-hardware)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Other Requirements](#other-requirements)
4. [Installation Instructions](#installation-instructions)
   1. [Install software requirements](#install-software-requirements)
   2. [Configure the environment](#configure-the-environment)
   3. [Install SimpleSAMLphp Service Provider](##install-simplesamlphp-service-provider)
5. [Configuration Instructions](#configuration-instructions)
   1. [Configure SSL on Apache2](#configure-ssl-on-apache2)
   2. [Configure SimpleSAMLphp (with IDEM WAYF)](#configure-shibboleth-sp-with-idem-wayf)
   3. [Configure an example federated resouce "secure"](#configure-an-example-federated-resouce-secure)
6. [Authors](#authors)


## Requirements Hardware

 * CPU: 2 Core
 * RAM: 4 GB
 * HDD: 20 GB

## Software that will be installed

 * ca-certificates
 * ntp
 * vim
 * libapache2-mod-php, php, php7.0-mcrypt, apache2 (>= 2.4)
 * openssl
 * cron
 * curl

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
   * ```apt install ca-certificates vim openssl```

### Configure the environment

1. Modify your ```/etc/hosts```:
   * ```vim /etc/hosts```
  
     ```bash
     127.0.1.1 sp.example.org sp
     ```
   (*Replace ```sp.example.org``` with your SP Full Qualified Domain Name*)

2. Be sure that your firewall **doesn't block** the traffic on port **443** (or you can't access to your SP)

### Install SimpleSAMLphp Service Provider

1. Become ROOT: 
   * ```sudo su -```

2. Install required packages SP:
   * ```bash
     apt install apache2 openssl ntp vim php php-curl php-dom php7.0-mcrypt curl cron
     ```

3. Install the SimpleSAMLphp SP:
   * ```cd /opt/```
   * ```wget https://github.com/simplesamlphp/simplesamlphp/releases/download/v1.15.4/simplesamlphp-1.15.4.tar.gz```
   * ```tar xzf simplesamlphp-1.15.4.tar.gz```
   * ```mv simplesamlphp-1.15.4 simplesamlphp

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
   * ```a2enmod ssl headers alias include negotiation```
   * ```a2ensite default-ssl.conf```
   * ```systemctl restart apache2```

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

### Configure SimpleSAMLphp SP (with IDEM WAYF)

1. Become ROOT: 
   * ```sudo su -```

2. Create the Apache2 configuration for the application: 

   * ```vim /etc/apache2/site-available/simplesaml.conf```
  
     ```bash
     Alias /simplesaml /opt/simplesamlphp/www

     RedirectMatch    ^/$  /simplesaml

     <Location /simplesaml>
       Require all granted
     </Location>
     ```
3. Enable the simplsaml Apache2 configuration:

   * ```a2ensite simplesaml.conf```

   * ```systemctl reload apache2.service```

4. Change the permission for SimpleSAMLphp logs:

   * ```chown www-data /opt/simplesamlphp/log```

5. Configure the SimpleSAMLphp SP:

   * Generate some useful opaque strings:
      * User Admin Password (```auth.adminpassword```)`: ```php /opt/simplesamlphp/bin/pwgen.php```
      * Secret Salt (```secretsalt```): ```tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo```
      * Cron Key (```key```): ```tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo```

   * ```vim /opt/simplesamlphp/config/config.php```
   
      ```bash
      ...
      'technicalcontact_name' => 'Technical Contact',
      'technicalcontact_email' => 'service.support@example.com',
      ...
      'secretsalt' => '#_YOUR_SECRET_SALT_HERE_#',
      ...
      'auth.adminpassword' => '#_YOUR_USER_ADMIN_PASSWORD_#',
      ...
      'admin.protectindexpage' => 'true',
      ...
      'logging.handler' => 'file',
      ```

6. Generate SAML Credentials:

   * ```mkdir /opt/simplesamlphp/saml-credentials```

   * ```Follow [Appendix A: Sample SAML2 Metadata embedded certificate](https://www.switch.ch/aai/support/certificates/embeddedcerts-requirements-appendix-a/)```

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

     ./metarefresh.php -s http://www.garr.it/idem-metadata/idem-test-metadata-sha256.xml > metarefresh-test.txt
     ```

   * Change the CRON configuration file:

     ```vim /opt/simplesamlphp/config/module_cron.php```

     ```bash
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
     ```

   * Go to ```https://sp.example.org/simplesaml/module.php/cron/croninfo.php ``` and copy the content of the crontab file

   * Paste the content copied to your ```crontab -e``` and change the value "```XXXXXXXXXX```" with "```*/30 * * * *```" under "```[frequent]```" cron.

   * Configure METAREFRESH:

     ```vim /opt/simplesamlphp/config/config-metarefresh.php```

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
              'cron'          => array('hourly'),
              'sources'       => array(
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
                                       'src' => 'http://www.garr.it/idem-metadata/idem-test-metadata-sha256.xml',
                                       'certificates' => array(
                                          '/opt/simpleasamlphp/cert/idem_signer.crt',
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
              'expireAfter'           => 60*60*24*5, // Maximum 5 days cache time
              'outputDir'     => 'metadata/idem-test-federation/',

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

   * ```mkdir /opt/simplesamlphp/metadata/idem-test-federation ; chown www-data /opt/simplesamlphp/metadata/idem-test-federation```

   * Change the SimpleSAMLphp configuration file:

     ```vim /opt/simplesamlphp/config/config.php```

     ```bash
     ...
     'metadata.sources' => array(
        array('type' => 'flatfile'),
        array(
           'type' => 'flatfile', 
           'directory' => 'metadata/idem-test-federation'
        ),
     ),
     ```

   * ```Remove/Rename the following files: ```

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
   
     ```wget https://www.idem.garr.it/documenti/doc_download/321-idem-metadata-signer-2019 -O /opt/simplesamlphp/cert/idem_signer.pem  ```

   * Force download of Federation metadata by pressing on ```Metarefresh: fetch metadata``` or wait 1 day

8. Set PHP 'memory_limit' to '256M' or more to allow the download of huge metadata files (like eduGAIN):

   * ```vim /etc/php/7.0/apache2/php.ini```

     ```bash
     memory_limit = 256M
     ```

9. Choose and modify your authsources:

   * ```vim ```

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
              * WARNING: SHA-1 is disallowed starting January the 1st, 2014.
              *
              * Uncomment the following option to start using SHA-256 for your signatures.
              * Currently, SimpleSAMLphp defaults to SHA-1, which has been deprecated since
              * 2011, and will be disallowed by NIST as of 2014. Please refer to the following
              * document for more information:
              *
              * http://csrc.nist.gov/publications/nistpubs/800-131A/sp800-131A.pdf
              *
              * If you are uncertain about identity providers supporting SHA-256 or other
              * algorithms of the SHA-2 family, you can configure it individually in the
              * IdP-remote metadata set for those that support it. Once you are certain that
              * all your configured IdPs support SHA-2, you can safely remove the configuration
              * options in the IdP-remote metadata set and uncomment the following option.
              *
              * Please refer to the hosted SP configuration reference for more information.
              */
             'signature.algorithm' => 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256',

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
     ...

     ```

10. OPTIONAL: Enable UTF-8 for SP metadata:

   * ```vim ./vendor/simplesamlphp/saml2/src/SAML2/DOMDocumentFactory.php```

     ```bash
     ...
          return new \DOMDocument('1.0','utf-8');
        }
     }
     ```

11. Now you are able to reach your Shibboleth SP Metadata on:

   * ```https://sp.example.org/simplesaml/module.php/saml/sp/metadata.php/default-sp```

   (change ```sp.example.org``` to you SP full qualified domain name)

12. Register you SP on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
   * Go to ```https://registry.idem.garr.it/``` and follow "Insert a New Service Provider into the IDEM Test Federation"


### Configure an example federated resouce "secure"

1. Create the "```secure```" application into the DocumentRoot:
   * ```mkdir /var/www/html/secure```

   * ```vim /var/www/html/secure/index.php```

     ```html
     <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
     <html>
        <head>
           <title>SSP-SP Example Page</title>
        </head>

        <body>
          <p>This is an Example Page
              that show the behaviour of a SimpleSAMLphp Service Provider</p>
     <?php
        require_once('/opt/simplesamlphp/lib/_autoload.php');

        $as = new SimpleSAML_Auth_Simple('default-sp');
        $as->requireAuth();
        $attributes = $as->getAttributes();

        header('Content-Type: text/plain; charset=utf-8');

        foreach ($attributes as $name => $values) {
           echo("$name:\n");
           foreach ($values as $value) {
              echo("\t$value\n");
           }
           echo("\n");
        }
     ?>
        </body>
     </html>
     ```

2. Install needed packages:
   * ```apt istall libapache2-mod-php```

   * ```systemctl restart apache2.service```

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
