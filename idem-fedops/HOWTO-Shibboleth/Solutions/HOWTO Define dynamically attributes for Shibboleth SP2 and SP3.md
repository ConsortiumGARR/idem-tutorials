# HOWTO Define dynamically attributes for Shibboleth SP2 and SP3

<img width="120px" src="https://wiki.idem.garrservices.it/IDEM_Approved.png" />

## Table of Contents

1. [Introduction (What is it for?)](#Introduction)
2. [Requirements](#requirements)
3. [Modify shibboleth SP configuration](#modify-shibboleth-sp-configuration)
4. [A complete example](#example)
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

## Credits

- Giuseppe De Marco (giuseppe.demarco@unical.it)
- Francesco Filicetti (francesco.filicetti@unical.it)
