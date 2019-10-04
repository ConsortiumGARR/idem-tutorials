# HOWTO Install and Configure a SimpleSAMLphp IdP v1.x on Debian Linux 9 (Stretch) 

[comment]: # (<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />)

## Table of Contents

1. [Requirements Hardware](#requirements-hardware)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Installation](#installation)
   1. [Prepare the environment](#prepare-the-environment)
   2. [Install SimpleSAMLphp](#install-simplesamlphp)
4. [Configuration](#configuration)
   1. [Configure SSL on Apache2](#configure-ssl-on-apache2)
   2. [Configure SimpleSAMLphp](#configure-simplesamlphp)
   3. [Configure the Identity Provider](#configure-the-identity-provider)
6. [Appendix A - How to release attributes to specific SP only](#appendix-a---how-to-release-attributes-to-specific-sp-only)
5. [Authors](#authors)


## Requirements Hardware

 * CPU: 2 Core
 * RAM: 4 GB
 * HDD: 20 GB

## Software that will be installed

 * ca-certificates
 * ntp
 * vim
 * libapache2-mod-php, php, php-mcrypt, php-dom, php-curl, php-mbstring, php-ldap apache2 (>= 2.4)
 * openssl
 * cron
 * curl

## Installation

The software installation provided by this guide is intended to run by ROOT user so...
   * `sudo su -`

### Prepare the environment

1. Change the default mirror with the GARR ones:
   * `sed -i 's/deb.debian.org/debian.mirror.garr.it/g' /etc/apt/sources.list`
   * `apt update && apt upgrade`
  
2. Install the required packages: 
   * `apt install ca-certificates vim openssl`

3. Modify your `/etc/hosts`:
   * `vim /etc/hosts`
  
     ```bash
     127.0.1.1 ssp-idp.example.org ssp-idp
     ```
   (*Replace `ssp-idp.example.org` with your SP Full Qualified Domain Name*)

4. Be sure that your firewall **doesn't block** traffic on port **443** (or you can't access to your IdP)

5. Import SSL credentials:
   * Import SSL Certificate into: "```/etc/ssl/certs/ssp-idp.example.org.crt```"
   * Import SSL Key into: "```/etc/ssl/private/ssp-idp.example.org.key```"
   * Import SSL CA: "```/usr/local/share/ca-certificates/ssl-ca.crt```"
   * Run the command: "```update-ca-certificates```"
   
### Install SimpleSAMLphp

1. Prepare the environment:
   * ```bash
     apt install apache2 ntp php php-curl php-dom php-mcrypt php-mbstring curl cron --no-install-recommends
     ```

2. Install:
   * `cd /var/`
   * `wget https://github.com/simplesamlphp/simplesamlphp/releases/download/v1.17.2/simplesamlphp-1.17.2.tar.gz`
   * `tar xzf simplesamlphp-1.17.2.tar.gz`
   * `mv simplesamlphp-1.17.2 simplesamlphp`

## Configuration

### Configure SSL on Apache2

1. Create a new directory for IdP:
   * `mkdir /var/www/html/ssp-idp.example.org`
   * `sudo chown -R www-data: /var/www/html/ssp-idp.example.org`

2. Create a new Virtualhost file as follows:
   * `vim /etc/apache2/sites-available/ssp-idp.example.org-ssl.conf`

   ```apache
   <IfModule mod_ssl.c>
      SSLStaplingCache shmcb:/var/run/ocsp(128000)
      <VirtualHost _default_:443>
        ServerName ssp-idp.example.org
        ServerAdmin admin@example.org
        DocumentRoot /var/www/html/ssp-idp.example.org

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
        
        SSLCertificateFile /etc/ssl/certs/ssp-idp.example.org.crt
        SSLCertificateKeyFile /etc/ssl/private/ssp-idp.example.org.key
        SSLCACertificateFile /etc/ssl/certs/ca-certificates.crt

        # Enable and Redirect to SimpleSamlPhp - Apache 2.4 configuration
        SetEnv SIMPLESAMLPHP_CONFIG_DIR /var/simplesamlphp/config

        Alias /simplesaml /var/simplesamlphp/www

        RedirectMatch    ^/$  /simplesaml

        <Directory /var/simplesamlphp/www>
           <IfModule mod_authz_core.c>
              Require all granted
           </IfModule>
        </Directory>

      </VirtualHost>
   </IfModule>
   ```

3. Configure Apache2 to redirect all HTTP traffic to HTTPS:
   * `vim /etc/apache2/sites-available/ssp-idp.example.org.conf`
   
   ```apache
   <VirtualHost *:80>
        ServerName "ssp-idp.example.org"
        Redirect permanent "/" "https://ssp-idp.example.org/"
   </VirtualHost>
   ```

4. Enable **proxy_http**, **SSL** and **headers** Apache2 modules:
   * `a2enmod proxy_http` - To redirect datas provided by Jetty to Apache through proxypass
   * `a2enmod ssl` - To support SSL protocol
   * `a2enmod headers` - To control of HTTP request and response headers.
   * `a2enmod alias` - To manipulation and control of URLs as requests arrive at the server.
   * `a2enmod include` - To process files before they are sent to the client.
   * `a2enmod negotiation` - Essential Apache module
   * `a2ensite ssp-idp.example.org-ssl.conf`
   * `a2ensite ssp-idp.example.org.conf`
   * `a2dissite 000-default.conf`
   * `systemctl restart apache2.service`

5. Verify the strength of your IdP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

6. **OPTIONAL STEPS**:
   If you want to host your IdP's Information/Privacy pages on the IdP itself, follow the next steps:
  
   1. Create all needed files with:
      * `vim /var/www/html/ssp-idp.example.org/info_page.html`

         ```bash
         <html>
            <head><title>Information Page</title></head>
            <body>
               <h1>Put here IdP Information page content</h1>
            </body>
         </html>
         ```

      * `vim /var/www/html/ssp-idp.example.org/privacy_page.html`

         ```bash
         <html>
            <head><title>Privacy Page</title></head>
            <body>
               <h1>Put here IdP Privacy page content</h1>
            </body>
         </html>
         ```

      * `touch /var/www/html/ssp-idp.example.org/logo80x60.png`

      * `touch /var/www/html/ssp-idp.example.org/favicon16x16.png`

   2. Replace them with the correct content.

### Configure SimpleSAMLphp

1. Assign the ownership of the SimpleSAMLphp logs to Apache user:
   * `chown www-data /var/simplesamlphp/log`

2. Generate some useful opaque strings:
   * User Admin Password (```auth.adminpassword```):
     `php /var/simplesamlphp/bin/pwgen.php`
        
   * Secret Salt (```secretsalt```):
     `tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo`
        
   * Cron Key (```key```):
     `tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo`

3. Change SimpleSAMLphp configuration:
   * `vim /var/simplesamlphp/config/config.php`
   
      ```bash
      'baseurlpath' => 'https://ssp-idp.example.org/simplesaml/',
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
      ...
      'enable.saml20-idp' => true,
      ...
      'store.type' => 'phpsession',
      ```

4. Check Login on the SSP appliance and retrieve the IdP "Entity ID" from "Fedearation" tab:
   * `https://ssp-idp.example.org/`

5. Configure a SMTP server to send mail only (Example):
   * `apt install mailutils postfix --no-install-recommends` (Internet Site => Insert your IdP FQDN)
   
   * `vim /etc/postfix/main.cf`

     ```bash
     ...
     inet_interfaces = localhost
     ...
     ```
     
   * `systemctl restart postfix.service`

6. Set PHP 'memory_limit' to '512M' or more to allow the download of huge metadata files (like eduGAIN):

   * `vim /etc/php/7.0/apache2/php.ini`

     ```bash
     memory_limit = 512M
     ```

   * `systemctl restart apache2.service`

### Configure the Identity Provider

1. Generate SAML Credentials, needed to sign/encrypt assertion between entities, by following [Appendix A: Sample SAML2 Metadata embedded certificate](https://www.switch.ch/aai/support/certificates/embeddedcerts-requirements-appendix-a/) with the IdP entityID found into:
   * `/var/simplesamlphp/cert/ssp-idp.crt`
   * `/var/simplesamlphp/cert/ssp-idp.key`

2. Load certificate and key for the IdP and assign the ownership to Apache user:
     * `vim /var/simplesamlphp/config/authsources.php`

       ```bash
       ...
       'privatekey' => '/var/simplesamlphp/cert/ssp-idp.key',
       'certificate' => '/var/simplesamlphp/cert/ssp-idp.crt',
       ...
       ```

     * `chown -R www-data: /var/simplesamlphp/cert`

3. Configure automatic download of Federation Metadata:

   * Load CRON module:

     ```bash
     cd /var/simplesamlphp/

     cp modules/cron/config-templates/module_cron.php config/
     ```

   * Load METAREFRESH module:
   
     ```bash
     cd /var/simplesamlphp/

     cp modules/metarefresh/config-templates/config-metarefresh.php config/
     ```

   * Enable CRON & METAREFRESH modules:
     * `vim /var/simplesamlphp/config/config.php`

       ```bash
       ...
       'module.enable' => [
          'cron' => true,
          'metarefresh' => true,
          'consent' => true,
       ],
       ...
       ```

   * Test it:
     * `cd /var/simplesamlphp/modules/metarefresh/bin`
     * `./metarefresh.php -s http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml > metarefresh-test.txt`

   * Change the CRON configuration file:

     `vim /var/simplesamlphp/config/module_cron.php`

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

   * Go to `https://ssp-idp.example.org/simplesaml/module.php/cron/croninfo.php` and copy the content of the crontab file:
   
     ```bash
     # Run cron: [daily]
     02 0 * * *  root  curl --silent "https://sp.example.org/simplesaml/module.php/cron/cron.php?key=<SECRET>&tag=daily" > /dev/null 2>&1

     # Run cron: [hourly]
     01 * * * *  root  curl --silent "https://sp.example.org/simplesaml/module.php/cron/cron.php?key=<SECRET>&tag=hourly" > /dev/null 2>&1

     # Run cron: [frequent]
     */30 * * * *  root  curl --silent "https://sp.example.org/simplesaml/module.php/cron/cron.php?key=<SECRET>&tag=frequent" > /dev/null 2>&1
     ```

   * Paste the copied content to your `crontab -e` and change the value "`XXXXXXXXXX`" with "`*/30 * * * *`" under "`[frequent]`" cron.

   * Configure METAREFRESH:
     * `vim /var/simplesamlphp/config/config-metarefresh.php`

       ```bash
       <?php

       $config = [

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

          'sets' => [
             'idem' => [
                'cron'    => ['hourly'],
                'sources' => [
                              [
                               'src' => 'http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml',
                               'certificates' => [
                                  '/var/simplesamlphp/cert/idem-cert.pem',
                               ],
                               'template' => [
                                  'tags'  => ['idem'],
                                  'authproc' => [
                                     51 => ['class' => 'core:AttributeMap', 'oid2name'],
                                  ],
                               ],

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
                                'types' => ['saml20-sp-remote'],   // Load only SAML v2.0 SP from metadata
                              ],
                             ],
                'expireAfter'=> 864000, // Maximum 10 days cache time (3600*24*10)
                'outputDir'     => 'metadata/idem/',

                /*
                 * Which output format the metadata should be saved as.
                 * Can be 'flatfile' or 'serialize'. 'flatfile' is the default.
                */
                'outputFormat' => 'flatfile',
             ],
          ],
       ];
       ```

   * Create metadata dir:
     * `mkdir /var/simplesamlphp/metadata/idem ; chown www-data /var/simplesamlphp/metadata/idem`

   * Change SimpleSAMLphp configuration to load the new metadata provider:

     ```vim /var/simplesamlphp/config/config.php```

     ```bash
     ...
     'metadata.sources' => [
        ['type' => 'flatfile'],
        [
           'type' => 'flatfile', 
           'directory' => 'metadata/idem'
        ],
     ),
     ```

   * Remove/Rename not needed files from:
   
     ```cd /var/simplesamlphp/metadata```

     ```
     rm adfs-idp-hosted.php adfs-sp-remote.php saml20-sp-remote.php shib13-idp-hosted.php shib13-idp-remote.php shib13-sp-hosted.php shib13-sp-remote.php wsfed-idp-remote.php wsfed-sp-hosted.php
     ```

   * Download the Federation signing certificate: 
   
     ```wget https://md.idem.garr.it/certs/idem-signer-20220121.pem -O /var/simplesamlphp/cert/idem-cert.pem```

   * Check the validity of the signing certificate:
     * ```cd /var/simplesamlphp/cert/```
     * ```openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout```
       
       (sha1: D1:68:6C:32:A4:E3:D4:FE:47:17:58:E7:15:FC:77:A8:44:D8:40:4D)
     * ```openssl x509 -in federation-cert.pem -fingerprint -md5 -noout```

       (md5: 48:3B:EE:27:0C:88:5D:A3:E7:0B:7C:74:9D:24:24:E0)

   * Go to 'https://ssp-idp.example.org/simplesaml/module.php/core/frontpage_federation.php' and forcing download of the Federation metadata by pressing on ```Metarefresh: fetch metadata``` or wait 1 day

4. Connect a directory service (openLDAP) to the IdP:
   1. Enable LDAP PHP module:
      * `apt install php-ldap`

      * `systemctl restart apache2.service`

   2. Enable LDAP Authentication Source:
      * `vim /var/simplesamlphp/config/authsources.php`
        * Enable "LDAP Authentication source" by removing comment for it
        * Rename "example-ldap" as you prefer
        * Configure LDAP connection by following comments

   3. Connect LDAP to the IdP:
      * `vim /var/simplesamlphp/metadata/saml20-idp-hosted.php`

        ```bash
        ...
        'auth' => 'example-ldap',
        ...
        ```

5. Configure IdP Authentication Process(authproc) and enrich IdP metadata:
   * `vim /var/simplesamlphp/metadata/saml20-idp-hosted.php`
   
     ```bash
     'auth' => 'example-ldap',
     'scope' => ['example.org'],

     'UIInfo' => [
        'DisplayName' => [
           'en' => 'English IDP Display Name',
           'it' => 'IDP Display Name in Italiano',
        ],
        'Description' => [
           'en' => 'Identity Provider for the users of University X',
           'it' => 'Identity Provider per gli utenti dell\' Università X',
        ],
        'InformationURL' => [
           'en' => 'https://www.your.organization.it/en/info',
           'it' => 'https://www.your.organization.it/it/info',
        ],
        'PrivacyStatementURL' => [
           'en' => 'https://www.your.organization.it/en/privacy',
           'it' => 'https://www.your.organization.it/it/privacy',
        ],
        'Logo' => [
           [
            'url' => 'https://www.your.organization.it/logo80x60.png',
            'height' => 60,
            'width' => 80,
           ],
           [
            'url' => 'https://www.your.organization.it/logo16x16.png',
            'height' => 16,
            'width' => 16,
           ],
        ],
     ],

     'OrganizationName' => [
        'en' => 'Your Organization Name',
        'it' => 'Il nome della tua organizzazione',
     ],
     'OrganizationDisplayName' => [
        'en' => 'Your Organization Display Name',
        'it' => 'Il Display Name della tua Organizzazione',
     ],
     'OrganizationURL' => [
        'en' => 'https://www.your.organization.it/en',
        'it' => 'https://www.your.organization.it/it',
     ],

     /*Uncomment the following to use the uri NameFormato on attributes.*/
     'attributes.NameFormat' => 'urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
     
     /* eduPersonTargetedID with oid NameFormat is a raw XML value */
     'attributeencodings' => ['urn:oid:1.3.6.1.4.1.5923.1.1.1.10' => 'raw'],

     'authproc' => [
        // Add schacHomeOrganization for domain of entity
        10 => [
               'class' => 'core:AttributeAdd',
               'schacHomeOrganization' => 'example.org',
               'schacHomeOrganizationType' => 'urn:schac:homeOrganizationType:int:university',
              ],

        // Add eduPersonPrincipalName
        11 => [
               'class' => 'core:ScopeAttribute',
               'scopeAttribute' => 'schacHomeOrganization',
               'sourceAttribute' => 'uid',
               'targetAttribute' => 'eduPersonPrincipalName',
              ],

        // Add eduPersonScopedAffiliation
        12 => [
               'class' => 'core:ScopeAttribute',
               'scopeAttribute' => 'eduPersonPrincipalName',
               'sourceAttribute' => 'eduPersonAffiliation',
               'targetAttribute' => 'eduPersonScopedAffiliation',
              ],

        // Adopts language from attribute to use in UI
        30 => 'core:LanguageAdaptor',

        // Consent module is enabled(with no permanent storage, using cookies)

        97 => [
               'class' => 'consent:Consent',
               'store' => 'consent:Cookie',
               'focus' => 'yes',
               'checked' => FALSE
              ],

        // Enable this authproc filter to automatically generated eduPersonTargetedID
        98 => [
               'class' => 'core:TargetedID',
               'attributename' => 'uid',
               'nameId' => TRUE,
              ],
 
        // If language is set in Consent module it will be added as an attribute
        99 => 'core:LanguageAdaptor',
     ],
     ...
     ```

6. Add the new `schacHomeOrganizationType` attribute to the SSP attribute map to be able to support it:
   * `vim /var/simplesamlphp/attributemap/name2oid.php`

     ```bash
     ...
     'schacHomeOrganizationType' => '1.3.6.1.4.1.25178.1.2.10',
     ...
     ```

     (Pay attention also to "commas"!)

7. Add translations of the new `schacHomeOrganizationType` attribute:
   * `vim /var/simplesamlphp/dictionaries/attributes.definition.json`

     ```bash
     ...
     "attribute_schachomeorganizationtype":{
        "en": "Home Organization Type"
     }
     ...
     ```

     (Pay attention also to "commas"!)

   * `vim /var/simplesamlphp/dictionaries/attributes.translation.json`

     ```bash
     ...
     "attribute_schachomeorganizationtype":{
        "it": "Tipo di Organizzazione"
     }
     ...
     ```

     (Pay attention also to "commas"!)


8. Enable UTF-8 on IdP metadata (to avoid encoding problems with accents):

   * `vim /var/simplesamlphp/vendor/simplesamlphp/saml2/src/SAML2/DOMDocumentFactory.php`

     ```bash
     ...
        public static function create()
        {
          return new \DOMDocument('1.0','utf-8');
        }
     }
     ```

6. Test your IDP with the LDAP Authentication Source enabled:
   
   * https://ssp-idp.example.org/simplesaml/module.php/core/authenticate.php

7. Now you are able to reach your Shibboleth SP Metadata on:

   * `https://ssp-idp.example.org/simplesaml/saml2/idp/metadata.php`

   (change ```ssp-idp.example.org``` to you SP full qualified domain name)

8. Register you IDP on IDEM Entity Registry (your entity has to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
   * Go to `https://registry.idem.garr.it/` and follow "**Insert a New Identity Provider into the IDEM Test Federation**"

### Appendix A - How to release attributes to specific SP only

1. Download and extract `attributepolicy` module:
   * `wget https://github.com/RikV/simplesaml-attributepolicy/archive/1.1.tar.gz -O /usr/local/src/ssp-attributepolicy.tar.gz`
   * `cd /usr/local/src`
   * `tar xzf ssp-attributepolicy.tar.gz`
   * `rm -R ssp-attributepolicy.tar.gz`
   
2. Load module in SimpleSAMLphp:
   * `ln -s /usr/local/src/simplesaml-attributepolicy-1.1/attributepolicy/ /var/simplesamlphp/modules/`
   
3. Activate module:
   * `vim /var/simplesamlphp/config/config.php`

     ```bash
     ...
     'module.enable' => [
        'cron' => true,
        'metarefresh' => true,
        'consent' => true,
        'attributepolicy' => true,
     ],
     ...
     ```

4. Create the Attribute Release Policy for IDEM Test Federation:
   * Copy the content of [module_attributepolicy_test.php](utils/module_attributepolicy_test.php) and paste it into `/var/simplesamlphp/config/module_attributepolicy.php`
   
   (the default template is into `/var/simplesamlphp/modules/attributepolicy/config-templates/module_attributepolicy.php`)

### Appendix B - How to manage sessions with Memcached

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
