# HOWTO Configure Shibboleth IdP v4.x & v5.x for Google Suite

1. Into `conf/relying-party.xml`, under `<util:list id="shibboleth.RelyingPartyOverrides">`, add the following `<bean>`:
   ```xml
   <bean id="Google" parent="RelyingPartyByName" c:relyingPartyIds="ENTITY-ID-GOOGLE-SP">
      <property name="profileConfigurations">
	       <list>
	          <bean parent="SAML2.SSO" p:encryptAssertions="true" p:encryptNameIDs="false" />
	       </list>
      </property>
   </bean>
   ```

2. Into `conf/saml-nameid.xml`, inside the `<util:list id="shibboleth.SAML2NameIDGenerators">` list, insert:
   ```xml
   <!-- Release to Google an "emailAddress" NameID with the value of GPrincipalMail -->
   <bean parent="shibboleth.SAML2AttributeSourcedGenerator"
         p:format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
         p:attributeSourceIds="#{ {'GPrincipalMail'} }">
      <property name="activationCondition">
         <bean parent="shibboleth.Conditions.RelyingPartyId" c:candidate="ENTITY-ID-GOOGLE-SP" />
      </property>
   </bean>
   ```

3. Into `conf/attribute-resolver.xml`, create the following `<AttributeDefinition>` to be able to generate the Google Principal (`GPrincipalMail`) attribute (if it is not already present into your LDAP directory):
   ```xml
   <AttributeDefinition xsi:type="Template" id="GPrincipalMail">
      <InputDataConnector ref="myLDAP" attributeNames="uid" />
      <Template>
         <![CDATA[
            ${uid}@uni_domain.it
         ]]>
      </Template>
   </AttributeDefinition>
   ```

4. Create `conf/attributes/custom/GPrincipalMail.properties` as follow (the example considers italian and english languages only):
   ```properties
   # GPrincipalMail

   id=GPrincipalMail
   transcoder=SAML2StringTranscoder
   displayName.en=Mail Google
   displayName.it=Mail Google
   description.en=Mail for Google
   description.it=Mail usato da Google
   saml2.name=urn:oid:0.9.2342.19200300.100.1.3
   saml1.encodeType=false
   ```

5. Into `metadata/google-md.xml`, add the following content by changing `university.edu` with the correct value of your institution:
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <EntityDescriptor entityID="ENTITY-ID-GOOGLE-SP"
       xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
       <SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"
           AuthnRequestsSigned="false"
           WantAssertionsSigned="true">
           <KeyDescriptor use="encryption">
               <KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#">
                   <X509Data>
                       <X509Certificate>GOOGLE-SP-MD-ENCRYPT-CERT</X509Certificate>
                   </X509Data>
               </KeyInfo>
               <EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#aes128-cbc"></EncryptionMethod>
               <EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#aes192-cbc"></EncryptionMethod>
               <EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#aes256-cbc"></EncryptionMethod>
               <EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p"></EncryptionMethod>
           </KeyDescriptor>
           <NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</NameIDFormat>
           <AssertionConsumerService index="1" Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
               Location="SP-GOOGLE-ACS-URL" />
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
   <AttributeFilterPolicy id="ENTITY-ID-GOOGLE-SP">
      <PolicyRequirementRule xsi:type="Requester" value="ENTITY-ID-GOOGLE-SP" />
      <AttributeRule attributeID="GPrincipalMail">
         <PermitValueRule xsi:type="ANY" />
      </AttributeRule>
   </AttributeFilterPolicy>
   ```

8. Test with AACLI:
   `bash /opt/shibboleth-idp/bin/aacli.sh -n <REPLACE_WITH_USERNAME_IDP> -r ENTITY-ID-GOOGLE-SP --saml2`
