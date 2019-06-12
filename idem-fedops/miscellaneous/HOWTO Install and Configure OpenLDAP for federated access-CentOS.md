# HOWTO Install and Configure OpenLDAP for federated access on CentOS

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [PhpLdapAdmin (PLA) - optional](#phpldapadmin-pla---optional)
   1. [PLA Installation](#pla-installation)
   2. [PLA Configuration](#pla-configuration)

## Requirements
* Centos 7.x (with SELinux deactivated)

## Installation

1. System Update:
   * `sudo yum upgrade`

2. Install required packages:
   * `sudo yum install openldap openldap-clients openldap-servers openssl`
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
   * `mkdir /etc/openldap/scratch`
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
      * `<INSTITUTE-DOMAIN_CHANGEME>` ==> `example.org`
      * `<ORGANIZATION-NAME_CHANGEME>` ==> `Example Org`

4. Create Certificate/Key:
  * Self signed (2048 bit - 3 years before expiration):

     * `openssl req -newkey rsa:2048 -x509 -nodes -out /etc/openldap/ldap.example.org.crt -keyout /etc/openldap/ldap.example.org.key -days 1095`

     * `chown ldap:ldap /etc/openldap/ldap.example.org.crt`

     * `chown ldap:ldap /etc/openldap/ldap.example.org.key`

  * Signed:

     * `openssl req -new -newkey rsa:2048 -nodes -out /etc/ssl/certs/ldap.example.org.csr -keyout /etc/ssl/private/ldap.example.org.key -subj "/C=FR/ST=/L=Rennes/O=RENATER/CN=ldap.example.org"`

  **NOTES**: This HOWTO will use Self Signed Certificate for LDAP

  5. Enable SSL for LDAP:
     * `sudo vim /etc/openldap/ldap.conf`

         ```bash
         #TLS_CACERTDIR  /etc/openldap/certs
         TLS_CACERT      /etc/openldap/ldap.example.org.crt
         ```
     * `sudo chown ldap:ldap /etc/openldap/ldap.conf`

     **NOTES**: Be sure to have set the correct FQDN on your `/etc/hosts` file

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

3. Bind openldap to LDAPS and LDAPI only (optionnal):

   * `sudo vim /etc/sysconfig/slapd`

```bash
SLAPD_URLS="ldapi:/// ldaps:///"
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

5. Create the 3 main branches, 'main', 'groups' and 'system', with:
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

6. Create the 'idpuser' needed to perform "Bind and Search" operations:
    * Generate password: `slappasswd`
    * `vim /etc/openldap/scratch/add_idpuser.ldif`

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
      `vim /etc/openldap/scratch/olcAcl.ldif`

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
   * `cd /etc/openldap/schema`
   * `wget https://raw.githubusercontent.com/malavolti/ansible-shibboleth/master/roles/openldap/files/eduperson-201602.ldif -O eduperson.ldif`
   * `wget https://raw.githubusercontent.com/malavolti/ansible-shibboleth/master/roles/openldap/files/schac-20150413.ldif -O schac.ldif`
   * `sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/eduperson.ldif`
   * `sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/schac.ldif`
   * Verify with: `ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:/// -b cn=schema,cn=config dn`

#########################################################################################################@

10. Add MemberOf Configuration:
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

14. Add your first user:
   * `sudo vim /etc/openldap/scratch/user1.ldif`

```bash
# USERNAME: user1 , PASSWORD: password
# Generate a new password with: sudo slappasswd -s <newPassword>
dn: uid=user1,ou=people,dc=example,dc=org
changetype: add
objectClass: inetOrgPerson
objectClass: eduPerson
objectClass: schacPersonalCharacteristics
objectClass: schacContactLocation
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
schacHomeOrganization: example.org
schacHomeOrganizationType: urn:mace:terena.org:schac:homeOrganizationType:it:university
```

   * `sudo ldapadd -D "cn=root,dc=example,dc=org" -W -f /etc/openldap/scratch/user1.ldif`

## LDAP IHM
# Apache Directory Studio
