# HOWTO Define dynamically attributes for Shibboleth IdP v3

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements)
2. [HOWTO Define dynamically attributes for Shibboleth IdP v3](#howto-define-dynamically-attributes-for-shibboleth-idp-v3)
   1. [Dynamic Definition examples for Java 7](#dynamic-definition-examples-for-java-7)
      1. [(Java7) schacHomeOrganization (institutional domain == idp.scope)](#java7-schachomeorganization-institutional-domain--idpscope)
      2. [(Java7) organizationName (schacHomeOrganization)](#java7-organizationname-schachomeorganization)
      3. [(Java7) organizationalUnit (organizationName)](#java7-organizationalunit-organizationName)
      4. [(Java7) eduPersonOrgDN (organizationName + schacHomeOrganization)](#java7-edupersonorgdn-organizationname--schachomeorganization)
      5. [(Java7) eduPersonOrgUnitDN (eduPersonOrgDN)](#java7-edupersonorgunitdn-edupersonorgdn)
      6. [(Java7) displayName (commonName OR givenName + surname OR givenName OR surname)](#java7-displayname-commonname-or-givenname--surname-or-givenname-or-surname)
   2. [Dynamic Definition examples for Java 8](#dynamic-definition-examples-for-java-8)
      1. [(Java8) schacHomeOrganization (institutional domain == idp.scope)](#java8-schachomeorganization-institutional-domain--idpscope)
      2. [(Java8) organizationName (schacHomeOrganization)](#java8-organizationname-schachomeorganization)
      3. [(Java8) organizationalUnit (organizationName)](#java8-organizationalunit-organizationname)
      4. [(Java8) eduPersonOrgDN (organizationName + schacHomeOrganization)](#java8-edupersonorgdn-organizationname--schachomeorganization)
      5. [(Java8) eduPersonOrgUnitDN (eduPersonOrgDN)](#java8-edupersonorgunitdn-edupersonorgdn)
      6. [(Java8) displayName (commonName OR givenName + surname OR givenName OR surname)](#java8-displayname-commonname-or-givenname--surname-or-givenname-or-surname)

## Requirements

* A machine with Shibboleth IdP v3 installed
* [Oracle | OpenJDK] Java 7 or Java 8

## HOWTO Define dynamically attributes for Shibboleth IdP v3
1. Chose which attribute generate dynamically from the examples below (pay attention on which is you Java JDK)
2. Modify your own **```attribute-resolver.xml```** by implementing the needed ```<AttributeDefinition>``` with the help of the examples provided here.
3. Solve each dependency ```<resolver:Dependency>``` by adding the ```<resolver:AttributeDefinition>``` needed for the generation of the new attribute.
4. Restart Tomcat or, more simply, the service ```AttributeResolverService```:
   
   ```cd /opt/shibboleth-idp/bin ; ./reload-service.sh -id shibboleth.AttributeResolverService```

### Dynamic Definition examples for Java 7

#### (Java7) schacHomeOrganization (institutional domain == idp.scope)
```xml
<!-- Example AttributeDefinition Script to generate schacHomeOrganization if not already released by LDAP -->
<resolver:AttributeDefinition xsi:type="ad:Script" id="schacHomeOrganization">
    <resolver:Dependency ref="myLDAP" />
    <resolver:DisplayName xml:lang="en">Institution Domain</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">Dominio istituzione</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Domain of the institution</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">Dominio dell'istituzione</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:1.3.6.1.4.1.25178.1.2.9" friendlyName="schacHomeOrganization" encodeType="false" />
    <ad:Script>
       <![CDATA[
        importPackage (Packages.org.slf4j);
        logger = LoggerFactory.getLogger("net.shibboleth.idp.attribute");

        // This implementation composes the value of the attribute schacHomeOrganization
        // from the values of the properties idp.scope inside idp.properties.

        if (typeof schacHomeOrganization === 'undefined' || schacHomeOrganization.getValues().size() < 1) {

           logger.info("No schacHomeOrganization in LDAP found, creating one");

           // compose value from 'schacHomeOrganization'
           schacHomeOrganization.addValue("%{idp.scope}");
           logger.info("schacHomeOrganization final value: " + schacHomeOrganization.getValues().get(0));

        } else {
           logger.info("schacHomeOrganization has value: " + schacHomeOrganization.getValues().get(0));
        }
       ]]>
    </ad:Script>
</resolver:AttributeDefinition>
```

#### (Java7) organizationName (schacHomeOrganization)
```xml
<!-- Example AttributeDefinition Script to generate organizationName if not already released by LDAP -->
<resolver:AttributeDefinition xsi:type="ad:Script" id="organizationName">
   <resolver:Dependency ref="myLDAP" />
   <resolver:Dependency ref="schacHomeOrganization" />
   <resolver:DisplayName xml:lang="en">Institution Name</resolver:DisplayName>
   <resolver:DisplayName xml:lang="it">Nome Istituzione</resolver:DisplayName>
   <resolver:DisplayDescription xml:lang="en">Name of the institution</resolver:DisplayDescription>
   <resolver:DisplayDescription xml:lang="it">Nome dell'istituzione</resolver:DisplayDescription>
   <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:2.5.4.10" friendlyName="o" encodeType="false" />
   <ad:Script>
      <![CDATA[
        importPackage (Packages.org.slf4j);
        logger = LoggerFactory.getLogger("net.shibboleth.idp.attribute");

        // This implementation composes the value of the attribute organizationName
        // from the values of the attribute schacHomeOrganization

        // check existance of schacHomeOrganization attribute and use it to generate organizationName attribute
        if (schacHomeOrganization != null && schacHomeOrganization.getValues().size() > 0) {
           scHO = schacHomeOrganization.getValues().get(0);
        } else {
           scHO = null;
        }

        if (typeof organizationName === 'undefined' || organizationName.getValues().size() < 1) {

           logger.info("No organizationName in LDAP found, creating one");

           // compose value from 'schacHomeOrganization'

           if (scHO != null) {
              organizationName.addValue(scHO);
              logger.info("organizationName final value: " + organizationName.getValues().get(0));
           }
        } else {
           logger.info("organizationName has value: " + organizationName.getValues().get(0));
        }
      ]]>
   </ad:Script>
</resolver:AttributeDefinition>
```

#### (Java7) organizationalUnit (organizationName)
```xml
<!-- Example AttributeDefinition Script to generate organizationalUnit if not already released by LDAP -->
<resolver:AttributeDefinition xsi:type="ad:Script" id="organizationalUnit">
    <resolver:Dependency ref="myLDAP" />
    <resolver:Dependency ref="organizationName" />
    <resolver:DisplayName xml:lang="en">Organizational unit path</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">DN dell'unità</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Organization unit path: The distinguished name (DN) of the directory entries representing the person's Organizational Unit(s)</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">DN dell'unità: Il DN dell'unità organizzativa di questo utente nella sua organizzazione</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:2.5.4.11" friendlyName="ou" encodeType="false" />
    <ad:Script>
      <![CDATA[
        importPackage (Packages.org.slf4j);
        logger = LoggerFactory.getLogger("net.shibboleth.idp.attribute");

        // This implementation composes the value of the attribute organizationalUnit
        // from the values of the attribute organizationName

        // check existance of organizationName attribute and use it to generate organizationalUnit attribute
        if (organizationName != null && organizationName.getValues().size() > 0) {
          o = organizationName.getValues().get(0);
        } else {
          o = null;
        }

        if (typeof organizationalUnit === 'undefined' || organizationalUnit.getValues().size() < 1) {

           logger.info("No organizationalUnit in LDAP found, creating one");

           if (o != null) {
              organizationalUnit.addValue(o);
              logger.info("organizationalUnit final value: " + organizationalUnit.getValues().get(0));
           }
        } else {
           logger.info("organizationalUnit has value: " + organizationalUnit.getValues().get(0));
        }
      ]]>
    </ad:Script>
</resolver:AttributeDefinition>
```

#### (Java7) eduPersonOrgDN (organizationName + schacHomeOrganization)
```xml
<!-- Example AttributeDefinition Script to generate eduPersonOrgDN if not already released by LDAP -->
<resolver:AttributeDefinition xsi:type="ad:Script" id="eduPersonOrgDN">
    <resolver:Dependency ref="myLDAP"/>
    <resolver:Dependency ref="schacHomeOrganization"/>
    <resolver:Dependency ref="organizationName"/>

    <resolver:DisplayName xml:lang="en">Organization path</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">DN dell'organizzazione</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Organization path: The distinguished name (DN) of the directory entry representing the organization with which the person is associated</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">DN dell'organizzazione: Il DN dell'organizzazione a cui è associato questo utente</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:1.3.6.1.4.1.5923.1.1.1.3" friendlyName="eduPersonOrgDN" encodeType="false"/>
    <ad:Script>
      <![CDATA[
        importPackage (Packages.org.slf4j);
        //importPackage(Packages.java.util);
        importPackage(Packages.java.lang);

        logger = LoggerFactory.getLogger("net.shibboleth.idp.attribute");

        // This implementation composes the value of the attribute eduPersonOrgDN
        // from the values of the attributes o and schacHomeOrganization.

        // check existance of organizationName attribute and use it to generate eduPersonOrgDN attribute
        if (organizationName != null && organizationName.getValues().size() > 0) {
          o = organizationName.getValues().get(0);
        } else {
          o = null;
        }

        // check existance of schacHomeOrganization attribute and use it to generate eduPersonOrgDN attribute
        if (schacHomeOrganization != null && schacHomeOrganization.getValues().size() > 0) {
          scHO = schacHomeOrganization.getValues().get(0);
        } else {
          scHO = null;
        }

        if (typeof eduPersonOrgDN === 'undefined' || eduPersonOrgDN.getValues().size() < 1 ){

           logger.info("No eduPersonOrgDN in LDAP found, creating one");

           // compose value from 'o' and 'schacHomeOrganization'
           if (o != null && scHO != null) {

              var strHO = String(new java.lang.String(scHO));
              schacHO = strHO.split(".");
              baseDN = schacHO.join(",dc=");

              eduPersonOrgDN.addValue("o=" + o + ",dc=" + baseDN);
              logger.info("eduPersonOrgDN final value: " + eduPersonOrgDN.getValues().get(0));
           }

        } else {
           logger.info("eduPersonOrgDN has value: " + eduPersonOrgDN.getValues().get(0));
        }
      ]]>
    </ad:Script>
</resolver:AttributeDefinition>
```

#### (Java7) eduPersonOrgUnitDN (eduPersonOrgDN)
```xml
<!-- Example AttributeDefinition Script to generate eduPersonOrgUnitDN if not already released by LDAP -->
<resolver:AttributeDefinition xsi:type="ad:Script" id="eduPersonOrgUnitDN">
    <resolver:Dependency ref="myLDAP"/>
    <resolver:Dependency ref="eduPersonOrgDN"/>
    <resolver:DisplayName xml:lang="en">Organizational unit path</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">DN dell'unità</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Organization unit path: The distinguished name (DN) of the directory entries representing the person's Organizational Unit(s)</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">DN dell'unità: Il DN dell'unità organizzativa di questo utente nella sua organizzazione</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:1.3.6.1.4.1.5923.1.1.1.4" friendlyName="eduPersonOrgUnitDN" encodeType="false"/>
    <ad:Script>
      <![CDATA[
        importPackage (Packages.org.slf4j);
        logger = LoggerFactory.getLogger("net.shibboleth.idp.attribute");

        // This implementation composes the value of the attribute eduPersonOrgUnitDN
        // from the values of the attribute eduPersonOrgDN.

        // check existance of eduPersonOrgDN attribute and use it to generate eduPersonOrgUnitDN attribute
        if (eduPersonOrgDN != null && eduPersonOrgDN.getValues().size() > 0) {
          ePODN = eduPersonOrgDN.getValues().get(0);
        } else {
          ePODN = null;
        }

        if (typeof eduPersonOrgUnitDN === 'undefined' || eduPersonOrgUnitDN.getValues().size() < 1 ) {

           logger.info("No eduPersonOrgUnitDN in LDAP found, creating one");

           // compose value from 'eduPersonOrgDN'
           if (ePODN != null) {

              eduPersonOrgUnitDN.addValue(ePODN);
              logger.info("eduPersonOrgUnitDN final value: " + eduPersonOrgUnitDN.getValues().get(0));
           }
        } else {
           logger.info("eduPersonOrgUnitDN has value: " + eduPersonOrgUnitDN.getValues().get(0));
        }
      ]]>
    </ad:Script>
</resolver:AttributeDefinition>
```

#### (Java7) displayName (commonName OR givenName + surname OR givenName OR surname)
```xml
<!-- Example AttributeDefinition Script to generate displayName if not already released by LDAP -->
<resolver:AttributeDefinition xsi:type="ad:Script" id="displayName">
    <resolver:Dependency ref="myLDAP" />
    <resolver:Dependency ref="commonName" />
    <resolver:Dependency ref="givenName" />
    <resolver:Dependency ref="surname" />
    <resolver:DisplayName xml:lang="en">Display Name</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">Display Name</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Display Name of the user</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">Nome e Cognome dell'utente</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML1String" name="urn:mace:dir:attribute-def:displayName" encodeType="false" />
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:2.16.840.1.113730.3.1.241" friendlyName="displayName" encodeType="false" />
    <ad:Script>
      <![CDATA[
        importPackage (Packages.org.slf4j);
        logger = LoggerFactory.getLogger("net.shibboleth.idp.attribute");

        // This implementation composes the value of the attribute displayName
        // from the values of the attributes givenName and surname.

        // check existance of commonName attribute and use it to generate displayName attribute
        if (commonName != null && commonName.getValues().size() > 0) {
          cn = commonName.getValues().get(0);
        } else {
          cn = null;
        }

        // compose value from givenName and surname

        // check whether givenName and surname exist
        if (givenName != null && givenName.getValues().size() > 0) {
          gn = givenName.getValues().get(0);
        } else {
          gn = null;
        }
        if (surname != null && surname.getValues().size() > 0) {
          sn = surname.getValues().get(0);
        } else {
          sn = null;
        }

        if (typeof displayName == "undefined" || displayName.getValues().size() < 1) {
           logger.info("No displayName in LDAP found, creating one");

           if (cn != null) {
              displayName.addValue(cn);
              logger.info("displayName final value: " + displayName.getValues().get(0));

           } else if (sn != null && gn != null) {
              displayName.addValue(gn + " " + sn);
              logger.info("displayName final value: " + displayName.getValues().get(0));

           } else if (sn != null) {
              displayName.addValue(sn);
              logger.info("displayName final value: " + displayName.getValues().get(0));

           } else if (gn != null) {
              displayName.addValue(gn);
              logger.info("displayName final value: " + displayName.getValues().get(0));
           }

        } else {
           logger.info("displayName had value: " + displayName.getValues().get(0));
        }
      ]]>
   </ad:Script>
</resolver:AttributeDefinition>
```

### Dynamic Definition examples for Java 8

#### (Java8) schacHomeOrganization (institutional domain == idp.scope)
```xml
<!-- Example AttributeDefinition Script to generate schacHomeOrganization if not already released by LDAP -->
<resolver:AttributeDefinition id="schacHomeOrganization" xsi:type="ad:Script">
    <resolver:Dependency ref="myLDAP" />
    <resolver:DisplayName xml:lang="en">Institution Domain</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">Dominio istituzione</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Domain of the institution</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">Dominio dell'istituzione</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:1.3.6.1.4.1.25178.1.2.9" friendlyName="schacHomeOrganization" encodeType="false" />
    <ad:Script>
      <![CDATA[
        logger = Java.type("org.slf4j.LoggerFactory").getLogger("net.shibboleth.idp.attribute.resolver.schacHomeOrganizationbuilder");
        valueType = Java.type("net.shibboleth.idp.attribute.StringAttributeValue");

        // This implementation composes the value of the attribute schacHomeOrganization
        // from the values of the properties idp.scope inside idp.properties.

        if (typeof schacHomeOrganization === 'undefined' || schacHomeOrganization.getValues().size() < 1) {

           logger.info("No schacHomeOrganization in LDAP found, creating one");

           // compose value from 'schacHomeOrganization'
           schacHomeOrganization.addValue(new valueType("%{idp.scope}"));
           logger.info("schacHomeOrganization final value: " + schacHomeOrganization.getValues().get(0));

        } else {
           logger.info("schacHomeOrganization has value: " + schacHomeOrganization.getValues().get(0));
        }
      ]]>
    </ad:Script>
</resolver:AttributeDefinition>
```

#### (Java8) organizationName (schacHomeOrganization)
```xml
<!-- Example AttributeDefinition Script to generate organizationName if not already released by LDAP -->
<resolver:AttributeDefinition xsi:type="ad:Script" id="organizationName">
    <resolver:Dependency ref="myLDAP" />
    <resolver:Dependency ref="schacHomeOrganization" />
    <resolver:DisplayName xml:lang="en">Institution Name</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">Nome Istituzione</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Name of the institution</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">Nome dell'istituzione</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:2.5.4.10" friendlyName="o" encodeType="false" />
    <ad:Script>
      <![CDATA[
        logger = Java.type("org.slf4j.LoggerFactory").getLogger("net.shibboleth.idp.attribute.resolver.schacHomeOrganizationbuilder");
        valueType = Java.type("net.shibboleth.idp.attribute.StringAttributeValue");

        // This implementation composes the value of the attribute organizationName
        // from the values of the attribute schacHomeOrganization

        // check existance of schacHomeOrganization attribute and use it to generate organizationName attribute
        if (schacHomeOrganization != null && schacHomeOrganization.getValues().size() > 0) {
            scHO = schacHomeOrganization.getValues().get(0);
        } else {
            scHO = null;
        }

        if (typeof organizationName === 'undefined' || organizationName.getValues().size() < 1) {

           logger.info("No organizationName in LDAP found, creating one");

           // compose value from 'schacHomeOrganization'

           if (scHO != null) {
              organizationName.addValue(new valueType(scHO));
              logger.info("organizationName final value: " + organizationName.getValues().get(0));
           }
        } else {
           logger.info("organizationName has value: " + organizationName.getValues().get(0));
        }
      ]]>
    </ad:Script>
</resolver:AttributeDefinition>
```

#### (Java8) organizationalUnit (organizationName)
```xml
<!-- Example AttributeDefinition Script to generate organizationalUnit if not already released by LDAP -->
<resolver:AttributeDefinition xsi:type="ad:Script" id="organizationalUnit">
    <resolver:Dependency ref="myLDAP" />
    <resolver:Dependency ref="organizationName" />
    <resolver:DisplayName xml:lang="en">Organizational unit path</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">DN dell'unità</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Organization unit path: The distinguished name (DN) of the directory entries representing the person's Organizational Unit(s)</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">DN dell'unità: Il DN dell'unità organizzativa di questo utente nella sua organizzazione</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:2.5.4.11" friendlyName="ou" encodeType="false" />
    <ad:Script>
      <![CDATA[
        logger = Java.type("org.slf4j.LoggerFactory").getLogger("net.shibboleth.idp.attribute.resolver.schacHomeOrganizationbuilder");
        valueType = Java.type("net.shibboleth.idp.attribute.StringAttributeValue");

        // This implementation composes the value of the attribute organizationalUnit
        // from the values of the attribute organizationName

        // check existance of organizationName attribute and use it to generate organizationalUnit attribute
        if (organizationName != null && organizationName.getValues().size() > 0) {
          o = organizationName.getValues().get(0);
        } else {
          o = null;
        }

        if (typeof organizationalUnit === 'undefined' || organizationalUnit.getValues().size() < 1) {

           logger.info("No organizationalUnit in LDAP found, creating one");

           if (o != null) {
              organizationalUnit.addValue(new valueType (o));
              logger.info("organizationalUnit final value: " + organizationalUnit.getValues().get(0));
           }
        } else {
           logger.info("organizationalUnit has value: " + organizationalUnit.getValues().get(0));
        }
      ]]>
    </ad:Script>
</resolver:AttributeDefinition>
```

#### (Java8) eduPersonOrgDN (organizationName + schacHomeOrganization)
```xml
<!-- Example AttributeDefinition Script to generate eduPersonOrgDN if not already released by LDAP -->
<resolver:AttributeDefinition id="eduPersonOrgDN" xsi:type="ad:Script">
    <resolver:Dependency ref="myLDAP"/>
    <resolver:Dependency ref="schacHomeOrganization"/>
    <resolver:Dependency ref="organizationName"/>

    <resolver:DisplayName xml:lang="en">Organization path</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">DN dell'organizzazione</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Organization path: The distinguished name (DN) of the directory entry representing the organization with which the person is associated</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">DN dell'organizzazione: Il DN dell'organizzazione a cui è associato questo utente</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:1.3.6.1.4.1.5923.1.1.1.3" friendlyName="eduPersonOrgDN" encodeType="false"/>
    <ad:Script>
      <![CDATA[
        logger = Java.type("org.slf4j.LoggerFactory").getLogger("net.shibboleth.idp.attribute.resolver.schacHomeOrganizationbuilder");
        valueType = Java.type("net.shibboleth.idp.attribute.StringAttributeValue");

        // This implementation composes the value of the attribute eduPersonOrgDN
        // from the values of the attributes o and schacHomeOrganization.

        // check existance of organizationName attribute and use it to generate eduPersonOrgDN attribute
        if (organizationName != null && organizationName.getValues().size() > 0) {
          o = organizationName.getValues().get(0);
        } else {
          o = null;
        }

        // check existance of schacHomeOrganization attribute and use it to generate eduPersonOrgDN attribute
        if (schacHomeOrganization != null && schacHomeOrganization.getValues().size() > 0) {
          scHO = schacHomeOrganization.getValues().get(0);
        } else {
          scHO = null;
        }

        if (typeof eduPersonOrgDN === 'undefined' || eduPersonOrgDN.getValues().size() < 1 ){

           logger.info("No eduPersonOrgDN in LDAP found, creating one");

           // compose value from 'o' and 'schacHomeOrganization'
           if (o != null && scHO != null) {

              var strHO = String(new java.lang.String(scHO));
              schacHO = strHO.split(".");
              baseDN = schacHO.join(",dc=");

              eduPersonOrgDN.addValue(new valueType("o=" + o + ",dc=" + baseDN));
              logger.info("eduPersonOrgDN final value: " + eduPersonOrgDN.getValues().get(0));
           }

        } else {
           logger.info("eduPersonOrgDN has value: " + eduPersonOrgDN.getValues().get(0));
        }
      ]]>
    </ad:Script>
</resolver:AttributeDefinition>
```

#### (Java8) eduPersonOrgUnitDN (eduPersonOrgDN)
```xml
<!-- Example AttributeDefinition Script to generate eduPersonOrgUnitDN if not already released by LDAP -->
<resolver:AttributeDefinition id="eduPersonOrgUnitDN" xsi:type="ad:Script">
    <resolver:Dependency ref="myLDAP"/>
    <resolver:Dependency ref="eduPersonOrgDN"/>
    <resolver:DisplayName xml:lang="en">Organizational unit path</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">DN dell'unità</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Organization unit path: The distinguished name (DN) of the directory entries representing the person's Organizational Unit(s)</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">DN dell'unità: Il DN dell'unità organizzativa di questo utente nella sua organizzazione</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:1.3.6.1.4.1.5923.1.1.1.4" friendlyName="eduPersonOrgUnitDN" encodeType="false"/>
    <ad:Script>
      <![CDATA[
        logger = Java.type("org.slf4j.LoggerFactory").getLogger("net.shibboleth.idp.attribute.resolver.schacHomeOrganizationbuilder");
        valueType = Java.type("net.shibboleth.idp.attribute.StringAttributeValue");

        // This implementation composes the value of the attribute eduPersonOrgUnitDN
        // from the values of the attribute eduPersonOrgDN.

        // check existance of eduPersonOrgDN attribute and use it to generate eduPersonOrgUnitDN attribute
        if (eduPersonOrgDN != null && eduPersonOrgDN.getValues().size() > 0) {
          ePODN = eduPersonOrgDN.getValues().get(0);
        } else {
          ePODN = null;
        }

        if (typeof eduPersonOrgUnitDN === 'undefined' || eduPersonOrgUnitDN.getValues().size() < 1 ) {

           logger.info("No eduPersonOrgUnitDN in LDAP found, creating one");

           // compose value from 'eduPersonOrgDN'
           if (ePODN != null) {

              eduPersonOrgUnitDN.addValue(new valueType(ePODN));
              logger.info("eduPersonOrgUnitDN final value: " + eduPersonOrgUnitDN.getValues().get(0));
           }
        } else {
           logger.info("eduPersonOrgUnitDN has value: " + eduPersonOrgUnitDN.getValues().get(0));
        }
      ]]>
    </ad:Script>
</resolver:AttributeDefinition>
```

#### (Java8) displayName (commonName OR givenName + surname OR givenName OR surname)
```xml
<!-- Example AttributeDefinition to generate displayName if not already released by LDAP -->
<resolver:AttributeDefinition xsi:type="ad:Script" id="displayName">
    <resolver:Dependency ref="myLDAP" />
    <resolver:Dependency ref="commonName" />
    <resolver:Dependency ref="givenName" />
    <resolver:Dependency ref="surname" />
    <resolver:DisplayName xml:lang="en">Display Name</resolver:DisplayName>
    <resolver:DisplayName xml:lang="it">Display Name</resolver:DisplayName>
    <resolver:DisplayDescription xml:lang="en">Display Name of the user</resolver:DisplayDescription>
    <resolver:DisplayDescription xml:lang="it">Nome e Cognome dell'utente</resolver:DisplayDescription>
    <resolver:AttributeEncoder xsi:type="enc:SAML1String" name="urn:mace:dir:attribute-def:displayName" encodeType="false" />
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:2.16.840.1.113730.3.1.241" friendlyName="displayName" encodeType="false" />
    <ad:Script>
      <![CDATA[
        logger = Java.type("org.slf4j.LoggerFactory").getLogger("net.shibboleth.idp.attribute.resolver.displayNamebuilder");
        valueType =  Java.type("net.shibboleth.idp.attribute.StringAttributeValue");

        // This implementation composes the value of the attribute displayName
        // from the values of the attributes givenName and surname.

        // check existance of commonName attribute and use it to generate displayName attribute
        if (commonName != null && commonName.getValues().size() > 0) {
          cn = commonName.getValues().get(0);
        } else {
          cn = null;
        }

        // compose value from givenName and surname

        // check whether givenName and surname exist
        if (givenName != null && givenName.getValues().size() > 0) {
          gn = givenName.getValues().get(0);
        } else {
          gn = null;
        }
        if (surname != null && surname.getValues().size() > 0) {
          sn = surname.getValues().get(0);
        } else {
          sn = null;
        }

        if (typeof displayName == "undefined" || displayName.getValues().size() < 1) {
           logger.info("No displayName in LDAP found, creating one");

           if (cn != null) {
              displayName.addValue(new valueType(cn));
              logger.info("displayName final value: " + displayName.getValues().get(0));

           } else if (sn != null && gn != null) {
              displayName.addValue(new valueType(gn + " " + sn));
              logger.info("displayName final value: " + displayName.getValues().get(0));

           } else if (sn != null) {
              displayName.addValue(new valueType(sn));
              logger.info("displayName final value: " + displayName.getValues().get(0));

           } else if (gn != null) {
              displayName = new IdPAttribute("displayName");
              displayName.addValue(new valueType(gn));
              logger.info("displayName final value: " + displayName.getValues().get(0));
           }

        } else {
           logger.info("displayName had value: " + displayName.getValues().get(0));
        }
      ]]>
   </ad:Script>
</resolver:AttributeDefinition>
```
