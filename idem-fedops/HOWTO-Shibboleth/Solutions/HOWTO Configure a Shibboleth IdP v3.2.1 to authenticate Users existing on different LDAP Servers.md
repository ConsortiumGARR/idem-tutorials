# HOWTO Configure a Shibboleth IdP v3.2.1 to authenticate users existing on different LDAP Servers

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements)
2. [OpenLDAP Case connected with bindSearchAuthenticator](#openldap-case-connected-with-bindSearchAuthenticator)
3. [Authors](#authors)

## Requirements

* A machine with Shibboleth v3.2.1 installed

## OpenLDAP Case connected with bindSearchAuthenticator

1. Copy ```ldap.properties``` into ```ldap2.properties```:

   `cp /opt/shibboleth-idp/conf/ldap.properties /opt/shibboleth-idp/conf/ldap2.properties`

2. Modify `idp.properties` and include `ldap2.properties` into the list

   `vim /opt/shibboleth-idp/conf/idp.properties`:
   
   ```
   # Load any additional property resources from a comma-delimited list
   idp.additionalProperties= /conf/ldap.properties, /conf/ldap2.properties, /conf/saml-nameid.properties, /conf/services.properties
   ```

3. Copy `authn/ldap-authn-config.xml` into `authn/ldap-authn-config-2.xml`.

4. Modify the new `authn/ldap-authn-config-2.xml`.
   The complete example show you how connect together 2 openLDAP with the `bindSearchAuthenticator` and the `certificateTrust` (no jvmTrust or keyStoreTrust)

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <beans xmlns="http://www.springframework.org/schema/beans"
          xmlns:context="http://www.springframework.org/schema/context"
          xmlns:util="http://www.springframework.org/schema/util"
          xmlns:p="http://www.springframework.org/schema/p"
          xmlns:c="http://www.springframework.org/schema/c"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd
                              http://www.springframework.org/schema/context http://www.springframework.org/schema/context/spring-context.xsd
                              http://www.springframework.org/schema/util http://www.springframework.org/schema/util/spring-util.xsd"
   
          default-init-method="initialize"
          default-destroy-method="destroy"
          default-lazy-init="true">
   
       <!-- NEW Aggregate Authenticator 
         idp.authn.LDAP.authenticator = aggregateAuthenticator
         idp.authn.LDAP.returnAttributes = 1.1
       -->
       <bean id="aggregateAuthenticator" class="org.ldaptive.auth.Authenticator"
         c:resolver-ref="aggregateDnResolver"
         c:handler-ref="aggregateAuthHandler" />
   
       <!-- Aggregate DN resolution -->
       <bean id="aggregateDnResolver" class="org.ldaptive.auth.AggregateDnResolver"
             c:resolvers-ref="dnResolvers"
             p:allowMultipleDns="true" />
       <util:map id="dnResolvers">
          <entry key="ldap1" value-ref="bindSearchDnResolver1" />
          <entry key="ldap2" value-ref="bindSearchDnResolver2" />
       </util:map>
   
       <alias name="%{idp.authn.LDAP.authenticator.1:anonSearchAuthenticator}" alias="shibboleth.authn.LDAP.authenticator" />
   
       <bean id="shibboleth.authn.LDAP.returnAttributes" parent="shibboleth.CommaDelimStringArray">
           <constructor-arg type="java.lang.String" value="%{idp.authn.LDAP.returnAttributes.1:1.1}" />
       </bean>
   
       <alias name="ValidateUsernamePasswordAgainstLDAP" alias="ValidateUsernamePassword" />
   
       <!-- LDAP 1 - BindAuthenticator
   
          idp.authn.LDAP.ldapURL.1 = undefined
          idp.authn.LDAP.useStartTLS.1 = true
          idp.authn.LDAP.useSSL.1 = false
          idp.authn.LDAP.connectionTimeout.1 = 3000
          idp.authn.LDAP.sslConfig.1 = certificateTrust1
          idp.authn.LDAP.trustCertificates.1 = undefined
          idp.authn.LDAP.dnFormat.1 = undefined
          idp.authn.LDAP.baseDN.1 = undefined
          idp.authn.ldap.subtreesearch.1 = false
          idp.authn.LDAP.userFilter.1 = undefined
          idp.authn.LDAP.bindDN.1 = undefined
          idp.authn.LDAP.bindDNCredential.1 = undefined
   
       -->
   
       <!-- Connection Configuration -->
       <bean id="connectionConfig1" class="org.ldaptive.ConnectionConfig" abstract="true" p:ldapUrl="%{idp.authn.LDAP.ldapURL.1:undefined}"
           p:useStartTLS="%{idp.authn.LDAP.useStartTLS.1:true}"
           p:useSSL="%{idp.authn.LDAP.useSSL.1:false}"
           p:connectTimeout="%{idp.authn.LDAP.connectTimeout.1:3000}"
           p:sslConfig-ref="sslConfig1" />
   
       <alias name="%{idp.authn.LDAP.sslConfig.1:certificateTrust1}" alias="sslConfig1" />
   
       <bean id="certificateTrust1" class="org.ldaptive.ssl.SslConfig">
           <property name="credentialConfig">
               <bean parent="shibboleth.X509ResourceCredentialConfig" p:trustCertificates="%{idp.authn.LDAP.trustCertificates.1:undefined}" />
           </property>
       </bean>
   
       <!-- Authentication handler -->
   
       <!-- Aggregate authentication -->
       <bean id="aggregateAuthHandler" class="org.ldaptive.auth.AggregateDnResolver$AuthenticationHandler"
             p:authenticationHandlers-ref="authHandlers" />
       <util:map id="authHandlers">
          <entry key="ldap1" value-ref="authHandler1" />
          <entry key="ldap2" value-ref="authHandler2" />
       </util:map>
   
       <bean id="authHandler1" class="org.ldaptive.auth.PooledBindAuthenticationHandler" p:connectionFactory-ref="bindPooledConnectionFactory1" />
       <bean id="bindPooledConnectionFactory1" class="org.ldaptive.pool.PooledConnectionFactory" p:connectionPool-ref="bindConnectionPool1" />
       <bean id="bindConnectionPool1" class="org.ldaptive.pool.BlockingConnectionPool" parent="connectionPool1"
           p:connectionFactory-ref="bindConnectionFactory1" p:name="bind-pool" />
       <bean id="bindConnectionFactory1" class="org.ldaptive.DefaultConnectionFactory" p:connectionConfig-ref="bindConnectionConfig1" />
       <bean id="bindConnectionConfig1" parent="connectionConfig1" />
   
       <!-- Pool Configuration -->
       <bean id="connectionPool1" class="org.ldaptive.pool.BlockingConnectionPool" abstract="true"
           p:blockWaitTime="%{idp.pool.LDAP.blockWaitTime.1:3000}"
           p:poolConfig-ref="poolConfig1"
           p:pruneStrategy-ref="pruneStrategy1"
           p:validator-ref="searchValidator1"
           p:failFastInitialize="%{idp.pool.LDAP.failFastInitialize.1:false}" />
       <bean id="poolConfig1" class="org.ldaptive.pool.PoolConfig"
           p:minPoolSize="%{idp.pool.LDAP.minSize.1:3}"
           p:maxPoolSize="%{idp.pool.LDAP.maxSize.1:10}"
           p:validateOnCheckOut="%{idp.pool.LDAP.validateOnCheckout.1:false}"
           p:validatePeriodically="%{idp.pool.LDAP.validatePeriodically.1:true}"
           p:validatePeriod="%{idp.pool.LDAP.validatePeriod.1:300}" />
       <bean id="pruneStrategy1" class="org.ldaptive.pool.IdlePruneStrategy"
           p:prunePeriod="%{idp.pool.LDAP.prunePeriod.1:300}"
           p:idleTime="%{idp.pool.LDAP.idleTime.1:600}" />
       <bean id="searchValidator1" class="org.ldaptive.pool.SearchValidator" />
   
       <!-- Bind Search Configuration -->
       <bean name="bindSearchAuthenticator1" class="org.ldaptive.auth.Authenticator" p:resolveEntryOnFailure="%{idp.authn.LDAP.resolveEntryOnFailure.1:false}">
           <constructor-arg index="0" ref="bindSearchDnResolver1" />
           <constructor-arg index="1" ref="authHandler1" />
       </bean>
       <bean id="bindSearchDnResolver1" class="org.ldaptive.auth.PooledSearchDnResolver"
           p:baseDn="#{'%{idp.authn.LDAP.baseDN.1:undefined}'.trim()}"
           p:subtreeSearch="%{idp.authn.LDAP.subtreeSearch.1:false}"
           p:userFilter="#{'%{idp.authn.LDAP.userFilter.1:undefined}'.trim()}"
           p:connectionFactory-ref="bindSearchPooledConnectionFactory1" />
       <bean id="bindSearchPooledConnectionFactory1" class="org.ldaptive.pool.PooledConnectionFactory"
           p:connectionPool-ref="bindSearchConnectionPool1" />
       <bean id="bindSearchConnectionPool1" class="org.ldaptive.pool.BlockingConnectionPool" parent="connectionPool1"
           p:connectionFactory-ref="bindSearchConnectionFactory1" p:name="search-pool" />
       <bean id="bindSearchConnectionFactory1" class="org.ldaptive.DefaultConnectionFactory" p:connectionConfig-ref="bindSearchConnectionConfig1" />
       <bean id="bindSearchConnectionConfig1" parent="connectionConfig1" p:connectionInitializer-ref="bindConnectionInitializer1" />
       <bean id="bindConnectionInitializer1" class="org.ldaptive.BindConnectionInitializer"
               p:bindDn="#{'%{idp.authn.LDAP.bindDN.1:undefined}'.trim()}">
           <property name="bindCredential">
               <bean class="org.ldaptive.Credential">
                   <constructor-arg value="%{idp.authn.LDAP.bindDNCredential.1:undefined}" />
               </bean>
           </property>
       </bean>
   
       <!-- Want to use ppolicy? Configure support by adding <bean id="authenticationResponseHandler" class="org.ldaptive.auth.ext.PasswordPolicyAuthenticationResponseHandler"
           /> add p:authenticationResponseHandlers-ref="authenticationResponseHandler" to the authenticator <bean id="authenticationControl"
           class="org.ldaptive.control.PasswordPolicyControl" /> add p:authenticationControls-ref="authenticationControl" to the authHandler -->
   
       <!-- LDAP 2 - BindAuthenticator
   
          idp.authn.LDAP.ldapURL.2 = undefined
          idp.authn.LDAP.useStartTLS.2 = true
          idp.authn.LDAP.useSSL.2 = false
          idp.authn.LDAP.connectionTimeout.2 = 3000
          idp.authn.LDAP.sslConfig.2 = certificateTrust2
          idp.authn.LDAP.trustCertificates.2 = undefined
          idp.authn.LDAP.dnFormat.2 = undefined
          idp.authn.LDAP.baseDN.2 = undefined
          idp.authn.ldap.subtreesearch.2 = false
          idp.authn.LDAP.userFilter.2 = undefined
          idp.authn.LDAP.bindDN.2 = undefined
          idp.authn.LDAP.bindDNCredential.2 = undefined
   
       -->
       
       <!-- Connection Configuration -->
       <bean id="connectionConfig2" class="org.ldaptive.ConnectionConfig" abstract="true" p:ldapUrl="%{idp.authn.LDAP.ldapURL.2:undefined}"
           p:useStartTLS="%{idp.authn.LDAP.useStartTLS.2:true}"
           p:useSSL="%{idp.authn.LDAP.useSSL.2:false}"
           p:connectTimeout="%{idp.authn.LDAP.connectTimeout.2:3000}"
           p:sslConfig-ref="sslConfig2" />
   
       <alias name="%{idp.authn.LDAP.sslConfig.2:certificateTrust2}" alias="sslConfig2" />
   
       <bean id="certificateTrust2" class="org.ldaptive.ssl.SslConfig">
           <property name="credentialConfig">
               <bean parent="shibboleth.X509ResourceCredentialConfig" p:trustCertificates="%{idp.authn.LDAP.trustCertificates.2:undefined}" />
           </property>
       </bean>
   
       <!-- Authentication handler -->
       <bean id="authHandler2" class="org.ldaptive.auth.PooledBindAuthenticationHandler" p:connectionFactory-ref="bindPooledConnectionFactory2" />
       <bean id="bindPooledConnectionFactory2" class="org.ldaptive.pool.PooledConnectionFactory" p:connectionPool-ref="bindConnectionPool2" />
       <bean id="bindConnectionPool2" class="org.ldaptive.pool.BlockingConnectionPool" parent="connectionPool2"
           p:connectionFactory-ref="bindConnectionFactory2" p:name="bind-pool" />
       <bean id="bindConnectionFactory2" class="org.ldaptive.DefaultConnectionFactory" p:connectionConfig-ref="bindConnectionConfig2" />
       <bean id="bindConnectionConfig2" parent="connectionConfig2" />
   
       <!-- Pool Configuration -->
       <bean id="connectionPool2" class="org.ldaptive.pool.BlockingConnectionPool" abstract="true"
           p:blockWaitTime="%{idp.pool.LDAP.blockWaitTime.2:3000}"
           p:poolConfig-ref="poolConfig2"
           p:pruneStrategy-ref="pruneStrategy2"
           p:validator-ref="searchValidator2"
           p:failFastInitialize="%{idp.pool.LDAP.failFastInitialize.2:false}" />
       <bean id="poolConfig2" class="org.ldaptive.pool.PoolConfig"
           p:minPoolSize="%{idp.pool.LDAP.minSize.2:3}"
           p:maxPoolSize="%{idp.pool.LDAP.maxSize.2:10}"
           p:validateOnCheckOut="%{idp.pool.LDAP.validateOnCheckout.2:false}"
           p:validatePeriodically="%{idp.pool.LDAP.validatePeriodically.2:true}"
           p:validatePeriod="%{idp.pool.LDAP.validatePeriod.2:300}" />
       <bean id="pruneStrategy2" class="org.ldaptive.pool.IdlePruneStrategy"
           p:prunePeriod="%{idp.pool.LDAP.prunePeriod.2:300}"
           p:idleTime="%{idp.pool.LDAP.idleTime.2:600}" />
       <bean id="searchValidator2" class="org.ldaptive.pool.SearchValidator" />
   
       <!-- Bind Search Configuration -->
       <bean name="bindSearchAuthenticator2" class="org.ldaptive.auth.Authenticator" p:resolveEntryOnFailure="%{idp.authn.LDAP.resolveEntryOnFailure.2:false}">
           <constructor-arg index="0" ref="bindSearchDnResolver2" />
           <constructor-arg index="1" ref="authHandler2" />
       </bean>
       <bean id="bindSearchDnResolver2" class="org.ldaptive.auth.PooledSearchDnResolver"
           p:baseDn="#{'%{idp.authn.LDAP.baseDN.2:undefined}'.trim()}"
           p:subtreeSearch="%{idp.authn.LDAP.subtreeSearch.2:false}"
           p:userFilter="#{'%{idp.authn.LDAP.userFilter.2:undefined}'.trim()}"
           p:connectionFactory-ref="bindSearchPooledConnectionFactory2" />
       <bean id="bindSearchPooledConnectionFactory2" class="org.ldaptive.pool.PooledConnectionFactory"
           p:connectionPool-ref="bindSearchConnectionPool2" />
       <bean id="bindSearchConnectionPool2" class="org.ldaptive.pool.BlockingConnectionPool" parent="connectionPool2"
           p:connectionFactory-ref="bindSearchConnectionFactory2" p:name="search-pool" />
       <bean id="bindSearchConnectionFactory2" class="org.ldaptive.DefaultConnectionFactory" p:connectionConfig-ref="bindSearchConnectionConfig2" />
       <bean id="bindSearchConnectionConfig2" parent="connectionConfig2" p:connectionInitializer-ref="bindConnectionInitializer2" />
       <bean id="bindConnectionInitializer2" class="org.ldaptive.BindConnectionInitializer"
               p:bindDn="#{'%{idp.authn.LDAP.bindDN.2:undefined}'.trim()}">
           <property name="bindCredential">
               <bean class="org.ldaptive.Credential">
                   <constructor-arg value="%{idp.authn.LDAP.bindDNCredential.2:undefined}" />
               </bean>
           </property>
       </bean>
   
       <!-- Want to use ppolicy? Configure support by adding <bean id="authenticationResponseHandler" class="org.ldaptive.auth.ext.PasswordPolicyAuthenticationResponseHandler"
           /> add p:authenticationResponseHandlers-ref="authenticationResponseHandler" to the authenticator <bean id="authenticationControl"
           class="org.ldaptive.control.PasswordPolicyControl" /> add p:authenticationControls-ref="authenticationControl" to the authHandler -->
   
   </beans>
   ```

5. Modify `authn/password-auth-config.xml` by importing the new `ldap-authn-config-2.xml` and by commenting out the previous one.

6. Modify the files `ldap.properties` and `ldap2.properties` in a way that the variables match with their names provided by `ldap-authn-config-2.xml`
(the variable will remain `idp.authn.LDAP.authenticator = aggregateAuthenticator`)

7. Open and modify the `attribute-resolver-v3-idem.xml` used:

   * `vim /opt/shibboleth-idp/conf/attribute-resolver-v3-idem.xml`

   ```xml
   <!-- Add the Dependency with ref="myLDAP-2" to all AttributeDefinition -->
   <!-- Example
       <resolver:AttributeDefinition xsi:type="ad:Simple" id="uid" sourceAttributeID="uid">
           <resolver:Dependency ref="myLDAP" />
           <resolver:Dependency ref="myLDAP-2" />
           <resolver:AttributeEncoder xsi:type="enc:SAML1String" name="urn:mace:dir:attribute-def:uid" encodeType="false" />
           <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:0.9.2342.19200300.100.1.1" friendlyName="uid" encodeType="false" />
       </resolver:AttributeDefinition>
   Example -->
   
       <!-- Example LDAP Connector 1 - with FailoverDataConnector that redirect on the LDAP Connector 2 in case of failure -->
       <resolver:DataConnector id="myLDAP" xsi:type="dc:LDAPDirectory"
           ldapURL="%{idp.attribute.resolver.LDAP.ldapURL.1}"
           baseDN="%{idp.attribute.resolver.LDAP.baseDN.1}"
           principal="%{idp.attribute.resolver.LDAP.bindDN.1}"
           principalCredential="%{idp.attribute.resolver.LDAP.bindDNCredential.1}"
           useStartTLS="%{idp.attribute.resolver.LDAP.useStartTLS.1:true}">
   
           <resolver:FailoverDataConnector ref="myLDAP-2" />
   
           <dc:FilterTemplate>
               <![CDATA[
                   %{idp.attribute.resolver.LDAP.searchFilter.1}
               ]]>
           </dc:FilterTemplate>
           <dc:StartTLSTrustCredential id="LDAPtoIdPCredential" xsi:type="sec:X509ResourceBacked">
               <sec:Certificate>%{idp.attribute.resolver.LDAP.trustCertificates.1}</sec:Certificate>
           </dc:StartTLSTrustCredential>
   
       </resolver:DataConnector>
   
       <!-- Example LDAP Connector 2 - WITHOUT FailoverDataConnector -->
       <resolver:DataConnector id="myLDAP-2" xsi:type="dc:LDAPDirectory"
           ldapURL="%{idp.attribute.resolver.LDAP.ldapURL.2}"
           baseDN="%{idp.attribute.resolver.LDAP.baseDN.2}"
           principal="%{idp.attribute.resolver.LDAP.bindDN.2}"
           principalCredential="%{idp.attribute.resolver.LDAP.bindDNCredential.2}"
           useStartTLS="%{idp.attribute.resolver.LDAP.useStartTLS.2:true}">
           <dc:FilterTemplate>
               <![CDATA[
                   %{idp.attribute.resolver.LDAP.searchFilter.2}
               ]]>
           </dc:FilterTemplate>
   <!-- Needed only if you use certificateTrust
           <dc:StartTLSTrustCredential id="LDAP_2toIdPCredential" xsi:type="sec:X509ResourceBacked">
               <sec:Certificate>%{idp.attribute.resolver.LDAP.trustCertificates.2}</sec:Certificate>
           </dc:StartTLSTrustCredential>
   -->
       </resolver:DataConnector>
   ```

8. Restart Tomcat to apply the changes.

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
