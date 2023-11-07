HOWTO Install and Configure the IdP-Authn-Plugin fudiscr
========================================================

# 1. privacyIDEA

### 1.1 Become the PrivacyIDEA user

* ``sudo su - privacyidea``
* ``source bin/activate``

### 1.2 Create an admin user

* ``pi-manage admin add idp-admin``
* ``pi-manage admin list``

### 1.3 Create an access token

* ``pi-manage api createtoken -r admin -u idp-admin -d 3650``

### 1.4 Access privacyIDEA server

  ``https://idem-day-mfa-42.aai-test.garr.it``

#### 1.4.1 Create Policies

**idp-admin**

    Config -> Policies -> Create new Policy
    Policy Name : 'idp-admin'
    Scope : admin
    Condition -> Admin : 'idp-admin'
    Action -> token -> tokenlist : check
    Action -> general -> triggerchallenge : check

**idp-application-tokentype**

    Config -> Policies -> Create new Policy
    Policy Name : 'idp-application-tokentype'
    Scope : authorization
    Action -> miscellaneous -> application_tokentype : check

<br>

# 2. Shibboleth IdP

### 2.1 MFA module activation

* ``sudo su -``
* ``cd /opt/shibboleth-idp``
* ``bin/module.sh -e idp.authn.MFA``
* ``bin/module.sh -l``

### 2.2 fudiscr plugin installation

* ``bin/plugin.sh -i https://identity.fu-berlin.de/downloads/shibboleth/idp/plugins/authn/fudiscr/current/fudis-shibboleth-idp-plugin-authn-fudiscr-current.tar.gz``

 if you want to install a specific version:

* ``bin/plugin.sh -i https://identity.fu-berlin.de/downloads/shibboleth/idp/plugins/authn/fudiscr/1.3.0/fudis-shibboleth-idp-plugin-authn-fudiscr-1.3.0.tar.gz``

* ``bin/plugin.sh -l``

 future updates will be installed automatically with the following command:

* ``bin/plugin.sh -u de.zedat.fudis.shibboleth.idp.plugin.authn.fudiscr``

### 2.3 fudiscr plugin configuration

edit the file:

* ``conf/authn/fudiscr.properties``

modify the following lines:

    #####
    # PrivacyIDEA
    #####
    fudiscr.privacyidea.base_uri=
    fudiscr.privacyidea.authorization_token=


### 2.4 MFA configuration

edit the file:

* ``conf/authn/authn.properties``

modify the following lines:

    idp.authn.flows = MFA
    
   
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


edit the file:

* ``conf/authn/mfa-authn-config.xml``

``` 
<util:map id="shibboleth.authn.MFA.TransitionMap">
<!-- First rule runs the Password login flow. -->
<entry key="">
    <bean parent="shibboleth.authn.MFA.Transition" p:nextFlow="authn/Password" />
</entry>

<!--
Second rule runs a function if Password succeeds, to determine whether an additional factor is required.
-->
<entry key="authn/Password">
    <bean parent="shibboleth.authn.MFA.Transition" :nextFlowStrategy-ref="checkSecondFactor" />
</entry>

<!-- An implicit final rule will return whatever the final flow returns. --> 
</util:map>

<!-- Example script to see if second factor is  required. -->
<bean id="checkSecondFactor"  parent="shibboleth.ContextFunctions.Scripted" factory method="inlineScript">
    <constructor-arg>
        <value>
        <![CDATA[
            nextFlow = "authn/fudiscr";
 
            // Check if second factor is necessary for request to be satisfied.
            authCtx = input.getSubcontext("net.shibboleth.idp.authn.context.AuthenticationContext");
            mfaCtx = authCtx.getSubcontext("net.shibboleth.idp.authn.context.MultiFactorAuthenticationContext");
            if (mfaCtx.isAcceptable()) {
                nextFlow = null;
            }
 
            nextFlow;   // pass control to second factor or end with the first
        ]]>
        </value>
    </constructor-arg>
</bean>
```

# 3. Author

* Marco Pirovano
