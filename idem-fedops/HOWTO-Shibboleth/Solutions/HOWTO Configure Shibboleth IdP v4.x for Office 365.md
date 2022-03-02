# HOWTO Configure Shibboleth IdP v4.x for Office 365

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

3. Into `conf/attribute-resolver.xml`, create the following `<AttributeDefinition>` to be able to generate the Google Principal (`GPrincipal`) attribute (if it is not already present into your LDAP directory):
   ```xml
   <!--  Microsoft Office365 - Azure AD ImmutableID & User ID  -->
   <AttributeDefinition xsi:type="Simple" id="ImmutableID">
      <InputDataConnector ref="myLDAP" attributeNames="uid"/>
   </AttributeDefinition>
   
   <AttributeDefinition scope="%{idp.scope}" xsi:type="Scoped" id="UserId">
      <InputDataConnector ref="myLDAP" attributeNames="uid"/>
    </AttributeDefinition>
   ```

4. Create `conf/attributes/custom/ImmutableID.properties`  as follow (the example considers italian and english languages only):
   ```properties
   # Azure AD ImmutableID

   id=ImmutableID
   transcoder=SAML2StringTranscoder
   displayName.en=Azure AD ImmutableID
   displayName.it=Azure AD ImmutableID
   description.en=Azure AD ImmutableID
   description.it=Azure AD ImmutableID
   saml2.name=urn:oid:0.9.2342.19200300.100.1.1
   saml1.encodeType=false
   ```
   
5. Create `conf/attributes/custom/UserId.properties` as follow (the example considers italian and english languages only):
   ```properties
   # Azure AD User ID

   id=UserId
   transcoder=SAML2ScopedStringTranscoder
   displayName.en=Azure AD User ID
   displayName.it=Azure AD User ID
   description.en=Azure AD User ID
   description.it=Azure AD User ID
   saml2.name=urn:oid:0.9.2342.19200300.100.1.1
   saml1.encodeType=false
   ```

6. Create Office 365 metadata:
   * `wget https://nexus.microsoftonline-p.com/federationmetadata/saml20/federationmetadata.xml -O /opt/shibboleth-idp/metadata/office365-md.xml`
   
   (and remove the NameIDFormat "`unspecified`" or the relase NameID will be always "`transient`")
   
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
      <AttributeRule attributeID="UserId">
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
