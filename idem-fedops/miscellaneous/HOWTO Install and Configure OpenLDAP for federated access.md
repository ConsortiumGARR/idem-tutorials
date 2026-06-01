# HOWTO Install and Configure OpenLDAP for federated access (Debian/Ubuntu)

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

01. [Requirements](#requirements)
02. [Notes](#notes)
03. [Utilities](#utilities)
04. [Configure the environment](#configure-the-environment)
05. [Configure APT Mirror](#configure-apt-mirror)
06. [Installation](#installation)
07. [Configuration](#configuration)
08. [Password Policies](#password-policies)
09. [Authors](#authors)

## Requirements

- Tested OS:
  - Debian: 13 (Trixie)
  - Ubuntu: 24.04 (Noble)

## Notes

This HOWTO uses `Vim` as text editor:

- `Esc button + i` means "insert"
- `Esc button + :w` means "write"
- `Esc button + :q` means "quit"
- `Esc button + :wq` means "write & quit"
- `Esc button + /` means "search text"
- `Esc button + u` means "undo"

and uses `example.org` to provide example values.

Please remember to **replace all occurencences** of the `example.org` domain name with the institutional domain name.

[[TOC](#table-of-contents)]

## Utilities

- Simple Bash script useful to convert a Domain Name into a Distinguished Name of LDAP:
  [domain2dn.sh](./domain2dn.sh)

- Apache Directory Studio: <https://directory.apache.org/studio/downloads.html>

## Configure the environment

01. Become ROOT:

    ``` text
    sudo su -
    ```

02. Be sure that your firewall **is not blocking** the traffic on port **389** for the OpenLDAP server.

03. Set the OpenLDAP hostname:

    **!!!ATTENTION!!!**: Replace, from the commands below, the label `<YOUR-SERVER-IP-ADDRESS>` with the IP address of the OpenLDAP server, the label `ldap.example.org` with the Full Qualified Domain Name of the OpenLDAP server and the label `<HOSTNAME>` with the OpenLDAP server hostname.

    - ``` text
      echo "<YOUR-SERVER-IP-ADDRESS> ldap.example.org <HOSTNAME>" >> /etc/hosts
      ```

    - ``` text
      hostnamectl set-hostname <HOSTNAME>
      ```

[[TOC](#table-of-contents)]

## Configure APT Mirror

Debian Mirror List: <https://www.debian.org/mirror/list>

Ubuntu Mirror List: <https://launchpad.net/ubuntu/+archivemirrors>

Select & Configure APT with your preferred mirror.
In the following is presented an example for the usage of the mirror provided by the Consortium GARR:

01. Become ROOT:

    ``` text
    sudo su -
    ```

02. Install package needed by mirrors protected by HTTPS:

    ``` text
    apt update && apt install apt-transport-https
    ```

03. Change the default mirror:

    - Debian example:

      ``` text
      bash -c 'cat > /etc/apt/sources.list.d/garr.sources <<EOF
      Types: deb
      URIs: https://debian.mirror.garr.it/debian/
      Suites: $(lsb_release -cs) $(lsb_release -cs)-updates $(lsb_release -cs)-backports
      Components: main
      Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

      Types: deb
      URIs: https://debian.mirror.garr.it/debian-security/
      Suites: $(lsb_release -cs)-security
      Components: main
      Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
      EOF'
      ```

    - Ubuntu example:

      ``` text
      bash -c 'cat > /etc/apt/sources.list.d/garr.sources <<EOF
      Types: deb
      URIs: https://ubuntu.mirror.garr.it/ubuntu/
      Suites: $(lsb_release -cs) $(lsb_release -cs)-updates $(lsb_release -cs)-backports
      Components: main universe restricted multiverse
      Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

      Types: deb
      URIs: https://ubuntu.mirror.garr.it/ubuntu-archive/
      Suites: $(lsb_release -cs)-security
      Components: main universe restricted multiverse
      Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
      EOF'
      ```

[[TOC](#table-of-contents)]

## Installation

01. System Update:

    ``` text
    sudo apt update ; sudo apt upgrade
    ```

02. Install needed packages to automate the SLAPD installation:

    ``` text
    sudo apt install debconf-utils
    ```

03. Automate SLAPD installation (Change all `_CHANGEME` values):

    - Create the `debconf-slapd.conf`:

      **NOTE: This HOWTO considers the following example values that have to be changed as your needs:**

        - `<LDAP-ROOT-PW_CHANGEME>` ==\> `ciaoldap`
        - `<INSTITUTE-DOMAIN_CHANGEME>` ==\> `example.org`
        - `<ORGANIZATION-NAME_CHANGEME>` ==\> `Example Org`

        ``` text
        sudo vim /root/debconf-slapd.conf
        ```

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

    - And load it with:

      ``` text
      sudo cat /root/debconf-slapd.conf | sudo debconf-set-selections
      ```

04. Install required package:

    ``` text
    sudo apt install slapd ldap-utils ldapscripts rsyslog
    ```

05. Create OpenLDAP server Certificate/Private Key (4096 bit - 3 years before expiration):

    **NOTE: the HOWTO will use self-signed certificate because the OpenLDAP server will be not exposed externally, but on a production instance the conditions may be different.**

    - ``` text
      sudo openssl req -newkey rsa:4096 -x509 -nodes -out /etc/ldap/$(hostname -f).crt -keyout /etc/ldap/$(hostname -f).key -days 1095 -subj "/CN=$(hostname -f)"
      ```

    - ``` text
      sudo chown openldap:openldap /etc/ldap/$(hostname -f).crt /etc/ldap/$(hostname -f).key
      ```

06. Verify that SSL certificate file matches the CA certificate file with:

    ``` text
    openssl verify --CAfile /etc/ldap/$(hostname -f).crt /etc/ldap/$(hostname -f).crt
    ```

    and make sure you get an `OK` as an outcome.

    The CA Certificate file and the Host Certificate file are the same because a self-signed certificate is used.

07. Enable StartTLS/SSL for LDAP:

    - ``` text
      sudo sed -i "s/TLS_CACERT.*/TLS_CACERT\t\/etc\/ldap\/$(hostname -f).crt/g" /etc/ldap/ldap.conf
      ```

    - ``` text
      sudo chown openldap:openldap /etc/ldap/ldap.conf
      ```

08. Restart OpenLDAP:

    ``` text
    sudo systemctl restart slapd
    ```

[[TOC](#table-of-contents)]

## Configuration

01. Create the `scratch` directory:

    ``` text
    sudo mkdir /etc/ldap/scratch
    ```

02. Configure LDAP for StartTLS/SSL:

    - ```bash
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

    - ```bash
      sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcTLS.ldif
      ```

03. Create the 3 main _Organizational Unit_ (OU), `people`, `groups` and `system`.

    _Example:_ The distinguish name of the domain name `example.org` will be `dc=example,dc=org`:

    - ```bash
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

    - ```text
      vim /etc/ldap/scratch/add_ou.ldif
      ```

      **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name. (Check [Notes](#notes) for help)

      The following script can help to convert a domain name into a distinguished name: [domain2dn.sh](./domain2dn.sh)

    - ``` text
      sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/add_ou.ldif

      sudo ldapsearch -x -b 'dc=example,dc=org'
      ```

      **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name and `<LDAP-ROOT-PW_CHANGEME>` with the LDAP ROOT password!

04. Create the user `idpuser` needed to perform _Bind and Search_ operations:

    - ``` text
      sudo bash -c 'cat > /etc/ldap/scratch/add_idpuser.ldif <<EOF
      dn: cn=idpuser,ou=system,dc=example,dc=org
      objectClass: inetOrgPerson
      cn: idpuser
      sn: idpuser
      givenName: idpuser
      userPassword: <INSERT-HERE-IDPUSER-PW>
      EOF'
      ```

    - ```text
      vim /etc/ldap/scratch/add_idpuser.ldif
      ```

      **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name and `<INSERT-HERE-IDPUSER-PW>` with password the `idpuser` user will use! (Check [Notes](#notes) for help)

        The following script can help to convert a domain name into a distinguished name: [domain2dn.sh](./domain2dn.sh)

    - ``` text
      sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/add_idpuser.ldif
      ```

05. Configure OpenLDAP ACL to allow `idpuser` to perform _search_ operation on the directory:

    - Check which configuration the OpenLDAP has:

        ``` text
        sudo ldapsearch  -Y EXTERNAL -H ldapi:/// -b cn=config 'olcDatabase={1}mdb'
        ```

    - Configure ACL for `idpuser` with:

        - ``` text
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

        - ``` text
          vim /etc/ldap/scratch/olcAcl.ldif
          ```

          **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name! (Check [Notes](#notes) for help)

          The following script can help to convert a domain name into a distinguished name: [domain2dn.sh](./domain2dn.sh)

        - ``` text
          sudo ldapadd  -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcAcl.ldif
          ```

    - Verify that OpenLDAP configuration has changed:

        ``` text
        sudo ldapsearch  -Y EXTERNAL -H ldapi:/// -b cn=config 'olcDatabase={1}mdb'
        ```

06. Check that `idpuser` can search other users (when users exist):

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!

    - ```bash
      sudo ldapsearch -x -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<INSERT-HERE-IDPUSER-PW>' -b 'ou=people,dc=example,dc=org'
      ```

07. Install needed schemas (eduPerson, SCHAC):

    - ``` text
      sudo wget https://raw.githubusercontent.com/REFEDS/eduperson/master/schema/openldap/eduperson.ldif -O /etc/ldap/schema/eduperson.ldif
      ```

    - ``` text
      sudo wget https://raw.githubusercontent.com/REFEDS/SCHAC/main/schema/openldap.ldif -O /etc/ldap/schema/schac.ldif
      ```

    - ``` text
      sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/eduperson.ldif
      ```

    - ``` text
      sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/schac.ldif
      ```

      and verify presence of the new `schac` and `eduPerson` schemas with:

    - ``` text
      sudo ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:/// -b 'cn=schema,cn=config' dn
      ```

08. Add MemberOf Configuration to OpenLDAP directory:

    - ```bash
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

    - Add it to the Directory:

      `sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/add_memberof.ldif`

09. Improve performance:

    - Create `olcDbIndex.ldif`:

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

    - Add it to the Directory:

      `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcDbIndex.ldif`

10. Configure Logging:

    - ```text
      sudo bash -c 'cat > /etc/rsyslog.d/99-slapd.conf <<EOF
      local4.* /var/log/slapd.log
      EOF'
      ```

    - ```text
      sudo bash -c 'cat > /etc/ldap/scratch/olcLogLevelStats.ldif <<EOF
      dn: cn=config
      changeType: modify
      replace: olcLogLevel
      olcLogLevel: stats
      EOF'
      ```

    - ```text
      sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcLogLevelStats.ldif
      ```

    - ```text
      sudo service rsyslog restart
      ```

    - ```text
      sudo service slapd restart
      ```

    - ``` text
      cat /var/log/slapd.log
      ```

11. Configure openLDAP olcSizeLimit:

    - ```text
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
      ```

    - ```text
      sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcSizeLimit.ldif
      ```

12. Add the first user:

    - Configure `user1.ldif`:

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

    - ``` text
      vim /etc/ldap/scratch/user1.ldif
      ```

      **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name, `example.org` with the institutional domain name. (Check [Notes](#notes) for help).

      The following script can help to convert a domain name into a distinguished name: [domain2dn.sh](./domain2dn.sh)

    - ``` text
      sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/user1.ldif
      ```

      **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name and `<LDAP-ROOT-PW_CHANGEME>` with the LDAP ROOT password!

13. Check that `idpuser` can find the inserted `user1`:

    ```bash
    sudo ldapsearch -x -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<INSERT-HERE-IDPUSER-PW>' -b 'uid=user1,ou=people,dc=example,dc=org'
    ```

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name and `<INSERT-HERE-IDPUSER-PW>` with the _idpuser_ password!

14. Check that LDAP has TLS (`anonymous` MUST BE returned):

    ``` text
    sudo ldapwhoami -H ldap:// -x -ZZ
    ```

15. Make `mail`, `eduPersonPrincipalName` and `schacPersonalUniqueID` unique:

    - Load `unique` module:

        - ``` text
          sudo bash -c 'cat > /etc/ldap/scratch/loadUniqueModule.ldif <<EOF
          dn: cn=module{0},cn=config
          changetype: modify
          add: olcModuleLoad
          olcModuleload: unique
          EOF'
          ```

        - ``` text
          sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/loadUniqueModule.ldif
          ```

    - Configure `mail`, `eduPersonPrincipalName` and `schacPersonalUniqueID` as unique:

      - ```text
        sudo bash -c 'cat > /etc/ldap/scratch/mail_ePPN_sPUI_unique.ldif <<EOF
        dn: olcOverlay=unique,olcDatabase={1}mdb,cn=config
        objectClass: olcOverlayConfig
        objectClass: olcUniqueConfig
        olcOverlay: unique
        olcUniqueAttribute: mail
        olcUniqueAttribute: schacPersonalUniqueID
        olcUniqueAttribute: eduPersonPrincipalName
        EOF'
        ```

        - ``` text
          sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/mail_ePPN_sPUI_unique.ldif
          ```

16. Disable Anonymous bind:

    - ```text
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
      ```

    - ```text
      sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/disableAnonymoysBind.ldif
      ```

[[TOC](#table-of-contents)]

## Password Policies

01. Load Password Policy module:

    - ```text
      sudo bash -c 'cat > /etc/ldap/scratch/load-ppolicy-mod.ldif <<EOF
      dn: cn=module{0},cn=config
      changetype: modify
      add: olcModuleLoad
      olcModuleLoad: ppolicy.so
      EOF'
      ```

    - ```text
      sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/load-ppolicy-mod.ldif
      ```

02. Create Password Policies OU Container:

    - ``` text
      sudo bash -c 'cat > /etc/ldap/scratch/policies-ou.ldif <<EOF
      dn: ou=policies,dc=example,dc=org
      objectClass: organizationalUnit
      objectClass: top
      ou: policies
      EOF'
      ```

    - ``` text
      vim /etc/ldap/scratch/policies-ou.ldif
      ```

      **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name.

      The following script can help to convert a domain name into a distinguished name: [domain2dn.sh](./domain2dn.sh)

    - ``` text
      sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/policies-ou.ldif 
      ```

      **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name and `<LDAP-ROOT-PW_CHANGEME>` with the LDAP ROOT password!

03. Create OpenLDAP Password Policy Overlay DN:

    - ``` text
      sudo bash -c 'cat > /etc/ldap/scratch/ppolicy-overlay.ldif <<EOF
      dn: olcOverlay=ppolicy,olcDatabase={1}mdb,cn=config
      objectClass: olcOverlayConfig
      objectClass: olcPPolicyConfig
      olcOverlay: ppolicy
      olcPPolicyDefault: cn=default,ou=policies,dc=example,dc=org
      olcPPolicyHashCleartext: TRUE
      EOF'
      ```

    - ``` text
      vim /etc/ldap/scratch/ppolicy-overlay.ldif
      ```

      **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name.

      The following script can help to convert a domain name into a distinguished name: [domain2dn.sh](./domain2dn.sh)

    - ``` text
      sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/ppolicy-overlay.ldif
      ```

04. Create the Default Password Policy:

    - ``` text
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
      # Password quality is checked if provided in cleartext; if unverifiable (e.g., hashed), the server accepts it with a warning.
      pwdCheckQuality: 1
      # Users can change their own password
      pwdAllowUserChange: TRUE
      EOF'
      ```

    - ``` text
      vim /etc/ldap/scratch/default-ppolicy.ldif
      ```

      **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name.

      The following script can help to convert a domain name into a distinguished name: [domain2dn.sh](./domain2dn.sh)

    - ``` text
      sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/default-ppolicy.ldif
      ```

      **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of the institutional domain name and `<LDAP-ROOT-PW_CHANGEME>` with the LDAP ROOT password!

    After this stage, the new users passwords has to follow the established Password Policies.

[[TOC](#table-of-contents)]

## References

- [OpenLDAP documentation](https://www.openldap.org/)

[[TOC](#table-of-contents)]

## Authors

### Original Author

Marco Malavolti (<mailto:marco.malavolti@garr.it>)

[[TOC](#table-of-contents)]
