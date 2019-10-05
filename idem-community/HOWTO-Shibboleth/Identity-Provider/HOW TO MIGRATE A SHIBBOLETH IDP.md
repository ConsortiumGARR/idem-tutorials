# HOW TO MIGRATE A SHIBBOLETH IDP

1. [Introduction](#introduction)
2. [Installation of the necessary software](#installation-of-the-necessary-software)
3. [Migration of the production IdP configuration](#migration-of-the-production-idp-configuration)
4. [Test](#test)
5. [Additional tasks](#additional-tasks)
6. [Authors](#authors)
7. [Credits](#credits)

## Introduction

This guide helps us with:

- Installation of a new Shibboleth IdP (local instance) on a GNU/Linux host;
- Migration of an existing Shibboleth IdP's configuration to the local one;
- Testing of the local IdP as it would be the production one, using the federation's Service Providers. 

This asset could be tested only with **HTTP-REDIRECT and HTTP-POST Saml bindinds**, this can be made fixing the fqdn's ip address of your local IdP as if it were the production one, with the help of ``/etc/hosts`` file.

Why should we migrate an Identity Provider? Here the most common use cases:

- duplicate it in a local environment for test purposes;
- upgrade Shibboleth IdP to another version and test it before going in production;
- customize the template, changing the general configuration, anything else in safe stage.

## Installation of the necessary software

You should have a production ShibIdP and a newer installation of another one where to migrate the production configuration.
You can install a new Shibboleth IdP with the help of the following resources:
- [GARR Idem tutorials](https://github.com/ConsortiumGARR/idem-tutorials)
- **Ansible playbooks**:
    - [IDEM playbook](https://github.com/ConsortiumGARR/ansible-shibboleth)
    - [Unical playbook](https://github.com/peppelinux/Ansible-Shibboleth-IDP-SP-Debian)

## Migration of the production IdP configuration

Remember to use a diff tool to do an appropriate file comparison between local and production configuration files, this should be always done to deal with configuration changements that can be made between different versions. It would be better to have a graphical directory tree diff tool, like [meld](http://meldmerge.org/).

1. copy all certificates in ``{idp_home}/credentials`` from production folder;

2. ``{idp_home}/conf``:
    - ``attribute-filter.xml``: include your Service Provider's ``AttributeFilterPolicy``;
    - compare and integrate ``attribute-resolver.xml`` from production folder;
    - ``metadata-providers.xml``: include your Service Provider's ``MetadataProvider``;
    - check ``relying-party.xml`` for any further declarations about SP entities;
    - compare ``idp.properties`` and integrate from production folder;
    - copy ``saml-nameid.properties`` from production folder;
    - change all files permissions: ``{idp_home}/conf -type f -exec chmod 644 {} +``

The followings should be done only if you want or have to deal with the same production datasources, otherwise you can even use a test instance of LDAP or MySQL. Remeber that if you have a persisten nameId storage, you should also migrate the MySQL (or the configured engine for that) into your MySQL test server:
    - copy ``global.xml`` from production folder (datasource configuration);
    - copy ``ldap.properties`` from production folder (check TLS Authority Certificates to avoid connection errors);

3. ``{idp_home}/metadata``:
    - copy ``idp-medatada.xml`` from production folder;
    - copy ``{sp_name_metadata}.xml`` for each SP from production folder;
    
4. copy ``{idp_home}/dist/conf/services.xml`` and ``{idp_home}/messages`` from production folders to reuse your production messages.

## Test

Once ``attribute-filter.xml`` and ``metadata-providers.xml`` have been migrated, put the production fqdn in `/etc/hosts` pointing to your local ip. This would be `127.0.0.1` if your test IdP is running on localhost.

Now connect to any of the federation Service Providers to test the new asset.

## Additional tasks

Customize the Shibboleth IdP template:
- https://github.com/UniversitaDellaCalabria/design-unical-shibboleth-idp-theme

## Authors

 * Giuseppe De Marco - Università della Calabria (giuseppe.demarco@unical.it)
 * Francesco Filicetti - Università della Calabria (francesco.filicetti@unical.it)

## Credits

* https://shibboleth.net/
