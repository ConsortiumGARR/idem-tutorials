# HOWTO Install and Configure OpenLDAP for federated access (Debian/Ubuntu)

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements)
2. [Notes](#notes)
3. [Utility](#utility)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [PhpLdapAdmin (PLA) - optional](#phpldapadmin-pla---optional)
   1. [PLA Installation](#pla-installation)
   2. [PLA Configuration](#pla-configuration)

## Requirements
* Debian 11 (Buster) or Ubuntu 20.04 (Local Fossa)

## Notes

This HOWTO uses `example.org` to provide this guide with example values.

Please remember to **replace all occurencences** of the `example.org` domain name with the domain name of your institution.

# Utility

* Simple Bash script useful to convert a Domain Name into a Distinguished Name of LDAP: 
  [domain2dn.sh](https://github.com/ConsortiumGARR/idem-tutorials/blob/master/idem-fedops/miscellaneous/domain2dn.sh)

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
     slapd shared/organization string <ORGANIZATION-NAME_CHANGEME>
     slapd slapd/no_configuration boolean false
     slapd slapd/purge_database boolean false
     slapd slapd/allow_ldap_v2 boolean false
     slapd slapd/backend select MDB
     ```

   * `sudo cat /root/debconf-slapd.conf | sudo debconf-set-selections`

   **NOTES**: The HOWTO considers the following values:
      * `<LDAP-ROOT-PW_CHANGEME>` ==> `ciaoldap`
      * `<INSTITUTE-DOMAIN_CHANGEME>` ==> `example.org`
      * `<ORGANIZATION-NAME_CHANGEME>` ==> `Example Org`

3. Install required package:
   * `sudo apt install slapd ldap-utils ldapscripts`

4. Create Certificate/Key (**This HOWTO will use Self Signed Certificate for LDAP**):
   * Self Signed (4096 bit - 3 years before expiration):

      * ```bash
        sudo openssl req -newkey rsa:4096 -x509 -nodes -out /etc/ldap/$(hostname -f).crt -keyout /etc/ldap/$(hostname -f).key -days 1095 -subj "/CN=$(hostname -f)"
        sudo chown openldap:openldap /etc/ldap/$(hostname -f).crt
        sudo chown openldap:openldap /etc/ldap/$(hostname -f).key
        sudo chown openldap:openldap /etc/ldap/$(hostname -f).crt /etc/ldap/$(hostname -f).key
        ```

   * Signed (**Do not use if you are not a NREN GARR Member**):
     * Add CA Cert into `/etc/ssl/certs`
       * If you use GARR TCS or GEANT TCS:
         ```bash
         sudo wget -O /etc/ssl/certs/GEANT_OV_RSA_CA_4.pem https://crt.sh/?d=2475254782

         sudo wget -O /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt https://crt.sh/?d=924467857

         sudo cat /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt >> /etc/ssl/certs/GEANT_OV_RSA_CA_4.pem

         sudo rm /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt
         ```

       * If you use ACME (Let's Encrypt):
         * `sudo ln -s /etc/letsencrypt/live/<SERVER_FQDN>/chain.pem /etc/ssl/certs/ACME-CA.pem`

     * Generate CSR(Certificate Signing Request) and the KEY:
       ```bash
       sudo openssl req -new -newkey rsa:4096 -nodes -out /etc/ssl/certs/$(hostname -f).csr -keyout /etc/ssl/private/$(hostname -f).key -subj "/C=IT/ST=/L=Rome/O=Consortium GARR/CN=$(hostname -f)"
        
       sudo cp /etc/ssl/certs/$(hostname -f).crt /etc/ldap/$(hostname -f).crt
       sudo cp /etc/ssl/private/$(hostname -f).key /etc/ldap/$(hostname -f).key
       sudo chown openldap:openldap /etc/ldap/$(hostname -f).crt /etc/ldap/$(hostname -f).key
       ```

5. Check `/etc/hosts` to be sure to have the correct FQDN for OpenLDAP server

6. Enable SSL for LDAP:
   ```bash
   sudo sed -i "s/TLS_CACERT.*/TLS_CACERT\t\/etc\/ldap\/$(hostname -f).crt/g" /etc/ldap/ldap.conf
   
   sudo chown openldap:openldap /etc/ldap/ldap.conf
   ```

7. Restart OpenLDAP:
   * `sudo service slapd restart`

## Configuration

1. Create `scratch` directory:
   * `sudo mkdir /etc/ldap/scratch`

2. Configure LDAP for SSL:
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
  
3. Apply with:
   ```bash
   sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcTLS.ldif
   ```

4. Create the 3 main _Organizational Unit_ (OU), `people`, `groups` and `system`.

   *Example:* if the domain name is `example.org` than  the distinguish name will be `dc=example,dc=org`:
   
   **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name and `<LDAP-ROOT-PW_CHANGEME>` with the LDAP ROOT password!

   * ```bash
     sudo bash -c 'cat > /etc/ldap/scratch/add_ou.ldif <<EOF
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
     EOF'
     ```

   * Apply with:
     ```bash
     sudo ldapadd -x -D 'cn=admin,dc=example,dc=org' -w '<LDAP-ROOT-PW_CHANGEME>' -H ldapi:/// -f /etc/ldap/scratch/add_ou.ldif
     ```

   * Verify with: `sudo ldapsearch -x -b 'dc=example,dc=org'`

5. Create the `idpuser` needed to perform "*Bind and Search*" operations:
   
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

5. Configure OpenLDAP ACL to allow `idpuser` to perform *search* operation on the directory:

   **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!
   
   * Check which configuration your directory has with:
     * `sudo ldapsearch  -Y EXTERNAL -H ldapi:/// -b cn=config 'olcDatabase={1}mdb'`

   * Configure ACL for `idpuser` with:

     ```bash
     sudo bash -c 'cat > /etc/ldap/scratch/olcAcl.ldif <<EOF
     dn: olcDatabase={1}mdb,cn=config
     changeType: modify
     replace: olcAccess
     olcAccess: {0}to * by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage by * break
     olcAccess: {1}to attrs=userPassword by self write by anonymous auth by dn="cn=admin,dc=example,dc=org" write by * none
     olcAccess: {2}to dn.base="" by anonymous auth by * read
     olcAccess: {3}to dn.base="cn=Subschema" by * read
     olcAccess: {4}to * by dn.exact="cn=idpuser,ou=system,dc=example,dc=org" read by anonymous auth by self read
     EOF'
     ```

   * Apply with:
     ```bash
     sudo ldapadd  -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcAcl.ldif
     ```

6. Check that `idpuser` can search other users (when users exist):

   **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!

   ```bash
   sudo ldapsearch -x -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<INSERT-HERE-IDPUSER-PW>' -b 'ou=people,dc=example,dc=org'
   ```

7. Install needed schemas (eduPerson, SCHAC, Password Policy):
   ```bash
   sudo wget https://raw.githubusercontent.com/malavolti/ansible-shibboleth/master/roles/openldap/files/eduperson-201602.ldif -O /etc/ldap/schema/eduperson.ldif
   sudo wget https://raw.githubusercontent.com/malavolti/ansible-shibboleth/master/roles/openldap/files/schac-20150413.ldif -O /etc/ldap/schema/schac.ldif
   sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/eduperson.ldif
   sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/schac.ldif
   sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/ppolicy.ldif
  
   sudo ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:/// -b 'cn=schema,cn=config dn'
   ```

   and verify presence of the new `schac` and `eduPerson` schemas.

8. Add MemberOf Configuration:
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
      
   sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/add_memberof.ldif
   ```

9. Improve performance:
   ```bash
   sudo bash -c 'cat > /etc/ldap/scratch/olcDbIndex.ldif <<EOF
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
   EOF'
     
   sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/olcDbIndex.ldif
   ```

10. Configure Logging:
    ```bash
    sudo mkdir /var/log/slapd

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

11. Configure openLDAP olcSizeLimit:
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

12. Add your first user:

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!
    * Configure `user1.ldif`:
      ```bash
      sudo bash -c 'cat > /etc/ldap/scratch/user1.ldif <<EOF
      # USERNAME: user1 , PASSWORD: ciaouser1
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
      preferredLanguage: it
      userPassword: {SSHA}u5tYgO6iVerMuuMJBsYnPHM+70ammhnj
      mail: test.user1@example.org
      eduPersonAffiliation: student
      eduPersonAffiliation: staff
      eduPersonAffiliation: member
      eduPersonEntitlement: urn:mace:terena.org:tcs:escience-user
      eduPersonEntitlement: urn:mace:terena.org:tcs:personal-user
      EOF'
      ```
      
   * Apply with:
     ```bash
     sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/scratch/user1.ldif
     ```

13. Check that `idpuser` can find `user1`:

    **Be carefull!** Replace `dc=example,dc=org` with distinguish name ([DN](https://ldap.com/ldap-dns-and-rdns/)) of your domain name!

    * `sudo ldapsearch -x -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<INSERT-HERE-IDPUSER-PW>' -b 'uid=user1,ou=people,dc=example,dc=org'`

14. Check that LDAP has TLS ('anonymous' MUST BE returned):
    * `sudo ldapwhoami -H ldap:// -x -ZZ`

15. Make mail, eduPersonPrincipalName and schacPersonalUniqueID as unique:
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

16. Disable Anonymous bind
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

# PhpLdapAdmin (PLA) - optional

## PLA Installation

1. Install requirements:
   * `sudo apt install apache2-utils python3-passlib gettext php php-ldap php-xml`

2. Download and extract PLA into the Apache2 DocumentRoot directory:
   ```bash
   sudo su
   
   mkdir /var/www/html/$(hostname -f)
   
   cd /var/www/html/$(hostname -f)
   
   wget https://github.com/leenooks/phpLDAPadmin/archive/refs/tags/1.2.6.2.tar.gz -O phpldapadmin.tar.gz
   
   tar -xzf phpldapadmin.tar.gz
   
   mv phpLDAPadmin-1.2.6.2 pla
   ```

3. Create PLA configuration file:
   ```bash
   cd /var/www/html/$(hostname -f)/pla/config
   
   sudo cp config.php.example config.php
   ```

4. Enable LDAP Apache module:
   * `sudo a2enmod ldap`

5. Restart Apache2:
   * `sudo systemctl restart apache2`

6. Login on PLA:
   * Navigate to `http://<YOUR-LDAP-FQDN>/pla`
   * Login with:
     * Username: `cn=admin,dc=example,dc=org`
     * Password: `<LDAP-ROOT-PW_CHANGEME>`

## PLA Configuration

1. Edit `/var/www/html/$(hostname -f)/pla/config/config.php` to configure PhpLdapAdmin.
