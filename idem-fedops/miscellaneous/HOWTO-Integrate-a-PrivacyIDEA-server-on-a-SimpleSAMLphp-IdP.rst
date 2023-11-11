===========================================================
HOWTO Integrate a PrivacyIDEA server on a SimpleSAMLphp IdP
===========================================================

.. image:: https://wiki.idem.garr.it/IDEM_Approved.png
   :width: 120 px
  
Table of Contents
-----------------

#. `Overview`_
#. `Requirements`_
#. `Configure PrivacyIDEA`_

   #. `Create Administrator`_
   #. `Login to the Web UI`_
   #. `Setup Policy for Admin`_

#. `Configure SimpleSAMLphp`_

   #. `Cirrus Filter`_
   #. `PrivacyIDEA Filter`_
   #. `No MFA Filter`_

#. `Reference`_
#. `Authors`_
#. `License`_

Overview
--------

This HOWTO aims to integrate a PrivacyIDEA server on a simpleSAMLphp Identity Provider to provide a Mutli Factor Authentication to the users.
To do so we will use two different modules:

* `PrivacyIDEA module for simpleSAMLphp`_
* `Cirrusgeneral module for simpleSAMLphp`_

In our use case, we have two different machine, one with the SimpleSAMLphp IdP and one with the PrivacyIDEA server.
Also, the Identity Provider can perform the multi factor authentication when the Service Provider has in its request 
a particular authnContextClassRef: ``https://refeds.org/profile/mfa`` 

For more you can check the `REFEDS MFA Profile`_


Requirements
------------

* PrivacyIDEA server (tested with v3.8.1)
* Composer
* simpleSAMLphp Identity Provider (tested with v1.19)

`TOC`_

Configure PrivacyIDEA
---------------------

Create Administrator
+++++++++++++++++++++

The creation of the administrator user for simpleSAMLphp in the PrivacyIDEA database
is done throught a command line in the PrivacyIDEA Virtual Environment:

* ``cd /opt/privacyidea``
* ``source bin/activate``
* ``pi-manage admin add ssp-admin``

`TOC`_

Login to the Web UI
+++++++++++++++++++

Open ``https://<PRIVACYIDEA_FQDN>/`` and enter the Admin username ``admin`` and ``<PASSWORD>``.

Administrators will be able to configure the system and to manage all tokens,
while normal users will only be able to manage their own tokens.

`TOC`_

Setup Policy for Admin
++++++++++++++++++++++

* Go to **Config** -> **Policies**
* Open **Create new Policy**
* Set the value of **Policy Name** to **ssp-admin**
* Set the value of **Scope** to **admin**
* Set the value of **Priority** to **5**

* Move on the **Condition** tab
* Leave the value of **Admin-Realm** to **None Selected** to enable policy for all admins' realms.
* Set the value of **Admin** to **ssp-admin**

* Move on the **Action** tab
* Check the ``tokenlist`` box under **token**.
* Check the ``triggerchallenge`` box under **general**.

* Save Policy

`TOC`_

Configure SimpleSAMLphp
-----------------------

#. Become ROOT:

   * ``sudo su -``

#. Move to the simplesamlphp folder:

   * ``cd /var/simplesamlphp``

#. Install the required packages:

   * ``composer require cirrusidentity/simplesamlphp-module-cirrusgeneral:2.0.3``

   * ``composer require privacyidea/simplesamlphp-module-privacyidea:3.1.2``

#. Configure the **saml20-idp-hosted.php**:

   * ``vim metadata/saml20-idp-hosted.php``

`TOC`_

Cirrus Filter
++++++++++++++

In the IdP configuration file we will create a new filter (in the **authproc** section):

.. code:: php

   // Configuration for privacyIDEA
   56 => [
          'class' => 'cirrusgeneral:PhpConditionalAuthProcInserter',
          'condition' => 'return (empty($state["saml:RequestedAuthnContext"]["AuthnContextClassRef"])) ? FALSE : ((in_array("https://refeds.org/profile/mfa",$state["saml:RequestedAuthnContext"]["AuthnContextClassRef"])) ? TRUE : FALSE );',
          'authproc' => [
         ],      
         // These will only get created if authnContext is not refeds MFA
         'elseAuthproc' => [],
   ],

`TOC`_

PrivacyIDEA Filter
+++++++++++++++++++

In the cirrus filter we can setup the PrivacyIDEA configuration (in the **authproc** section):

