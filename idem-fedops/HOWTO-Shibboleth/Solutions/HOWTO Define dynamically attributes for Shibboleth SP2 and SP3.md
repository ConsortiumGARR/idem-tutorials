# HOWTO Define dynamically attributes for Shibboleth SP2 and SP3

<img width="120px" src="https://wiki.idem.garrservices.it/IDEM_Approved.png" />

## Table of Contents

1. [Introduction (What is it for?)](#Introduction)
2. [Requirements](#requirements)
3. [Modify shibboleth SP configuration](#modify-shibboleth-sp-configuration)
4. [A complete jinja powered example](#a-complete-jinja-powered-example)
5. [Credits](#credits)

## Introduction

This guide briefly explains how to edit /etc/shibbolet2.xml to process attributes, using regex (or any transformation), to generate a new custom attribute.

## Requirements

* A machine with Shibboleth IdP v3 installed

## Modify shibboleth SP configuration

1. Enable library extension, add OutofProcess statement in /etc/shibboleth2.xml.
```
    <OutOfProcess>
        <Extensions>
            <Library path="plugins.so" fatal="true"/>
        </Extensions>
    </OutOfProcess>
```

2. Add a new AttributeResolver statement for the attributes you need to process.
````
        <!-- example of a custom attribute extracted from a default value from IDP -->
        <AttributeResolver type="Transform" source="schacPersonalUniqueID">
            <Regex match="^urn:schac:personalUniqueID:IT:CF:(.+)$" dest="codice_fiscale">$1</Regex>
        </AttributeResolver>
````

## A complete jinja powered example
This is a Jinja2 template, mind the variables in the brackets {{}}.

````
<SPConfig xmlns="urn:mace:shibboleth:2.0:native:sp:config"
    xmlns:conf="urn:mace:shibboleth:2.0:native:sp:config"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"    
    xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    clockSkew="180">

    <!--
    By default, in-memory StorageService, ReplayCache, ArtifactMap, and SessionCache
    are used. See example-shibboleth2.xml for samples of explicitly configuring them.
    -->

    <!--
    To customize behavior for specific resources on Apache, and to link vhosts or
    resources to ApplicationOverride settings below, use web server options/commands.
    See https://wiki.shibboleth.net/confluence/display/SHIB2/NativeSPConfigurationElements for help.
    
    For examples with the RequestMap XML syntax instead, see the example-shibboleth2.xml
    file, and the https://wiki.shibboleth.net/confluence/display/SHIB2/NativeSPRequestMapHowTo topic.
    -->

    <OutOfProcess>
        <Extensions>
            <Library path="plugins.so" fatal="true"/>
        </Extensions>
    </OutOfProcess>

{% if httpd == 'nginx'  %}
    <RequestMapper type="XML">
        <RequestMap>
        <Host name="{{ sp_fqdn }}"
                authType="shibboleth"
                requireSession="true"
                redirectToSSL="443">
                <Path name="/secure" />
        </Host>
        </RequestMap>
    </RequestMapper>
{% endif %}

    <!-- The ApplicationDefaults element is where most of Shibboleth's SAML bits are defined. -->
    <ApplicationDefaults entityID="https://{{ sp_fqdn }}/shibboleth"
                         REMOTE_USER="eppn persistent-id targeted-id">

        <!--
        Controls session lifetimes, address checks, cookie handling, and the protocol handlers.
        You MUST supply an effectively unique handlerURL value for each of your applications.
        The value defaults to /Shibboleth.sso, and should be a relative path, with the SP computing
        a relative value based on the virtual host. Using handlerSSL="true", the default, will force
        the protocol to be https. You should also set cookieProps to "https" for SSL-only sites.
        Note that while we default checkAddress to "false", this has a negative impact on the
        security of your site. Stealing sessions via cookie theft is much easier with this disabled.
        -->
        <Sessions lifetime="28800" timeout="3600" relayState="ss:mem"
                  checkAddress="true" handlerSSL="true" cookieProps="https">

            <!--
            Configures SSO for a default IdP. To allow for >1 IdP, remove
            entityID property and adjust discoveryURL to point to discovery service.
            (Set discoveryProtocol to "WAYF" for legacy Shibboleth WAYF support.)
            You can also override entityID on /Login query string, or in RequestMap/htaccess.
            -->
            <SSO entityID="{{ idp_entity_id }}">
              SAML2 <!--SAML1-->
            </SSO>

            <!-- SAML and local-only logout. -->
            <Logout>SAML2 Local</Logout>
            
            <!-- Extension service that generates "approximate" metadata based on SP configuration. -->
            <Handler type="MetadataGenerator" Location="/Metadata" signing="false"/>

            <!-- Status reporting service. -->
            <Handler type="Status" Location="/Status" acl="127.0.0.1 ::1"/>

            <!-- Session diagnostic service. -->
            <Handler type="Session" Location="/Session" showAttributeValues="false"/>

            <!-- JSON feed of discovery information. -->
            <Handler type="DiscoveryFeed" Location="/DiscoFeed"/>
        </Sessions>

        <!--
        Allows overriding of error template information/filenames. You can
        also add attributes with values that can be plugged into the templates.
        -->
        <Errors supportContact="root@{{ domain }}"
            helpLocation="/about.html"
            styleSheet="/shibboleth-sp/main.css"/>
        
        <!-- Example of remotely supplied batch of signed metadata. -->
        <!--
        <MetadataProvider type="XML" uri="http://federation.org/federation-metadata.xml"
              backingFilePath="federation-metadata.xml" reloadInterval="7200">
            <MetadataFilter type="RequireValidUntil" maxValidityInterval="2419200"/>
            <MetadataFilter type="Signature" certificate="fedsigner.pem"/>
        </MetadataProvider>
        -->

        <!-- Example of locally maintained metadata. -->
        <!--
        <MetadataProvider type="XML" file="partner-metadata.xml"/>
        -->
        <MetadataProvider type="XML"
			  file="/etc/shibboleth/metadata/{{ idp_fqdn }}-metadata.xml"/>
        <!-- Map to extract attributes from SAML assertions. -->
        <AttributeExtractor type="XML" validate="true" reloadChanges="false" path="attribute-map.xml"/>
        
        <!-- Use a SAML query if no attributes are supplied during SSO. -->
        <AttributeResolver type="Query" subjectMatch="true"/>
        
        <!-- example of a custom attribute extracted from a default value from IDP -->
        <AttributeResolver type="Transform" source="schacPersonalUniqueID">
            <Regex match="^urn:schac:personalUniqueID:IT:CF:(.+)$" dest="codice_fiscale">$1</Regex>
        </AttributeResolver>

        <!-- Default filtering policy for recognized attributes, lets other data pass. -->
        <AttributeFilter type="XML" validate="true" path="attribute-policy.xml"/>

        <!-- Simple file-based resolver for using a single keypair. -->
        <CredentialResolver type="File" key="sp-key.pem" certificate="sp-cert.pem"/>

        <!--
        The default settings can be overridden by creating ApplicationOverride elements (see
        the https://wiki.shibboleth.net/confluence/display/SHIB2/NativeSPApplicationOverride topic).
        Resource requests are mapped by web server commands, or the RequestMapper, to an
        applicationId setting.
        
        Example of a second application (for a second vhost) that has a different entityID.
        Resources on the vhost would map to an applicationId of "admin":
        -->
        <!--
        <ApplicationOverride id="admin" entityID="https://admin.example.org/shibboleth"/>
        -->
    </ApplicationDefaults>
    
    <!-- Policies that determine how to process and authenticate runtime messages. -->
    <SecurityPolicyProvider type="XML" validate="true" path="security-policy.xml"/>

    <!-- Low-level configuration about protocols and bindings available for use. -->
    <ProtocolProvider type="XML" validate="true" reloadChanges="false" path="protocols.xml"/>

</SPConfig>
````

## Credits

- Giuseppe De Marco (giuseppe.demarco@unical.it)
- Francesco Filicetti (francesco.filicetti@unical.it)
