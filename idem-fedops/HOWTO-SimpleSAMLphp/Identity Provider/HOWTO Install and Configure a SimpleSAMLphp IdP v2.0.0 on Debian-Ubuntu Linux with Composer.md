# HOWTO Install and Configure a SimpleSAMLphp IdP v2.0.0 on Debian-Ubuntu Linux with Composer

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements)
   1. [Hardware](#hardware)
   2. [Other](#other)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Notes](#notes)
4. [Configure the environment](#configure-the-environment)
5. [Install Instructions](#install-instructions)
   1. [Install useful basic packages](#install-useful-basic-packages)
   2. [Install SimpleSAMLphp](#install-simplesamlphp)
6. [Configuration Instructions](#configuration-instructions)
   1. [Configure SSL on Apache2](#configure-ssl-on-apache2)
   2. [Configure SimpleSAMLphp](#configure-simplesamlphp)
   3. [Configure the Identity Provider](#configure-the-identity-provider)
      1. [Configure SAML Metadata Credentials](#configure-saml-metadata-credentials)
      2. [Configure Metadata](#configure-metadata)
      3. [Configure Attribute Release Policies](#configure-attribute-release-policies)
   4. [Configure the Directory (openLDAP or AD) Connection](#configure-the-directory-openldap-or-ad-connection)
   5. [Download IdP Metadata](#download-idp-metadata)
   6. [Register the IdP on the IDEM Test Federation](#register-the-idp-on-the-idem-test-federation)
7. [Appendix A - How to manage sessions with Memcached](#appendix-a---how-to-manage-sessions-with-memcached)
8. [Appendix B - Enable UTF-8 on IdP metadata (to avoid encoding problems with accents)](#appendix-b---enable-utf-8-on-idp-metadata-to-avoid-encoding-problems-with-accents)
9. [Appendix C - How to collect useful statistics](#appendix-c---how-to-collect-useful-statistics)
10. [Utility](#utility)
11. [Authors](#authors)
      1. [Original Author](#original-author)

## Requirements

### Hardware

* CPU: 2 Core (64 bit)
* RAM: 2 GB
* HDD: 20 GB
* OS: Ubuntu 22.04 (jammy)

[[TOC]](#table-of-contents)

### Other

* Apache >= 2.4
* PHP >= 7.4.0
* SSL Credentials: HTTPS Certificate & Key
* Logo:
  * size: 80x60 px (or other that respect the aspect-ratio)
  * format: PNG
  * style: with a transparent background
* Favicon:
  * size: 16x16 px (or other that respect the aspect-ratio)
  * format: PNG
  * style: with a transparent background

[[TOC]](#table-of-contents)

## Software that will be installed

* ca-certificates
* ntp
* vim
* apache2
* php
* php extensions (date,dom,hash,intl,json,libxml,mbstring,openssl,pcre,SPL,zlib,ldap extensions)
* zip
* unzip
* composer
* memcached (optional)
* openssl
* cron
* curl
* git

[[TOC]](#table-of-contents)

## Notes

This HOWTO uses `example.org` and `idp.example.org` to provide this guide with example values.

Please remember to **replace all occurencences** of the `example.org` value with the IdP domain name
and `idp.example.org` value with the Full Qualified Name of the Identity Provider.

[[TOC]](#table-of-contents)

## Configure the environment

1. Become ROOT:
   * `sudo su -`

2. Be sure that your firewall **is not blocking** the traffic on port **443** and **80** for the IdP server.

3. Set the IdP hostname:

   (**ATTENTION**: *Replace `idp.example.org` with your IdP Full Qualified Domain Name and `<HOSTNAME>` with the IdP hostname*)

   * `vim /etc/hosts`

     ```bash
     <YOUR SERVER IP ADDRESS> idp.example.org <HOSTNAME>
     ```

   * `hostnamectl set-hostname <HOSTNAME>`

4. (OPTIONAL) Change the default mirror to the GARR ones *(only for italian institutions)* on `/etc/apt/sources.list`:
   * `debian.mirror.garr.it` (Debian)
   * `ubuntu.mirror.garr.it` (Ubuntu)

   Debian Mirror List: https://www.debian.org/mirror/list<br/>Ubuntu Mirror List: https://launchpad.net/ubuntu/+archivemirrors

5. General packages update:

   ```bash
   apt update && apt-get upgrade -y --no-install-recommends
   ```

[TOC](#table-of-contents)

## Install Instructions

### Install useful basic packages

1. Become ROOT:
   * `sudo su -`

2. Install useful packages:

   ```bash
   apt install vim wget ca-certificates openssl ntp fail2ban --no-install-recommends
   ```

[[TOC]](#table-of-contents)

### Install SimpleSAMLphp

1. Become ROOT & move into its HOME dir:
   * `sudo su -`

2. Prepare the environment:

   ```bash
   apt install git zip unzip apache2 php php-mbstring php-date php-intl php-xml php-curl libpcre3 libpcre3-dev zlib1g zlib1g-dev curl cron --no-install-recommends
   ```

3. Download Composer setup:
   * `wget "https://getcomposer.org/installer" -O /usr/local/src/composer-setup.php`

4. Install Composer:
   * `php /usr/local/src/composer-setup.php --install-dir=/usr/local/bin --filename=composer`

     **NOTE**: To update Composer use: `composer self-update`

5. Create the required directories:
   * `mkdir -p /var/simplesamlphp/cert /var/simplesamlphp/config /var/simplesamlphp/metadata /var/simplesamlphp/data`

6. Install SimpleSAMLphp:
   * `cd /var/simplesamlphp`
   * `composer require simplesamlphp/simplesamlphp --update-no-dev`
   * To the question "**Do you trust "simplesamlphp/composer-module-installer**" to execute code and wish to enable it now? (writes "allow-plugins" to composer.json) [y,n,d,?]" answer `y`

7. Load `config` and `metadata` configuration files into `/var/simplesamlphp`:
   * `cp -r /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/config/config.php.dist /var/simplesamlphp/config/config.php`
   * `cp -r /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/metadata/saml20-idp-hosted.php.dist /var/simplesamlphp/metadata/saml20-idp-hosted.php`

[[TOC]](#table-of-contents)

## Configuration Instructions

### Configure SSL on Apache2

1. Become ROOT:
   * `sudo su -`

2. Create the DocumentRoot:

   ```bash
   mkdir /var/www/html/$(hostname -f)

   chown -R www-data: /var/www/html/$(hostname -f)

   echo '<h1>It Works!</h1>' > /var/www/html/$(hostname -f)/index.html
   ```

3. Create the Virtualhost file (**please pay attention: you need to edit this file and customize it, check the internal initial comment**):

   ```bash
   wget https://registry.idem.garr.it/idem-conf/simplesamlphp/2/IDP/apache2/idp.example.org.conf -O /etc/apache2/sites-available/$(hostname -f).conf
   ```

4. Put SSL credentials in the right place:
   * HTTPS Server Certificate (Public Key) inside `/etc/ssl/certs/$(hostname -f).crt`
   * HTTPS Server Key (Private Key) inside `/etc/ssl/private/$(hostname -f).key`
   * Add CA Cert into `/etc/ssl/certs`:
     * If GARR TCS or GEANT TCS is used:

       ```bash
       wget -O /etc/ssl/certs/GEANT_OV_RSA_CA_4.pem https://crt.sh/?d=2475254782
       
       wget -O /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt https://crt.sh/?d=924467857
       
       cat /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt >> /etc/ssl/certs/GEANT_OV_RSA_CA_4.pem
       
       rm /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt
       ```

     * If ACME (Let's Encrypt) is used:
       * `ln -s /etc/letsencrypt/live/<SERVER_FQDN>/chain.pem /etc/ssl/certs/ACME-CA.pem`

5. Configure the right privileges for the SSL Certificate and Key used by HTTPS:

   ```bash
   chmod 400 /etc/ssl/private/$(hostname -f).key

   chmod 644 /etc/ssl/certs/$(hostname -f).crt
   ```

   (*`$(hostname -f)` will provide your IdP Full Qualified Domain Name*)

6. Enable the following Apache2 modules and VirtualHost:
   * `a2enmod ssl` - To support SSL protocol
   * `a2enmod headers` - To control of HTTP request and response headers.
   * `a2enmod alias` - To manipulation and control of URLs as requests arrive at the server.
   * `a2enmod include` - To process files before they are sent to the client.
   * `a2enmod negotiation` - Essential Apache module
   * `a2ensite $(hostname -f).conf` - Enable SSP IdP VirtualHost
   * `a2dissite 000-default.conf default-ssl` - Disable HTTP & HTTPS default VirtualHost
   * `systemctl restart apache2.service`

7. Check that IdP works:
   * ht<span>tps://</span>idp.example.org/simplesaml

8. Verify the strength of your IdP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

9. **OPTIONAL STEPS**:
   If you want to host your IdP's Information/Privacy pages on the IdP itself, follow the steps:

   1. Create all needed files:
      * `vim /var/www/html/$(hostname -f)/info_page.html`

         ```bash
         <html>
            <head><title>Information Page</title></head>
            <body>
               <h1>Put here IdP Information page content</h1>
            </body>
         </html>
         ```

      * `vim /var/www/html/$(hostname -f)/privacy_page.html`

         ```bash
         <html>
            <head><title>Privacy Page</title></head>
            <body>
               <h1>Put here IdP Privacy page content</h1>
            </body>
         </html>
         ```

      * `touch /var/www/html/$(hostname -f)/logo.png` (80x60 px or bigger with the same aspect-ratio)

      * `touch /var/www/html/$(hostname -f)/favicon.png` (16x16 px or bigger with the same aspect-ratio)

   2. Replace them with the correct content.

[[TOC]](#table-of-contents)

### Configure SimpleSAMLphp

1. Become ROOT:
   * `sudo su -`

2. Generate secrets:
   * `<USER_ADMIN_PASSWORD>' (`auth.adminpassword`):
     * `php /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/bin/pwgen.php`

   * `<SECRET_SALT>` (`secretsalt`):
     * `tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo`

3. Change SimpleSAMLphp configuration:
   * `vim /var/simplesamlphp/config/config.php`

      ```php
      'baseurlpath' => 'simplesaml/',
      /* ...other things... */
      'loggingdir' => null,
      'datadir' => '/var/simplesamlphp/data/',
      'tempdir' => '/tmp/simplesaml',
      /* ...other things... */
      'certdir' => '/var/simplesamlphp/cert/',
      /* ...other things... */
      'technicalcontact_name' => 'Technical Contact',
      'technicalcontact_email' => 'technical.support@example.com',
      /* ...other things... */
      'secretsalt' => '<SECRET_SALT>',
      /* ...other things... */
      'auth.adminpassword' => '<USER_ADMIN_PASSWORD>',
      /* ...other things... */
      'logging.level' => 'SimpleSAML\Logger::NOTICE',
      'logging.handler' => 'syslog',
      /* ...other things... */
      'enable.saml20-idp' => true,
      /* ...other things ... */
      'theme.header' = '<ORGANIZATION_NAME>',
      /* ...other things... */
      // Comment out entire "authproc.idp" element because it will be used the 'authproc' into the 'saml20-idp-hosted.php' metadata
      /* ...other things... */
      'metadatadir' => '/var/simplesamlphp/metadata',
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

   * `systemctl restart rsyslog.service`

4. Create the `authsources.php` file:
   * `vim /var/simplesamlphp/config/authsources.php`

     ```php
     <?php

     $config = [

        // This is a authentication source which handles admin authentication.
        'admin' => [
            'core:AdminPassword',
        ],
     ];   
     ```

5. Install Consent module:
   * `composer require simplesamlphp/simplesamlphp-module-consent --update-no-dev`

6. Enable Consent module and create the `nameid` internal attribute:
   * `vim /var/simplesamlphp/config/config.php`

     ```php
     /* ...other things...*/
     'module.enable' => [
        'exampleauth' => false,
        'core' => true,
        'admin' => true,
        'saml' => true,
        'consent' => true,
     ],
     /* ...other things...*/
     ```

     ```php
     'authproc.sp' => [
        // Generates 'nameid' internal attribute
        // used by Consent module as identifyingAttribute
        // for each SP.
        21 => [
              'class' => 'saml:NameIDAttribute',
        ],
     ],
     ```

7. Check if the module is enabled on the Administration page :
   * `https://idp.example.org/simplesaml/admin`

8. Configure a SMTP server to send mail only (Example):
   * `apt install mailutils postfix --no-install-recommends` (Internet Site => Insert your IdP FQDN)

   * `vim /etc/postfix/main.cf`

     ```bash
     /* ...other things... */
     inet_interfaces = localhost
     /* ...other things... */
     ```

   * `systemctl restart postfix.service`

[[TOC]](#table-of-contents)

### Configure the Identity Provider

#### Configure SAML Metadata Credentials

1. Become ROOT:
   * `sudo su -`

2. Generate `md-sign-enc-cert.crt` and `md-sign-enc-cert.key`:
   * `vim /var/simplesamlphp/cert/ssp-md-credentials.cnf`:

     (*Replace `idp.example.org` with your IDP Full Qualified Domain Name*)

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
     default_keyfile=md-sign-enc-cert.key

     [dn]
     CN=idp.example.org

     [ext]
     subjectAltName=DNS:idp.example.org, \
                    URI:https://idp.example.org/simplesaml/module.php/saml/idp/metadata
     subjectKeyIdentifier=hash
     ```

   * `cd /var/simplesamlphp/cert`
   * `openssl req -new -x509 -config ssp-md-credentials.cnf -out md-sign-enc-cert.crt -days 3650`
   * `chown -R www-data: /var/simplesamlphp/cert`
   * `chmod 400 /var/simplesamlphp/cert/md-sign-enc-cert.key`

[[TOC]](#table-of-contents)

#### Configure Metadata

1. Become ROOT:
   * `sudo su -`

2. Configure the IdP metadata:
   * `vim /var/simplesamlphp/metadata/saml20-idp-hosted.php`

     ```php
     $metadata['https://idp.example.org/simplesaml/module.php/saml/idp/metadata'] = [
        'host' => '__DEFAULT__',
        'privatekey' => 'md-sign-enc-cert.key',
        'certificate' => 'md-sign-enc-cert.crt',
        
        'scope' => ['<IDP-SCOPE-1>','<IDP-SCOPE-2>'],   //Usually the scopes are the domain names belonging the institution

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
        
        /* eduPersonTargetedID with oid NameFormat is a raw XML value, ma potrebbe essere 'base64' */
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
                 'identifyingAttribute' => 'uid',  //the source attribute needed by the NameID generation
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
                 
           // Add subject-id
           13 => [
                  'class' => 'saml:SubjectID',
                  'identifyingAttribute' => 'uid',
                  'scopeAttribute' => 'schacHomeOrganization',
           ],

           // Add pairwise-id
           14 => [
                  'class' => 'saml:PairwiseID',
                  'identifyingAttribute' => 'uid',
                  'scopeAttribute' => 'schacHomeOrganization',
           ],

           // Enable this authproc filter to automatically generated eduPersonTargetedID/persistent nameID
           20 => [
                  'class' => 'saml:PersistentNameID2TargetedID',
                  'attribute' => 'eduPersonTargetedID',
                  'nameId' => true,
                 ],

           // The Attribute Limit will be use to release all possibile values supported by IdP to SPs
           // Remember to Comment out entire "authproc.idp" element into "config/config.php" file
           // or no attribute will be released.
           
           50 => [
                  'class' => 'core:AttributeLimit',
                  'uid','givenName','sn','cn','mail','displayName','mobile',
                  'title','preferredLanguage','telephoneNumber',
                  'schacMotherTongue','schacPersonalTitle','schacHomeOrganization',
                  'schacHomeOrganizationType','schacUserPresenceID','schacPersonalPosition',
                  'schacPersonalUniqueCode','schacPersonalUniqueID',
                  'eduPersonPrincipalName','eduPersonEntitlement',
                  'urn:oasis:names:tc:SAML:attribute:subject-id',
                  'urn:oasis:names:tc:SAML:attribute:pairwise-id',
                  'eduPersonTargetedID','eduPersonOrcid','eduPersonOrgDN','eduPersonOrgUnitDN',
                  'eduPersonScopedAffiliation' => [
                     'regex' => true,
                     '/^student@.*/',
                     '/^staff@.*/',
                     '/^member@.*/',
                     '/^alum@.*/',
                     '/^affiliate@.*/',
                     '/^library-walk-in@.*/',
                     '/^faculty@.*/',  // NO IDEM
                     '/^employee@.*/', // NO IDEM
                  ],
                  'eduPersonAffiliation' => [
                     'student',
                     'staff',
                     'member',
                     'alum',
                     'affiliate',
                     'library-walk-in',
                     'faculty',  // NO IDEM
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
                'code'  =>
                '
                $config_dir = apache_getenv("SIMPLESAMLPHP_CONFIG_DIR");
                include($config_dir."/idem-attribute-filter.php");
                '
           ],

           // Convert the attributes' names into Name
           // to be able to see their names on the Consent page
           80 => ['class' => 'core:AttributeMap','oid2name'],

           // Consent module is enabled without persistence.
           // In order to generate the privacy preserving hashes in the consent module, 
           // is needed to pick one attribute that is always available and that is unique to all users. 
           // An example of such an attribute is uid or eduPersonPrincipalName.
           //
           // This setup uses no persistent storage at all. 
           // This means that the user will always be asked to give consent each time he logs in.
           90 => [
                  'class' => 'consent:Consent',
                  'identifyingAttribute' => 'nameid',
                  'focus' => 'yes',
                  'includeValues' => true,
                  'attributes.exclude' => ['nameid'],
           ],
    
           // If language is set in Consent module it will be added as 'preferredLanguage' attribute
           99 => 'core:LanguageAdaptor',
           
           // Convert LDAP names to oids needed to send attributes to the SP
           100 => ['class' => 'core:AttributeMap', 'name2oid'],
        ],
        
        'auth' => 'example-userpass';
        
        // ... other things ...
     ];
     ```

3. **NOTE**: Remember to Comment out entire "**authproc.idp**" element into "**config/config.php**" file or *no attributes will be released*.

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
  * `sudo wget https://registry.idem.garr.it/idem-conf/simplesamlphp/2/IDP/config/idem-attribute-filter.php -O /var/simplesamlphp/config/idem-attribute-filter.php`

* Change the `require` line into `idem-attribute-filter.php` by setting the correct path of the `name2oid.php` file if differs on your instance.

[[TOC]](#table-of-contents)

### Configure the Directory (openLDAP or AD) Connection

1. Become ROOT:
   * `sudo su -`

2. Enable LDAP PHP module:
   * `apt install php-ldap --no-install-recommends`
   * `systemctl restart apache2.service`

3. Install the SimpleSAMLphp LDAP module:
   * `cd /var/simplesamlphp`
   * `composer require simplesamlphp/simplesamlphp-module-ldap --update-no-dev`

4. Check that you can reach the Directory from your IDP server:
   * For OpenLDAP:

     * StartTLS or Plain LDAP:

       ```bash
       ldapsearch -x -H <LDAP-URI> -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<IDPUSER-PASSWORD>' -b 'ou=people,dc=example,dc=org' '(&(objectClass=inetOrgPerson)(uid=<USERNAME-USED-IN-THE-LOGIN-FORM>))'
       ```

     * SSL:

       ```bash
       ldapsearch -x -H <LDAP-URI> -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<IDPUSER-PASSWORD>' -b 'ou=people,dc=example,dc=org' '(&(objectClass=inetOrgPerson)(uid=<USERNAME-USED-IN-THE-LOGIN-FORM>))'
       ```

       * the baseDN (`-b` parameter) ==> `ou=people,dc=example,dc=org` (branch containing the registered users):<br/>
        corresponds to `search.base` authsource LDAP setting.
       * the bindDN (`-D` parameter) ==> `cn=idpuser,ou=system,dc=example,dc=org` (distinguished name for the user that can made queries on the LDAP, read only is sufficient):<br/>
        corresponds to `search.username` authsource LDAP setting.
       * the Search Filter ==> `(&(objectClass=inetOrgPerson)(uid=<USERNAME-USED-IN-THE-LOGIN-FORM>))`:<br/>
        corresponds to `search.filter' authsource LDAP setting.

   * For Active Directory:

     ```bash
     ldapsearch -x -H <LDAP-URI> -D 'CN=idpuser,CN=Users,DC=ad,DC=example,DC=org' -w '<IDPUSER-PASSWORD>' -b 'CN=Users,DC=ad,DC=example,DC=org' '(sAMAccountName=<USERNAME-USED-IN-THE-LOGIN-FORM>)'
     ```

     * the baseDN (`-b` parameter) ==> `CN=Users,DC=ad,DC=example,DC=org` (branch containing the registered users):<br/>
       corresponds to `search.base` authsource LDAP setting.
     * the bindDN (`-D` parameter) ==> `CN=idpuser,CN=Users,DC=ad,DC=example,DC=org` (distinguished name for the user that can made queries on the LDAP, read only is sufficient):<br/>
       corresponds to `search.username` authsource LDAP setting.
     * the Search Filter `(&(objectClass=inetOrgPerson)(uid=<USERNAME-USED-IN-THE-LOGIN-FORM>))`:<br/>
       corresponds to `search.filter' authsource LDAP setting.

5. Add the `ldap:Ldap` Authentication Source:
   * `vim /var/simplesamlphp/config/authsources.php`

     **NOTE**:
     Replace the list provided into the `attributes` array with the attributes released by institutional LDAP/AD, <br/>
     and all `example` values with the correct one.

     ```php
     <?php

     $config = [

         // This is a authentication source which handles admin authentication.
         'admin' => [
             'core:AdminPassword',
         ],

         // LDAP authentication source.
         'ldap' => [
             'ldap:Ldap',
             'connection_string' => 'ldap://ldap.example.org',
              'encryption' => 'none',
              'version' => 3,
              'ldap.debug' => true,
              'options' => [
                 /**
                  * Set whether to follow referrals.
                  * AD Controllers may require 0x00 to function.
                  * Possible values are 0x00 (NEVER), 0x01 (SEARCHING),
                  *   0x02 (FINDING) or 0x03 (ALWAYS).
                  */
                 'referrals' => 0x03,
                  'network_timeout' => 3,
             ],
             'connector' => '\SimpleSAML\Module\ldap\Connector\Ldap',
             // Pay attention on 'eduPersonTargetedID', 'eduPersonPrincipalName', 'eduPersonScopedAffiliation', 'schacHomeOrganization' and 'schacHomeOrganizationType'
             // Because they will be managed by the Authentication Process Filter inside metadata/saml20-idp-hosted.php
             // If you need to manage them directly on your Directory Service, remove the AuthProcFilter number 10,11,12,20 from metadata/saml20-idp-hosted.php
             'attributes' => ['uid','sn','givenName','cn','displayName','mail','eduPersonAffiliation','eduPersonEntitlement'],
             'search.filter' => '(&(objectClass=inetOrgPerson)(uid=%username%))',
             'dnpattern' => 'uid=%username%,ou=people,dc=example,dc=org',
             'search.enable' => false,
             'search.base' => [
                 'ou=people,dc=example,dc=org',
             ],
             'search.scope' => 'sub',
             'search.attributes' => ['uid'],
             'search.username' => '<LDAP-DN-OF-USER-THAT-PERFORMS-QUERIES-ON-DIRECTORY>',
             'search.password' => '<QUERY-USER-PASSWORD>',
         ],
     ];
     ```

6. Connect LDAP to the IdP:
   * `vim /var/simplesamlphp/metadata/saml20-idp-hosted.php`

     ```php
        /* ...other things before end of file...*/
        'auth' => 'ldap',
     ];
     ```

7. Enable the SimpleSAMLphp LDAP module:
   * `vim /var/simplesamlphp/config/config.php`

     ```php
     /* ...other things...*/
     'module.enable' => [
        'exampleauth' => false,
        'core' => true,
        'admin' => true,
        'saml' => true,
        'consent' => true,
        'ldap' => true,
     ],
     /* ...other things...*/
     ```

8. Try the LDAP Authentication Source on:
   * `https://idp.example.org/simplesaml/module.php/admin/test`

     (*Replace `idp.example.org` with your IDP Full Qualified Domain Name*)

[[TOC]](#table-of-contents)

### Download IdP Metadata

* `https://idp.example.org/simplesaml/module.php/saml/idp/metadata`

  (*Replace `idp.example.org` with your IDP Full Qualified Domain Name*)

### Register the IdP on the IDEM Test Federation

Follow these steps **ONLY IF** your organization is connected to the [GARR Network](https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites?key=all)

1. Register you IdP metadata on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
   * `https://registry.idem.garr.it/`

2. Configure the IdP to retrieve the Test Federation Metadata:

   * Follow the instructions on: <https://mdx.idem.garr.it/>

3. Wait that your IdP Metadata is approved by an IDEM Federation Operator into the metadata stream and the next steps provided by the operator itself.

4. Follow the [instructions provided by IDEM](https://wiki.idem.garr.it/wiki/RegistraEntita).

[[TOC]](#table-of-contents)

## Appendix A - How to manage sessions with Memcached

1. Become ROOT:
   * `sudo su -`

2. Install needed packages:
   * `apt install memcached php-memcached --no-install-recommends`

3. Enable PHP memcached module:
   * `phpenmod memcached`

4. Restart Apache:
   * `systemctl restart apache2.service`

5. Enable memcache on simplesamlphp:
   * `vim /var/simplesamlphp/config/config.php`

     ```php
     /* ...other things... */
     'store.type' => 'memcache',
     /* ...other things... */
     ```

[[TOC]](#table-of-contents)

## Appendix B - Enable UTF-8 on IdP metadata (to avoid encoding problems with accents)

* `vim /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/src/SimpleSAML/Metadata/SAMLBuilder.php`

```bash
public function getEntityDescriptorText(bool $formatted = true): string
{
   $xml = $this->getEntityDescriptor();
   if ($formatted) {
       $xmlUtils = new Utils\XML();
       $xmlUtils->formatDOMElement($xml);
   }

   $xml->ownerDocument->encoding = "utf-8";

   return $xml->ownerDocument->saveXML();
}
```

[[TOC]](#table-of-contents)

## Appendix C - How to collect useful statistics

Follow: <https://simplesamlphp.org/docs/contrib_modules/statistics/statistics.html>

1. Enable the 'statistics' and the 'cron' modules:
   * `vim /var/simplesamlphp/config/config.php`

     ```php
     /* ...other things...*/
     'module.enable' => [
        'exampleauth' => false,
        'core' => true,
        'admin' => true,
        'saml' => true,
        'consent' => true,
        'ldap' => true,
        'statistics' => true,
        'cron' => true,
     ],
     /* ...other things...*/
     ```

2. Install the 'statistics' module:
   * `cd /var/simplesamlphp`
   * `composer require simplesamlphp/simplesamlphp-module-statistics --update-no-dev`

3. Configure the 'statistics' and `cron` module
   * statistics:

     ```bash
     cp /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/modules/statistics/config-templates/*.php /var/simplesamlphp/config
     ```

   * cron:

     ```bash
     cp /var/simplesamlphp/vendor/simplesamlphp/simplesamlphp/modules/cron/config-templates/*.php /var/simplesamlphp/config
     ```

4. Prepare the environment for 'statistics' module:
   * `mkdir /var/simplesamlphp/stats`
   * `chown www-data /var/simplesamlphp/stats` (required to allow SimpleSAMLphp to write datas)
   * `chown www-data /var/log/simplesamlphp.stat` (require to allow SimpleSAMLphp to read datas)

5. Replace the word `secret` with your personal opaque value into:
   * `sed -i "s/secret/$(tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null ; echo)/g" /var/simplesamlphp/config/module_cron.php`

6. Copy the suggestion for a crontab file from the location `/simplesaml/module.php/cron/info` into your crontab:
   * `crontab -e`
   * Paste the suggestion before the end of file

[[TOC]](#table-of-contents)

## Utility

* [The Mozilla Observatory](https://observatory.mozilla.org/):
  The Mozilla Observatory has helped over 240,000 websites by teaching developers, system administrators, and security professionals how to configure their sites safely and securely.

* [simplesamlphp-module-statistics](https://packagist.org/packages/simplesamlphp/simplesamlphp-module-statistics)
* [simplesamlphp-module-ldap](https://packagist.org/packages/simplesamlphp/simplesamlphp-module-ldap)
* [simplesamlphp-module-consent](https://packagist.org/packages/simplesamlphp/simplesamlphp-module-consent)

[[TOC]](#table-of-contents)

## Authors

### Original Author

* Marco Malavolti (marco.malavolti@garr.it)

[[TOC]](#table-of-contents)
