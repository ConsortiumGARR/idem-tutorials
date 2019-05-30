# HOWTO Install and Configure OpenLDAP for federated access

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [PhpLdapAdmin (PLA) - optional](#phpldapadmin-pla---optional)
   1. [PLA Installation](#pla-installation)
   2. [PLA Configuration](#pla-configuration)

## Requirements
* Debian 9 (Stretch)

## Installation

1. System Update:
   * `sudo apt update ; sudo apt upgrade`

2. Automate SLAPD installation (Change all "_CHANGEME" values):
   * `sudo apt install debconf-utils`
   * `sudo vim /root/debconf-slapd.conf`

     ```bash
     slapd slapd/password1 password <LDAP-ROOT-PW_CHANGEME>
     slapd slapd/password2 password <LDAP-ROOT-PW_CHANGEME>
     slapd slapd/move_old_database boolean true
     slapd slapd/domain string <INSTITUTE-DOMAIN_CHANGEME>
     slapd shared/organization string <ORGANIZATION-NAME_CHANGE>
     slapd slapd/no_configuration boolean false
     slapd slapd/purge_database boolean false
     slapd slapd/allow_ldap_v2 boolean false
     slapd slapd/backend select MDB
      ```
   * `cat /root/debconf-slapd.conf | debconf-set-selections`
	
   **NOTES**: From now until the end of this HOWTO, we'll consider that:
      * `<LDAP-ROOT-PW_CHANGEME>` ==> `ciaoldap`
      * `<INSTITUTE-DOMAIN_CHANGEME>` ==> `example.org`
      * `<ORGANIZATION-NAME_CHANGE>` ==> `Example Org`

3. Install require package:
   * `sudo apt install slapd ldap-utils ldapscripts`
    
4. Create Certificate/Key:
   * Self signed (2048 bit - 3 years before expiration):

      * `openssl req -newkey rsa:2048 -x509 -nodes -out /etc/ldap/ldap.example.org.crt -keyout /etc/ldap/ldap.example.org.key -days 1095`
        
      * `chown openldap:openldap /etc/ldap/ldap.example.org.crt`
        
      * `chown openldap:openldap /etc/ldap/ldap.example.org.key`
      
   * Signed:
      
      * `openssl req -new -newkey rsa:2048 -nodes -out /etc/ssl/certs/ldap.example.org.csr -keyout /etc/ssl/private/ldap.example.org.key -subj "/C=IT/ST=/L=Rome/O=Consortium GARR/CN=ldap.example.org"`
        
   **NOTES**: This HOWTO will use Self Signed Certificate for LDAP

5. Enable SSL for LDAP:
   * `sudo vim /etc/ldap/ldap.conf`

       ```bash
       TLS_CACERT      /etc/ldap/ldap.example.org.crt
       ```
   * `sudo chown openldap:openldap /etc/ldap/ldap.conf`

   **NOTES**: Be sure to have set the correct FQDN on your `/etc/hosts` file

6. Restart OpenLDAP:
   * `sudo service slapd restart`

## Configuration

1. Configure LDAP for SSL:
   * `sudo vim /etc/ldap/olcTLS.ldif`

      ```bash
      dn: cn=config
      changetype: modify
      replace: olcTLSCACertificateFile
      olcTLSCACertificateFile: /etc/ldap/ldap.example.org.crt
      -
      replace: olcTLSCertificateFile
      olcTLSCertificateFile: /etc/ldap/ldap.example.org.crt
      -
      replace: olcTLSCertificateKeyFile
      olcTLSCertificateKeyFile: /etc/ldap/ldap.example.org.key
      ```
   * `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/olcTLS.ldif`

2. Create the 3 main branches, 'main', 'groups' and 'system', with:
   * `mkdir /etc/ldap/scratch`
   * `vim /etc/ldap/scratch/add_ou.ldif`
   
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

    * `sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w <LDAP-ROOT-PW_CHANGEME> -H ldapi:/// -f /etc/ldap/scratch/add_ou.ldif`
    
    * Verify with: `sudo ldapsearch -x -b dc=example,dc=org`
    
3. Create the 'idpuser' needed to perform "Bind and Search" operations:
    * `vim /etc/ldap/scratch/add_idpuser.ldif`
    
      ```bash
      dn: cn=idpuser,ou=system,dc=example,dc=org
      objectClass: inetOrgPerson
      cn: idpuser
      sn: idpuser
      givenName: idpuser
      userPassword: <INSERT-HERE-IDPUSER-PW>
      ```
    * `sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w <LDAP-ROOT-PW_CHANGEME> -H ldapi:/// -f /etc/ldap/scratch/add_idpuser.ldif`
    
4. Configure OpenLDAP ACL to allow 'idpuser' to perform 'search' on the directory:
    * Check which configuration your directory has with:
      `sudo ldapsearch  -Y EXTERNAL -H ldapi:/// -b cn=config 'olcDatabase={1}mdb'`
      
    * Configure ACL for 'idpuser' with:
      `vim /etc/ldap/scratch/olcAcl.ldif`
      
      ```bash
      dn: olcDatabase={1}mdb,cn=config
      changeType: modify
      replace: olcAccess
      olcAccess: {0}to * by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage by * break
      olcAccess: {1}to attrs=userPassword by self write by anonymous auth by dn="cn=admin,dc=example,dc=org" write by * none
      olcAccess: {2}to dn.base="" by anonymous auth by * read
      olcAccess: {3}to dn.base="cn=Subschema" by * read
      olcAccess: {4}to * by dn.exact="cn=idpuser,ou=system,dc=example,dc=org" read by anonymous auth by self read
      ```

    * `sudo ldapmodify  -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcAcl.ldif`

5. Check that 'idpuser' can search other users (when users exist):
    * `sudo ldapsearch -x -D 'cn=idpuser,ou=system,dc=example,dc=org' -w <INSERT-HERE-IDPUSER-PW> -b "ou=people,dc=example,dc=org"`

6. Install needed schemas (eduPerson, SCHAC, Password Policy):
   * `cd /etc/ldap/schema`
   * `wget https://raw.githubusercontent.com/malavolti/ansible-shibboleth/master/roles/openldap/files/eduperson-201602.ldif -O eduperson.ldif`
   * `wget https://raw.githubusercontent.com/malavolti/ansible-shibboleth/master/roles/openldap/files/schac-20150413.ldif -O schac.ldif`
   * `sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/eduperson.ldif`
   * `sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/schac.ldif`
   * `sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/ppolicy.ldif`
   * Verify with: `ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:/// -b cn=schema,cn=config dn`

7. Add MemberOf Configuration:
   1. `sudo vim /etc/ldap/scratch/add_memberof.ldif`
   
      ```bash
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
      ```

   2. `sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/add_memberof.ldif`
   
   3. `sudo vim /etc/ldap/scratch/add_refint1.ldif`
   
      ```bash
      dn: cn=module{1},cn=config
      add: olcmoduleload
      olcmoduleload: refint   
      ```
   
   4. `sudo ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/add_refint1.ldif` 
   
   5. `sudo vim /etc/ldap/scratch/add_refint2.ldif`
   
      ```bash
      dn: olcOverlay={1}refint,olcDatabase={1}mdb,cn=config
      objectClass: olcConfig
      objectClass: olcOverlayConfig
      objectClass: olcRefintConfig
      objectClass: top
      olcOverlay: {1}refint
      olcRefintAttribute: memberof member manager owner
      ```
   
   6. `sudo ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/add_refint2.ldif`
   
8. Improve performance:
   * `sudo vim /etc/ldap/scratch/olcDbIndex.ldif`

     ```bash
     dn: olcDatabase={1}mdb,cn=config
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

   * `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcDbIndex.ldif`

9. Configure Logging:
   * `sudo mkdir /var/log/slapd`
   * `sudo vim /etc/rsyslog.d/99-slapd.conf`

      ```bash
      local4.* /var/log/slapd/slapd.log
      ```
      
   * `sudo vim /etc/ldap/scratch/olcLogLevelStats.ldif`

     ```bash
     dn: cn=config
     changeType: modify
     replace: olcLogLevel
     olcLogLevel: stats
     ```

   * `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcLogLevelStats.ldif`
   * `sudo service rsyslog restart`
   * `sudo service slapd restart`


10. Configure openLDAP olcSizeLimit:
   * `sudo vim /etc/ldap/scratch/olcSizeLimit.ldif`

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

   * `sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcSizeLimit.ldif`
 
11. Add your first user:
   * `sudo vim /etc/ldap/scratch/user1.ldif`

     ```bash
     # USERNAME: user1 , PASSWORD: ciaouser1
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
     preferredLanguage: it
     userPassword: {SSHA}u5tYgO6iVerMuuMJBsYnPHM+70ammhnj
     mail: test.user1@example.org
     eduPersonAffiliation: student
     eduPersonAffiliation: staff
     eduPersonAffiliation: member
     schacHomeOrganization: example.org
     schacHomeOrganizationType: urn:mace:terena.org:schac:homeOrganizationType:it:university
     ```

   * `sudo ldapadd -D cn=admin,dc=example,dc=org -w <LDAP-ROOT-PW_CHANGEME> -f /etc/ldap/scratch/user1.ldif`

# PhpLdapAdmin (PLA) - optional

## PLA Installation

1. Install requirements:
   * `sudo apt install apache2-utils python-passlib gettext php php-ldap php-xml`

2. Download and extract PLA into `/opt` directory:
   * `cd /var/www/html ; wget https://github.com/FST777/phpLDAPadmin/archive/v2.0.0-alpha.tar.gz -O phpldapadmin.tar.gz`
   * `tar -xzf phpldapadmin.tar.gz ; mv phpLDAPadmin-2.0.0-alpha pla`

3. Create PLA configuration file:
   * `cd /var/www/html/pla/config`
   * `sudo cp config.php.example config.php`

4. Enable LDAP Apache module:
   * `sudo a2enmod ldap`

5. Restart Apache2:
   * `sudo systemctl restart apache2`
   
6. Login on PLA:
   * Navigate to `http://<YOUR-LDAP-FQDN>/pla`
   * Login with:
     * Username: `cn=admin,dc=example,dc=org`
     * Password: `<LDAP-ROOT-PW_CHANGEME>`
   
# PLA Configuration

1. Edit `/var/www/html/pla/config/config.php` to configure PhpLdapAdmin.