.. code-block:: php

   [
      'class' => 'privacyidea:PrivacyideaAuthProc',
      /**
      * The URL of the privacyidea server.
      * Required
      */
      'privacyideaServerURL' => 'https://idem-day-mfa-<N>.aai-test.garr.it',
      /**
      * Set the privacyidea realm.
      * Optional.
      */
      'realm' => 'idem-day-org-<N>.it',
      /**
      * The uidKey is the username's attribute key.
      * You can choose a single one or multiple ones. The first set will be used.
      * Example: 'uidKey' => ['uid', 'userName', 'uName'],
      *
      * Required.
      */
      'uidKey' => 'uid',
      /**
      * Disable SSL verification.
      * Values should be 'true' or 'false'. Default is 'true'.
      * NOTE: This should always be enabled in a productive environment!
      * 
      * Optional.
      */
      'sslVerifyHost' => 'true',
      'sslVerifyPeer' => 'true',
      /**
      * Specify the static password for the 'sendStaticPass' authentication flow.
      * Required by the 'sendStaticPass' authentication flow.
      */
      'staticPass' => '',
      /**
      * Specify the username and password of your service account from privacyIDEA server.
      * Required by the 'triggerChallenge' authentication flow.
      */
      'serviceAccount' => '<ADMIN_USERNAME>',
      'servicePass' => '<ADMIN_PASSWORD>',
      /**
      * Choose one of the following authentication flows:
      * 
      * 'default' - Default authentication flow.
      * 
      * 'sendStaticPass' - If you want to use the passOnNoToken or passOnNoUser policy in privacyidea,
      * you can use this flow, and specify a static pass which will be sent before the actual
      * authentication to trigger the policies in privacyidea.
      * NOTE: This 'sendStaticPass' isn't combinable with 'doEnrollToken' option.
      * NOTE: This won't be processed if the user has a challenge-response token that were triggered before.
      * 
      * 'triggerChallenge' - Before the login interface is shown, the filter will attempt to trigger challenge-response
      * token with the specified serviceAccount.
      * 
      * Required.
      */
      'authenticationFlow' => 'default',
      /**
      * Set the realm for your service account.
      * Optional (by the 'triggerChallenge' authentication flow).
      */
      'serviceRealm' => '',
      /**
      * Set this to 'true' if you want to use single sign on.
      * All information required for SSO will be saved in the session.
      * After logging out, the SSO data will be removed from the session.
      * 
      * Optional.
      */
      'SSO' => 'true',
      /**
      * Custom hint for the OTP field.
      * Optional.
      */
      'otpFieldHint' => 'Please enter the OTP code!',
      /**
      * Other authproc filters can disable this filter.
      * If privacyIDEA should consider the setting, you have to enter the path and key of the state.
      * The value of this key has to be set by a previous auth proc filter.
      * privacyIDEA will only be disabled, if the value of the key is set to false,
      * in any other situation (e.g. the key is not set or does not exist), privacyIDEA will be enabled.
      * 
      * Optional.
      */
      'enabledPath' => 'privacyIDEA',
      'enabledKey' => 'enable',
      /**
      * You can exclude clients with specified ip addresses.
      * Enter a range like "10.0.0.0-10.2.0.0" or a single ip like "192.168.178.2"
      * The selected ip addresses do not need 2FA.
      * 
      * Optional.
      */
      'excludeClientIPs' => [],
      /**
      * If you want to selectively disable the privacyIDEA authentication using
      * the entityID and/or SAML attributes, you may enable this.
      * Value has to be a 'true' or 'false'.
      * 
      * Optional.
      */
      'checkEntityID' => 'true',
      /**
      * Depending on excludeEntityIDs and includeAttributes this will set the state variable 
      * $state[$setPath][$setPath] to true or false.
      * To selectively enable or disable privacyIDEA, make sure that you specify setPath and setKey such
      * that they equal enabledPath and enabledKey from privacyidea:privacyidea.
      * 
      * Optional.
      */
      'setPath' => 'privacyIDEA',
      'setKey' => 'enabled',
      /**
      * The requesting SAML provider's entityID will be tested against this list of regular expressions.
      * If there is a match, the filter will set the specified state variable to false and thereby disables 
      * privacyIDEA for this entityID The first matching expression will take precedence.
      * 
      * Optional.
      */
      'excludeEntityIDs' => [
         '/http(s)\/\/conditional-no2fa-provider.de\/(.*)/',
         '/http(.*)no2fa-provider.de/'
      ],
      /**
      *  Per value in excludeEntityIDs, you may specify another set of regular expressions to match the
      *  attributes in the SAML request. If there is a match in any attribute value, this filter will
      *  set the state variable to true and thereby enable privacyIDEA where it would be normally disabled
      *  due to the matching entityID. This may be used to enable 2FA at this entityID only for privileged
      *  accounts.
      *  The key in includeAttributes must be identical to a value in excludeEntityIDs to have an effect!
      */
      'includeAttributes' => [
         '/http(s)\/\/conditional-no2fa-provider.de\/(.*)/' => [
               'memberOf' => [
                  '/cn=2fa-required([-_])regexmatch(.*),cn=groups,(.*)/',
                  'cn=2fa-required-exactmatch,ou=section,dc=privacyidea,dc=org'
               ],
               'myAttribute' => [
                  '/(.*)2fa-required/',
                  '2fa-required',
               ]
         ]
      ],
   ],
   [
      'class' => 'saml:AuthnContextClassRef',
      'AuthnContextClassRef' => 'https://refeds.org/profile/mfa',
   ],

`TOC`_

No MFA Filter
++++++++++++++

In the second part of the cirrus filter, **elseAuthproc**, we insert the behaviour of the IdP authentication when the MFA is not required:

.. code:: php

   [
      'class' => 'saml:AuthnContextClassRef',
      'AuthnContextClassRef' => 'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport',
   ],

`TOC`_

Reference
---------

* `PrivacyIDEA Documentation`_
* `PrivacyIDEA module for simpleSAMLphp`_
* `Cirrusgeneral module for simpleSAMLphp`_
* `SimpleSAMLphp Documentation`_
* `Composer`_

`TOC`_

Authors
-------

* `Mario Di Lorenzo <mailto:mario.dilorenzo@garr.it>`_
* `Marco Malavolti <mailto:marco.malavolti@garr.it>`_

License
-------

This HOWTO is licensed under `CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>`_.

`TOC`_

.. _PrivacyIDEA module for simpleSAMLphp : https://github.com/privacyidea/simplesamlphp-module-privacyidea
.. _Cirrusgeneral module for simpleSAMLphp: https://github.com/cirrusidentity/simplesamlphp-module-cirrusgeneral
.. _REFEDS MFA Profile: https://wiki.refeds.org/display/PRO/Introducing+the+REFEDS+MFA+Profile
.. _PrivacyIDEA Documentation: https://privacyidea.readthedocs.io
.. _simpleSAMLphp Documentation: https://simplesamlphp.org/docs/stable/index.html
.. _Composer: https://getcomposer.org/
.. _TOC: `Table of Contents`_
