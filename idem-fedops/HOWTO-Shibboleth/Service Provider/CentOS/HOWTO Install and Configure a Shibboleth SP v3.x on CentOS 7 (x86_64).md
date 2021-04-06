# HOWTO Install and Configure a Shibboleth SP v3.x on CentOS 7 (x86_64)

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements-hardware)
   1. [Hardware](#hardware)
   2. [Other](#other)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Notes](#notes)
4. [Installation Instructions](#installation-instructions)
   1. [Install software requirements](#install-software-requirements)
   2. [Install Apache2 Web Server](#install-apache2-web-server)
   3. [Install Shibboleth Service Provider](#install-shibboleth-service-provider)
5. [Configuration Instructions](#configuration-instructions)
   1. [Configure the environment](#configure-the-environment)
   2. [Configure SSL on Apache2](#configure-ssl-on-apache2)
   3. [Configure Shibboleth SP](#configure-shibboleth-sp)
   4. [Configure an example federated resource "secure"](#configure-an-example-federated-resource-secure)
   5. [Enable attributes on attribute mapping](#enable-attributes-on-attribute-mapping)
   6. [Connect SP directly to an IdP](#connect-sp-directly-to-an-idp)
   7. [Connect SP to the Federation](#connect-sp-to-the-federation)
6. [Test](#test)
7. [Appendix A - SE Linux](#appendix-a---se-linux)
8. [Appendix B - Enable Attribute Checker Support on Shibboleth SP](#appendix-b---enable-attribute-checker-support-on-shibboleth-sp)
9. [Authors](#authors)


## Requirements

### Hardware

 * CPU: 2 Core
 * RAM: 4 GB
 * HDD: 20 GB

### Other

 * SSL Credentials: HTTPS Certificate & Key & Certification Authority (CA)
 * Logo:
   * size: 80x60 px (or other that respect the aspect-ratio)
   * format: PNG

## Software that will be installed

 * ca-certificates
 * ntp
 * vim
 * httpd.x86_64 (Apache >= 2.4)
 * php
 * openssl
 * shibboleth.x86_64

## Notes

This HOWTO use `example.org` to provide this guide with example values.

Please, remember to **replace all occurence** of `example.org` domain name, or part of it, with the SP domain name into the configuration files.

## Installation Instructions

### Install software requirements

1. Become ROOT:
   * `sudo su -`
  
2. Install the packages required: 
   * `yum install ca-certificates vim openssl`

### Install Apache2 Web Server
1. Become ROOT: 
   * `sudo su -`

2. Create the Shibboleth Repository:
   * `yum install httpd.x86_64`

3. Deactivate the `welcome` sites:
   * `mv /etc/httpd/conf.d/welcome.conf /etc/httpd/conf.d/welcome.conf.deactivated`
   
4. Prevent Apache from listing web directory files to visitors:
   * `sed -i "s/Options Indexes FollowSymLinks/Options FollowSymLinks/" /etc/httpd/conf/httpd.conf`
   
5. Start the Apache service and enable it to auto-start on boot:
   * `systemctl start httpd.service`
   * `systemctl enable httpd.service`

### Install Shibboleth Service Provider

1. Become ROOT: 
   * `sudo su -`

2. Create the Shibboleth Repository:
   * `vim /etc/yum.repos.d/shibboleth.repo`
   
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

   * Save changes by clicking on the `Esc` button and by digiting `:wq`

3. Update the repositories with:

   * `yum update -y`

4. Discover what architecture do you have with:

   * ```echo "I am running: $(cat /etc/redhat-release) ($(arch))"```
   
5. Install Shibboleth Service Provider:

   * `yum install shibboleth.x86_64 -y`

   From this point the location of the SP directory will be: `/etc/shibboleth`

## Configuration Instructions

### Configure the environment

1. Become ROOT: 
   * `sudo su -`

2. Modify your `/etc/hosts`:
   * `vim /etc/hosts`
  
     ```bash
     VV.ZZ.XX.YY sp.example.org sp
     ```
     (*Replace `VV.ZZ.XX.YY` with your SP's public IP*)
   
     (*Replace `sp.example.org` with your SP Full Qualified Domain Name*)
   
     (*Replace `sp` with your SP Hostname*)

3. Be sure that your firewall **doesn't block** the traffic on port **443** (or you can't access to your SP)

### Configure SSL on Apache2

> According to [NSA and NIST](https://www.keylength.com/en/compare/), RSA with 3072 bit-modulus is the minimum to protect up to TOP SECRET over than 2030.

1. Become ROOT: 
   * `sudo su -`

2. Load SSL credentials in the right place:
   * HTTPS Server Certificate (Public Key) inside `/etc/pki/tls/certs/$(hostname -f).crt`
   * HTTPS Server Key (Private Key) inside `/etc/pki/tls/private/$(hostname -f).key`	
   * Add CA Cert into `/etc/pki/tls/certs`
     * If you use GARR TCS (Sectigo CA): 
       ```bash
       wget -O /etc/pki/tls/certs/GEANT_OV_RSA_CA_4.pem https://crt.sh/?d=2475254782
 
       wget -O /etc/pki/tls/certs/SectigoRSAOrganizationValidationSecureServerCA.crt https://crt.sh/?d=924467857

       cat /etc/pki/tls/certs/SectigoRSAOrganizationValidationSecureServerCA.crt >> /etc/pki/tls/certs/GEANT_OV_RSA_CA_4.pem

       rm /etc/pki/tls/certs/SectigoRSAOrganizationValidationSecureServerCA.crt
       ```
       
     * If you use ACME (Let's Encrypt): 
       * `ln -s /etc/letsencrypt/live/<SERVER_FQDN>/chain.pem /etc/pki/tls/certs/ACME-CA.pem`
 
     (OPTIONAL) Create a Certificate and a Key self-signed for HTTPS if you don't have yet the official ones provided by the Certificate Authority:
     * ```bash
       openssl req -x509 -newkey rsa:3072 -keyout /etc/pki/tls/private/$(hostname -f).key -out /etc/pki/tls/certs/$(hostname -f).crt -nodes -days 1095
       ```

3. Install "mod_ssl" to enable HTTPS configuration:
   * `yum install mod_ssl -y`

4. Create the DocumentRoot:
   * `mkdir /var/www/html/$(hostname -f)`
   * `sudo chown -R apache: /var/www/html/$(hostname -f)`
   * `echo '<h1>It Works!</h1>' > /var/www/html/$(hostname -f)/index.html`

5. Create the Virtualhost file (pay attention and follow the starting comment):
   * ```bash
     wget https://registry.idem.garr.it/idem-conf/shibboleth/SP3/apache2/sp.example.org.conf -O /etc/httpd/conf.d/000-$(hostname -f).conf
     ```

6. Reload Apache2 web server:
   * `systemctl restart httpd.service`

7. Configure Apache2 to open port **80** only for localhost:
   * `vim /etc/httpd/conf/httpd.conf`

     ```apache
     ...
     # Listen 12.34.56.78:80
     Listen 127.0.0.1:80
     ```

8. Deactivate the `000-default` site:
   * `mv /etc/httpd/conf.d/000-default.conf /etc/httpd/conf.d/000-default.conf.deactivated`

9. Restart Apache to apply changes
   * `systemctl restart httpd.service`
  
10. Verify the strength of your server on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

### Configure Shibboleth SP

1. Become ROOT: 
   * `sudo su -`

2. Change the SP entityID and technical contact email address:
   * `sed -i "s/sp.example.org/$(hostname -f)/" shibboleth2.xml`
   * `sed -i "s/root@localhost/<TECH-CONTACT-EMAIL-ADDRESS-HERE>/" shibboleth2.xml`

3. Create SP metadata Signing and Encryption credentials:
   * `cd /etc/shibboleth`  
   * `./keygen.sh -u shibd -g shibd -h $(hostname -f) -y 30 -e https://$(hostname -f)/shibboleth -n sp-signing -f`
   * `./keygen.sh -u shibd -g shibd -h $(hostname -f) -y 30 -e https://$(hostname -f)/shibboleth -n sp-encrypt -f`
   * `LD_LIBRARY_PATH=/opt/shibboleth/lib64 /usr/sbin/shibd -t`
   * `systemctl restart shibd.service`
   * `systemctl restart httpd.service`

4. Now you are able to reach your Shibboleth SP Metadata on:
   * `https://sp.example.org/Shibboleth.sso/Metadata`

   (*Replace `sp.example.org` with your SP Full Qualified Domain Name*)

### Configure an example federated resource "secure"

1. Check that the Apache configuration has the "secure" Location configured:
   * `vim /etc/httpd/conf.d/shib.conf`
  
     ```bash
     ...
     <Location /secure>
       AuthType shibboleth
       ShibRequestSetting requireSession 1
       require shib-session
     </Location>
     ```

2. Create the "`secure`" application into the DocumentRoot:
   * `mkdir /var/www/html/$(hostname -f)/secure`

   * ```bash
     wget https://registry.idem.garr.it/idem-conf/shibboleth/SP3/secure/index.php.txt -O /var/www/html/$(hostname -f)/secure/index.php
     ```

3. Install PHP 7.x:
   1. Enable Remi and EPEL yum repositories on your system:
      * `yum install epel-release`
      * `rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-7.rpm`

   2. Install PHP 7.x:
      * 7.1: `yum --enablerepo=remi-php71 install php`
      * 7.2: `yum --enablerepo=remi-php72 install php`
   
   3. Verify:
      * `php -v`

4. Restart `httpd` daemon to enable PHP:
      * `systemctl restart httpd.service`

### Enable attributes on attribute mapping

Enable attribute support by removing comment from the related content into "`/etc/shibboleth/attribute-map.xml`"

### Connect SP directly to an IdP

> Follow these steps if your organization **IS NOT** connected to the [GARR Network](https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites?key=all) or **IF** you need to connect your SP with only one IdP

1. Edit `shibboleth2.xml` opportunely:
   * `vim /etc/shibboleth/shibboleth2.xml`

     ```bash

     <!-- If it is needed to manage the authentication on several IdPs
          install and configure the Shibboleth Embedded Discovery Service
          by following this HOWTO: https://url.garrlab.it/nakt7 
     -->
     <SSO entityID="https://idp.example.org/idp/shibboleth">
        SAML2
     </SSO>

     <MetadataProvider type="XML" validate="true"
                       url="https://idp.example.org/idp/shibboleth"
                       backingFilePath="idp-metadata.xml" maxRefreshDelay="7200" />
     ```
 
     (*Replace `entityID` with the IdP entityID and `url` with an URL where it can be downloaded its metadata*)
     
     (`idp-metadata.xml` will be saved into `/var/cache/shibboleth`)
 
 2. Restart `shibd` and `httpd` daemon:
    * `sudo systemctl restart shibd`
    * `sudo systemctl restart httpd`

### Connect SP to the Federation

> Follow these steps **IF AND ONLY IF** your organization is connected to the [GARR Network](https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites?key=all)

1. Retrieve the IDEM GARR Federation Certificate needed to verify the signed metadata:
   * `cd /etc/shibboleth/`
   * `curl https://md.idem.garr.it/certs/idem-signer-20220121.pem -o federation-cert.pem`
   * Check the validity:
     *  `cd /etc/shibboleth`
     *  `openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout`
       
         (sha1: D1:68:6C:32:A4:E3:D4:FE:47:17:58:E7:15:FC:77:A8:44:D8:40:4D)
     *  `openssl x509 -in federation-cert.pem -fingerprint -md5 -noout`

         (md5: 48:3B:EE:27:0C:88:5D:A3:E7:0B:7C:74:9D:24:24:E0)

2. Edit `shibboleth2.xml` opportunely:
   * `vim /etc/shibboleth/shibboleth2.xml`

     ```bash

     <!-- If it is needed to manage the authentication on several IdPs
          install and configure the Shibboleth Embedded Discovery Service
          by following this HOWTO: https://url.garrlab.it/nakt7s 
     -->
     <SSO discoveryProtocol="SAMLDS" discoveryURL="https://wayf.idem-test.garr.it/WAYF">
        SAML2
     </SSO>

     <MetadataProvider type="XML" url="http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml"
                       backingFilePath="idem-test-metadata-sha256.xml" maxRefreshDelay="7200">
           <MetadataFilter type="Signature" certificate="federation-cert.pem"/>
           <MetadataFilter type="RequireValidUntil" maxValidityInterval="864000" />
     </MetadataProvider>
     ```

3. Register you SP on IDEM Entity Registry:
   (your entity has to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
   * Go to `https://registry.idem.garr.it` and follow "Insert a New Service Provider into the IDEM Test Federation"

## Test

Open the `https://sp.example.org/secure` application into your web browser

(*Replace `sp.example.org` with your SP Full Qualified Domain Name*)

## Appendix A - SE Linux

If you'll met problem, probably they are related to SE Linux.

If you want to disable it until the next server reboot, doing this:

* `sudo setenforce 0`

If you want to disable it forever do this:

* `sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config ; setenforce permissive`

The SE Linux is disabled if you will find `Current mode: permissive` from the command `sestatus`.

## Appendix B - Enable Attribute Checker Support on Shibboleth SP

1. Add a sessionHook for attribute checker: `sessionHook="/Shibboleth.sso/AttrChecker"` and the `metadataAttributePrefix="Meta-"` to `ApplicationDefaults`:
   * `vim /etc/shibboleth/shibboleth2.xml`

     ```bash
     <ApplicationDefaults entityID="https://sp.example.org/shibboleth"
                          REMOTE_USER="eppn subject-id pairwise-id persistent-id"
                          cipherSuites="DEFAULT:!EXP:!LOW:!aNULL:!eNULL:!DES:!IDEA:!SEED:!RC4:!3DES:!kRSA:!SSLv2:!SSLv3:!TLSv1:!TLSv1.1"
                          sessionHook="/Shibboleth.sso/AttrChecker"
                          metadataAttributePrefix="Meta-">
     ```
     
     (*Replace `sp.example.org` with your SP Full Qualified Domain Name*)

2. Add the attribute checker handler with the list of required attributes to Sessions (in the example below: `displayName`, `givenName`, `mail`, `cn`, `sn`, `eppn`, `schacHomeOrganization`, `schacHomeOrganizationType`). The attributes' names HAVE TO MATCH with those are defined on `attribute-map.xml`:
   * `vim /etc/shibboleth/shibboleth2.xml`

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
   * `vim /etc/shibboleth/shibboleth2.xml`

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
   * `systemctl restart shibd.service`
   
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
   * Create your `track.png` with into your DocumentRoot:
   
     ```bash
     echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" | base64 -d > /var/www/html/track.png
     ```

   * Example result into `/var/log/httpd/access.log`:
     ```bash
     ./httpd/access.log:193.206.129.66 - - [20/Sep/2018:15:05:07 +0000] "GET /track.png?idp=https://garr-idp-test.irccs.garr.it/idp/shibboleth&miss=-SHIB_givenName-SHIB_cn-SHIB_sn-SHIB_eppn-SHIB_schacHomeOrganization-SHIB_schacHomeOrganizationType HTTP/1.1" 404 637 "https://sp.example.org/Shibboleth.sso/AttrChecker?return=https%3A%2F%2Fsp.example.org%2FShibboleth.sso%2FSAML2%2FPOST%3Fhook%3D1%26target%3Dss%253Amem%253A43af2031f33c3f4b1d61019471537e5bc3fde8431992247b3b6fd93a14e9802d&target=https%3A%2F%2Fsp.example.org%2Fsecure%2F"
     ```

Thanks eduGAIN for the original "HOWTO" posted [here](https://wiki.geant.org/display/eduGAIN/How+to+configure+Shibboleth+SP+attribute+checker).


## Authors

### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
 * Barbara Monticini (barbara.monticini@garr.it)
