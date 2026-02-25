# HOWTO Configure Shibboleth IdP v4.x for Office 365

## Index

1. [Instructions](#instructions)
2. [Utilities](#utilities)
   1. [Unsupportable identifier format](#unsupportable-identifier-format) 

## Instructions

Reference: https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-fed-saml-idp

1. Into `conf/relying-party.xml`, under `<util:list id="shibboleth.RelyingPartyOverrides">`, add the following `<bean>`:
   ```xml
   <bean id="Office365" parent="RelyingPartyByName" c:relyingPartyIds="urn:federation:MicrosoftOnline">
      <property name="profileConfigurations">
         <list>
            <bean parent="SAML2.SSO" p:encryptAssertions="false" p:signAssertions="true" p:signResponses="false" />
            <bean parent="SAML2.ECP" p:encryptAssertions="false" p:signAssertions="true" p:signResponses="false" p:nameIDFormatPrecedence="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" />
         </list>
      </property>
   </bean>
   ```

2. Into `conf/saml-nameid.xml`, inside the `<util:list id="shibboleth.SAML2NameIDGenerators">` list, insert:
   ```xml
   <!-- Uncommenting this bean requires configuration in saml-nameid.properties. -->
   <!--<ref bean="shibboleth.SAML2PersistentGenerator" />-->
	
   <!-- Release Persistent NameID to all but not to MicrosoftOnline-->
   <bean parent="shibboleth.SAML2PersistentGenerator">
      <property name="activationCondition">
         <bean parent="shibboleth.Conditions.NOT">
            <constructor-arg>
               <bean parent="shibboleth.Conditions.RelyingPartyId" c:candidate="urn:federation:MicrosoftOnline" />
            </constructor-arg>
         </bean>
      </property>
   </bean>

   <!-- Microsoft custom Persistent ID Generator -->
   <bean parent="shibboleth.SAML2AttributeSourcedGenerator"
         p:omitQualifiers="true"
         p:format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"
         p:attributeSourceIds="#{ {'ImmutableID'} }">
      <property name="activationCondition">
         <bean parent="shibboleth.Conditions.RelyingPartyId" c:candidate="urn:federation:MicrosoftOnline" />
      </property>
   </bean>
   ```

3. Into `conf/attribute-resolver.xml`, create the following `<AttributeDefinition>` to be able to generate the ImmutableID (`ImmutableID`) attribute and the User ID (`UserId`) scoped attribute starting from the `uid` attribute (`uid` and `objectGUID` must be part of the `exportAttributes` list on the `ldap.properties` configuration file)
   ```xml
   <!--  Microsoft Office365 - Azure AD ImmutableID & User ID  -->
   <AttributeDefinition xsi:type="Simple" id="ImmutableID">
      <InputDataConnector ref="myLDAP" attributeNames="objectGUID"/>
   </AttributeDefinition>
   
   <AttributeDefinition scope="%{idp.scope}" xsi:type="Scoped" id="IDPEmail">
      <InputDataConnector ref="myLDAP" attributeNames="uid"/>
    </AttributeDefinition>
   ```

4. Create `conf/attributes/custom/ImmutableID.properties`  as follow (the example considers italian and english languages only):
   ```properties
   # Azure AD ImmutableID (objectGUID)

   id=ImmutableID
   transcoder=SAML2StringTranscoder
   displayName.en=Azure AD ImmutableID
   displayName.it=Azure AD ImmutableID
   description.en=Azure AD ImmutableID
   description.it=Azure AD ImmutableID
   saml2.name=urn:oid:1.2.840.113556.1.4.2
   saml2.encodeType=false
   ```
   
5. Create `conf/attributes/custom/IDPEmail.properties` as follow (the example considers italian and english languages only):
   ```properties
   # Azure AD IDPEmail

   id=IDPEmail
   transcoder=SAML2ScopedStringTranscoder
   displayName.en=Azure AD IDPEmail
   displayName.it=Azure AD IDPEmail
   saml2.name=IDPEmail
   saml2.friendlyName=
   saml2.nameFormat=
   saml2.encodeType=false
   ```

6. Create Office 365 metadata:
   * `wget https://nexus.microsoftonline-p.com/federationmetadata/saml20/federationmetadata.xml -O /opt/shibboleth-idp/metadata/office365-md.xml`
   
7. Into `conf/metadata-providers.xml` add the Office 365 metadata:
   ```xml
   <MetadataProvider id="Office365" xsi:type="FilesystemMetadataProvider" metadataFile="%{idp.home}/metadata/office365-md.xml"/>
   ```
   
8. Into `conf/attribute-filter.xml`, configure the attribute release:
   ```xml
   <!-- Attribute Filter Policy for Microsoft Office365/Azure -->
   <AttributeFilterPolicy id="PolicyForWindowsAzureAD">
      <PolicyRequirementRule xsi:type="Requester" value="urn:federation:MicrosoftOnline" />

      <!-- Release userPrincipalName as Azure AD User ID -->
      <AttributeRule attributeID="IDPEmail">
         <PermitValueRule xsi:type="ANY"/>
      </AttributeRule>

      <!-- Release Immutable ID to Azure AD -->
      <AttributeRule attributeID="ImmutableID">
         <PermitValueRule xsi:type="ANY"/>
      </AttributeRule>

   </AttributeFilterPolicy>
   ```

9. Test with AACLI:
   `bash /opt/shibboleth-idp/bin/aacli.sh -n <REPLACE_WITH_USERNAME_IDP> -r urn:federation:MicrosoftOnline --saml2`

## Utilities

### Unsupportable identifier format

If the Shibboleth IdP returns an error like:

```
WARN [org.opensaml.saml.saml2.profile.impl.AddNameIDToSubjects:334] - Profile Action AddNameIDToSubjects: Request specified use of an unsupportable identifier format: urn:oasis:names:tc:SAML:2.0:nameid-format:persistent
WARN [org.opensaml.profile.action.impl.LogEvent:101] - A non-proceed event occurred while processing the request: InvalidNameIDPolicy
```
   
try to run AACLI for the Microsoft resource:
   
`bash /opt/shibboleth-idp/bin/aacli.sh -n <USERNAME> -r urn:federation:MicrosoftOnline  --saml2`
   
by replacing `<USERNAME>` with the username of a real user.
   
This will help to discover what kind of NameID the IDP is releasing to the SP.
   
If the NameID released is the `transient` one, check the Microsoft SP metadata and remove the `transient` `<md:NameIDFormat>` element from it before trying again.
