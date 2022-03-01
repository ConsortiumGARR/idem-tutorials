# HOWTO Define dynamically attributes for Shibboleth IdP v4

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements)
2. [HOWTO Define dynamically attributes for Shibboleth IdP v4](#howto-define-dynamically-attributes-for-shibboleth-idp-v4)
3. [Dynamic Definition examples](#dynamic-definition-examples)

## Requirements

* A machine with Shibboleth IdP v4 installed
* Java (from version 8 to 14)

## HOWTO Define dynamically attributes for Shibboleth IdP v4

1. Chose which attribute generate dynamically from the examples below
2. Modify your own **`attribute-resolver.xml`** by implementing the needed `<AttributeDefinition>` with the help of the examples.
3. Restart Jetty or, more simply, the service `AttributeResolverService`:
   
   `cd /opt/shibboleth-idp/bin ; ./reload-service.sh -id shibboleth.AttributeResolverService`

## Dynamic Definition examples

### Rename an LDAP attribute
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
