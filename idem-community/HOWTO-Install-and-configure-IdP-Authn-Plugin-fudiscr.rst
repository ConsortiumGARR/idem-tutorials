HOWTO Install and Configure the IdP-Authn-Plugin fudiscr
========================================================

.. image:: https://wiki.idem.garr.it/IDEM_Approved.png
   :width: 120 px

Table of Contents
-----------------

#. `Overview`_
#. `Requirements`_
#. `Configure PrivacyIDEA`_

   #. `Create Administrator`_
   #. `Create the idp-admin authorization token`_
   #. `Create the idp-admin policies on the PrivacyIDEA server`_

      #. `Setup Policy for idp-admin`_
      #. `Enable application_tokentype policy`_

#. `Configure Shibboleth IdP`_

   #. `Enable MFA module`_
   #. `Install fudiscr plugin`_
   #. `Configure fudiscr plugin`_

#. `Restart Jetty`_
#. `Authors`_

Overview
--------


Requirements
------------

* PrivacyIDEA (tested with v3.8.1)
* Shibboleth Identity Provider (tested with v4.3.1)
* de.zedat.fudis.shibboleth.idp.plugin.authn.fudiscr (tested with v1.3.0)

Configure PrivacyIDEA
---------------------

Create Administrator
++++++++++++++++++++

The creation of the administrator user for Shibboleth in the PrivacyIDEA database
is done throught a command line in the PrivacyIDEA Virtual Environment:

* .. code-block:: text

     cd /opt/privacyidea

* .. code-block:: text

     source bin/activate

* .. code-block:: text

     pi-manage admin add idp-admin

`TOC`_

Create the idp-admin authorization token
++++++++++++++++++++++++++++++++++++++++

.. code-block:: text

   pi-manage api createtoken -r admin -u idp-admin -d 3650

Create the idp-admin policies on the PrivacyIDEA server
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

Setup Policy for idp-admin
;;;;;;;;;;;;;;;;;;;;;;;;;;

* Go to **Config** -> **Policies**
* Open **Create new Policy**
* Set the value of **Policy Name** to **idp-admin**
* Set the value of **Scope** to **admin**
* Set the value of **Priority** to **last policy number + 1**
* Move on the **Condition** tab
* Leave the value of **Admin-Realm** to **None Selected** to enable policy for all admins' realms.
* Set the value of **Admin** to **idp-admin**
* Move on the **Action** tab
* Search ``tokenlist`` on the *Filter action...* box and check it.
* Search ``triggerchallenge`` on the *Filter action...* box and check it.
* Save Policy

Enable application_tokentype policy
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

DOC: `application_tokentype`_

By enabling ``application_tokentype`` policy, an application can determine via ``type``
parameter which tokens of a user check.

* Go to **Config** -> **Policies**
* Open **Create new Policy**
* Set the value of **Policy Name** to **idp-application-tokentype**
* Set the value of **Scope** to **authorization**
* Set the value of **Priority** to **last policy number + 1**
* Move on the **Action** tab
* Search ``application_tokentype`` on the *Filter action...* box and check it.
* Save Policy

Configure Shibboleth IdP
------------------------

Enable MFA module
+++++++++++++++++

*  .. code-block:: text

      sudo su -

*  .. code-block:: text

      /opt/shibboleth-idp/bin/module.sh -e idp.authn.MFA

*  .. code-block:: text

      /opt/shibboleth-idp/bin/module.sh -l

Install fudiscr plugin
++++++++++++++++++++++

.. code-block:: text

   /opt/shibboleth-idp/bin/plugin.sh -i https://identity.fu-berlin.de/downloads/shibboleth/idp/plugins/authn/fudiscr/current/fudis-shibboleth-idp-plugin-authn-fudiscr-current.tar.gz

If you need to install a specific version:

.. code-block:: text

   /opt/shibboleth-idp/bin/plugin.sh -i https://identity.fu-berlin.de/downloads/shibboleth/idp/plugins/authn/fudiscr/1.3.0/fudis-shibboleth-idp-plugin-authn-fudiscr-1.3.0.tar.gz

If you need to check the plugins installed into Shibboleth IdP

.. code-block:: text

   /opt/shibboleth-idp/bin/plugin.sh -l

If you need to update ``fudiscr`` plugin:

.. code-block:: text

   /opt/shibboleth-idp/bin/plugin.sh -u de.zedat.fudis.shibboleth.idp.plugin.authn.fudiscr

Configure fudiscr plugin
++++++++++++++++++++++++

.. code-block:: text

   vim /opt/shibboleth-idp/conf/authn/fudiscr.properties

and set the following lines with the right value:

.. code-block:: text

   #...other things...

   #####
   # PrivacyIDEA
   #####
   fudiscr.privacyidea.base_uri=<PRIVACYIDEA-URI>
   fudiscr.privacyidea.authorization_token=<IDP-ADMIN-AUTHORIZATION-TOKEN>

Replace ``<PRIVACYIDEA-URI>`` with an uri likes ``https://privacyidea.server.url``
and ``<IDP-ADMIN-AUTHORIZATION-TOKEN>`` with the authorization token created
in the section `Create the idp-admin authorization token`_

Configure Shibboleth MFA plugin
+++++++++++++++++++++++++++++++

#. Edit ``authn.properties``:

   .. code-block:: text

      vim /opt/shibboleth-idp/conf/authn/authn.properties

   and enable the MFA Flow by setting the ``idp.authn.flows`` property:

   .. code-block:: text

      idp.authn.flows = MFA

   and add the missing ``supportPrincipals`` as follow:

   .. code-block:: text

      #### MFA ####

      idp.authn.MFA.supportedPrincipals = \
         saml2/urn:oasis:names:tc:SAML:2.0:ac:classes:InternetProtocol, \
         saml2/urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport, \
         saml2/urn:oasis:names:tc:SAML:2.0:ac:classes:Password, \
         saml1/urn:oasis:names:tc:SAML:1.0:am:password, \
         saml2/urn:de:zedat:fudis:SAML:2.0:ac:classes:CR, \
         saml2/https://refeds.org/profile/mfa

      #### FUDISCR plugin ####

      idp.authn.fudiscr.supportedPrincipals = \
         saml2/urn:de:zedat:fudis:SAML:2.0:ac:classes:CR, \
         saml2/https://refeds.org/profile/mfa

#. Edit ``mfa-authn-config.xml``:

   * .. code-block:: text

        sed -i 's|authn/Password|authn/fudiscr|g' mfa-authn-config.xml

   * .. code-block:: text

        sed -i 's|authn/IPAddress|authn/Password|g' mfa-authn-config.xml

`TOC`_

Restart Jetty
-------------

.. code-block:: text

   /etc/init.d/jetty stop ; /etc/init.d/jetty run

Authors
-------

* Marco Pirovano
* Marco Malavolti

.. _application_tokentype: https://privacyidea.readthedocs.io/en/v3.8.1/policies/authorization.html?highlight=application_tokentype#application-tokentype
.. _TOC: `Table of Contents`_
