# HOWTO Install and Configure a SimpleSAMLphp IdP v1.x on Debian Linux with Composer 

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements Hardware](#requirements-hardware)
2. [Requirements Software](#requirements-software)
3. [Software that will be installed](#software-that-will-be-installed)
4. [Installation](#installation)
   1. [Prepare the environment](#prepare-the-environment)
   2. [Install SimpleSAMLphp](#install-simplesamlphp)
5. [Configuration](#configuration)
   1. [Configure SSL on Apache2](#configure-ssl-on-apache2)
   2. [Configure SimpleSAMLphp](#configure-simplesamlphp)
   3. [Configure the Identity Provider](#configure-the-identity-provider)
      1. [Configure Metadata](#configure-metadata)
      2. [Configure Attribute Release Policies](#configure-attribute-release-policies)
      3. [Configure SAML Metadata Credentials](#configure-saml-metadata-credentials)
      4. [Configure the authentication source](#configure-the-authentication-source)
      5. [Configure automatic download of Federation Metadata](#configure-automatic-download-of-federation-metadata)
      6. [Add translations of the new 'schacHomeOrganizationType' attribute](#add-translations-of-the-new-schachomeorganizationtype-attribute)
      7. [Enable UTF-8 on IdP metadata (to avoid encoding problems with accents)](#enable-utf-8-on-idp-metadata-to-avoid-encoding-problems-with-accents)
      8. [Download IdP Metadata](#download-idp-metadata)
      9. [Register IdP on IDEM Entity Registry](#register-idp-on-idem-entity-registry)
6. [Appendix A - How to manage sessions with Memcache](#appendix-a---how-to-manage-sessions-with-memcached)
7. [Appendix B - How to collect useful statistics](#appendix-b---how-to-collect-useful-statistics)
8. [Utility](#utility)
9. [Authors](#authors)


## Requirements Hardware

* CPU: 2 Core
* RAM: 4 GB
* HDD: 20 GB

[[TOC]](#table-of-contents)

## Requirements Software

* PHP >= 7.2.5
* OS: Debian 11 (Buster)

[[TOC]](#table-of-contents)

## Software that will be installed

* ca-certificates
* ntp
* vim
* apache2 (>= 2.4)
* php zip unzip
* composer
* memcached (optional)
* openssl
* cron
* curl
* build-essential

[[TOC]](#table-of-contents)

## Installation

The software installation provided by this guide is intended to run by ROOT user:
   * `sudo su -`

[[TOC]](#table-of-contents)

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
   (*Replace `ssp-idp.example.org` with your IDP Full Qualified Domain Name*)

4. Be sure that your firewall **doesn't block** traffic on port **443** (or you can't access to your IdP)

5. Import SSL credentials:
   * Import SSL Certificate into: `/etc/ssl/certs/ssp-idp.example.org.crt`
   * Import SSL Key into: `/etc/ssl/private/ssp-idp.example.org.key`
   * Import SSL CA: `/usr/local/share/ca-certificates/ssl-ca.crt`
   * Run the command: `update-ca-certificates`

[[TOC]](#table-of-contents)

### Install Composer

---
**NOTE**

To update Composer use: `composer self-update`

---

1. Become ROOT:
   * `sudo su`

2. Prepare the environment:
   * ```bash
     apt install apache2 ntp php curl cron build-essential zip unzip rsyslog logrotate --no-install-recommends
     ``` 
3. Download Composer setup:
   * `wget "https://getcomposer.org/installer" -O /usr/local/src/composer-setup.php`

4. Install Composer:
   * `php /usr/local/src/composer-setup.php --install-dir=/usr/local/bin --filename=composer`

[[TOC]](#table-of-contents)

### Install SimpleSAMLphp

1. Become ROOT:
   * `sudo su`

2. Create the required directories:
   * `mkdir -p /var/simplesamlphp/cert /var/simplesamlphp/log /var/simplesamlphp/data`

3. Install SimpleSAMLphp:
   * `cd /var/simplesamlphp`
   * `composer require --prefer-stable simplesamlphp/simplesamlphp`
   * To the question "Do you trust "simplesamlphp/composer-module-installer" to execute code and wish to enable it now? (writes "allow-plugins" to composer.json) [y,n,d,?]" answer `y`

4. Create `config` and `metadata` directories into `/var/simplesamlphp` by:
   * `cp -r /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/config-templates /var/simplesamlphp/config`
   * `cp -r /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/metadata-templates /var/simplesamlphp/metadata`

[[TOC]](#table-of-contents)

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

          Alias /simplesaml /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/www

          RedirectMatch    ^/$  /simplesaml

          <Directory /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/www>
             <IfModule mod_authz_core.c>
                Require all granted
             </IfModule>
          </Directory>

        </VirtualHost>
     </IfModule>
     ```

3. Enable the following Apache2 modules:
   * `a2enmod ssl` - To support SSL protocol
   * `a2enmod headers` - To control of HTTP request and response headers.
   * `a2enmod alias` - To manipulation and control of URLs as requests arrive at the server.
   * `a2enmod include` - To process files before they are sent to the client.
   * `a2enmod negotiation` - Essential Apache module
   * `a2ensite ssp-idp.example.org-ssl.conf` - Enable SSP IdP Site
   * `a2dissite 000-default.conf` - Disable HTTP default site
   * `systemctl restart apache2.service`

4. Verify the strength of your IdP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

5. **OPTIONAL STEPS**:
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

[[TOC]](#table-of-contents)

### Configure SimpleSAMLphp

1. Assign the ownership of the SimpleSAMLphp logs to Apache user:
   * `chown www-data /var/simplesamlphp/log`

2. Generate some useful opaque strings:
   * User Admin Password (`auth.adminpassword`):
     * `php /var/simplesamlphp/bin/pwgen.php`
        
   * Secret Salt (`secretsalt`):
     * `tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo`

3. Change SimpleSAMLphp configuration:
   * `vim /var/simplesamlphp/config/config.php`
   
      ```php
      'baseurlpath' => 'simplesaml/',
      /* ...other things... */
      'certdir' => '/var/simplesamlphp/cert/',
      'loggingdir' => '/var/simplesamlphp/log/',
      'datadir' => '/var/simplesamlphp/data/',
      'tempdir' => '/tmp/simplesaml',
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
      'metadatadir' => '/var/simplesamlphp/metadata',
      /* ...other things ... */
      'theme.header' = '#_YOUR_ORGANIZATION_NAME_#',
      /* ...other things... */
      // Comment out line "50 => 'core:AttributeLimit'," into "authproc.idp" section
      // because we will use core:AttributeLimit into the "authproc" section on "metadata/saml20-idp-hosted.php"
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
     
   * `sudo systemctl restart rsyslog.service`

4. Enable Log rotation:

   * `sudo vim /etc/logrotate.d/simplesamlphp`

     ```bash
     /var/log/simplesamlphp.log /var/log/simplesamlphp.stat {
         monthly
         missingok
         rotate 12
         compress
         dateext
         dateformat .%Y-%m
         postrotate
             systemctl reload rsyslog
         endscript
     }
     ```

   * `sudo systemctl restart logrotate.service`

5. Check Login on the SSP appliance and retrieve the IdP "Entity ID" from "Fedearation" tab:
   * `https://ssp-idp.example.org/`

6. Configure a SMTP server to send mail only (Example):
   * `apt install mailutils postfix --no-install-recommends` (Internet Site => Insert your IdP FQDN)
   
   * `vim /etc/postfix/main.cf`

     ```bash
     /* ...other things... */
     inet_interfaces = localhost
     /* ...other things... */
     ```
     
   * `systemctl restart postfix.service`

7. **if MDX IDEM is not used**, set PHP `memory_limit` to '1024M' or more to allow the download of huge metadata files (like eduGAIN):

   * `vim /etc/php/7.4/mods-available/ssp.ini`

     ```bash
     ; configuration for SSP
     ; priority=20
     memory_limit = 1024M
     ```

   * `sudo phpenmod ssp`
   * `systemctl restart apache2.service`

[[TOC]](#table-of-contents)

### Configure the Identity Provider

#### Configure Metadata

* `vim /var/simplesamlphp/metadata/saml20-idp-hosted.php`

  ```php
  $metadata['__DYNAMIC:1__'] = [
     'host' => '__DEFAULT__',
     'privatekey' => 'ssp-idp.key',
     'certificate' => 'ssp-idp.crt',
     
     'scope' => ['<INSERT-HERE-IDP-SCOPE>'],   // Usually the scope is the domain name
     'userid.attribute' => 'uid', //deprecated, but needed by Consent module. It takes the same value of the persistent NameID source attribute

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

     /* The <LogoutResponse> message MUST be signed if the HTTP POST or Redirect binding is used */
     'sign.logout' => true,

     'NameIDFormat' => [
        'urn:oasis:names:tc:SAML:2.0:nameid-format:transient',
        'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent'
     ],

     'authproc' => [
        // Generate the transient NameID.
        1 => [
              'class' => 'saml:TransientNameID',
        ],

        // Generate the persistent NameID
        2 => [
              'class' => 'saml:PersistentNameID',
              'attribute' => 'uid',  //the source attribute needed by the NameID generation
        ],
     
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

        // Enable this authproc filter to automatically generated eduPersonTargetedID/persistent nameID
        20 => [
               'class' => 'saml:PersistentNameID2TargetedID',
               'attribute' => 'eduPersonTargetedID',
               'nameId' => true,
              ],

        // Adopts language from attribute to use in UI
        30 => 'core:LanguageAdaptor',

        // The Attribute Limit will be use to release all possibile values supported by IdP to SPs
        // Remember to comment out the line "50 => 'core:AttributeLimit'," into the "config/config.php" file
        // or no attribute will be released.
        50 => [
               'class' => 'core:AttributeLimit',
               'uid','givenName','sn','cn','mail','displayName','mobile',
               'title','preferredLanguage','telephoneNumber',
               'schacMotherTongue','schacPersonalTitle','schacHomeOrganization',
               'schacHomeOrganizationType','schacUserPresenceID','schacPersonalPosition',
               'schacPersonalUniqueCode','schacPersonalUniqueID',
               'eduPersonPrincipalName','eduPersonEntitlement',
               'eduPersonTargetedID','eduPersonOrcid','eduPersonOrgDN','eduPersonOrgUnitDN',
               'eduPersonScopedAffiliation','eduPersonAffiliation' => [
                  'student',
                  'staff',
                  'member',
                  'alum',
                  'affiliate',
                  'library-walk-in',
                  'faculty', // NO IDEM
                  'employee', // NO IDEM
               ],
        ],

        // Convert the attributes' names into OID because
        // SSP will use them from parsed metadata on the $attributes array.
        51 => ['class' => 'core:AttributeMap','name2oid'],

        // IDEM Attribute Filter:
        // IDEM SPs + Entity Category SPs + Custom SPs
        60 =>[
             'class' => 'core:PHP',
             'code'	=>
             '
             $config_dir = apache_getenv("SIMPLESAMLPHP_CONFIG_DIR");
             include($config_dir."/idem-attribute-filter.php");
             '
        ],

        // Convert the attributes' names into Name
        // to be able to see their names on the Consent page
        80 => ['class' => 'core:AttributeMap','oid2name'],

        // Consent module is enabled(with no permanent storage, using cookies)
        90 => [
               'class' => 'consent:Consent',
               'store' => 'consent:Cookie',
               'focus' => 'yes',
               'checked' => false
              ],
 
        // If language is set in Consent module it will be added as 'preferredLanguage' attribute
        99 => 'core:LanguageAdaptor',
        
        // Convert LDAP names to oids needed to send attributes to the SP
        100 => ['class' => 'core:AttributeMap', 'name2oid'],
     ],
  ];
  ```

  **NOTE**: Remember to Comment out the line "**50 => 'core:AttributeLimit',**" into "**authproc.idp**" section because we will use `core:AttributeLimit` into the "**authproc**" section on `metadata/saml20-idp-hosted.php` to limit the attributes released. If you keep the line *no attributes will be released*.

[[TOC]](#table-of-contents)

#### Configure Attribute Release Policies

> :warning: **These rules have been tested on a Test Federation**: Be careful to use without having understood them before!

> The following rules are set with the `idem-attribute-filter.php` file used by the `saml20-idp-hosted.php` file.
>
> IDEM + Entity Category + Custom SPs Attribute Release Policies:
> 1) Release "`eduPersonTargetedID`" ONLY IF the preferred "`<md:NameIDFormat>`" of the SP
>    IS NOT the "`persistent`" ones.
> 2) Release the "`eduPersonScopedAffiliation`" to all IDEM SPs
> 3) Release all required (`isRequired="true"`) attributes to all IDEM SPs
> 4) Release all required (`isRequired="true"`) attributes to all CoCo SP (if the EC is supported)
> 5) Release all R&S subset attributes:
> `mail`, `givenName`, `sn`, `displayName`, `eduPersonScopedAffiliation`, `eduPersonPrincipalName`, `eduPersonTargetedID`
> 6) Release attributes to those SPs that do not requrest attributes by their metadata,
>    or that has needed to receive a specific value for one or more attributes

   * Download IDEM ARP into SimpleSAMLphp `config` directory:
     * `cd /var/simplesamlphp/config`
     * `sudo wget https://registry.idem.garr.it/idem-conf/simplesamlphp/SSP1/idem-attribute-filter.php`

   * Change the `require` line into `idem-attribute-filter.php` by setting the correct path of the `attributemap.php` file

[[TOC]](#table-of-contents)

#### Configure SAML Metadata Credentials

* `vim /var/simplesamlphp/cert/ssp-idp-credentials.cnf`:

  (*Replace `ssp-idp.example.org` with your IDP Full Qualified Domain Name*)

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
  subjectAltName=DNS:ssp-idp.example.org, \
                 URI:https://ssp-idp.example.org/idp/simplesaml/saml2/idp/metadata.php
  subjectKeyIdentifier=hash
  ```

* `cd /var/simplesamlphp/cert`
* `openssl req -new -x509 -config ssp-idp-credentials.cnf -text -out ssp-idp.crt -days 3650`
* `chown -R www-data: /var/simplesamlphp/cert`
* `chmod 400 /var/simplesamlphp/cert/ssp-idp.key`

[[TOC]](#table-of-contents)

#### Configure the authentication source

1. Enable LDAP PHP module:
   * `apt install php-ldap`
   * `systemctl restart apache2.service`

2. Enable `ldap:LDAP` Authentication Source:
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

4. Try the LDAP Authentication Source on: 
   * `https://ssp-idp.example.org/simplesaml/module.php/core/authenticate.php`

     (*Replace `ssp-idp.example.org` with your IDP Full Qualified Domain Name*)

[[TOC]](#table-of-contents)

#### Configure automatic download of Federation Metadata
   
1. **IDEM MDX (recommended): https://mdx.idem.garr.it/**

2. IDEM MDS (legacy):
   1. Load CRON module:
      * `cd /var/simplesamlphp`
      * `cp vendor/simplesamlphp/simplesamlphp/modules/cron/config-templates/module_cron.php config/`

   2. Load METAREFRESH module:
      * `cd /var/simplesamlphp`
      * `cp vendor/simplesamlphp/simplesamlphp/modules/metarefresh/config-templates/config-metarefresh.php config/`

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
      * `cd /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/modules/metarefresh/bin`
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

      (*Replace `ssp-idp.example.org` with your IDP Full Qualified Domain Name*)

      ```bash
      # Run cron: [hourly]
      01 * * * *  root  curl --silent "https://ssp-idp.example.org/simplesaml/module.php/cron/cron.php?key=<SECRET>&tag=hourly" > /dev/null 2>&1
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
                 'outputDir'   => '/var/simplesamlphp/metadata/',

                 /*
                  * Which output format the metadata should be saved as.
                  * Can be 'flatfile' or 'serialize'. 'flatfile' is the default.
                 */
                 'outputFormat' => 'flatfile',
              ],
           ],
        ];
        ```

   9. Remove not needed files from:
       * `cd /var/simplesamlphp/metadata ; rm !(saml20-idp-hosted.php)`

   10. Download the Federation signing certificate: 
       * ```bash
         wget https://md.idem.garr.it/certs/idem-signer-20241118.pem -O /var/simplesamlphp/cert/federation-cert.pem
         ```

   11. Check the validity of the signing certificate:
       * `cd /var/simplesamlphp/cert`
       * `openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout`

         (sha1: 0E:21:81:8E:06:02:D1:D9:D1:CF:3D:4C:41:ED:5F:F3:43:70:16:79)
       * `openssl x509 -in federation-cert.pem -fingerprint -md5 -noout`

         (md5: 73:B7:29:FA:7C:AE:5C:E7:58:1F:10:0B:FC:EE:DA:A9)

   12. Go to `https://ssp-idp.example.org/simplesaml/module.php/core/frontpage_federation.php` and forcing download of the Federation metadata by pressing on `Metarefresh: fetch metadata` or wait 1 day

       (*Replace `ssp-idp.example.org` with your IDP Full Qualified Domain Name*)

[[TOC]](#table-of-contents)

#### Add translations of the new `schacHomeOrganizationType` attribute

* `vim /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/dictionaries/attributes.definition.json`

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

* `vim /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/dictionaries/attributes.translation.json`

  ```json
     /* ...other things before the end of file... */
     "attribute_schachomeorganizationtype":{
        "it": "Tipo di Organizzazione"
     }
  }
  ```

  (Pay attention also to "commas"!)

[[TOC]](#table-of-contents)

#### Enable UTF-8 on IdP metadata (to avoid encoding problems with accents)

* `vim /var/simplesamlphp/vendor/simplesamlphp/saml2/src/SAML2/DOMDocumentFactory.php`

  ```bash
  /* ...other things... */
     public static function create() : DOMDocument
     {
       return new DOMDocument('1.0','utf-8');
     }
  }
  ```

[[TOC]](#table-of-contents)

#### Download IdP Metadata

* `https://ssp-idp.example.org/simplesaml/saml2/idp/metadata.php`

  (*Replace `ssp-idp.example.org` with your IDP Full Qualified Domain Name*)

[[TOC]](#table-of-contents)

#### Register IdP on IDEM Entity Registry

Go to `https://registry.idem.garr.it` and follow "**Insert a New Identity Provider into the IDEM Test Federation**" (your entity has to be approved by an IDEM Federation Operator before become part of IDEM Test Federation)

[[TOC]](#table-of-contents)

### Appendix A - How to manage sessions with Memcached

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
[[TOC]](#table-of-contents)

### Appendix B - How to collect useful statistics

Follow **[SimpleSAMLphp statistics module](https://simplesamlphp.org/docs/contrib_modules/statistics/statistics.html)** documentation

[[TOC]](#table-of-contents)

### Utility

* [The Mozilla Observatory](https://observatory.mozilla.org/):
  The Mozilla Observatory has helped over 240,000 websites by teaching developers, system administrators, and security professionals how to configure their sites safely and securely.

[[TOC]](#table-of-contents)

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
