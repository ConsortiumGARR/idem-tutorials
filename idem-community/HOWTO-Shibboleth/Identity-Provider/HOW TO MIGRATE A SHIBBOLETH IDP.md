# HOW TO MIGRATE A SHIBBOLETH IDP

1. [INTRODUCTION](#introduction)
2. [INSTALLATION OF THE NECESSARY SOFTWARE](#installation-of-the-necessary-software)
3. [HOT WO MIGRATE](#how-to-migrate)
4. [AUTHORS](#authors)
5. [CREDITS](#credits)


## INTRODUCTION

This guide helps us with:

- Installation of a new Shibboleth IdP (local instance) on a GNU/Linux host;
- Migration of an existing Shibboleth IdP's configuration to the local one;
- Testing of the local IdP as it would be the production one, using the federation's Service Providers. 

This asset could be tested only with HTTP-REDIRECT and HTTP-POST Saml bindinds, this can be made fixing the fqdn's ip address of your local IdP as it would be the production one, with the help of ``/etc/hosts`` file.

Why should we migrate an Identity Provider? Here the most common use cases:

- duplicate it in a local environment for test purposes;
- upgrade Shibboleth IdP to another version and test it before going in production;
- customize the template, changing the general configuration, anything else in safe stage.

## INSTALLATION OF THE NECESSARY SOFTWARE

You should have a production ShibIdP and a newer installation of another one where to migrate the production configuration.
You can install a new Shibboleth IdP with the help of the following resources:
- [GARR Idem tutorials](https://github.com/ConsortiumGARR/idem-tutorials)
- **Ansible playbooks**:
    - IDEM playbook (thans to Marco Malavolti)
    - https://github.com/peppelinux/Ansible-Shibboleth-IDP-SP-Debian

## HOW TO MIGRATE

Our purpose is to make a working replica of our Shibboleth IdP.

After running the playbook, we have a clean instance running.

Follow these steps:

1. copy all certificates in ``{idp_home}/credentials`` from production folder;

2. in ``{idp_home}/conf``:
    - ``attribute-filter.xml``: include your Service Provider's ``AttributeFilterPolicy``;
    - compare and integrate ``attribute-resolver.xml`` from production folder;
    - ``metadata-providers.xml``: include your Service Provider's ``MetadataProvider``;
    - copy ``global.xml`` from production folder (datasource configuration);
    - compare ``idp.properties`` and integrate from production folder;
    - copy ``ldap.properties`` from production folder;
    - copy ``saml-nameid.properties`` from production folder;
    - change all files permissions: ``{idp_home}/conf -type f -exec chmod 644 {} +``

3. in ``{idp_home}/metadata``:
    - copy ``idp-medatada.xml`` from production folder;
    - copy ``{sp_name_metadata}.xml`` for each SP from production folder;
    
4. copy ``{idp_home}/dist/conf/services.xml`` and ``{idp_home}/messages`` from production folders to reuse your production messages.

Important note: we have to set LDAP configuration files (certificates and auth informations).

## AUTHORS

 * Giuseppe De Marco - Università della Calabria (giuseppe.demarco@unical.it)
 * Francesco Filicetti - Università della Calabria (francesco.filicetti@unical.it)

## CREDITS

* https://shibboleth.net/
