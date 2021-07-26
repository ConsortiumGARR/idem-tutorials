# HOWTO Release only one value of a specific attribute to a specific resource

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements)
2. [HOWTO Create an Attribute Filter Custom to release a specific value to a specific resource](#HOWTO-create-an-attribute-filter-custom-to-release-a-specific-value-to-a-specific-resource)
3. [Authors](#authors)

## Requirements

* A machine with an Identity Provider Shibboleth v3.2.1 installed

## HOWTO Create an Attribute Filter Custom to release a specific value to a specific resource

1. Create a new ```attribute-filter-custom.xml``` file if you haven't got it on your IdP:

   * `vim /opt/shibboleth-idp/conf/attribute-fiter-custom.xml`

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!--
    This file is an EXAMPLE policy file only.
   -->
   <AttributeFilterPolicyGroup id="ShibbolethFilterPolicyElsevier"
        xmlns="urn:mace:shibboleth:2.0:afp"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="urn:mace:shibboleth:2.0:afp http://shibboleth.net/schema/idp/shibboleth-afp.xsd">

        <!-- Release the 'eduPersonEntitlement' attribute with a specific value to Elsevier ScienceDirect SP(identified by its entityID) -->
        <AttributeFilterPolicy id="Elsevier_ScienceDirect">
          <PolicyRequirementRule xsi:type="AND">
             <Rule xsi:type="RegistrationAuthority" registrars="http://www.idem.garr.it/" />
             <Rule xsi:type="Requester" value="https://sdauth.sciencedirect.com/" />
          </PolicyRequirementRule>

          <AttributeRule attributeID="eduPersonEntitlement">
             <DenyValueRule xsi:type="NOT">
                <Rule xsi:type="Value" value="urn:mace:dir:entitlement:common-lib-terms" />
             </DenyValueRule>
          </AttributeRule>
        </AttributeFilterPolicy>

   </AttributeFilterPolicyGroup>
   ```

2. Modify `service.xml` and include `attribute-filter-custom.xml`:

   * `vim /opt/shibboleth-idp/conf/service.xml`:
   
   ```xml
   ...
    <util:list id ="shibboleth.AttributeFilterResources">
        ...
        <value>%{idp.home}/conf/attribute-filter-custom.xml</value>
        ...
   </util:list>
   ...
   ```

3. Restart the Attribute Filter service to apply:

   * `cd /opt/shibboleth-idp/bin ; ./reload-service.sh -id shibboleth.AttributeFilterService`

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
