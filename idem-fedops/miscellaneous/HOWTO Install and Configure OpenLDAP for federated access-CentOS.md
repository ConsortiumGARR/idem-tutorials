# HOWTO Install and Configure OpenLDAP for federated access on CentOS

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements)
2. [Notes](#notes)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Utilities](#utilities)
6. [LDAP Administration tools](#ldap-administration-tools)

## Requirements

 * Centos 7.x (with SELinux deactivated)

## Notes

This HOWTO use `example.org` to provide this guide with example values.

Please, remember to **replace all occurence** of `example.org` domain name, or part of it, with the domain name into the configuration files.

## Installation

1. System Update:
   * `sudo yum upgrade`

2. Install required packages:
   * `sudo yum install openldap openldap-clients openldap-servers openssl vim`
   * `sudo cp /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG`
   * `sudo chown -R ldap:ldap /var/lib/ldap/`
   * `sudo systemctl enable slapd`
   * `sudo systemctl start slapd`

3. Setup openldap root password:
   * `sudo slappasswd`

     ```bash
     New password: <LDAP-ROOT-PW_CHANGEME>
     Re-enter new password: <LDAP-ROOT-PW_CHANGEME>
     {SSHA}nk8A/+uFKfDb1OhaYmPUFlQmWwcdtNF4
     ```

   * `sudo mkdir /etc/openldap/scratch`

   * `sudo vim /etc/openldap/scratch/db.ldif`

     ```bash
     dn: olcDatabase={2}hdb,cn=config
     changetype: modify
     replace: olcSuffix
     olcSuffix: dc=example,dc=org

     dn: olcDatabase={2}hdb,cn=config
     changetype: modify
     replace: olcRootDN
     olcRootDN: cn=root,dc=example,dc=org

     dn: olcDatabase={2}hdb,cn=config
     changetype: modify
     replace: olcRootPW
     olcRootPW: {SSHA}nk8A/+uFKfDb1OhaYmPUFlQmWwcdtNF4
     ```

   * `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/openldap/scratch/db.ldif`

   **NOTES**: From now until the end of this HOWTO, we'll consider that:
    * `<LDAP-ROOT-PW_CHANGEME>` ==> `password`

4. Create Certificate/Key:
   * Self signed (3072 bit - 3 years before expiration) - **This HOWTO will use Self Signed Certificate for LDAP**:

     ```bash
     sudo openssl req -newkey rsa:3072 -x509 -nodes -out /etc/openldap/$(hostname -f).crt -keyout /etc/openldap/$(hostname -f).key -days 1095 -subj "/CN=$(hostname -f)"

     sudo chown ldap:ldap /etc/openldap/$(hostname -f).crt

     sudo chown ldap:ldap /etc/openldap/$(hostname -f).key
     ```

   * Signed:

     ```bash
     sudo openssl req -new -newkey rsa:3072 -nodes -out /etc/pki/tls/$(hostname -f).csr -keyout /etc/pki/tls/private/$(hostname -f).key -subj "/C=IT/CN=$(hostname -f)"
     ```

     (According to [NSA and NIST](https://www.keylength.com/en/compare/), RSA with 3072 bit-modulus is the minimum to protect up to TOP SECRET over than 2030)

5. Enable SSL for LDAP:
   * `sudo vim /etc/openldap/ldap.conf`

     ```bash
     #TLS_CACERTDIR  /etc/openldap/certs
     TLS_CACERT      /etc/openldap/ldap.example.org.crt
     ```

   * `sudo chown ldap:ldap /etc/openldap/ldap.conf`

  **NOTES**: Be sure to have set the correct FQDN in the `/etc/hosts` file

6. Restart OpenLDAP:
   * `sudo systemctl restart slapd`

## Configuration

1. Import LDAP schemas
   * `sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/cosine.ldif`
   * `sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/ppolicy.ldif`
   * `sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/inetorgperson.ldif`
   * `sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/openldap.ldif`
   * `sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/dyngroup.ldif`

2. Configure LDAP for SSL:
   * `sudo vim /etc/openldap/olcTLS.ldif`

     ```bash
     dn: cn=config
     changetype: modify
     replace: olcTLSCACertificateFile
     olcTLSCACertificateFile: /etc/openldap/ldap.example.org.crt
     -
     replace: olcTLSCertificateFile
     olcTLSCertificateFile: /etc/openldap/ldap.example.org.crt
     -
     replace: olcTLSCertificateKeyFile
     olcTLSCertificateKeyFile: /etc/openldap/ldap.example.org.key
     ```

   * `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/openldap/olcTLS.ldif`

3. Add openldap binding to LDAPS (optional):
   > LDAPS uses 636 port , LDAP (StartTLS or Plain) uses 389 port

   * `sudo vim /etc/sysconfig/slapd`

     ```bash
     SLAPD_URLS="ldapi:/// ldap:/// ldaps:///"
     ```

   * `sudo systemctl restart slapd`

4. Create organization and root user in LDAP (example.org):

   * `sudo vim /etc/openldap/scratch/add_org.ldif`

     ```bash
     dn: dc=example,dc=org
     objectClass: dcObject
     objectClass: organization
     o: example.org
     dc: example
     ```

   * `sudo ldapadd -W -D "cn=root,dc=example,dc=org" -H ldapi:/// -f /etc/openldap/scratch/add_org.ldif`

5. Create three branches, `peole`, `groups` and `system`, with:
   * `vim /etc/openldap/scratch/add_ou.ldif`

     ```bash
     dn: ou=people,dc=example,dc=org
     objectClass: organizationalUnit
     objectClass: top
     ou: People

     dn: ou=groups,dc=example,dc=org
     objectClass: organizationalUnit
     objectClass: top
     ou: Groups

     dn: ou=system,dc=example,dc=org
     objectClass: organizationalUnit
     objectClass: top
     ou: System
     ```

   * `sudo ldapadd -W -D "cn=root,dc=example,dc=org" -H ldapi:/// -f /etc/openldap/scratch/add_ou.ldif`

   * Verify with: `sudo ldapsearch -x -b dc=example,dc=org`

6. Create the `idpuser` needed to perform "Bind and Search" operations:
   * Generate password: `slappasswd`
 
   * `sudo vim /etc/openldap/scratch/add_idpuser.ldif`

     ```bash
     dn: cn=idpuser,ou=system,dc=example,dc=org
     objectClass: inetOrgPerson
     cn: idpuser
     sn: idpuser
     givenName: idpuser
     userPassword: <INSERT-HERE-IDPUSER-PW>
     ```

   * `sudo ldapadd -W -D "cn=root,dc=example,dc=org" -H ldapi:/// -f /etc/openldap/scratch/add_idpuser.ldif`

7. Configure OpenLDAP ACL to allow 'idpuser' to perform 'search' on the directory:
   * Check which configuration your directory has with:
     `sudo ldapsearch  -Y EXTERNAL -H ldapi:/// -b cn=config 'olcDatabase={2}hdb'`

   * Configure ACL for 'idpuser' with:
     `sudo vim /etc/openldap/scratch/olcAcl.ldif`

      ```bash
      dn: olcDatabase={2}hdb,cn=config
      changeType: modify
      replace: olcAccess
      olcAccess: {0}to * by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage by * break
      olcAccess: {1}to attrs=userPassword by self write by anonymous auth by dn="cn=root,dc=example,dc=org" write by * none
      olcAccess: {2}to dn.base="" by anonymous auth by * read
      olcAccess: {3}to dn.base="cn=Subschema" by * read
      olcAccess: {4}to * by dn.exact="cn=idpuser,ou=system,dc=example,dc=org" read by anonymous auth by self read
      ```

   * `sudo ldapmodify  -Y EXTERNAL -H ldapi:/// -f /etc/openldap/scratch/olcAcl.ldif`

8. Check that 'idpuser' can search other users (when users exist):
   * `sudo ldapsearch -x -D 'cn=idpuser,ou=system,dc=example,dc=org' -W -b "ou=people,dc=example,dc=org"`

9. Install needed schemas (eduPerson, SCHAC, Password Policy):
   * Run the following commands:
     ```bash
     cd /etc/openldap/schema

     sudo curl https://raw.githubusercontent.com/GEANT/ansible-shibboleth/master/roles/openldap/files/eduperson-201602.ldif -o eduperson.ldif

     sudo curl https://raw.githubusercontent.com/GEANT/ansible-shibboleth/master/roles/openldap/files/schac-20150413.ldif -o schac.ldif

     sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/eduperson.ldif

     sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/schac.ldif
     ```
   
   * Verify all with: `ldapsearch -Y EXTERNAL -H ldapi:/// -b cn=schema,cn=config dn`

10. Add `memberof` Configuration:
    
    1. `sudo vim /etc/openldap/scratch/add_memberof.ldif`

        ```bash
        dn: cn=module,cn=config
        cn: module
        objectClass: olcModuleList
        olcModuleLoad: memberof
        olcModulePath: /usr/lib64/openldap/

        dn: olcOverlay={0}memberof,olcDatabase={2}hdb,cn=config
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
        ```

    2. `sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /etc/openldap/scratch/add_memberof.ldif`

    3. `sudo vim /etc/openldap/scratch/add_refint1.ldif`

        ```bash
        dn: cn=module{0},cn=config
        add: olcmoduleload
        olcmoduleload: refint   
        ```

    4. `sudo ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f /etc/openldap/scratch/add_refint1.ldif`

    5. `sudo vim /etc/openldap/scratch/add_refint2.ldif`

        ```bash
        dn: olcOverlay={1}refint,olcDatabase={2}hdb,cn=config
        objectClass: olcConfig
        objectClass: olcOverlayConfig
        objectClass: olcRefintConfig
        objectClass: top
        olcOverlay: {1}refint
        olcRefintAttribute: memberof member manager owner
        ```

    6. `sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /etc/openldap/scratch/add_refint2.ldif`

11. Improve performance:
    * `sudo vim /etc/openldap/scratch/olcDbIndex.ldif`

      ```bash
      dn: olcDatabase={2}hdb,cn=config
      changetype: modify
      replace: olcDbIndex
      olcDbIndex: objectClass eq
      olcDbIndex: member eq
      olcDbIndex: cn pres,eq,sub
      olcDbIndex: ou pres,eq,sub
      olcDbIndex: uid pres,eq
      olcDbIndex: entryUUID eq
      olcDbIndex: sn pres,eq,sub
      olcDbIndex: mail pres,eq,sub
      ```

    * `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/openldap/scratch/olcDbIndex.ldif`

12. Configure Logging:
    * `sudo vim /etc/rsyslog.d/99-slapd.conf`

      ```bash
      local4.* /var/log/openldap.log
      ```

    * `sudo vim /etc/openldap/scratch/olcLogLevelStats.ldif`

      ```bash
      dn: cn=config
      changeType: modify
      replace: olcLogLevel
      olcLogLevel: stats
      ```

    * `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/openldap/scratch/olcLogLevelStats.ldif`
    * `sudo service rsyslog restart`
    * `sudo service slapd restart`

13. Configure openLDAP olcSizeLimit:
    * `sudo vim /etc/openldap/scratch/olcSizeLimit.ldif`

      ```bash
      dn: cn=config
      changetype: modify
      replace: olcSizeLimit
      olcSizeLimit: unlimited

      dn: olcDatabase={-1}frontend,cn=config
      changetype: modify
      replace: olcSizeLimit
      olcSizeLimit: unlimited
      ```

    * `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/openldap/scratch/olcSizeLimit.ldif`

14. Add an user:
    * `sudo vim /etc/openldap/scratch/user1.ldif`

      ```bash
      # USERNAME: user1 , PASSWORD: password
      # Generate a new password with: sudo slappasswd -s <newPassword>
      dn: uid=user1,ou=people,dc=example,dc=org
      changetype: add
      objectClass: inetOrgPerson
      objectClass: eduPerson
      uid: user1
      sn: User1
      givenName: Test
      cn: Test User1
      displayName: Test User1
      preferredLanguage: en
      userPassword: {SSHA}nk8A/+uFKfDb1OhaYmPUFlQmWwcdtNF4
      mail: test.user1@example.org
      eduPersonAffiliation: student
      eduPersonAffiliation: staff
      eduPersonAffiliation: member
      ```

    * `sudo ldapadd -D "cn=root,dc=example,dc=org" -W -f /etc/openldap/scratch/user1.ldif`

15. Check that 'idpuser' can find user1:
    * ```bash 
      sudo ldapsearch -x -D 'cn=idpuser,ou=system,dc=example,dc=org' -W -b "uid=user1,ou=people,dc=example,dc=org"
      ```

16. Check that LDAP anonymous binding work with StartTLS:
    * `sudo ldapwhoami -H ldap:// -x -ZZ`
   
      ```bash
      anonymous
      ```

17. Disable Anonymous binding:

    ```
    ldapmodify -Y EXTERNAL -H ldapi:/// <<EOF
    dn: cn=config
    changetype: modify
    add: olcDisallows
    olcDisallows: bind_anon

    dn: olcDatabase={-1}frontend,cn=config
    changetype: modify
    add: olcRequires
    olcRequires: authc
    EOF
    ```

18. Check that LDAP StartTLS is working for `idpuser` and not anymore for `anonymous` user:
    * `sudo ldapwhoami -x -D 'cn=idpuser,ou=system,dc=example,dc=org' -W -ZZ -v`

      ```bash
      ldap_initialize( <DEFAULT> )
      Enter LDAP Password:
      dn:cn=idpuser,ou=system,dc=example,dc=org
      Result: Success (0)
      ```

    * `sudo ldapwhoami -H ldap:// -x -ZZ`

      ```bash
      ldap_bind: Inappropriate authentication (48)
	            additional info: anonymous bind disallowed
      ```
    
## Utilities

### Bash scripts

* [domain2dn](./domain2dn.sh): An useful script to convert a domain name (e.g.: `example.org`) into its corresponding LDAP distinguish name (e.g.: `dc=example,dc=org`).

## LDAP Administration tools

* [Apache Directory Studio](https://directory.apache.org/studio/): Apache Directory Studio is a complete directory tooling platform intended to be used with any LDAP server.
