# HOWTO Install and Configure OpenLDAP for federated access (Debian/Ubuntu)

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

01. [Requirements](#requirements)
02. [Notes](#notes)
03. [Utility](#utility)
04. [Installation](#installation)
05. [Configuration](#configuration)
06. [Password Policies](#password-policies)
07. [Utilities](#utilities)
08. [Authors](#authors)

## Requirements

* Tested OS:

  * Debian 12 (Bookworm)
  * Ubuntu 22.04 (Jammy Jellyfish)
  * Ubuntu 24.04 (Noble)

## Notes

This HOWTO uses `example.org` to provide this guide with example values.

Please remember to **replace all occurencences** of the `example.org` domain name with the domain name of your institution.

## Utility

* Simple Bash script useful to convert a Domain Name into a Distinguished Name of LDAP:
  [domain2dn.sh](https://github.com/ConsortiumGARR/idem-tutorials/blob/master/idem-fedops/miscellaneous/domain2dn.sh)

## Installation

01. System Update:

    * `sudo apt update ; sudo apt upgrade`

02. Automate SLAPD installation (Change all "_CHANGEME" values):

    * `sudo apt install debconf-utils`
    * `sudo vim /root/debconf-slapd.conf`

      ```bash
      slapd slapd/password1 password <LDAP-ROOT-PW_CHANGEME>
      slapd slapd/password2 password <LDAP-ROOT-PW_CHANGEME>
      slapd slapd/move_old_database boolean true
      slapd slapd/domain string <INSTITUTE-DOMAIN_CHANGEME>
      slapd shared/organization string <ORGANIZATION-NAME_CHANGEME>
      slapd slapd/no_configuration boolean false
      slapd slapd/purge_database boolean false
      slapd slapd/allow_ldap_v2 boolean false
      slapd slapd/backend select MDB
      ```

    * `sudo cat /root/debconf-slapd.conf | sudo debconf-set-selections`

    **NOTES**: The HOWTO considers the following values that have to be changed as your needs:

      * `<LDAP-ROOT-PW_CHANGEME>` ==> `ciaoldap`
      * `<INSTITUTE-DOMAIN_CHANGEME>` ==> `example.org`
      * `<ORGANIZATION-NAME_CHANGEME>` ==> `Example Org`

03. Install required package:

    * `sudo apt install slapd ldap-utils ldapscripts rsyslog`

04. Check `/etc/hosts` to be sure to have the correct FQDN for OpenLDAP server

05. Create Certificate/Key (**This HOWTO will use Self Signed Certificate for LDAP**):

    * Self Signed (4096 bit - 3 years before expiration):

      * ```bash
        sudo openssl req -newkey rsa:4096 -x509 -nodes -out /etc/ldap/$(hostname -f).crt -keyout /etc/ldap/$(hostname -f).key -days 1095 -subj "/CN=$(hostname -f)"
        ```

      * ```bash
        sudo chown openldap:openldap /etc/ldap/$(hostname -f).crt /etc/ldap/$(hostname -f).key
        ```

    * Signed (**Do not use if you are not a NREN GARR Member**):

      * Add CA Cert into `/etc/ssl/certs`

        * If you use GARR TCS or GEANT TCS:

          ```bash
          wget -O /etc/ssl/certs/GEANT_TLS_RSA_1.pem https://crt.sh/?d=16099180997
          ```

        * If you use ACME (Let's Encrypt):

          ```bash
          sudo ln -s /etc/letsencrypt/live/<SERVER_FQDN>/chain.pem /etc/ssl/certs/ACME-CA.pem
          ```

      * Generate CSR(Certificate Signing Request) and the KEY:

        ```bash
        sudo openssl req -new -newkey rsa:4096 -nodes -out /etc/ssl/certs/$(hostname -f).csr -keyout /etc/ssl/private/$(hostname -f).key -subj "/C=IT/ST=/L=Rome/O=Consortium GARR/CN=$(hostname -f)"
        ```

      * Once obtained the SSL Certificate, copy it and the key into openldap directory:

        ```bash
        sudo cp /etc/ssl/certs/$(hostname -f).crt /etc/ldap/$(hostname -f).crt

        sudo cp /etc/ssl/private/$(hostname -f).key /etc/ldap/$(hostname -f).key

        sudo chown openldap:openldap /etc/ldap/$(hostname -f).crt /etc/ldap/$(hostname -f).key
        ```

06. Enable SSL for LDAP:

    ```bash
    sudo sed -i "s/TLS_CACERT.*/TLS_CACERT\t\/etc\/ldap\/$(hostname -f).crt/g" /etc/ldap/ldap.conf

    sudo chown openldap:openldap /etc/ldap/ldap.conf
    ```

07. Restart OpenLDAP:

    * `sudo service slapd restart`

## Configuration

01. Create `scratch` directory:

    `sudo mkdir /etc/ldap/scratch`

02. Configure LDAP for StartTLS/SSL:

    ```bash
    sudo bash -c 'cat > /etc/ldap/scratch/olcTLS.ldif <<EOF
    dn: cn=config
    changetype: modify
    replace: olcTLSCACertificateFile
    olcTLSCACertificateFile: /etc/ldap/$(hostname -f).crt
    -
    replace: olcTLSCertificateFile
    olcTLSCertificateFile: /etc/ldap/$(hostname -f).crt
    -
    replace: olcTLSCertificateKeyFile
    olcTLSCertificateKeyFile: /etc/ldap/$(hostname -f).key
    EOF'
    ```

03. Apply with:

    ```bash
    sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcTLS.ldif
    ```

04. Create the 3 main _Organizational Unit_ (OU), `people`, `groups` and `system`.

    _Example:_ if the domain name is `example.org` than  the distinguish name will be `dc=example,dc=org`:

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name and `<LDAP-ROOT-PW_CHANGEME>` with the LDAP ROOT password!

    * ```bash
      sudo bash -c 'cat > /etc/ldap/scratch/add_ou.ldif <<EOF
      dn: ou=people,dc=example,dc=org
      objectClass: organizationalUnit
      objectClass: top
      ou: people

      dn: ou=groups,dc=example,dc=org
      objectClass: organizationalUnit
      objectClass: top
      ou: groups

      dn: ou=system,dc=example,dc=org
      objectClass: organizationalUnit
      objectClass: top
      ou: system
      EOF'
      ```

    * Apply with:

      ```bash
      sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/add_ou.ldif
      ```

    * Verify with: `sudo ldapsearch -x -b 'dc=example,dc=org'`

05. Create the `idpuser` needed to perform _Bind and Search_ operations:

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name, `<LDAP-ROOT-PW_CHANGEME>` with the LDAP ROOT password and `<INSERT-HERE-IDPUSER-PW>` with password for the `idpuser` user!

    * ```bash
      sudo bash -c 'cat > /etc/ldap/scratch/add_idpuser.ldif <<EOF
      dn: cn=idpuser,ou=system,dc=example,dc=org
      objectClass: inetOrgPerson
      cn: idpuser
      sn: idpuser
      givenName: idpuser
      userPassword: <INSERT-HERE-IDPUSER-PW>
      EOF'
      ```

    * Apply with:

      ```bash
      sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/add_idpuser.ldif
      ```

06. Configure OpenLDAP ACL to allow `idpuser` to perform _search_ operation on the directory:

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!

    * Check which configuration your directory has:

      * `sudo ldapsearch  -Y EXTERNAL -H ldapi:/// -b cn=config 'olcDatabase={1}mdb'`

    * Configure ACL for `idpuser` with:

      ```bash
      sudo bash -c 'cat > /etc/ldap/scratch/olcAcl.ldif <<EOF
      dn: olcDatabase={1}mdb,cn=config
      changeType: modify
      replace: olcAccess
      olcAccess: {0}to * by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage by * break
      olcAccess: {1}to attrs=userPassword,shadowLastChange by self write by anonymous auth by dn="cn=admin,dc=example,dc=org" write by * none
      olcAccess: {2}to dn.base="" by anonymous auth by * read
      olcAccess: {3}to dn.base="cn=Subschema" by * read
      olcAccess: {4}to * by dn.exact="cn=idpuser,ou=system,dc=example,dc=org" read by self read by anonymous auth by * none
      EOF'
      ```

    * Apply with:

      ```bash
      sudo ldapadd  -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcAcl.ldif
      ```

07. Check that `idpuser` can search other users (when users exist):

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!

    ```bash
    sudo ldapsearch -x -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<INSERT-HERE-IDPUSER-PW>' -b 'ou=people,dc=example,dc=org'
    ```

08. Install needed schemas (eduPerson, SCHAC):

    ```bash
    sudo wget https://raw.githubusercontent.com/REFEDS/eduperson/master/schema/openldap/eduperson.ldif -O /etc/ldap/schema/eduperson.ldif

    sudo wget https://raw.githubusercontent.com/REFEDS/SCHAC/main/schema/openldap.ldif -O /etc/ldap/schema/schac.ldif
     
    sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/eduperson.ldif

    sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/schac.ldif
    ```

    and verify presence of the new `schac` and `eduPerson` schemas with:

    `sudo ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:/// -b 'cn=schema,cn=config' dn`

09. Add MemberOf Configuration:

    * Create `add_memberof.ldif`:

      ```bash
      sudo bash -c 'cat > /etc/ldap/scratch/add_memberof.ldif <<EOF
      dn: cn=module,cn=config
      cn: module
      objectClass: olcModuleList
      olcModuleLoad: memberof
      olcModulePath: /usr/lib/ldap

      dn: olcOverlay={0}memberof,olcDatabase={1}mdb,cn=config
      objectClass: olcConfig
      objectClass: olcMemberOf
      objectClass: olcOverlayConfig
      objectClass: top
      olcOverlay: memberof
      olcMemberOfDangling: ignore
      olcMemberOfRefInt: TRUE
      olcMemberOfGroupOC: groupOfNames
      olcMemberOfMemberAD: member
      olcMemberOfMemberOfAD: memberOf
      EOF'
      ```

    * Add it to the Directory:

      `sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/add_memberof.ldif`

10. Improve performance:

    * Create `olcDbIndex.ldif`:

      ```bash
      sudo bash -c 'cat > /etc/ldap/scratch/olcDbIndex.ldif <<EOF
      dn: olcDatabase={1}mdb,cn=config
      changetype: modify
      replace: olcDbIndex
      # UID Bind
      olcDbIndex: uid eq,sub
      # Groups
      olcDbIndex: member eq
      olcDbIndex: memberUid eq
      # SAML Attributes
      olcDbIndex: cn,sn,givenName pres,eq,sub
      olcDbIndex: mail eq,sub
      olcDbIndex: eduPersonAffiliation,eduPersonEntitlement eq
      # STRUCTURE
      olcDbIndex: ou pres,eq,sub
      EOF'
      ```

    * Add it to the Directory:

      `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcDbIndex.ldif`

11. Configure Logging:

    ```bash
    sudo mkdir /var/log/slapd

    sudo chown syslog /var/log/slapd

    sudo bash -c 'cat > /etc/rsyslog.d/99-slapd.conf <<EOF
    local4.* /var/log/slapd/slapd.log
    EOF'

    sudo bash -c 'cat > /etc/ldap/scratch/olcLogLevelStats.ldif <<EOF
    dn: cn=config
    changeType: modify
    replace: olcLogLevel
    olcLogLevel: stats
    EOF'

    sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcLogLevelStats.ldif

    sudo service rsyslog restart

    sudo service slapd restart
    ```

12. Configure openLDAP olcSizeLimit:

    ```bash
    sudo bash -c 'cat > /etc/ldap/scratch/olcSizeLimit.ldif <<EOF
    dn: cn=config
    changetype: modify
    replace: olcSizeLimit
    olcSizeLimit: unlimited

    dn: olcDatabase={-1}frontend,cn=config
    changetype: modify
    replace: olcSizeLimit
    olcSizeLimit: unlimited
    EOF'
     
    sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcSizeLimit.ldif
    ```

13. Add the first user:

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!

    * Configure `user1.ldif`:

      ```bash
      sudo bash -c 'cat > /etc/ldap/scratch/user1.ldif <<EOF
      # USERNAME: user1 , PASSWORD: hello-world-12
      dn: uid=user1,ou=people,dc=aai-test,dc=garr,dc=it
      changetype: add
      objectClass: inetOrgPerson
      objectClass: eduPerson
      uid: user1
      sn: User1
      givenName: Test
      cn: Test User1
      displayName: Test User1
      preferredLanguage: it
      userPassword: hello-world-12
      mail: test.user1@institute-domain.it
      eduPersonAffiliation: student
      eduPersonAffiliation: staff
      eduPersonAffiliation: member
      eduPersonEntitlement: urn:mace:dir:entitlement:common-lib-terms
      eduPersonEntitlement: urn:mace:terena.org:tcs:personal-user
      EOF'
      ```

    * Apply with:

      ```bash
      sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/user1.ldif
      ```

14. Check that `idpuser` can find `user1`:

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!

    ```bash
    sudo ldapsearch -x -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<INSERT-HERE-IDPUSER-PW>' -b 'uid=user1,ou=people,dc=example,dc=org'
    ```

16. Check that LDAP has TLS ('anonymous' MUST BE returned):

    `sudo ldapwhoami -H ldap:// -x -ZZ`

17. Make sure that `mail`, `eduPersonPrincipalName` and `schacPersonalUniqueID` are unique:

    * Load `unique` module:

      ```bash
      sudo bash -c 'cat > /etc/ldap/scratch/loadUniqueModule.ldif <<EOF
      dn: cn=module{0},cn=config
      changetype: modify
      add: olcModuleLoad
      olcModuleload: unique
      EOF'

      sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/loadUniqueModule.ldif
      ```

    * Configure mail, eduPersonPrincipalName and schacPersonalUniqueID as unique:

      ```bash
      sudo bash -c 'cat > /etc/ldap/scratch/mail_ePPN_sPUI_unique.ldif <<EOF
      dn: olcOverlay=unique,olcDatabase={1}mdb,cn=config
      objectClass: olcOverlayConfig
      objectClass: olcUniqueConfig
      olcOverlay: unique
      olcUniqueAttribute: mail
      olcUniqueAttribute: schacPersonalUniqueID
      olcUniqueAttribute: eduPersonPrincipalName
      EOF'

      sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/mail_ePPN_sPUI_unique.ldif
      ```

18. Disable Anonymous bind:

    ```bash
    sudo bash -c 'cat > /etc/ldap/scratch/disableAnonymoysBind.ldif <<EOF
    dn: cn=config
    changetype: modify
    add: olcDisallows
    olcDisallows: bind_anon

    dn: olcDatabase={-1}frontend,cn=config
    changetype: modify
    add: olcRequires
    olcRequires: authc
    EOF'

    sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/disableAnonymoysBind.ldif
    ```

## Password Policies

01. Load Password Policy module:

    ```bash
    sudo bash -c 'cat > /etc/ldap/scratch/load-ppolicy-mod.ldif <<EOF
    dn: cn=module{0},cn=config
    changetype: modify
    add: olcModuleLoad
    olcModuleLoad: ppolicy.so
    EOF'

    sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/load-ppolicy-mod.ldif
    ```

02. Create Password Policies OU Container:

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!

    ```bash
    sudo bash -c 'cat > /etc/ldap/scratch/policies-ou.ldif <<EOF
    dn: ou=policies,dc=example,dc=org
    objectClass: organizationalUnit
    objectClass: top
    ou: policies
    EOF'

    sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/policies-ou.ldif 
    ```

03. Create OpenLDAP Password Policy Overlay DN:

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!

    ```bash
    sudo bash -c 'cat > /etc/ldap/scratch/ppolicy-overlay.ldif <<EOF
    dn: olcOverlay=ppolicy,olcDatabase={1}mdb,cn=config
    objectClass: olcOverlayConfig
    objectClass: olcPPolicyConfig
    olcOverlay: ppolicy
    olcPPolicyDefault: cn=default,ou=policies,dc=example,dc=org
    olcPPolicyHashCleartext: TRUE
    EOF'

    sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/ppolicy-overlay.ldif
    ```

04. Create the Default Password Policy:

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!

    ```bash
    sudo bash -c 'cat > /etc/ldap/scratch/default-ppolicy.ldif <<EOF
    dn: cn=default,ou=policies,dc=example,dc=org
    objectClass: pwdPolicy
    objectClass: device
    objectClass: top
    cn: default
    # Applies policy to userPassword attribute
    pwdAttribute: userPassword
    # Enables account lockout after failures
    pwdLockout: TRUE
     # Maximum failed login attempts before lockout
    pwdMaxFailure: 5
    # Lockout duration in seconds (15 minutes)
    pwdLockoutDuration: 900
    # Password maximum age in seconds (0 = never expires)
    pwdMaxAge: 0
    # Minimum password length in characters
    pwdMinLength: 12
    # Number of old passwords stored (no reuse)
    pwdInHistory: 5
    # 0=off, 1=low, 2=strict quality check
    pwdCheckQuality: 2
    # Users can change their own password
    pwdAllowUserChange: TRUE
    EOF'

    sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/policies-ou.ldif
    ```

## Utilities

* Apache Directory Studio: <https://directory.apache.org/studio/downloads.html>

## Authors

### Original Author

Marco Malavolti (<mailto:marco.malavolti@garr.it>)
