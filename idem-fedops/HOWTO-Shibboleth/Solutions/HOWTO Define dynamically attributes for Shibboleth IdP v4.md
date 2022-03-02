# HOWTO Define dynamically attributes for Shibboleth IdP v4

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements)
2. [HOWTO Define dynamically attributes for Shibboleth IdP v4](#howto-define-dynamically-attributes-for-shibboleth-idp-v4)
3. [Dynamic Definition examples](#dynamic-definition-examples)
   1. [Simple - Renaming attributes](#simple---renaming-attributes)
   2. [Template](#template)
   3. [Mapped](#mapped)
   4. [ScriptedAttribute](#scriptedattribute)
   5. [Scoped](#scoped)
4. [Authors](#authors)
    * [Original Author](#original-author)


## Requirements

* A machine with Shibboleth IdP v4 installed
* Java (from version 8 to 14)

## HOWTO Define dynamically attributes for Shibboleth IdP v4

1. Chose which attribute generate dynamically from the examples below
2. Modify your own **`attribute-resolver.xml`** by implementing the needed `<AttributeDefinition>` with the help of the examples.
3. Restart Jetty or, more simply, the service `AttributeResolverService`:
   
   `cd /opt/shibboleth-idp/bin ; ./reload-service.sh -id shibboleth.AttributeResolverService`

## Dynamic Definition examples

### Simple - renaming attributes

```xml
<!-- sAMAccountName >> uid -->
<AttributeDefinition xsi:type="Simple" id="uid">
   <InputDataConnector ref="myLDAP" attributeNames="sAMAaccountName" />
</AttributeDefinition>
```

### Template

```xml
<!-- Define the attribute 'displayName' as the result of a template that using 'sn' and 'givenName' LDAP attributes -->
<AttributeDefinition xsi:type="Template" id="displayName">
   <InputDataConnector ref="myLDAP" attributeNames="sn givenName" />
   <Template>
      <![CDATA[
         ${sn} ${givenName}
      ]]>
   </Template>
</AttributeDefinition>
```

### Mapped

```xml
<!-- MAPPED: Assegnare un'affiliazione ai diversi utenti dell'istituzione -->
<AttributeDefinition id="eduPersonAffiliation" xsi:type="Mapped">
    <InputDataConnector ref="myLDAP" attributeNames="title" />
    <DefaultValue passThru="true">affiliate</DefaultValue>
    <ValueMap>
        <ReturnValue>student</ReturnValue>
        <SourceValue>studente</SourceValue>
        <SourceValue>dottorando</SourceValue>
    </ValueMap>
    <ValueMap>
        <ReturnValue>member</ReturnValue>
        <SourceValue>studente</SourceValue>
        <SourceValue>dottorando</SourceValue>
    </ValueMap>
    <ValueMap>
        <ReturnValue>affiliate</ReturnValue>
        <SourceValue>ospite</SourceValue>
    </ValueMap>
    <ValueMap>
        <ReturnValue>staff</ReturnValue>
        <SourceValue>dottorando</SourceValue>
    </ValueMap>
    <ValueMap>
        <ReturnValue>staff</ReturnValue>
        <SourceValue>dirigente</SourceValue>
    </ValueMap>
    <ValueMap>
        <ReturnValue>some_string_to_add_before_value:$1</ReturnValue>
        <SourceValue>(.+)</SourceValue>
    </ValueMap>
 </AttributeDefinition>
```

### ScriptedAttribute

#### 1 - Add to all users with 'staff' affiliation a specific value of eduPersonEntitlement

```xml
<AttributeDefinition xsi:type="ScriptedAttribute" id="eduPersonEntitlement">
    <InputDataConnector ref="myLDAP" attributeNames="eduPersonEntitlement eduPersonAffiliation" />
    <Script>
       <![CDATA[
           logger = Java.type("org.slf4j.LoggerFactory").getLogger("net.shibboleth.idp.attribute.resolver.epebuilder");
           if (typeof eduPersonEntitlement == "undefined" || eduPersonEntitlement.getValues().size() < 1) {
              logger.info("No ePE in LDAP found, creating one");
              for (i = 0; i < eduPersonAffiliation.getValues().size(); i++){
                  affiliation = eduPersonAffiliation.getValues().get(i);
                  if (affiliation == 'staff') {
                     eduPersonEntitlement.addValue('urn:mace:dir:entitlement:common-lib-terms');
                  }
              }
           } else {
             logger.info("ePE has " + eduPersonEntitlement.getValues().size() + " values");
             for (i = 0; i < eduPersonAffiliation.getValues().size(); i++){
                 affiliation = eduPersonAffiliation.getValues().get(i);
                 if (affiliation == 'staff') {
                    eduPersonEntitlement.addValue('urn:mace:dir:entitlement:common-lib-terms');
                 }
             }
           }
           for (i = 0; i < eduPersonEntitlement.getValues().size(); i++){
               logger.info("ePE value "+i+": " + eduPersonEntitlement.getValues().get(i));
           }
       ]]>
    </Script>
</AttributeDefinition>
```

#### 2 - Compose the value of 'displayName' attribute by leverage upon other attributes

```xml
<AttributeDefinition xsi:type="ScriptedAttribute" id="displayName">
    <InputDataConnector ref="myLDAP" attributeNames="displayName cn givenName sn" />
    <Script>
       <![CDATA[
         logger = Java.type("org.slf4j.LoggerFactory").getLogger("net.shibboleth.idp.attribute.resolver.displayNameBuilder");
         // This implementation composes the value of the attribute displayName
         // from the values of the attributes 'cn' or 'givenName' + 'sn'
         // check existance of commonName attribute and use it to generate displayName attribute
         if (cn != null && cn.getValues().size() > 0) {
            commonName = cn.getValues().get(0);
         } else {
           commonName = null;
         }
         // compose value from givenName and surname
         // check whether givenName and surname exist
         if (givenName != null && givenName.getValues().size() > 0) {
            gn = givenName.getValues().get(0);
         } else {
           gn = null;
         }
         if (sn != null && sn.getValues().size() > 0) {
            surname = sn.getValues().get(0);
         } else {
           surname = null;
         }
         if (typeof displayName == 'undefined' || displayName.getValues().size() < 1) {
            logger.info("No displayName in LDAP found, creating one");
            # The "addValue()" parameter can be a String or an implementation of IdPAttributeValue: ByteAttributeValue, EmptyAttributeValue, ScopedStringAttributeValue or XMLObjectAttributeValue.
            # See Doc: https://build.shibboleth.net/nexus/service/local/repositories/site/content/java-identity-provider/4.0.1/apidocs/net/shibboleth/idp/attribute/package-summary.html
            # XXX.addValue(commonName) == XXX.addValue( String(commonName) )
            # or
            # valueType = Java.type("net.shibboleth.idp.attribute.StringAttributeValue");
            # XXX.addValue(new valueType(commonName))
            if (commonName != null) {
               displayName.addValue(commonName);
               logger.info('displayName final value: ' + displayName.getValues().get(0));
            } else if (surname != null && gn != null) {
              displayName.addValue(gn + ' ' + surname);
              logger.info('displayName final value: ' + displayName.getValues().get(0));
            } else if (surname != null) {
              displayName.addValue(surname);
              logger.info('displayName final value: ' + displayName.getValues().get(0));
            } else if (gn != null) {
              displayName.addValue(gn);
              logger.info('displayName final value: ' + displayName.getValues().get(0));
            }
         } else {
           logger.info('displayName had value: ' + displayName.getValues().get(0));
         }
        ]]>
    </Script>
</AttributeDefinition>
```

### Scoped

```xml
<AttributeDefinition scope="%{idp.scope}" xsi:type="Scoped" id="eduPersonScopedAffiliation">
     <InputDataConnector ref="myLDAP" attributeNames="eduPersonAffiliation" />
</AttributeDefinition>
```

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
