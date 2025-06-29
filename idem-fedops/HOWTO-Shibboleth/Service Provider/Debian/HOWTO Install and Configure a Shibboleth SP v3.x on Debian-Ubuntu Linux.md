# HOWTO Install and Configure a Shibboleth SP v3.x on Debian-Ubuntu Linux

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

01. [Requirements Hardware](#requirements-hardware)
02. [Software that will be installed](#software-that-will-be-installed)
03. [Other Requirements](#other-requirements)
04. [Installation Instructions](#installation-instructions)
    01. [Install software requirements](#install-software-requirements)
    02. [Configure the environment](#configure-the-environment)
    03. [Install Shibboleth Service Provider](#install-shibboleth-service-provider)
05. [Configuration Instructions](#configuration-instructions)
    01. [Configure SSL on Apache2](#configure-ssl-on-apache2)
    02. [Configure Shibboleth SP](#configure-shibboleth-sp)
    03. [Configure an example federated resource "secure"](#configure-an-example-federated-resource-secure)
    04. [Enable Attribute Support on Shibboleth SP](#enable-attribute-support-on-shibboleth-sp)
    05. [Connect SP to the Federation](#connect-sp-to-the-federation)
    06. [Connect SP directly to an IdP](#connect-sp-directly-to-an-idp)
06. [Test](#test)
07. [Enable Attribute Checker Support on Shibboleth SP](#enable-attribute-checker-support-on-shibboleth-sp)
08. [Increase startup timeout](#increase-startup-timeout)
09. [OPTIONAL - Maintain 'shibd' working](#optional---maintain-shibd-working)
10. [Utility](#utility)
11. [Authors](#authors)
12. [Thanks](#thanks)

## Requirements Hardware

- CPU: 2 Core
- RAM: 4 GB
- HDD: 20 GB
- OS: Debian 10

## Software that will be installed

- ca-certificates
- ntp
- vim
- libapache2-mod-php, php, libapache2-mod-shib, apache2 (>= 2.4)
- openssl

## Other Requirements

- SSL Credentials: HTTPS Certificate & Key

## Notes

This HOWTO use `example.org` as domain name and `sp.example.org` as FQDN (Full Qualified Domain Name) to provide example values to this guide.

Please, remember to **replace all occurence** of `example.org` domain name, or part of it, with the SP domain name into the configuration files and also `sp.example.org` with the FQDN of your SP server.

## Installation Instructions

### Install software requirements

01. Become ROOT:

    - `sudo su -`

02. Change the default mirror to the GARR ones on `/etc/apt/sources.list` (OPTIONAL):

    - `debian.mirror.garr.it` (Debian)
    - `ubuntu.mirror.garr.it` (Ubuntu)

03. Update packages:

    - `apt update && apt-get upgrade -y --no-install-recommends`
  
04. Install the packages required:

    - `apt install ca-certificates vim openssl`

### Configure the environment

01. Modify your `/etc/hosts`:

    - `vim /etc/hosts`
  
      ```bash
      127.0.1.1 sp.example.org sp
      ```

      (*Replace `sp.example.org` with your SP Full Qualified Domain Name*)

      (*Replace `sp` with your SP Hostname*)

02. Be sure that your firewall **doesn't block** the traffic on port **443** (or you can't access to your SP)

### Install Shibboleth Service Provider

01. Become ROOT:

    - `sudo su -`

02. Install Shibboleth SP:

    - `apt install apache2 libapache2-mod-shib ntp --no-install-recommends`

      From this point the location of the SP directory is: `/etc/shibboleth`

## Configuration Instructions

### Configure SSL on Apache2

> According to [NSA and NIST](https://www.keylength.com/en/compare/), RSA with 3072 bit-modulus is the minimum to protect up to TOP SECRET over than 2030.

01. Become ROOT:

    - `sudo su -`

02. Create the DocumentRoot:

    ```bash
    mkdir /var/www/html/$(hostname -f)
    
    sudo chown -R www-data: /var/www/html/$(hostname -f)
    
    echo '<h1>It Works!</h1>' > /var/www/html/$(hostname -f)/index.html
    ```

03. Create the Virtualhost file (**please pay attention: you need to edit this file and customize it, check the initial comment inside of it**):

    ```bash
    wget https://github.com/ConsortiumGARR/idem-tutorials/raw/master/idem-fedops/HOWTO-Shibboleth/Service%20Provider/utils/sp.example.org.conf -O /etc/apache2/sites-available/000-$(hostname -f).conf
    ```

04. Put SSL credentials in the right place:

    - HTTPS Server Certificate (Public Key) inside `/etc/ssl/certs`
    - HTTPS Server Key (Private Key) inside `/etc/ssl/private`
    - Add CA Cert into `/etc/ssl/certs`

      - If you use GARR TCS or GEANT TCS:

        ```bash
        wget -O /etc/ssl/certs/GEANT_TLS_RSA_1.pem https://crt.sh/?d=16099180997
        ```

      - If you use ACME (Let's Encrypt):

        - `ln -s /etc/letsencrypt/live/<SERVER_FQDN>/chain.pem /etc/ssl/certs/ACME-CA.pem`

05. Configure the right privileges for the SSL Certificate and Key used by HTTPS:

    ```bash
    chmod 400 /etc/ssl/private/$(hostname -f).key

    chmod 644 /etc/ssl/certs/$(hostname -f).crt
    ```

    ( *`$(hostname -f)` will provide your IdP Full Qualified Domain Name* )

06. Enable **proxy_http**, **SSL** and **headers** Apache2 modules:

    ```bash
    a2enmod ssl headers alias include negotiation

    a2dissite 000-default.conf default-ssl

    a2ensite 000-$(hostname -f).conf

    systemctl restart apache2.service
    ```

07. Verify the strength of your SP's machine on:

    - [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

### Configure Shibboleth SP

01. Become ROOT:

    - `sudo su -`

02. Change the SP entityID and technical contact email address:

    ```bash
    sed -i "s/sp.example.org/$(hostname -f)/" /etc/shibboleth/shibboleth2.xml

    sed -i "s/root@localhost/<TECH-CONTACT-EMAIL-ADDRESS-HERE>/" /etc/shibboleth/shibboleth2.xml

    sed -i 's/handlerSSL="false"/handlerSSL="true"/' /etc/shibboleth/shibboleth2.xml

    sed -i 's/cookieProps="http"/cookieProps="https"/' /etc/shibboleth/shibboleth2.xml

    sed -i 's/cookieProps="https">/cookieProps="https" redirectLimit="exact">/' /etc/shibboleth/shibboleth2.xml
    ```

03. Create SP metadata Signing and Encryption credentials:

    - Ubuntu:

      ```bash
      cd /etc/shibboleth

      shib-keygen -u _shibd -g _shibd -h $(hostname -f) -y 30 -e https://$(hostname -f)/shibboleth -n sp-signing -f

      shib-keygen -u _shibd -g _shibd -h $(hostname -f) -y 30 -e https://$(hostname -f)/shibboleth -n sp-encrypt -f

      /usr/sbin/shibd -t

      systemctl restart shibd.service

      systemctl restart apache2.service
      ```

    - Debian

      ```bash
      cd /etc/shibboleth

      ./keygen.sh -u shibd -g shibd -h $(hostname -f) -y 30 -e https://$(hostname -f)/shibboleth -n sp-signing -f

      ./keygen.sh -u shibd -g shibd -h $(hostname -f) -y 30 -e https://$(hostname -f)/shibboleth -n sp-encrypt -f

      LD_LIBRARY_PATH=/opt/shibboleth/lib64 /usr/sbin/shibd -t

      systemctl restart shibd.service

      systemctl restart apache2.service
      ```

04. Enable Shibboleth Apache2 configuration:

    ```bash
    a2enmod shib
    ```

05. Remove the `#` character from the `#Redirect ...` line on the Apache2 configuration to enable it:

    - `vim /etc/apache2/sites-available/000-$(hostname -f).conf`

      ```bash
      #Redirect "/shibboleth" "/Shibboleth.sso/Metadata"
      ```

06. Reload Apache2 service to apply changes:

    - `systemctl reload apache2.service`

07. Now you are able to reach your Shibboleth SP Metadata from its entityID:

    - `https://sp.example.org/shibboleth`

    or from its Metadata endpoint:

    - `https://sp.example.org/Shibboleth.sso/Metadata`

      ( *Replace `sp.example.org` with your SP Full Qualified Domain Name* )

### Configure an example federated resource "secure"

01. Create the Apache2 configuration for the application:

    - `sudo su -`

    - `vim /etc/apache2/conf-available/secure.conf`

      ```bash
      <Location /secure>
        Authtype shibboleth
        ShibRequireSession On
        require valid-user
      </Location>
      ```

    - `a2enconf secure`

02. Create the "`secure`" application into the DocumentRoot:

    ```bash
    mkdir -p /var/www/html/$(hostname -f)/secure

    wget https://github.com/ConsortiumGARR/idem-tutorials/raw/master/idem-fedops/HOWTO-Shibboleth/Service%20Provider/utils/index.php.txt -O /var/www/html/$(hostname -f)/secure/index.php
    ```

03. Install needed packages and restart Apache2:

    ```bash
    apt install libapache2-mod-php php

    systemctl restart apache2.service
    ```

### Enable Attribute Support on Shibboleth SP
>
> The Attribute Map file is used by the Service Provider to recognize and support new attributes released by an Identity Provider

Enable attribute support by removing comment from the related content into `/etc/shibboleth/attribute-map.xml` than restart `shibd` service with:

- `sudo systemctl restart shibd.service`

### Connect SP to the Federation

> Follow these steps **IF AND ONLY IF** your organization will join as a Partner or a Member into [IDEM Federation](https://idem.garr.it/en/federazione-idem-en/idem-federation)

01. Register you SP on IDEM Entity Registry:
    (your entity has to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):

    - Go to `https://registry.idem.garr.it`, follow "Insert a New Service Provider into the IDEM Test Federation" and insert your SP metadata

02. Configure the SP to retrieve the Federation Metadata:

    01. **IDEM MDX (recommended): <https://mdx.idem.garr.it/>**

    02. IDEM MDS (legacy):

        01. Retrieve the IDEM GARR Federation Certificate needed to verify the signed metadata:

            - `cd /etc/shibboleth/`
            - `curl https://md.idem.garr.it/certs/idem-signer-20241118.pem -o federation-cert.pem`
            - Check the validity:
              - `cd /etc/shibboleth`
              - `openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout`

                (sha1: 0E:21:81:8E:06:02:D1:D9:D1:CF:3D:4C:41:ED:5F:F3:43:70:16:79)

              - `openssl x509 -in federation-cert.pem -fingerprint -md5 -noout`

                (md5: 73:B7:29:FA:7C:AE:5C:E7:58:1F:10:0B:FC:EE:DA:A9)

        02. Edit `shibboleth2.xml` opportunely:

            - `vim /etc/shibboleth/shibboleth2.xml`

              ```bash

                  <!-- If it is needed to manage the authentication on several IdPs
                        install and configure the Shibboleth Embedded Discovery Service
                        by following this HOWTO: https://u.garr.it/howtoshibeds 
                  -->
                  <SSO discoveryProtocol="SAMLDS" discoveryURL="https://wayf.idem-test.garr.it/WAYF">
                     SAML2
                  </SSO>
                  <!-- other things -->
              </Sessions>
           
              <MetadataProvider type="XML" url="http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml"
                                backingFilePath="idem-test-metadata-sha256.xml" maxRefreshDelay="7200">
                    <MetadataFilter type="Signature" certificate="federation-cert.pem"/>
                    <MetadataFilter type="RequireValidUntil" maxValidityInterval="864000" />
              </MetadataProvider>
              ```

        03. Restart `shibd` and `Apache2` daemon:

            - `sudo systemctl restart shibd`
            - `sudo systemctl restart apache2`

03. Jump to [Test](#test)

### Connect SP directly to an IdP

> Follow these steps **IF** you need to connect one SP with only one IdP. It is useful for test purposes.

01. Edit `shibboleth2.xml` opportunely:

    - `vim /etc/shibboleth/shibboleth2.xml`

      ```bash

      <!-- If it is needed to manage the authentication on several IdPs
           install and configure the Shibboleth Embedded Discovery Service
           by following this HOWTO: https://url.garrlab.it/nakt7 
      -->
      <SSO entityID="https://idp.example.org/idp/shibboleth">
         SAML2
      </SSO>
      <!-- ... other things ... -->
      <MetadataProvider type="XML" validate="true"
                        url="https://idp.example.org/idp/shibboleth"
                        backingFilePath="idp-metadata.xml" maxRefreshDelay="7200" />
      ```

      ( *Replace `entityID` with the IdP entityID and `url` with an URL where it can be downloaded its metadata* )

      (`idp-metadata.xml` will be saved into `/var/cache/shibboleth`)

02. Restart `shibd` and `Apache2` daemon:

    - `sudo systemctl restart shibd`
    - `sudo systemctl restart apache2`

03. Jump to [Test](#test)

## Test

Open the `https://sp.example.org/secure` application into your web browser

(*Replace `sp.example.org` with your SP Full Qualified Domain Name*)

## Enable Attribute Checker Support on Shibboleth SP

01. Add a sessionHook for attribute checker: `sessionHook="/Shibboleth.sso/AttrChecker"` and the `metadataAttributePrefix="Meta-"` to `ApplicationDefaults`:

    - `vim /etc/shibboleth/shibboleth2.xml`

      ```bash
      <ApplicationDefaults entityID="https://sp.example.org/shibboleth"
                           REMOTE_USER="eppn subject-id pairwise-id persistent-id"
                           cipherSuites="DEFAULT:!EXP:!LOW:!aNULL:!eNULL:!DES:!IDEA:!SEED:!RC4:!3DES:!kRSA:!SSLv2:!SSLv3:!TLSv1:!TLSv1.1"
                           sessionHook="/Shibboleth.sso/AttrChecker"
                           metadataAttributePrefix="Meta-" >
      ```

02. Add the attribute checker handler with the list of required attributes to Sessions (in the example below: `displayName`, `givenName`, `mail`, `cn`, `sn`, `eppn`, `schacHomeOrganization`, `schacHomeOrganizationType`). The attributes' names HAVE TO MATCH with those are defined on `attribute-map.xml`:

    - `vim /etc/shibboleth/shibboleth2.xml`

      ```bash
         ...
         <!-- Attribute Checker -->
         <Handler type="AttributeChecker" 
                  Location="/AttrChecker" 
                  template="attrChecker.html" 
                  attributes="displayName givenName mail cn sn eppn schacHomeOrganization schacHomeOrganizationType" 
                  flushSession="true"/>
      </Sessions>
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

03. Add the following `<AttributeExtractor>` element under `<AttributeExtractor type="XML" validate="true" reloadChanges="false" path="attribute-map.xml"/>`:

    - `vim /etc/shibboleth/shibboleth2.xml`

      ```bash
      <!-- Extracts support information for IdP from its metadata. -->
      <AttributeExtractor type="Metadata" 
                          errorURL="errorURL" 
                          DisplayName="displayName"
                          InformationURL="informationURL"  
                          PrivacyStatementURL="privacyStatementURL"
                          OrganizationURL="organizationURL">
        <ContactPerson id="Technical-Contact"  contactType="technical" formatter="$EmailAddress" />
        <Logo id="Small-Logo" height="16" width="16" formatter="$_string"/>
      </AttributeExtractor>
      ```

04. Save and restart "shibd" service:

    - `systemctl restart shibd.service`

05. Customize Attribute Checker template:

    - `cd /etc/shibboleth`
    - `cp attrChecker.html attrChecker.html.orig`
    - `wget https://raw.githubusercontent.com/CSCfi/shibboleth-attrchecker/master/attrChecker.html -O attrChecker.html`
    - `sed -i 's/SHIB_//g' /etc/shibboleth/attrChecker.html`
    - `sed -i 's/eduPersonPrincipalName/eppn/g' /etc/shibboleth/attrChecker.html`
    - `sed -i 's/Meta-Support-Contact/Meta-Technical-Contact/g' /etc/shibboleth/attrChecker.html`
    - `sed -i 's/supportContact/technicalContact/g' /etc/shibboleth/attrChecker.html`
    - `sed -i 's/support/technical/g' /etc/shibboleth/attrChecker.html`

    There are three locations needing modifications to do on `attrChecker.html`:

    01. The pixel tracking link after the comment "PixelTracking".
        The Image tag and all required attributes after the variable must be configured here.
        After "`miss=`" define all required attributes you updated in `shibboleth2.xml` using shibboleth tagging.

        Eg `<shibmlpifnot $attribute>-$attribute</shibmlpifnot>` (this echoes `$attribute` if it's not received by shibboleth).
        The attributes' names HAVE TO MATCH with those are defined on `attribute-map.xml`.

        This example uses `-` as a delimiter.

    02. The table showing missing attributes between the tags `<!--TableStart-->` and `<!--TableEnd-->`.
        You have to insert again all the same attributes as above.

        Define row for each required attribute (eg: `displayName` below)

        ```html
        <tr <shibmlpifnot displayName> class='warning text-danger'</shibmlpifnot>>
          <td>displayName</td>
          <td><shibmlp displayName /></td>
        </tr>
        ```

    03. The email template between the tags `<textarea>` and `</textarea>` after "*The attributes that were not released to the service are*:".

        Again define all required attributes using shibboleth tagging like in section 1 ( eg: `<shibmlpifnot $attribute> * $attribute</shibmlpifnot>`).
        The attributes' names HAVE TO MATCH with those are defined on `attribute-map.xml`.
        Note that for SP identifier target URL is used instead of entityID.
        There aren't yet any tag for SP entityID so you can replace this target URL manually.

06. Enable Logging:

    - Create your `track.png` with into your DocumentRoot:

      ```bash
      echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" | base64 -d > /var/www/html/$(hostname -f)/track.png
      ```

    - Results into `/var/log/apache2/other_vhosts_access.log`:

      ```bash
      ./apache2/other_vhosts_access.log:193.206.129.66 - - [20/Sep/2018:15:05:07 +0000] "GET /track.png?idp=https://garr-idp-test.irccs.garr.it/idp/shibboleth&miss=-SHIB_givenName-SHIB_cn-SHIB_sn-SHIB_eppn-SHIB_schacHomeOrganization-SHIB_schacHomeOrganizationType HTTP/1.1" 404 637 "https://sp.example.org/Shibboleth.sso/AttrChecker?return=https%3A%2F%2Fsp.example.org%2FShibboleth.sso%2FSAML2%2FPOST%3Fhook%3D1%26target%3Dss%253Amem%253A43af2031f33c3f4b1d61019471537e5bc3fde8431992247b3b6fd93a14e9802d&target=https%3A%2F%2Fsp.example.org%2Fsecure%2F"
      ```

## Increase startup timeout

Shibboleth Documentation: <https://wiki.shibboleth.net/confluence/display/SP3/LinuxSystemd>

```bash
sudo mkdir /etc/systemd/system/shibd.service.d

echo -e '[Service]\nTimeoutStartSec=60min' | sudo tee /etc/systemd/system/shibd.service.d/timeout.conf

sudo systemctl daemon-reload

sudo systemctl restart shibd.service
```

## OPTIONAL - Maintain '```shibd```' working

01. Edit '`shibd`' init script:

    - `vim /etc/init.d/shibd`

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

02. Create a new watchdog for '`shibd`':

    - `vim /etc/cron.hourly/watch-shibd.sh`

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

03. Reload daemon:

    - `systemctl daemon-reload`

## Utility

- [The Mozilla Observatory](https://observatory.mozilla.org/):
  The Mozilla Observatory has helped over 240,000 websites by teaching developers, system administrators, and security professionals how to configure their sites safely and securely.

## Authors

### Original Author

- Marco Malavolti (<marco.malavolti@garr.it>)

## Thanks

- eduGAIN Wiki: For the original [How to configure Shibboleth SP attribute checker](https://wiki.geant.org/display/eduGAIN/How+to+configure+Shibboleth+SP+attribute+checker)
