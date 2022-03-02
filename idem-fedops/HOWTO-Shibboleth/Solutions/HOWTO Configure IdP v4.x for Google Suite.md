# HOWTO Configure IdP v4.x for Google Suite

1. Into `conf/relying-party.xml`, under `<util:list id="shibboleth.RelyingPartyOverrides">`, add the following `<bean>`:
   ```xml
   <bean id="Google" parent="RelyingPartyByName" c:relyingPartyIds="google.com">
      <property name="profileConfigurations">
	       <list>
	          <bean parent="SAML2.SSO" p:encryptAssertions="false" p:encryptNameIDs="false" />
	       </list>
      </property>
   </bean>
   ```

2. Into `conf/saml-nameid.xml`, inside the `<util:list id="shibboleth.SAML2NameIDGenerators">` list, insert:
   ```xml
   <!-- Release to Google an "emailAddress" NameID with the value of Gprincipal -->
   <bean parent="shibboleth.SAML2AttributeSourcedGenerator"
         p:format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
         p:attributeSourceIds="#{ {'Gprincipal'} }">
      <property name="activationCondition">
         <bean parent="shibboleth.Conditions.RelyingPartyId" c:candidate="google.com" />
      </property>
   </bean>
   ```

3. Into `conf/attribute-resolver.xml`, create the following `<AttributeDefinition>` to be able to generate the Google Principal (`GPrincipal`) attribute (if it is not already present into your LDAP directory):
   ```xml
   <AttributeDefinition xsi:type="Template" id="Gprincipal">
      <InputDataConnector ref="myLDAP" attributeNames="uid" />
      <Template>
         <![CDATA[
            ${uid}@gmail.com
         ]]>
      </Template>
   </AttributeDefinition>
   ```

4. Create `conf/attributes/custom/Gprincipal.properties` as follow (the example considers italian and english languages only):
   ```properties
   # Gprincipal

   id=Gprincipal
   transcoder=SAML2StringTranscoder
   displayName.en=Username Google
   displayName.it=Username Google
   description.en=Username for Google
   description.it=Username usato da Google
   saml2.name=urn:oid:0.9.2342.19200300.100.1.3
   saml1.encodeType=false
   ```

5. Into `metadata/google-md.xml`, add the following content by changing `university.edu` with the correct value of your institution:
   ```xml
   <?xml version="1.0" encoding="UTF-8" standalone="no"?>

   <!-- entityID = "google.com" -->
   <EntityDescriptor entityID="google.com" xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
      <SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
         <NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</NameIDFormat>
         <AssertionConsumerService index="1" Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://www.google.com/a/university.edu/acs" />
      </SPSSODescriptor>
   </EntityDescriptor>
   ```
   
6. Into `conf/metadata-providers.xml` add the Google metadata:
   ```xml
   <MetadataProvider id="Google”  xsi:type="FilesystemMetadataProvider" metadataFile="%{idp.home}/metadata/google-md.xml"/>
   ```
   
7. Into `conf/attribute-filter.xml`, configure the attribute release:
   ```xml
   <!-- G Suite (Google Apps)  -->
   <AttributeFilterPolicy id="google.com">
      <PolicyRequirementRule xsi:type="Requester" value="google.com" />
      <AttributeRule attributeID="Gprincipal">
         <PermitValueRule xsi:type="ANY" />
      </AttributeRule>
   </AttributeFilterPolicy>
   ```

8. Test with AACLI:
   `bash /opt/shibboleth-idp/bin/aacli.sh -n <REPLACE_WITH_USERNAME_IDP> -r google.com --saml2`
