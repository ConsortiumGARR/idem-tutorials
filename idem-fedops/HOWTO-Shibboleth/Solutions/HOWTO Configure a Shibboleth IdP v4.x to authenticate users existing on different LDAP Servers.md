# HOWTO Configure a Shibboleth IdP v4.x to authenticate users existing on different LDAP Servers

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements)
2. [Files involved](#files-involved)
3. [Notes before start](#notes-before-you-start)
4. [OpenLDAP Case connected with bindSearchAuthenticator](#openldap-case-connected-with-bindsearchauthenticator)
5. [Active Directory Case connected with bindSearchAuthenticator](#active-directory-case-connected-with-bindsearchauthenticator)
6. [Authors](#authors)


## Requirements

* A machine with Shibboleth IdP v4.x installed (tested with v4.1.4)
* Two LDAP/AD provided by different servers.

## Files Involved

* `conf/authn/password-authn-config.xml`
* `conf/ldap.properties`
* `credentials/secrets.properties`
* `conf/attribute-resolver.xml`

## Notes before you start

The tutorial values only `idp.attribute.resolver.LDAP.exportAttributes.1` because it is valid, and will be used,  by both LDAP servers connected to the Shibboleth IdP.

The LDAP servers, in this example, provide the same set of attributes from two different machines.

The value of `idp.attribute.resolver.LDAP.exportAttributes.2` have to be left empty because the attribute set provided by the `idp.attribute.resolver.LDAP.exportAttributes.1` value will be used also for the second `<DataConnector>`.

If the second LDAP server connected to the Shibboleth IdP manage different attributes, it is needed to value `idp.attribute.resolver.LDAP.exportAttributes.2` with those attributes that are not already included by the first one.

The attributes listed in each `idp.attribute.resolver.LDAP.exportAttributes` properties have to be different.

## OpenLDAP Case connected with bindSearchAuthenticator

1. Change the **shibboleth.authn.Password.Validators** list into `conf/authn/password-authn-config.xml` as following:
   ```xml
   <!--
       These use the settings defined in conf/ldap.properties except:
         - p:ldapUrl
         - p:baseDn
         - p:bindDn
         - p:bindDnCredential
         - p:userFilter

       overridden here.
   -->
   <util:list id="shibboleth.authn.Password.Validators">
       <bean p:id="ldap_1" parent="shibboleth.LDAPValidator">
           <property name="authenticator">
               <bean parent="shibboleth.LDAPAuthenticationFactory" 
                     p:ldapUrl="%{idp.authn.LDAP.ldapURL.1:ldap://localhost:10389}"
                     p:baseDn="#{'%{idp.authn.LDAP.baseDN.1:undefined}'.trim()}"
                     p:bindDn="#{'%{idp.authn.LDAP.bindDN.1:undefined}'.trim()}"
                     p:bindDnCredential="%{idp.authn.LDAP.bindDNCredential.1:undefined}"
                     p:userFilter="#{'%{idp.authn.LDAP.userFilter.1:undefined}'.trim()}" />
           </property>
       </bean>
       <bean p:id="ldap_2" parent="shibboleth.LDAPValidator">
           <property name="authenticator">
               <bean parent="shibboleth.LDAPAuthenticationFactory" 
                     p:ldapUrl="%{idp.authn.LDAP.ldapURL.2:ldap://localhost:10389}"
                     p:baseDn="#{'%{idp.authn.LDAP.baseDN.2:undefined}'.trim()}"
                     p:bindDn="#{'%{idp.authn.LDAP.bindDN.2:undefined}'.trim()}"
                     p:bindDnCredential="%{idp.authn.LDAP.bindDNCredential.2:undefined}"
                     p:userFilter="#{'%{idp.authn.LDAP.userFilter.2:undefined}'.trim()}" />
           </property>
       </bean>
   </util:list>
   ```

2. Insert into `conf/ldap.properties` the properties added into `conf/authn/password-authn-config.xml`:
   ```xml
   # LDAP 1 authentication configuration properties:
   # - conf/authn/password-authn-config.xml         (LDAP chaining)
   # - conf/ldap.properties                         (LDAP properties)
   idp.authn.LDAP.ldapURL.1                          = ldap://<URL-LDAP-1>:389
   idp.authn.LDAP.baseDN.1                           = ou=people-1,dc=example,dc=org
   idp.authn.LDAP.bindDN.1                           = cn=admin-1,dc=people,dc=example,dc=org
   idp.authn.LDAP.userFilter.1                       = (uid={user})

   # LDAP 2 authentication configuration properties:
   # - conf/authn/password-authn-config.xml         (LDAP chaining)
   # - conf/ldap.properties                         (LDAP properties)
   idp.authn.LDAP.ldapURL.2                          = ldap://<URL-LDAP-2>:389
   idp.authn.LDAP.baseDN.2                           = ou=people-2,dc=example,dc=org
   idp.authn.LDAP.bindDN.2                           = cn=admin-2,ou=people,dc=example,dc=org
   idp.authn.LDAP.userFilter.2                       = (mail={user})

   # LDAP authentication common properties (1 and 2 share them on this example):
   idp.authn.LDAP.authenticator                    = bindSearchAuthenticator
   idp.authn.LDAP.useStartTLS                      = false
   idp.authn.LDAP.returnAttributes                 = passwordExpirationTime,loginGraceRemaining      ## Return attributes during authentication
   idp.authn.LDAP.connectTimeout                   = PT3S     # Time in milliseconds that connects will block
   idp.authn.LDAP.responseTimeout                  = PT3S     # Time in milliseconds to wait for responses
   idp.authn.LDAP.subtreeSearch                    = true

   # LDAP 1 DataConnector configuration on conf/attribute-resolver.xml
   idp.attribute.resolver.LDAP.ldapURL.1             = %{idp.authn.LDAP.ldapURL.1}
   idp.attribute.resolver.LDAP.connectTimeout.1      = %{idp.authn.LDAP.connectTimeout:PT3S}
   idp.attribute.resolver.LDAP.responseTimeout.1     = %{idp.authn.LDAP.responseTimeout:PT3S}
   idp.attribute.resolver.LDAP.baseDN.1              = %{idp.authn.LDAP.baseDN.1:undefined}
   idp.attribute.resolver.LDAP.bindDN.1              = %{idp.authn.LDAP.bindDN.1:undefined}
   idp.attribute.resolver.LDAP.useStartTLS.1         = %{idp.authn.LDAP.useStartTLS:true}
   idp.attribute.resolver.LDAP.searchFilter.1        = (uid=$resolutionContext.principal)

   # LDAP 2 DataConnector configuration on conf/attribute-resolver.xml
   idp.attribute.resolver.LDAP.ldapURL.2             = %{idp.authn.LDAP.ldapURL.2}
   idp.attribute.resolver.LDAP.connectTimeout.2      = %{idp.authn.LDAP.connectTimeout:PT3S}
   idp.attribute.resolver.LDAP.responseTimeout.2     = %{idp.authn.LDAP.responseTimeout:PT3S}
   idp.attribute.resolver.LDAP.baseDN.2              = %{idp.authn.LDAP.baseDN.2:undefined}
   idp.attribute.resolver.LDAP.bindDN.2              = %{idp.authn.LDAP.bindDN.2:undefined}
   idp.attribute.resolver.LDAP.useStartTLS.2         = %{idp.authn.LDAP.useStartTLS:true}
   idp.attribute.resolver.LDAP.searchFilter.2        = (mail=$resolutionContext.principal)

   # LDAP Common exportAttribute configuration for LDAP-1 and LDAP-2 on attribute-resolver.xml
   idp.attribute.resolver.LDAP.exportAttributes.1    = uid givenName sn cn mail displayName mobile title preferredLanguage telephoneNumber eduPersonAffiliation eduPersonEntitlement eduPersonOrgDN eduPersonOrgUnitDN eduPersonOrcid schacMotherTongue schacPersonalTitle schacUserPresenceID schacPersonalUniqueID schacPersonalPositon 
   ```

3. Insert into `credentials/secrets.properties` the new credential:
   ```xml
   # LDAP 1 access to authn and attribute stores.
   idp.authn.LDAP.bindDNCredential.1              = <PASSWORD-LDAP-USER-1>
   idp.attribute.resolver.LDAP.bindDNCredential.1 = %{idp.authn.LDAP.bindDNCredential.1:undefined}

   # LDAP 2 access to authn and attribute stores.
   idp.authn.LDAP.bindDNCredential.2              = <PASSWORD-LDAP-USER-2>
   idp.attribute.resolver.LDAP.bindDNCredential.2 = %{idp.authn.LDAP.bindDNCredential.2:undefined}
   ```

4. Change the `conf/attribute-resolver.xml` by adding the new `<DataConnector>`:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>

   <AttributeResolver
           xmlns="urn:mace:shibboleth:2.0:resolver"
           xmlns:sec="urn:mace:shibboleth:2.0:security"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="urn:mace:shibboleth:2.0:resolver http://shibboleth.net/schema/idp/shibboleth-attribute-resolver.xsd
                               urn:mace:shibboleth:2.0:security http://shibboleth.net/schema/idp/shibboleth-security.xsd">

       <!-- ========================================== -->
       <!--      Attribute Definitions                 -->
       <!-- ========================================== -->

       <AttributeDefinition scope="%{idp.scope}" xsi:type="Scoped" id="eduPersonScopedAffiliation">
           <InputDataConnector ref="LDAP-1" attributeNames="eduPersonAffiliation" />
           <InputDataConnector ref="LDAP-2" attributeNames="eduPersonAffiliation" />
       </AttributeDefinition>

       <AttributeDefinition scope="%{idp.scope}" xsi:type="Scoped" id="eduPersonPrincipalName">
           <InputDataConnector ref="LDAP-1" attributeNames="%{idp.persistentId.sourceAttribute}" />
           <InputDataConnector ref="LDAP-2" attributeNames="%{idp.persistentId.sourceAttribute}" />
       </AttributeDefinition>

       <!-- AttributeDefinition for eduPersonTargetedID - Computed Mode -->
       <AttributeDefinition xsi:type="SAML2NameID" nameIdFormat="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" id="eduPersonTargetedID">
           <InputDataConnector ref="myComputedId" attributeNames="computedID"/>
       </AttributeDefinition>

       <!-- AttributeDefinition for eduPersonTargetedID - Stored Mode -->
       <!--
       <AttributeDefinition xsi:type="SAML2NameID" nameIdFormat="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" id="eduPersonTargetedID">
           <InputDataConnector ref="myStoredId" attributeNames="persistentID" />
       </AttributeDefinition>
       -->

       <AttributeDefinition xsi:type="Simple" id="schacHomeOrganization">
           <InputDataConnector ref="staticAttributes" attributeNames="schacHomeOrganization"/>
       </AttributeDefinition>

       <AttributeDefinition xsi:type="Simple" id="schacHomeOrganizationType">
           <InputDataConnector ref="staticAttributes" attributeNames="schacHomeOrganizationType"/>
       </AttributeDefinition>

       <!-- ========================================== -->
       <!--      Data Connectors                       -->
       <!-- ========================================== -->

       <!-- LDAP 1 DataConnector -->
       <DataConnector id="LDAP-1" xsi:type="LDAPDirectory"
           ldapURL="%{idp.attribute.resolver.LDAP.ldapURL.1}"
           baseDN="%{idp.attribute.resolver.LDAP.baseDN.1}"
           principal="%{idp.attribute.resolver.LDAP.bindDN.1}"
           principalCredential="%{idp.attribute.resolver.LDAP.bindDNCredential.1}"
           useStartTLS="%{idp.attribute.resolver.LDAP.useStartTLS.1:true}"
           connectTimeout="%{idp.attribute.resolver.LDAP.connectTimeout}"
           responseTimeout="%{idp.attribute.resolver.LDAP.responseTimeout}"
           exportAttributes="%{idp.attribute.resolver.LDAP.exportAttributes.1}">
           <FailoverDataConnector ref="LDAP-2" />
           <FilterTemplate>
               <![CDATA[
                   %{idp.attribute.resolver.LDAP.searchFilter.1}
               ]]>
           </FilterTemplate>
           <ConnectionPool
               minPoolSize="%{idp.pool.LDAP.minSize:3}"
               maxPoolSize="%{idp.pool.LDAP.maxSize:10}"
               blockWaitTime="%{idp.pool.LDAP.blockWaitTime:PT3S}"
               validatePeriodically="%{idp.pool.LDAP.validatePeriodically:true}"
               validateTimerPeriod="%{idp.pool.LDAP.validatePeriod:PT5M}"
               validateDN="%{idp.pool.LDAP.validateDN:}"
               validateFilter="%{idp.pool.LDAP.validateFilter:(objectClass=*)}"
               expirationTime="%{idp.pool.LDAP.idleTime:PT10M}"/>

       </DataConnector>

       <!-- LDAP 2 DataConnector -->
       <DataConnector id="LDAP-2" xsi:type="LDAPDirectory"
           ldapURL="%{idp.attribute.resolver.LDAP.ldapURL.2}"
           baseDN="%{idp.attribute.resolver.LDAP.baseDN.2}"
           principal="%{idp.attribute.resolver.LDAP.bindDN.2}"
           principalCredential="%{idp.attribute.resolver.LDAP.bindDNCredential.2}"
           useStartTLS="%{idp.attribute.resolver.LDAP.useStartTLS.2:true}"
           connectTimeout="%{idp.attribute.resolver.LDAP.connectTimeout.2}"
           responseTimeout="%{idp.attribute.resolver.LDAP.responseTimeout.2}"
           exportAttributes="%{idp.attribute.resolver.LDAP.exportAttributes.2:}">
           <FilterTemplate>
               <![CDATA[
                   %{idp.attribute.resolver.LDAP.searchFilter}
               ]]>
           </FilterTemplate>
           <ConnectionPool
               minPoolSize="%{idp.pool.LDAP.minSize:3}"
               maxPoolSize="%{idp.pool.LDAP.maxSize:10}"
               blockWaitTime="%{idp.pool.LDAP.blockWaitTime:PT3S}"
               validatePeriodically="%{idp.pool.LDAP.validatePeriodically:true}"
               validateTimerPeriod="%{idp.pool.LDAP.validatePeriod:PT5M}"
               validateDN="%{idp.pool.LDAP.validateDN:}"
               validateFilter="%{idp.pool.LDAP.validateFilter:(objectClass=*)}"
               expirationTime="%{idp.pool.LDAP.idleTime:PT10M}"/>

       </DataConnector>

       <!--  Data Connector for eduPersonTargetedID - Computed Mode  -->
       <DataConnector id="myComputedId" xsi:type="ComputedId" 
                      generatedAttributeID="computedID" 
                      salt="%{idp.persistentId.salt}" 
                      algorithm="%{idp.persistentId.algorithm:SHA}"
                      encoding="%{idp.persistentId.encoding:BASE32}">

           <InputDataConnector ref="LDAP-1" attributeNames="%{idp.persistentId.sourceAttribute}"/>
           <InputDataConnector ref="LDAP-2" attributeNames="%{idp.persistentId.sourceAttribute}"/>
       </DataConnector>

       <!--  Data Connector for eduPersonTargetedID - Stored Mode  -->
       <!-- 
       <DataConnector id="stored" xsi:type="StoredId"
           generatedAttributeID="storedId"
           salt="%{idp.persistentId.salt}"
           queryTimeout="0">

           <InputDataConnector ref="LDAP-1" attributeNames="%{idp.persistentId.sourceAttribute}"/>
           <InputDataConnector ref="LDAP-2" attributeNames="%{idp.persistentId.sourceAttribute}"/>

           <BeanManagedConnection>MyDataSource</BeanManagedConnection>
       </DataConnector>
       -->
     
       <!--  Example Data Connector for static attributes  -->
       <DataConnector id="staticAttributes" xsi:type="Static">
          <Attribute id="schacHomeOrganization">
             <Value>%{idp.scope}</Value>
          </Attribute>
          <!--  One of the values defined here:
                https://wiki.refeds.org/pages/viewpage.action?pageId=44957715#SCHACURNRegistry-homeOrganizationType
          -->
          <Attribute id="schacHomeOrganizationType">
             <Value>urn:schac:homeOrganizationType:eu:higherEducationalInstitution</Value>
          </Attribute>
      </DataConnector>
     
   </AttributeResolver>
   ```

5. Restart Jetty to apply:
   * `sudo systemctl restart jetty`

## Active Directory Case connected with bindSearchAuthenticator

1. Change the **shibboleth.authn.Password.Validators** list into `conf/authn/password-authn-config.xml` as following:
   ```xml
   <!--
       These use the settings defined in conf/ldap.properties except:
         - p:ldapUrl
         - p:baseDn
         - p:bindDn
         - p:bindDnCredential
         - p:userFilter
         - p:dnFormat

       overridden here.
   -->
   <util:list id="shibboleth.authn.Password.Validators">
       <bean p:id="ldap_1" parent="shibboleth.LDAPValidator">
           <property name="authenticator">
               <bean parent="shibboleth.LDAPAuthenticationFactory" 
                     p:ldapUrl="%{idp.authn.LDAP.ldapURL.1:ldap://localhost:10389}"
                     p:baseDn="#{'%{idp.authn.LDAP.baseDN.1:undefined}'.trim()}"
                     p:bindDn="#{'%{idp.authn.LDAP.bindDN.1:undefined}'.trim()}"
                     p:bindDnCredential="%{idp.authn.LDAP.bindDNCredential.1:undefined}"
                     p:userFilter="#{'%{idp.authn.LDAP.userFilter.1:undefined}'.trim()}"
                     p:dnFormat="%{idp.authn.LDAP.dnFormat.1:undefined}" />
           </property>
       </bean>
       <bean p:id="ldap_2" parent="shibboleth.LDAPValidator">
           <property name="authenticator">
               <bean parent="shibboleth.LDAPAuthenticationFactory" 
                     p:ldapUrl="%{idp.authn.LDAP.ldapURL.2:ldap://localhost:10389}"
                     p:baseDn="#{'%{idp.authn.LDAP.baseDN.2:undefined}'.trim()}"
                     p:bindDn="#{'%{idp.authn.LDAP.bindDN.2:undefined}'.trim()}"
                     p:bindDnCredential="%{idp.authn.LDAP.bindDNCredential.2:undefined}"
                     p:userFilter="#{'%{idp.authn.LDAP.userFilter.2:undefined}'.trim()}"
                     p:dnFormat="%{idp.authn.LDAP.dnFormat.2:undefined}" />
           </property>
       </bean>
   </util:list>
   ```

2. Insert into `conf/ldap.properties` the properties added into `conf/authn/password-authn-config.xml`:
   ```xml
   # AD 1 authentication configuration properties:
   # - conf/authn/password-authn-config.xml         (LDAP chaining)
   # - conf/ldap.properties                         (LDAP properties)
   idp.authn.LDAP.ldapURL.1                          = ldap://<URL-AD-1>:389
   idp.authn.LDAP.baseDN.1                           = ou=people-1,dc=example,dc=org
   idp.authn.LDAP.bindDN.1                           = cn=admin-1,dc=people,dc=example,dc=org
   idp.authn.LDAP.userFilter.1                       = (sAMAccountName={user})
   idp.authn.LDAP.dnFormat.1                         = %s@example.org

   # AD 2 authentication configuration properties:
   # - conf/authn/password-authn-config.xml         (LDAP chaining)
   # - conf/ldap.properties                         (LDAP properties)
   idp.authn.LDAP.ldapURL.2                          = ldap://<URL-AD-2>:389
   idp.authn.LDAP.baseDN.2                           = ou=people-2,dc=example,dc=org
   idp.authn.LDAP.bindDN.2                           = cn=admin-2,ou=people,dc=example,dc=org
   idp.authn.LDAP.userFilter.2                       = (mail={user})
   idp.authn.LDAP.dnFormat.2                         = %s@example.org

   # AD authentication common properties (1 and 2 share them on this example):
   idp.authn.LDAP.authenticator                    = bindSearchAuthenticator
   idp.authn.LDAP.useStartTLS                      = false
   idp.authn.LDAP.returnAttributes                 = passwordExpirationTime,loginGraceRemaining      ## Return attributes during authentication
   idp.authn.LDAP.connectTimeout                   = PT3S     # Time in milliseconds that connects will block
   idp.authn.LDAP.responseTimeout                  = PT3S     # Time in milliseconds to wait for responses
   idp.authn.LDAP.subtreeSearch                    = true

   # AD 1 DataConnector configuration on conf/attribute-resolver.xml
   idp.attribute.resolver.LDAP.ldapURL.1             = %{idp.authn.LDAP.ldapURL.1}
   idp.attribute.resolver.LDAP.connectTimeout.1      = %{idp.authn.LDAP.connectTimeout:PT3S}
   idp.attribute.resolver.LDAP.responseTimeout.1     = %{idp.authn.LDAP.responseTimeout:PT3S}
   idp.attribute.resolver.LDAP.baseDN.1              = %{idp.authn.LDAP.baseDN.1:undefined}
   idp.attribute.resolver.LDAP.bindDN.1              = %{idp.authn.LDAP.bindDN.1:undefined}
   idp.attribute.resolver.LDAP.useStartTLS.1         = %{idp.authn.LDAP.useStartTLS:true}
   idp.attribute.resolver.LDAP.searchFilter.1        = (uid=$resolutionContext.principal)

   # AD 2 DataConnector configuration on conf/attribute-resolver.xml
   idp.attribute.resolver.LDAP.ldapURL.2             = %{idp.authn.LDAP.ldapURL.2}
   idp.attribute.resolver.LDAP.connectTimeout.2      = %{idp.authn.LDAP.connectTimeout:PT3S}
   idp.attribute.resolver.LDAP.responseTimeout.2     = %{idp.authn.LDAP.responseTimeout:PT3S}
   idp.attribute.resolver.LDAP.baseDN.2              = %{idp.authn.LDAP.baseDN.2:undefined}
   idp.attribute.resolver.LDAP.bindDN.2              = %{idp.authn.LDAP.bindDN.2:undefined}
   idp.attribute.resolver.LDAP.useStartTLS.2         = %{idp.authn.LDAP.useStartTLS:true}
   idp.attribute.resolver.LDAP.searchFilter.2        = (mail=$resolutionContext.principal)

   # AD Common exportAttribute configuration for LDAP-1 and LDAP-2 on attribute-resolver.xml
   idp.attribute.resolver.LDAP.exportAttributes.1    = sAMAccountName givenName sn cn mail displayName mobile title preferredLanguage telephoneNumber eduPersonAffiliation eduPersonEntitlement eduPersonOrgDN eduPersonOrgUnitDN eduPersonOrcid schacMotherTongue schacPersonalTitle schacUserPresenceID schacPersonalUniqueID schacPersonalPositon 
   ```

3. Insert into `credentials/secrets.properties` the new credential:
   ```xml
   # LDAP 1 access to authn and attribute stores.
   idp.authn.LDAP.bindDNCredential.1              = <PASSWORD-AD-USER-1>
   idp.attribute.resolver.LDAP.bindDNCredential.1 = %{idp.authn.LDAP.bindDNCredential.1:undefined}

   # LDAP 2 access to authn and attribute stores.
   idp.authn.LDAP.bindDNCredential.2              = <PASSWORD-AD-USER-2>
   idp.attribute.resolver.LDAP.bindDNCredential.2 = %{idp.authn.LDAP.bindDNCredential.2:undefined}
   ```

4. Change the `attribute-resolver.xml` by adding the new `<DataConnector>`:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>

   <AttributeResolver
           xmlns="urn:mace:shibboleth:2.0:resolver"
           xmlns:sec="urn:mace:shibboleth:2.0:security"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="urn:mace:shibboleth:2.0:resolver http://shibboleth.net/schema/idp/shibboleth-attribute-resolver.xsd
                               urn:mace:shibboleth:2.0:security http://shibboleth.net/schema/idp/shibboleth-security.xsd">

       <!-- ========================================== -->
       <!--      Attribute Definitions                 -->
       <!-- ========================================== -->

       <AttributeDefinition scope="%{idp.scope}" xsi:type="Scoped" id="eduPersonScopedAffiliation">
           <InputDataConnector ref="AD-1" attributeNames="eduPersonAffiliation" />
           <InputDataConnector ref="AD-2" attributeNames="eduPersonAffiliation" />
       </AttributeDefinition>

       <AttributeDefinition scope="%{idp.scope}" xsi:type="Scoped" id="eduPersonPrincipalName">
           <InputDataConnector ref="AD-1" attributeNames="%{idp.persistentId.sourceAttribute}" />
           <InputDataConnector ref="AD-2" attributeNames="%{idp.persistentId.sourceAttribute}" />
       </AttributeDefinition>

       <!-- AttributeDefinition for eduPersonTargetedID - Computed Mode -->
       <AttributeDefinition xsi:type="SAML2NameID" nameIdFormat="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" id="eduPersonTargetedID">
           <InputDataConnector ref="myComputedId" attributeNames="computedID"/>
       </AttributeDefinition>

       <!-- AttributeDefinition for eduPersonTargetedID - Stored Mode -->
       <!--
       <AttributeDefinition xsi:type="SAML2NameID" nameIdFormat="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" id="eduPersonTargetedID">
           <InputDataConnector ref="myStoredId" attributeNames="persistentID" />
       </AttributeDefinition>
       -->

       <AttributeDefinition xsi:type="Simple" id="schacHomeOrganization">
           <InputDataConnector ref="staticAttributes" attributeNames="schacHomeOrganization"/>
       </AttributeDefinition>

       <AttributeDefinition xsi:type="Simple" id="schacHomeOrganizationType">
           <InputDataConnector ref="staticAttributes" attributeNames="schacHomeOrganizationType"/>
       </AttributeDefinition>

       <!-- ========================================== -->
       <!--      Data Connectors                       -->
       <!-- ========================================== -->

       <!-- AD 1 DataConnector -->
       <DataConnector id="AD-1" xsi:type="LDAPDirectory"
           ldapURL="%{idp.attribute.resolver.LDAP.ldapURL.1}"
           baseDN="%{idp.attribute.resolver.LDAP.baseDN.1}"
           principal="%{idp.attribute.resolver.LDAP.bindDN.1}"
           principalCredential="%{idp.attribute.resolver.LDAP.bindDNCredential.1}"
           useStartTLS="%{idp.attribute.resolver.LDAP.useStartTLS.1:true}"
           connectTimeout="%{idp.attribute.resolver.LDAP.connectTimeout}"
           responseTimeout="%{idp.attribute.resolver.LDAP.responseTimeout}"
           exportAttributes="%{idp.attribute.resolver.LDAP.exportAttributes.1}">
           <FailoverDataConnector ref="LDAP-2" />
           <FilterTemplate>
               <![CDATA[
                   %{idp.attribute.resolver.LDAP.searchFilter.1}
               ]]>
           </FilterTemplate>
           <ConnectionPool
               minPoolSize="%{idp.pool.LDAP.minSize:3}"
               maxPoolSize="%{idp.pool.LDAP.maxSize:10}"
               blockWaitTime="%{idp.pool.LDAP.blockWaitTime:PT3S}"
               validatePeriodically="%{idp.pool.LDAP.validatePeriodically:true}"
               validateTimerPeriod="%{idp.pool.LDAP.validatePeriod:PT5M}"
               validateDN="%{idp.pool.LDAP.validateDN:}"
               validateFilter="%{idp.pool.LDAP.validateFilter:(objectClass=*)}"
               expirationTime="%{idp.pool.LDAP.idleTime:PT10M}"/>

       </DataConnector>

       <!-- AD 2 DataConnector -->
       <DataConnector id="AD-2" xsi:type="LDAPDirectory"
           ldapURL="%{idp.attribute.resolver.LDAP.ldapURL.2}"
           baseDN="%{idp.attribute.resolver.LDAP.baseDN.2}"
           principal="%{idp.attribute.resolver.LDAP.bindDN.2}"
           principalCredential="%{idp.attribute.resolver.LDAP.bindDNCredential.2}"
           useStartTLS="%{idp.attribute.resolver.LDAP.useStartTLS.2:true}"
           connectTimeout="%{idp.attribute.resolver.LDAP.connectTimeout.2}"
           responseTimeout="%{idp.attribute.resolver.LDAP.responseTimeout.2}"
           exportAttributes="%{idp.attribute.resolver.LDAP.exportAttributes.2:}">
           <FilterTemplate>
               <![CDATA[
                   %{idp.attribute.resolver.LDAP.searchFilter}
               ]]>
           </FilterTemplate>
           <ConnectionPool
               minPoolSize="%{idp.pool.LDAP.minSize:3}"
               maxPoolSize="%{idp.pool.LDAP.maxSize:10}"
               blockWaitTime="%{idp.pool.LDAP.blockWaitTime:PT3S}"
               validatePeriodically="%{idp.pool.LDAP.validatePeriodically:true}"
               validateTimerPeriod="%{idp.pool.LDAP.validatePeriod:PT5M}"
               validateDN="%{idp.pool.LDAP.validateDN:}"
               validateFilter="%{idp.pool.LDAP.validateFilter:(objectClass=*)}"
               expirationTime="%{idp.pool.LDAP.idleTime:PT10M}"/>

       </DataConnector>

       <!--  Data Connector for eduPersonTargetedID - Computed Mode  -->
       <DataConnector id="myComputedId" xsi:type="ComputedId" 
                      generatedAttributeID="computedID" 
                      salt="%{idp.persistentId.salt}" 
                      algorithm="%{idp.persistentId.algorithm:SHA}"
                      encoding="%{idp.persistentId.encoding:BASE32}">

           <InputDataConnector ref="AD-1" attributeNames="%{idp.persistentId.sourceAttribute}"/>
           <InputDataConnector ref="AD-2" attributeNames="%{idp.persistentId.sourceAttribute}"/>
       </DataConnector>

       <!--  Data Connector for eduPersonTargetedID - Stored Mode  -->
       <!-- 
       <DataConnector id="stored" xsi:type="StoredId"
           generatedAttributeID="storedId"
           salt="%{idp.persistentId.salt}"
           queryTimeout="0">

           <InputDataConnector ref="AD-1" attributeNames="%{idp.persistentId.sourceAttribute}"/>
           <InputDataConnector ref="AD-2" attributeNames="%{idp.persistentId.sourceAttribute}"/>

           <BeanManagedConnection>MyDataSource</BeanManagedConnection>
       </DataConnector>
       -->
     
       <!--  Example Data Connector for static attributes  -->
       <DataConnector id="staticAttributes" xsi:type="Static">
          <Attribute id="schacHomeOrganization">
             <Value>%{idp.scope}</Value>
          </Attribute>
          <!--  One of the values defined here:
                https://wiki.refeds.org/pages/viewpage.action?pageId=44957715#SCHACURNRegistry-homeOrganizationType
          -->
          <Attribute id="schacHomeOrganizationType">
             <Value>urn:schac:homeOrganizationType:eu:higherEducationalInstitution</Value>
          </Attribute>
      </DataConnector>
     
   </AttributeResolver>
   ```

5. Restart Jetty to apply:
   * `sudo systemctl restart jetty`

## Authors

### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
