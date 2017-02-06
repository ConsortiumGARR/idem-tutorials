# HOWTO Install and Configure a Shibboleth Embedded Discovery Service

The Embedded Discovery Service (EDS) allows a Service Provider to run a discovery service within their own site. As such the discovery service can look like any other page on the site and thus not be as jarring to a user as being redirected to a totally different, third-party, discovery service site.
The EDS is a set of Javascript and CSS files, so installing it and using it is straight forward and does not require any additional software. Note: you must already have an installed and configured Shibboleth Service Provider, V2.4+, in order to use the EDS.

## Index

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Whitelist - How to allow IdPs to access the federated resource](#whitelist---how-to-allow-idps-to-access-the-federated-resource)
  1. [How to allow the access to IdPs by specifying their entityID](#how-to-allow-the-access-to-idps-by-specifying-their-entityid)
  2. [How to allow the access to IdPs that support a specific Entity Category](#how-to-allow-the-access-to-idps-that-support-a-specific-entity-category)
  3. [How to allow the access to IdPs that support SIRTFI](#how-to-allow-the-access-to-idps-that-support-sirtfy)
5. [Blacklist - How to disallow IdPs to access the federated resource](#blacklist---how-to-disallow-idps-to-access-the-federated resource)
  1. [How to disallow the access to IdPs by specifying their entityID](#how-to-disallow-the-access-to-idps-by-specifying-their-entityid)
  2. [How to disallow the access to IdPs that support a specific Entity Category](#how-to-disallow-the-access-to-idps-that-support-a-specific-entity-category)
6. [Best Practices to follow to maximize the access to the resource](#best-practices-to-follow-to-maximize-the-access-to-the-resource)
7. [Authors](#authors)
8. [Credits](#credits)

## Requirements
* A working Shibboleth Service Provider (>= 2.4)

## Installation
1. `sudo su -`
2. `cd /usr/local/src`
3. `wget https://shibboleth.net/downloads/embedded-discovery-service/1.2.0/shibboleth-embedded-ds-1.2.0.tar.gz`
4. `tar xzf shibboleth-embedded-ds-1.2.0.tar.gz`
5. `cd shibboleth-embedded-ds-1.2.0`
6. `make install`
7. Enable Discovery Service Web Page
  * `cp shibboleth-ds.conf /etc/apache2/sites-available/shibboleth-ds.conf`
     (make sure that "`Allow from all`" becomes "`Require all granted`" if you have Apache >= 2.4)
8. Update "`shibboleth2.xml`" file to the new Discovery Service page:
  * `vim /etc/shibboleth/shibboleth2.xml`
 
    ```xml
    <SSO discoveryProtocol="SAMLDS" 
         discoveryURL="https://###YOUR.SP.FQDN###/shibboleth-ds/index.html"
         isDefault="true">
       SAML2
    </SSO>
    <!-- SAML and local-only logout. -->
    <Logout>SAML2 Local</Logout>
    ...
    <!-- JSON feed of discovery information. -->
    <Handler type="DiscoveryFeed" Location="/DiscoFeed"/>
    ```
9. Enable the Discovery Service Page:
  * `a2ensite shibboleth-ds.conf`
10. Restart Apache to load the new web site:
   * `service shibd restart ; service apache2 restart`

## Configuration
The behaviour of Shibboleth Embedded Discovery Service is controlled by `IdPSelectUIParms` class contained. `idpselect_config.js`.
In the most of cases you have to modify only this file to change the behaviour of Discovery Service.
Find here the EDS Configuration Options: https://wiki.shibboleth.net/confluence/display/EDS10/3.+Configuration

## Whitelist - How to allow IdPs to access the federated resource
### How to allow the access to IdPs by specifying their entityID
1. Modify "**shibboleth2.xml**":
  * `vim /etc/shibboleth/shibboleth2.xml`

    ```xml
    <MetadataProvider type="XML"
                      uri="http://www.garr.it/idem-metadata/idem-metadata-sha256.xml"
                      backingFilePath="idem-metadata-sha256.xml">
       <MetadataFilter type="Signature" certificate="/etc/shibboleth/idem_signer_2019.pem"/>
       <MetadataFilter type="Whitelist">
           <Include>https://entityid.idp1.permesso.it/shibboleth</Include>
           <Include>https://entityid.idp2.permesso.it/shibboleth</Include>
           <Include>https://entityid.idp3.permesso.it/shibboleth</Include>
       </MetadataFilter>
    </MetadataProvider>
    ```
2. Restart "**shibd**" service:
  * `service shibd restart`

### How to allow the access to IdPs that support a specific Entity Category
1. Modify "**shibboleth2.xml**":
  * `vim /etc/shibboleth/shibboleth2.xml`
   
    ```xml
    <MetadataProvider type="XML"
                      uri="http://www.garr.it/idem-metadata/idem-metadata-sha256.xml"
                      backingFilePath="idem-metadata-sha256.xml">
       <MetadataFilter type="Signature" certificate="/etc/shibboleth/idem_signer_2019.pem"/>
       <MetadataFilter type="Whitelist" matcher="EntityAttributes">
           <saml:Attribute Name="http://macedir.org/entity-category"
                           NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
               <saml:AttributeValue>http://refeds.org/category/research-and-scholarship</saml:AttributeValue>
           </saml:Attribute>
       </MetadataFilter>
    </MetadataProvider>
    ```
2. Restart "**shibd**" service:
  * `service shibd restart`

### How to allow the access to IdPs that support SIRTFI
1. Modify "**shibboleth2.xml**":
  * `vim /etc/shibboleth/shibboleth2.xml`
  
    ```xml
    <MetadataProvider type="XML"
                      uri="http://www.garr.it/idem-metadata/idem-metadata-sha256.xml"
                      backingFilePath="idem-metadata-sha256.xml">
       <MetadataFilter type="Signature" certificate="/etc/shibboleth/idem_signer_2019.pem"/>
       <MetadataFilter type="Whitelist" matcher="EntityAttributes">
           <saml:Attribute Name="urn:oasis:names:tc:SAML:attribute:assurancecertification"
                           NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
               <saml:AttributeValue>https://refeds.org/sirtfi</saml:AttributeValue>
           </saml:Attribute>
       </MetadataFilter>
    </MetadataProvider>
    ```
2. Restart "**shibd**" service:
  * `service shibd restart`

## Blacklist - How to disallow IdPs to access the federated resource
### How to disallow the access to IdPs by specifying their entityID
1. Modify "**shibboleth2.xml**":
  * `vim /etc/shibboleth/shibboleth2.xml`
  
    ```xml
    <MetadataProvider type="XML"
                      uri="http://www.garr.it/idem-metadata/idem-metadata-sha256.xml"
                      backingFilePath="idem-metadata-sha256.xml">
       <MetadataFilter type="Signature" certificate="/etc/shibboleth/idem_signer_2019.pem"/>
       <MetadataFilter type="Blacklist">
           <Include>https://entityid.idp1.permesso.it/shibboleth</Include>
           <Include>https://entityid.idp2.permesso.it/shibboleth</Include>
           <Include>https://entityid.idp3.permesso.it/shibboleth</Include>
       </MetadataFilter>
    </MetadataProvider>
    ```
2. Restart "**shibd**" service:
  * `service shibd restart`

### How to disallow the access to IdPs that support a specific Entity Category
1. Modify "**shibboleth2.xml**":
  * `vim /etc/shibboleth/shibboleth2.xml`

    ```xml
    <MetadataProvider type="XML"
                      uri="http://www.garr.it/idem-metadata/idem-metadata-sha256.xml"
                      backingFilePath="idem-metadata-sha256.xml">
       <MetadataFilter type="Signature" certificate="/etc/shibboleth/idem_signer_2019.pem"/>
       <MetadataFilter type="Blacklist" matcher="EntityAttributes">
           <saml:Attribute Name="http://macedir.org/entity-category"
                           NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
               <saml:AttributeValue>https://federation.renater.fr/scope/commercial</saml:AttributeValue>
           </saml:Attribute>
       </MetadataFilter>
    </MetadataProvider>
    ```
2. Restart "**shibd**" service:
  * `service shibd restart`

## Best Practices to follow to maximize the access to the resource
* [REFEDS Discovery Guide](https://discovery.refeds.org/)

## Authors
### Original Author
 * Marco Malavolti (marco.malavolti@garr.it)
 
## Credits
* [Consortium Shibboleth](https://shibboleth.net/)
* [REFEDS Discovery Guide](https://discovery.refeds.org/)

