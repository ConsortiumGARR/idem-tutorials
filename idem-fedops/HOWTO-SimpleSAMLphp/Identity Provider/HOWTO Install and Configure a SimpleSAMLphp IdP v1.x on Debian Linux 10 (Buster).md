# HOWTO Install and Configure a SimpleSAMLphp IdP v1.x on Debian Linux 10 (Buster) 

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

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
      1. [Configure Metadata](#configure-metadata)
      2. [Configure SAML Metadata Credentials](#configure-saml-metadata-credentials)
      3. [Configure the authentication source](#configure-the-authentication-source)
      4. [Configure automatic download of Federation Metadata](#configure-automatic-download-of-federation-metadata)
      5. [Add translations of the new 'schacHomeOrganizationType' attribute](#add-translations-of-the-new-schachomeorganizationtype-attribute)
      6. [Enable UTF-8 on IdP metadata (to avoid encoding problems with accents)](#enable-utf-8-on-idp-metadata-to-avoid-encoding-problems-with-accents)
      7. [Download IdP Metadata](#download-idp-metadata)
      8. [Register IdP on IDEM Entity Registry](#register-idp-on-idem-entity-registry)
5. [Appendix A - How to release attributes to specific SP only](#appendix-a---how-to-release-attributes-to-specific-sp-only)
6. [Appendix B - How to manage sessions with Memcache](#appendix-b---how-to-manage-sessions-with-memcached)
7. [Appendix C - How to collect useful-statistics](#appendix-c---how-to-collect-useful-statistics)
5. [Authors](#authors)


## Requirements Hardware

 * CPU: 2 Core
 * RAM: 4 GB
 * HDD: 20 GB

## Software that will be installed

 * ca-certificates
 * ntp
 * vim
 * apache2 (>= 2.4)
 * php php-curl php-dom php-mbstring php-dev libmcrypt-dev php-pear build-essential
 * memcached php-memcached
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

1. Become ROOT:
   * `sudo su`

1. Prepare the environment:
   * ```bash
     apt install apache2 ntp php php-curl php-dom php-mbstring php-dev libmcrypt-dev php-pear curl cron build-essential --no-install-recommends --no-install-recommends
     ```
   * `pecl channel-update pecl.php.net`
     
   * `pecl install channel://pecl.php.net/mcrypt-1.0.2`

   * `php -m | grep mcrypt` (must return "`mcrypt`")


2. Install SimpleSAMLphp:
   * `cd /var/`
   * ```bash
     wget https://github.com/simplesamlphp/simplesamlphp/releases/download/v1.19.3/simplesamlphp-1.19.3.tar.gz
     ```
   * `tar xzf simplesamlphp-1.19.3.tar.gz`
   * `mv simplesamlphp-1.19.3 simplesamlphp`

## Configuration

### Configure SSL on Apache2

1. Create a new directory for IdP:
   * `mkdir /var/www/html/ssp-idp.example.org`
   * `sudo chown -R www-data: /var/www/html/ssp-idp.example.org`

2. Create a new Virtualhost file as follows:
   * `vim /etc/apache2/sites-available/ssp-idp.example.org-ssl.conf`

   ```apache
   # Configure Apache2 to redirect all HTTP traffic to HTTPS
   <VirtualHost *:80>
        ServerName "ssp-idp.example.org"
        Redirect permanent "/" "https://ssp-idp.example.org/"
   </VirtualHost>
   
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

4. Enable the following Apache2 modules:
   * `a2enmod ssl` - To support SSL protocol
   * `a2enmod headers` - To control of HTTP request and response headers.
   * `a2enmod alias` - To manipulation and control of URLs as requests arrive at the server.
   * `a2enmod include` - To process files before they are sent to the client.
   * `a2enmod negotiation` - Essential Apache module
   * `a2ensite ssp-idp.example.org-ssl.conf`
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

      * `touch /var/www/html/ssp-idp.example.org/logo.png` (80x60 px or bigger with the same aspect-ratio)

      * `touch /var/www/html/ssp-idp.example.org/favicon.png` (16x16 px or bigger with the same aspect-ratio)

   2. Replace them with the correct content.

### Configure SimpleSAMLphp

1. Assign the ownership of the SimpleSAMLphp logs to Apache user:
   * `chown www-data /var/simplesamlphp/log`

2. Generate some useful opaque strings:
   * User Admin Password (```auth.adminpassword```):
     * `php /var/simplesamlphp/bin/pwgen.php`
        
   * Secret Salt (```secretsalt```):
     * `tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo`

3. Change SimpleSAMLphp configuration:
   * `vim /var/simplesamlphp/config/config.php`
   
      ```php
      'baseurlpath' => 'simplesaml/',
      /* ...other things... */
      'technicalcontact_name' => 'Technical Contact',
      'technicalcontact_email' => 'service.support@example.com',
      /* ...other things... */
      'secretsalt' => '#_YOUR_SECRET_SALT_HERE_#',
      /* ...other things... */
      'auth.adminpassword' => '#_YOUR_USER_ADMIN_PASSWORD_#',
      /* ...other things... */
      'admin.protectindexpage' => true,
      /* ...other things... */
      'logging.level' => 'SimpleSAML\Logger::NOTICE',
      'logging.handler' => 'syslog',
      /* ...other things... */
      'enable.saml20-idp' => true,
      /* ...other things... */
      'store.type' => 'phpsession',
      ```
      
   * `vim /etc/rsyslog.d/22-ssp-log.conf`
   
     ```bash
     # SimpleSAMLphp logging
     local5.*                        /var/log/simplesamlphp.log
     # Notice level is reserved for statistics only...
     local5.=notice                  /var/log/simplesamlphp.stat
     ```
     
   * `sydo systemctl restart rsyslog.service`

4. Check Login on the SSP appliance and retrieve the IdP "Entity ID" from "Fedearation" tab:
   * `https://ssp-idp.example.org/`

5. Configure a SMTP server to send mail only (Example):
   * `apt install mailutils postfix --no-install-recommends` (Internet Site => Insert your IdP FQDN)
   
   * `vim /etc/postfix/main.cf`

     ```bash
     /* ...other things... */
     inet_interfaces = localhost
     /* ...other things... */
     ```
     
   * `systemctl restart postfix.service`

6. Enable `mcrypt` module and set PHP `memory_limit` to '1024M' or more to allow the download of huge metadata files (like eduGAIN):

   * `vim /etc/php/7.3/mods-available/ssp.ini`

     ```bash
     ; configuration for SSP
     ; priority=20
     extension=mcrypt.so
     memory_limit = 1024M
     ```

   * `sudo phpenmod ssp`
   * `systemctl restart apache2.service`

### Configure the Identity Provider

#### Configure Metadata

   * `vim /var/simplesamlphp/metadata/saml20-idp-hosted.php`

     ```php
     $metadata['__DYNAMIC:1__'] = [
        'host' => '__DEFAULT__',
        'privatekey' => 'ssp-idp.key',
        'certificate' => 'ssp-idp.crt',
        
        'scope' => ['<INSERT-HERE-IDP-SCOPE>'],   // Usually the scope is the domain name

        'UIInfo' => [
           'DisplayName' => [
              'en' => '<INSERT-HERE-THE-ENGLISH-IDP-DISPLAY-NAME>',
              'it' => '<INSERT-HERE-THE-ITALIAN-IDP-DISPLAY-NAME>',
           ],
           'Description' => [
              'en' => '<INSERT-HERE-THE-ENGLISH-IDP-DESCRIPTION>',
              'it' => '<INSERT-HERE-THE-ITALIAN-IDP-DESCRIPTION>',
           ],
           'InformationURL' => [
              'en' => '<INSERT-HERE-THE-ENGLISH-INFORMATION-PAGE-URL>',
              'it' => '<INSERT-HERE-THE-ITALIAN-INFORMATION-PAGE-URL>',
           ],
           'PrivacyStatementURL' => [
              'en' => '<INSERT-HERE-THE-ENGLISH-PRIVACY-POLICY-PAGE-URL>',
              'it' => '<INSERT-HERE-THE-ITALIAN-PRIVACY-POLICY-PAGE-URL>',
           ],
           'Logo' => [
              [
               'url' => '<INSERT-HERE-THE-80X60-LOGO-URL>',
               'height' => 60,
               'width' => 80,
              ],
              [
               'url' => '<INSERT-HERE-THE-16X16-LOGO-URL>',
               'height' => 16,
               'width' => 16,
              ],
           ],
        ],

        'OrganizationName' => [
           'en' => '<INSERT-HERE-THE-ENGLISH-ORGANIZATION-NAME>',
           'it' => '<INSERT-HERE-THE-ITALIAN-ORGANIZATION-NAME>',
        ],
        'OrganizationDisplayName' => [
           'en' => '<INSERT-HERE-THE-ENGLISH-ORGANIZATION-DISPLAY-NAME>',
           'it' => '<INSERT-HERE-THE-ITALIAN-ORGANIZATION-DISPLAY-NAME>',
        ],
        'OrganizationURL' => [
           'en' => '<INSERT-HERE-THE-ENGLISH-ORGANIZATION-PAGE-URL>',
           'it' => '<INSERT-HERE-THE-ENGLISH-ORGANIZATION-PAGE-URL>',
        ],

        /*Uncomment the following to use the uri NameFormat on attributes.*/
        'attributes.NameFormat' => 'urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
        
        /* eduPersonTargetedID with oid NameFormat is a raw XML value */
        'attributeencodings' => ['urn:oid:1.3.6.1.4.1.5923.1.1.1.10' => 'raw'],

        'NameIDFormat' => [
           'urn:oasis:names:tc:SAML:2.0:nameid-format:transient',
           'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent'
        ],

        'authproc' => [
           // Add schacHomeOrganization for domain of entity
           10 => [
                  'class' => 'core:AttributeAdd',
                  'schacHomeOrganization' => '<INSERT-HERE-YOUR-DOMAIN-NAME>',
                  'schacHomeOrganizationType' => 'urn:schac:homeOrganizationType:eu:higherEducationalInstitution',
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
           
           100 => ['class' => 'core:AttributeMap', 'name2oid'],
        ],
     ];
     ```

#### Configure SAML Metadata Credentials

   * `vim /var/simplesamlphp/cert/ssp-idp-credentials.cnf`:
   
     ```cnf
     [req]
     default_bits=4096
     default_md=sha256
     encrypt_key=no
     distinguished_name=dn
     # PrintableStrings only
     string_mask=MASK:0002
     prompt=no
     x509_extensions=ext

     # customize the "default_keyfile,", "CN" and "subjectAltName" lines below
     default_keyfile=ssp-idp.key

     [dn]
     CN=ssp-idp.example.org

     [ext]
     subjectAltName = DNS:ssp-idp.example.org, \
                      URI:https://ssp-idp.example.org/idp/simplesaml
     subjectKeyIdentifier=hash
     ```

   * `cd /var/simplesamlphp/cert`
   * `openssl req -new -x509 -config ssp-idp-credentials.cnf -text -out ssp-idp.crt -days 3650`
   * `chown -R www-data: /var/simplesamlphp/cert`
   * `chmod 400 /var/simplesamlphp/cert/ssp-idp.key`

#### Configure the authentication source

   1. Enable LDAP PHP module:
      * `apt install php-ldap`
      * `systemctl restart apache2.service`

   2. Enable ldap:LDAP Authentication Source:
      * `vim /var/simplesamlphp/config/authsources.php`
      
        ```php
        <?php

        $config = [

             // This is a authentication source which handles admin authentication.
             'admin' => [
                 'core:AdminPassword',
             ],

             // LDAP authentication source.
             'ldap' => [
                 'ldap:LDAP',
                 'hostname' => 'ldap.example.org',
                 'enable_tls' => true,
                 'debug' => false,
                 'timeout' => 0,
                 'port' => 389,
                 'referrals' => true,
                 'attributes' => null,
                 'dnpattern' => 'uid=%username%,ou=people,dc=example,dc=org',
                 'search.base' => 'ou=people,dc=example,dc=org',
                 'search.attributes' => ['uid'],
                 'search.username' => '<LDAP_USER_DN_USED_FOR_QUERIES>',
                 'search.password' => '<LDAP_USER_PASSWORD>',
             ],
        ];
        ```

   3. Connect LDAP to the IdP:
      * `vim /var/simplesamlphp/metadata/saml20-idp-hosted.php`

        ```php
           /* ...other things before end of file...*/
           'auth' => 'ldap',
        ];
        ```

   4. Try the LDAP Authentication Source on: https://<IDP-FQDN>/simplesaml/module.php/core/authenticate.php

#### Configure automatic download of Federation Metadata

   1. Load CRON module:
      * `cd /var/simplesamlphp`
      * `cp modules/cron/config-templates/module_cron.php config/`

   2. Load METAREFRESH module:
      * `cd /var/simplesamlphp`
      * `cp modules/metarefresh/config-templates/config-metarefresh.php config/`

   3. Enable CRON & METAREFRESH modules:
      * `vim /var/simplesamlphp/config/config.php`

        ```php
        /* ...other things... */
        'module.enable' => [
           'cron' => true,
           'metarefresh' => true,
           'consent' => true,
        ],
        /* ...other things... */
        ```

   4. Test it:
      * `cd /var/simplesamlphp/modules/metarefresh/bin`
      * `./metarefresh.php -s http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml > metarefresh-test.txt`

   5. Generate the CRON `<SECRET>`:
      * `tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo`

   6. Change the CRON configuration file:
      * `vim /var/simplesamlphp/config/module_cron.php`

        ```php
        <?php
        /*
         * Configuration for the Cron module.
         */

        $config = [
           'key' => '<SECRET>',
           'allowed_tags' => ['hourly'],
           'debug_message' => TRUE,
           'sendemail' => TRUE,
        ];
        ?>
        ```

   7. Insert the following Cron job to the crontab file (`crontab -e`):
   
      ```bash
      # Run cron: [hourly]
      01 * * * *  root  curl --silent "https://idp.example.org/simplesaml/module.php/cron/cron.php?key=<SECRET>&tag=hourly" > /dev/null 2>&1
      ```

   8. Configure METAREFRESH:
      * `vim /var/simplesamlphp/config/config-metarefresh.php`

        ```php
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
                                   '/var/simplesamlphp/cert/federation-cert.pem',
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
                 'expireAfter' => 864000, // Maximum 10 days cache time (3600*24*10)
                 'outputDir'   => 'metadata/',

                 /*
                  * Which output format the metadata should be saved as.
                  * Can be 'flatfile' or 'serialize'. 'flatfile' is the default.
                 */
                 'outputFormat' => 'flatfile',
              ],
           ],
        ];
        ```

   9. Change SimpleSAMLphp configuration to load the new metadata provider:
      * `vim /var/simplesamlphp/config/config.php`

        ```php
        'metadata.sources' => [
            ['type' => 'flatfile'],
         ],
         ```

   10. Remove not needed files from:
       * `cd /var/simplesamlphp/metadata ; rm !(saml20-idp-hosted.php)`

   11. Download the Federation signing certificate: 
       * ```bash
         wget https://md.idem.garr.it/certs/idem-signer-20241118.pem -O /var/simplesamlphp/cert/federation-cert.pem
         ```

   12. Check the validity of the signing certificate:
       * `cd /var/simplesamlphp/cert`
       * `openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout`
       
         (sha1: D1:68:6C:32:A4:E3:D4:FE:47:17:58:E7:15:FC:77:A8:44:D8:40:4D)
       * `openssl x509 -in federation-cert.pem -fingerprint -md5 -noout`

         (md5: 48:3B:EE:27:0C:88:5D:A3:E7:0B:7C:74:9D:24:24:E0)

   13. Go to 'https://ssp-idp.example.org/simplesaml/module.php/core/frontpage_federation.php' and forcing download of the Federation metadata by pressing on `Metarefresh: fetch metadata` or wait 1 day

#### Add translations of the new `schacHomeOrganizationType` attribute

   * `vim /var/simplesamlphp/dictionaries/attributes.definition.json`

     ```json
     /* ...other things... */
     "attribute_schachomeorganization":{
        "en": "Home organization domain name"
     },
     "attribute_schachomeorganizationtype":{
        "en": "Home organization type"
     },
     /* ...other things... */
     ```

     (Pay attention also to "commas"!)

   * `vim /var/simplesamlphp/dictionaries/attributes.translation.json`

     ```json
        /* ...other things before the end of file... */
        "attribute_schachomeorganizationtype":{
           "it": "Tipo di Organizzazione"
        }
     }
     ```

     (Pay attention also to "commas"!)

#### Enable UTF-8 on IdP metadata (to avoid encoding problems with accents)

   * `vim /var/simplesamlphp/vendor/simplesamlphp/saml2/src/SAML2/DOMDocumentFactory.php`

     ```bash
     /* ...other things... */
        public static function create()
        {
          return new \DOMDocument('1.0','utf-8');
        }
     }
     ```

#### Download IdP Metadata

   * `https://ssp-idp.example.org/simplesaml/saml2/idp/metadata.php`

   (change ```ssp-idp.example.org``` to you IDP full qualified domain name)

#### Register IdP on IDEM Entity Registry

   * Go to `https://registry.idem.garr.it` and follow "**Insert a New Identity Provider into the IDEM Test Federation**" (your entity has to be approved by an IDEM Federation Operator before become part of IDEM Test Federation)

### Appendix A - How to release attributes to specific SP only

1. Download and extract `attributepolicy` module:
   * ```bash
     wget https://github.com/RikV/simplesaml-attributepolicy/archive/1.1.tar.gz -O /usr/local/src/ssp-attributepolicy.tar.gz
     ```
   * `cd /usr/local/src`
   * `tar xzf ssp-attributepolicy.tar.gz`
   * `rm -R ssp-attributepolicy.tar.gz`
   
2. Load module in SimpleSAMLphp:
   * `ln -s /usr/local/src/simplesaml-attributepolicy-1.1/attributepolicy/ /var/simplesamlphp/modules/`
   
3. Activate module:
   * `vim /var/simplesamlphp/config/config.php`

     ```php
     /* ...other things... */
     'module.enable' => [
        'cron' => true,
        'metarefresh' => true,
        'consent' => true,
        'attributepolicy' => true,
     ],
     /* ...other things... */
     ```

4. Create the Attribute Release Policy for IDEM Test Federation:
   * Copy the content of [module_attributepolicy_test.php](utils/module_attributepolicy_test.php) and paste it into `/var/simplesamlphp/config/module_attributepolicy.php`
   
   (the default template is into 
    ```bash 
    /var/simplesamlphp/modules/attributepolicy/config-templates/module_attributepolicy.php
    ```
    )

### Appendix B - How to manage sessions with Memcached

1. Install needed packages:
   * `sudo apt install memcached php-memcached`

2. Enable PHP memcached module:
   * `sudo phpenmod memcached`

3. Restart Apache:
   * `sudo systemctl restart apache2.service`

4. Enable memcache on simplesamlphp:
   * `vim /var/simplesamlphp/config/config.php`
   
     ```php
     /* ...other things... */
     'store.type' => 'memcache',
     /* ...other things... */
     ```
     
### Appendix C - How to collect useful statistics

Follow https://simplesamlphp.org/docs/stable/statistics:statistics

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
