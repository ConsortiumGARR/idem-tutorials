# HOW TO MIGRATE A SHIBBOLETH IDP

#### Authors: Giuseppe De Marco / Francesco Filicetti - Università della Calabria

## TABLE OF CONTENTS

1. [INTRODUCTION](#introduction)
2. [INSTALLATION OF THE NECESSARY SOFTWARE](#installation-of-the-necessary-software)
3. [HOT WO MIGRATE](#how-to-migrate)
4. [AUTHORS](#authors)
5. [CREDITS](#credits)


## INTRODUCTION

This guide helps us to migrate a Shibboleth IdP and test it as it would come from a production environment, through the federation's Service Providers.  
This means that tests can be made only with HTTP-REDIRECT and HTTP-POST, managing your local ``/etcs/hosts`` file.

Why should we migrate an Identity Provider? Here the most common use cases:

- duplicate it in a local environment for test purposes;
- upgrade Shibboleth IdP to another version and test it before going in production;
- customize the template or the general configuration to find out potential problems with SP.

## INSTALLATION OF THE NECESSARY SOFTWARE

On your local machine you can bootstrap a full working environment to run a Shibboleth IdP.

Use one of these **Ansible playbooks** to setup it:

- IDEM playbook (thans to Marco Malavolti)
- https://github.com/peppelinux/Ansible-Shibboleth-IDP-SP-Debian (thanks to Giuseppe De Marco)

Follow instructions to make all software work.

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
