# HOWTO Install and Configure a Shibboleth IdP v4.x on CentOS with Apache2 + Jetty9

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements](#requirements)
   1. [Hardware](#hardware)
   2. [Other](#other)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Notes](#notes)
4. [Install Instructions](#install-instructions)
   1. [Install software requirements](#install-software-requirements)
   2. [Configure the environment](#configure-the-environment)
   3. [Install Shibboleth Identity Provider v4.x](#install-shibboleth-identity-provider-v4x)
   4. [Install Jetty 9 Web Server](#install-jetty-9-web-server)
5. [Configuration Instructions](#configuration-instructions)
   1. [Configure Jetty](#configure-jetty)
   2. [Configure SSL on Apache2 (front-end of Jetty)](#configure-ssl-on-apache2-front-end-of-jetty)
   3. [Configure Shibboleth Identity Provider Storage](#configure-shibboleth-identity-provider-storage)
      1. [Strategy A - Default (HTML Local Storage, Encryption GCM, No Database) - Recommended](#strategy-a---default-html-local-storage-encryption-gcm-no-database---recommended)
      2. [Strategy B - JPA Storage Service - using a database](#strategy-b---jpa-storage-service---using-a-database)
   4. [Configure the Directory (openLDAP or AD) Connection](#configure-the-directory-openldap-or-ad-connection)
   5. [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)
      1. [Strategy A - Computed mode - Default & Recommended](#strategy-a---computed-mode---default--recommended)
      2. [Strategy B - Stored mode - using a database](#strategy-b---stored-mode---using-a-database)
   6. [Configure the attribute resolver (sample)](#configure-the-attribute-resolver-sample)
   7. [Configure Shibboleth Identity Provider to release the eduPersonTargetedID](#configure-shibboleth-identity-provider-to-release-the-edupersontargetedid)
      1. [Strategy A - Computed mode - using the computed persistent NameID](#strategy-a---computed-mode---using-the-computed-persistent-nameid)
      2. [Strategy B - Stored mode - using a database](#strategy-b---stored-mode---using-the-persistent-nameid-database)
   8. [Configure the attribute resolution with Attribute Registry](#configure-the-attribute-resolution-with-attribute-registry)
   9. [Configure Shibboleth IdP Logging](#configure-shibboleth-idp-logging)
   10. [Translate IdP messages into the preferred language](#translate-idp-messages-into-preferred-language)
   11. [Enrich IdP Login Page with the Institutional Logo](#enrich-idp-login-page-with-the-institutional-logo)
   12. [Enrich IdP Login Page with Information and Privacy Policy pages](#enrich-idp-login-page-with-information-and-privacy-policy-pages)
   13. [Change default login page footer text](#change-default-login-page-footer-text)
   14. [Change default "Forgot your password?" and "Need help?" endpoints](#change-default-forgot-your-password-and-need-help-endpoints)
   15. [Disable SAML1 Deprecated Protocol](#disable-saml1-deprecated-protocol)
   16. [Secure cookies and other IDP data](#secure-cookies-and-other-idp-data)
   17. [Configure Attribute Filter Policy to release attributes to Federated Resources](#configure-attribute-filter-policy-to-release-attributes-to-federated-resources)
   18. [Register the IdP on the IDEM Test Federation](#register-the-idp-on-the-idem-test-federation)
6. [Appendix A: Enable Consent Module: Attribute Release + Terms of Use Consent](#appendix-a-enable-consent-module-attribute-release--terms-of-use-consent)
7. [Appendix B: Import persistent-id from a previous database](#appendix-b-import-persistent-id-from-a-previous-database)
8. [Appendix C: Useful logs to find problems](#appendix-c-useful-logs-to-find-problems)
9. [Appendix D: Connect an SP with the IdP](#appendix-d-connect-an-sp-with-the-idp)
10. [Utilities](#utilities)
11. [Useful Documentation](#useful-documentation)
12. [Authors](#authors)
    * [Original Author](#original-author)

## Requirements

### Hardware

 * CPU: 2 Core (64 bit)
 * RAM: 4 GB
 * HDD: 20 GB
 * OS: Centos 7 (EOL: 30/06/2024)
 
### Other

 * SSL Credentials: HTTPS Certificate & Key
 * Logo:
   * size: 80x60 px (or other that respect the aspect-ratio)
   * format: PNG
 * Favicon: 
   * size: 16x16 px (or other that respect the aspect-ratio)
   * format: PNG

## Software that will be installed

 * ca-certificates
 * chrony
 * vim
 * Amazon Corretto 11 JDK
 * jetty 9.4.x
 * apache2 (>= 2.4)
 * openssl
 * tar
 * wget
 * mariadb-server (if JPAStorageService is used)
 * mysql-connector-java (if JPAStorageService is used)
 * apache-commons-dbcp (if JPAStorageService is used)

## Notes

This HOWTO uses `example.org` to provide this guide with example values.

Please remember to **replace all occurencences** of the `example.org` domain name with the IdP domain name in the configuration files.

## Install Instructions

### Install software requirements

1. Become ROOT:
   * `sudo su -`

2. Update packages:
   * `yum update ; yum upgrade -y`
   
3. Install the packages required:
   * `yum install -y vim wget openssl httpd chrony mod_ssl tar openldap-clients`

4. Install Amazon Corretto JDK:
     * `rpm --import https://yum.corretto.aws/corretto.key`
     * `wget https://yum.corretto.aws/corretto.repo -O /etc/yum.repos.d/corretto.repo`
     * `yum install -y java-11-amazon-corretto-devel`
   
5. Check that Amanzon Corretto JDK is installed and selected:
   * `java -version`
   * `update-alternatives --config java` (press [Enter] to leave settings unchanged)

6. Activate Chrony:
   * `systemctl enable chronyd`
   * `date`

7. Configure the Timezone:
   * `timedatectl list-timezones` - List all possible values to use with `set-timezone`.
   * `timedatectl set-timezone Europe/Rome` - Example for Italy

### Configure the environment

1. Become ROOT:
   * `sudo su -`

2. Be sure that your firewall **is not blocking** the traffic on port **443** and **80**.

3. Set the IdP hostname:
   * `vim /etc/hosts`

     ```bash
     <YOUR SERVER IP ADDRESS> idp.example.org <HOSTNAME>
     ```

   * `hostnamectl set-hostname <HOSTNAME>`
   
     (*Replace `idp.example.org` with your IdP Full Qualified Domain Name and `<HOSTNAME>` with the IdP hostname*)

4. Set the variable `JAVA_HOME` for the entire environment:
   * `echo export JAVA_HOME=/usr/lib/jvm/java > /etc/profile.d/javaenv.sh`
   * `chmod 0755 /etc/profile.d/javaenv.sh`

### Install Shibboleth Identity Provider v4.x

The Identity Provider (IdP) is responsible for user authentication and providing user information to the Service Provider (SP). It is located at the home organization, which is the organization which maintains the user's account.
It is a Java Web Application that can be deployed with its WAR file.

1. Become ROOT:
   * `sudo su -`

2. Download the Shibboleth Identity Provider v4.x.y (replace '4.x.y' with the latest version found [here](https://shibboleth.net/downloads/identity-provider/)):
   * `cd /usr/local/src`
   * `wget http://shibboleth.net/downloads/identity-provider/4.x.y/shibboleth-identity-provider-4.x.y.tar.gz`
   * `tar -xzf shibboleth-identity-provider-4.x.y.tar.gz`

3. Run the installer `install.sh`:
   > According to [NSA and NIST](https://www.keylength.com/en/compare/), RSA with 3072 bit-modulus is the minimum to protect up to TOP SECRET over than 2030.

   * `cd /usr/local/src/shibboleth-identity-provider-4.x.y/bin`
   * `bash install.sh -Didp.host.name=$(hostname -f) -Didp.keysize=3072`

     ```bash
     Buildfile: /usr/local/src/shibboleth-identity-provider-4.x.y/bin/build.xml

     install:
     Source (Distribution) Directory (press <enter> to accept default): [/usr/local/src/shibboleth-identity-provider-4.x.y] ?
     Installation Directory: [/opt/shibboleth-idp] ?
     Backchannel PKCS12 Password: ###PASSWORD-FOR-BACKCHANNEL###
     Re-enter password:           ###PASSWORD-FOR-BACKCHANNEL###
     Cookie Encryption Key Password: ###PASSWORD-FOR-COOKIE-ENCRYPTION###
     Re-enter password:              ###PASSWORD-FOR-COOKIE-ENCRYPTION###
     SAML EntityID: [https://idp.example.org/idp/shibboleth] ?
     Attribute Scope: [example.org] ?
     ```

     By starting from this point, the variable **idp.home** refers to the directory: `/opt/shibboleth-idp`
     
     Backup the `###PASSWORD-FOR-BACKCHANNEL###` value somewhere to be able to find it when you need it.
     
     The `###PASSWORD-FOR-COOKIE-ENCRYPTION###` will be saved into `/opt/shibboleth-idp/credentials/secrets.properties` as `idp.sealer.storePassword` and `idp.sealer.keyPassword` value.

### Install Jetty 9 Web Server

Jetty is a Web server and a Java Servlet container. It will be used to run the IdP application through its WAR file.

1. Become ROOT:
   * `sudo su -`

2. Download and Extract Jetty:
   ```bash
   cd /usr/local/src
   
   wget https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-distribution/9.4.39.v20210325/jetty-distribution-9.4.39.v20210325.tar.gz
   
   tar xzvf jetty-distribution-9.4.39.v20210325.tar.gz
   ```

3. Create the `jetty-src` folder as a symbolic link. It will be useful for future Jetty updates:
   * `ln -nsf jetty-distribution-9.4.39.v20210325 jetty-src`

4. Create the user/group `jetty` that can run the web server:
   * `useradd --system --home-dir /usr/local/src/jetty-src --user-group jetty`

5. Create your custom Jetty configuration that overrides the default one and will survive upgrades:
   * `mkdir /opt/jetty`
   * `wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/jetty/start.ini -O /opt/jetty/start.ini`

6. Create the TMPDIR directory used by Jetty:
   * `mkdir /opt/jetty/tmp ; chown jetty:jetty /opt/jetty/tmp`
   * `chown -R jetty:jetty /opt/jetty/ /usr/local/src/jetty-src/`

7. Create the Jetty Log's folder:
   * `mkdir /var/log/jetty`
   * `mkdir /opt/jetty/logs`
   * `chown jetty:jetty /var/log/jetty/ /opt/jetty/logs/`

8. Configure **/etc/default/jetty**:
   * `vim /etc/default/jetty`

     ```bash
     JETTY_HOME=/usr/local/src/jetty-src
     JETTY_BASE=/opt/jetty
     JETTY_USER=jetty
     JETTY_START_LOG=/var/log/jetty/start.log
     TMPDIR=/opt/jetty/tmp
     ```

9. Create the service loadable from command line:
   * `cd /etc/init.d`
   * `ln -s /usr/local/src/jetty-src/bin/jetty.sh jetty`
   * `chkconfig --add jetty`
   * `systemctl enable jetty`

10. Check if all settings are OK:
    * `systemctl check jetty` (inactive)
    * `systemctl start jetty`
    * `systemctl check jetty` (active)

    If you receive an error likes "*Job for jetty.service failed because the control process exited with error code. See "systemctl status jetty.service" and "journalctl -xe" for details.*", try this:
      * `rm /var/run/jetty/jetty.pid`
      * `systemctl start jetty.service`

## Configuration Instructions

### Configure Jetty

1. Become ROOT:
   * `sudo su -`

2. Configure the IdP Context Descriptor:
   * `mkdir /opt/jetty/webapps`
   * `vim /opt/jetty/webapps/idp.xml`

     ```xml
     <Configure class="org.eclipse.jetty.webapp.WebAppContext">
       <Set name="war"><SystemProperty name="idp.home"/>/war/idp.war</Set>
       <Set name="contextPath">/idp</Set>
       <Set name="extractWAR">false</Set>
       <Set name="copyWebDir">false</Set>
       <Set name="copyWebInf">true</Set>
       <Set name="persistTempDirectory">false</Set>
     </Configure>
     ```

3. Make the **jetty** user owner of IdP main directories:
   * `cd /opt/shibboleth-idp`
   * `chown -R jetty logs/ metadata/ credentials/ conf/ war/`

4. Restart Jetty:
   * `systemctl restart jetty.service`

### Configure SSL on Apache2 (front-end of Jetty)

The Apache HTTP Server will be configured as a reverse proxy and it will be used for SSL offloading.

1. Become ROOT:
   * `sudo su -`

2. Create the DocumentRoot:
   * `mkdir /var/www/html/$(hostname -f)`
   * `sudo chown -R apache: /var/www/html/$(hostname -f)`
   * `echo '<h1>It Works!</h1>' > /var/www/html/$(hostname -f)/index.html`

3. Create the Virtualhost file (**please pay attention: you need to edit this file and customize it, check the initial comment inside of it**):
   * ```bash
     wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/apache2/idp.example.org.conf -O /etc/httpd/conf.d/000-$(hostname -f).conf
     ```

4. Deactivate the `welcome` site:
   * `mv /etc/httpd/conf.d/welcome.conf /etc/httpd/conf.d/welcome.conf.deactivated`
   
5. Put SSL credentials in the right place:
   * HTTPS Server Certificate (Public Key) inside `/etc/pki/tls/certs`
   * HTTPS Server Key (Private Key) inside `/etc/pki/tls/private`
   * Add CA Cert into `/etc/pki/tls/certs`
     * If you use GARR TCS (Sectigo CA):
       ```bash
       wget -O /etc/pki/tls/certs/GEANT_OV_RSA_CA_4.pem https://crt.sh/?d=2475254782
       
       wget -O /etc/pki/tls/certs/SectigoRSAOrganizationValidationSecureServerCA.crt https://crt.sh/?d=924467857
       
       cat /etc/pki/tls/certs/SectigoRSAOrganizationValidationSecureServerCA.crt >> /etc/pki/tls/certs/GEANT_OV_RSA_CA_4.pem
       
       rm /etc/pki/tls/certs/SectigoRSAOrganizationValidationSecureServerCA.crt
       ```

     * If you use ACME (Let's Encrypt):
       * `ln -s /etc/letsencrypt/live/<SERVER_FQDN>/chain.pem /etc/pki/tls/certs/ACME-CA.pem`

6. Configure the right privileges for the SSL Certificate and Key used by HTTPS:
   * `chmod 400 /etc/pki/tls/private/$(hostname -f).key`
   * `chmod 644 /etc/pki/tls/certs/$(hostname -f).crt`
   
     (*`$(hostname -f)` will provide your IdP Full Qualified Domain Name*)

7. Configure SELinux to allow `mod_proxy` to initiate outbound connections:
   * `sestatus`

   If SELinux is enabled:
   * `/usr/sbin/setsebool -P httpd_can_network_connect 1`

8. Restart Apache: 
   * `systemctl restart httpd.service`

9. Check that IdP metadata is available on:
   * ht<span>tps://</span>idp.example.org/idp/shibboleth

10. Verify the strength of your IdP's machine on:
    * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)
   
### Configure Shibboleth Identity Provider Storage

> Shibboleth Documentation reference: https://wiki.shibboleth.net/confluence/display/IDP4/StorageConfiguration
>
> The IdP provides a number of general-purpose storage facilities that can be used by core subsystems like session management and consent. 

#### Strategy A - Default (HTML Local Storage, Encryption GCM, No Database) - Recommended

> The HTML Local Storage requires JavaScript be enabled because reading and writing to the client requires an explicit page be rendered.
> Note that this feature is safe to enable globally. The implementation is written to check for this capability in each client, and to back off to cookies.
> The default configuration generates encrypted assertions that a large percentage of non-Shibboleth SPs are going to be unable to decrypt, resulting a wide variety of failures and error messages. Some old Shibboleth SPs or software running on old Operating Systems will also fail to work.

:warning: **IMPORTANT TO DO**

> The IDEM Federation Operators collect a list of Service Providers that don't support the new default encryption algorithm and provide a solution [**here**](https://wiki.idem.garr.it/wiki/Idp4noGCMsps) (Italian only).

If you don't change anything, the IdP stores data in a browser session cookie or HTML local storage and encrypt his assertions with AES-GCM encryption algorithm.

The IDEM Federation Operators collect a list of Service Providers that don't support the new default encryption algorithm and provide a solution [**here**](https://wiki.idem.garr.it/wiki/Idp4noGCMsps) (Italian only). 

See the configuration files and the Shibboleth documentation for details.

Check IdP Status:
   * `bash /opt/shibboleth-idp/bin/status.sh`

#### Strategy B - JPA Storage Service - using a database

This Storage service will memorize User Consent data on persistent database SQL.

1. Become ROOT: 
   * `sudo su -`

2. Install required packages:
   * `yum install mariadb-server mysql-connector-java apache-commons-dbcp`

3. Activate MariaDB database service:
   * `systemctl start mariadb.service`

4. Address several security concerns in a default MariaDB installation (if it is not already done):
   * `mysql_secure_installation`
 
5. (OPTIONAL) MySQL DB Access without password:
   * `vim /root/.my.cnf`

     ```cnf
     [client]
     user=root
     password=##ROOT-DB-PASSWORD-CHANGEME##
     ```

6. Create `StorageRecords` table on `storageservice` database:
   * `wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/db/shib-ss-db.sql -O /root/shib-ss-db.sql`
   * fill missing data on `shib-ss-db.sql` before import
   * `mysql -u root < /root/shib-ss-db.sql`
   * `systemctl restart mariadb.service`

7. Rebuild IdP with the needed libraries:
   * `cd /opt/shibboleth-idp`
   * `ln -s /usr/share/java/mysql-connector-java.jar edit-webapp/WEB-INF/lib`
   * `ln -s /usr/share/java/commons-dbcp.jar edit-webapp/WEB-INF/lib`
   * `ln -s /usr/share/java/commons-pool.jar edit-webapp/WEB-INF/lib`
   * `bin/build.sh`

8. Enable JPA Storage Service:
   * `vim /opt/shibboleth-idp/conf/global.xml` 
     
     and add the following directives to the tail, just before the last **`</beans>`** tag:

     ```xml
     <!-- DB-independent Configuration -->

     <bean id="storageservice.JPAStorageService" 
           class="org.opensaml.storage.impl.JPAStorageService"
           p:cleanupInterval="%{idp.storage.cleanupInterval:PT10M}"
           c:factory-ref="storageservice.JPAStorageService.EntityManagerFactory"/>

     <bean id="storageservice.JPAStorageService.EntityManagerFactory"
           class="org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean">
           <property name="packagesToScan" value="org.opensaml.storage.impl"/>
           <property name="dataSource" ref="storageservice.JPAStorageService.DataSource"/>
           <property name="jpaVendorAdapter" ref="storageservice.JPAStorageService.JPAVendorAdapter"/>
           <property name="jpaDialect">
              <bean class="org.springframework.orm.jpa.vendor.HibernateJpaDialect" />
           </property>
     </bean>

     <!-- DB-dependent Configuration -->

     <bean id="storageservice.JPAStorageService.JPAVendorAdapter" 
           class="org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter">
           <property name="database" value="MYSQL" />
     </bean>

     <!-- Bean to store IdP data unrelated with persistent identifiers on 'storageservice' database -->

     <bean id="storageservice.JPAStorageService.DataSource"
           class="org.apache.commons.dbcp.BasicDataSource" destroy-method="close" lazy-init="true"
           p:driverClassName="com.mysql.jdbc.Driver"
           p:url="jdbc:mysql://localhost:3306/storageservice?autoReconnect=true"
           p:username="###_SS-USERNAME-CHANGEME_###"
           p:password="###_SS-DB-USER-PASSWORD-CHANGEME_###"
           p:maxActive="10"
           p:maxIdle="5"
           p:maxWait="15000"
           p:testOnBorrow="true"
           p:validationQuery="select 1"
           p:validationQueryTimeout="5" />
     ```

     :warning: **IMPORTANT**:
     
     remember to change "**`###_SS-USERNAME-CHANGEME_###`**" and "**`###_SS-DB-USER-PASSWORD-CHANGEME_###`**" with your DB user and password data

9. Set the consent storage service to the JPA storage service:
   * `vim /opt/shibboleth-idp/conf/idp.properties`

     ```properties
     idp.consent.StorageService = storageservice.JPAStorageService
     ```
	 
10. Restart Jetty to apply the changes:
    * `systemctl restart jetty.service`

11. Check IdP Status:
    * `bash /opt/shibboleth-idp/bin/status.sh`

### Configure the Directory (openLDAP or AD) Connection

1. Check that you can reach the Directory from your IDP server:
   * For Active Directory:
     ```bash
     ldapsearch -x -h <AD-SERVER-FQDN-OR-IP> -D 'CN=idpuser,CN=Users,DC=ad,DC=example,DC=org' -w '<IDPUSER-PASSWORD>' -b 'CN=Users,DC=ad,DC=example,DC=org' '(sAMAccountName=<USERNAME-USED-IN-THE-LOGIN-FORM>)'
     ```

     * the baseDN (`-b` parameter) ==> `CN=Users,DC=ad,DC=example,DC=org` (branch containing the registered users)
     * the bindDN (`-D` parameter) ==> `CN=idpuser,CN=Users,DC=ad,DC=example,DC=org` (distinguished name for the user that can made queries on the LDAP, read only is sufficient)
     * the searchFilter `(sAMAccountName=<USERNAME-USED-IN-THE-LOGIN-FORM>)` corresponds to the `(sAMAccountName=$resolutionContext.principal)` searchFilter configured into `conf/ldap.properties`

   * For OpenLDAP:
     ```bash
     ldapsearch -x -h <LDAP-SERVER-FQDN-OR-IP> -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<IDPUSER-PASSWORD>' -b 'ou=people,dc=example,dc=org' '(uid=<USERNAME-USED-IN-THE-LOGIN-FORM>)'
     ```
     
     * the baseDN (`-b` parameter) ==> `ou=people,dc=example,dc=org` (branch containing the registered users)
     * the bindDN (`-D` parameter) ==> `cn=idpuser,ou=system,dc=example,dc=org` (distinguished name for the user that can made queries on the LDAP, read only is sufficient)
     * the searchFilter `(uid=<USERNAME-USED-IN-THE-LOGIN-FORM>)` corresponds to the `(uid=$resolutionContext.principal)` searchFilter configured into `conf/ldap.properties`

2. Connect the openLDAP to the IdP to allow the authentication of the users:
   
   (for **TLS** solutions put the LDAP certificate into `/opt/shibboleth-idp/credentials/ldap-server.crt`)

   * For OpenLDAP:
     * Solution 1: LDAP + STARTTLS:
       * `vim /opt/shibboleth-idp/credentials/secrets.properties`
         
         ```properties
         # Default access to LDAP authn and attribute stores. 
         idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
         idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
         ```
         
       * `vim /opt/shibboleth-idp/conf/ldap.properties`

          The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP. 
          The list MUST contain the attribute chosen for the persistent-id generation (*idp.persistentId.sourceAttribute*).

          ```properties
          idp.authn.LDAP.authenticator = bindSearchAuthenticator
          idp.authn.LDAP.ldapURL = ldap://ldap.example.org
          idp.authn.LDAP.useStartTLS = true
          idp.authn.LDAP.sslConfig = certificateTrust
          idp.authn.LDAP.trustCertificates = %{idp.home}/credentials/ldap-server.crt
          # List of attributes to request during authentication
          idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemaining
          idp.authn.LDAP.baseDN = ou=people,dc=example,dc=org
          idp.authn.LDAP.subtreeSearch = false
          idp.authn.LDAP.bindDN = cn=idpuser,ou=system,dc=example,dc=org
          # The userFilter is used to locate a directory entry to bind against for LDAP authentication.
          idp.authn.LDAP.userFilter = (uid={user})

          # LDAP attribute configuration, see attribute-resolver.xml
          # Note, this likely won't apply to the use of legacy V2 resolver configurations
          idp.attribute.resolver.LDAP.ldapURL             = %{idp.authn.LDAP.ldapURL}
          idp.attribute.resolver.LDAP.connectTimeout      = %{idp.authn.LDAP.connectTimeout:PT3S}
          idp.attribute.resolver.LDAP.responseTimeout     = %{idp.authn.LDAP.responseTimeout:PT3S}
          idp.attribute.resolver.LDAP.baseDN              = %{idp.authn.LDAP.baseDN:undefined}
          idp.attribute.resolver.LDAP.bindDN              = %{idp.authn.LDAP.bindDN:undefined}
          idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
          idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
          # The searchFilter is is used to find user attributes from an LDAP source
          idp.attribute.resolver.LDAP.searchFilter        = (uid=$resolutionContext.principal)
          # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
          idp.attribute.resolver.LDAP.exportAttributes    = ### List space-separated of attributes to retrieve directly from the directory ###
          ```

     * Solution 2: LDAP + TLS:
       * `vim /opt/shibboleth-idp/credentials/secrets.properties`
         
         ```properties
         # Default access to LDAP authn and attribute stores. 
         idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
         idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
         ```
         
       * `vim /opt/shibboleth-idp/conf/ldap.properties`

          The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP. 
          The list MUST contain the attribute chosen for the persistent-id generation (*idp.persistentId.sourceAttribute*).

          ```properties
          idp.authn.LDAP.authenticator = bindSearchAuthenticator
          idp.authn.LDAP.ldapURL = ldaps://ldap.example.org
          idp.authn.LDAP.useStartTLS = false
          idp.authn.LDAP.sslConfig = certificateTrust
          idp.authn.LDAP.trustCertificates = %{idp.home}/credentials/ldap-server.crt
          # List of attributes to request during authentication
          idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemaining
          idp.authn.LDAP.baseDN = ou=people,dc=example,dc=org
          idp.authn.LDAP.subtreeSearch = false
          idp.authn.LDAP.bindDN = cn=idpuser,ou=system,dc=example,dc=org
          # The userFilter is used to locate a directory entry to bind against for LDAP authentication.
          idp.authn.LDAP.userFilter = (uid={user})

          # LDAP attribute configuration, see attribute-resolver.xml
          # Note, this likely won't apply to the use of legacy V2 resolver configurations
          idp.attribute.resolver.LDAP.ldapURL             = %{idp.authn.LDAP.ldapURL}
          idp.attribute.resolver.LDAP.connectTimeout      = %{idp.authn.LDAP.connectTimeout:PT3S}
          idp.attribute.resolver.LDAP.responseTimeout     = %{idp.authn.LDAP.responseTimeout:PT3S}
          idp.attribute.resolver.LDAP.baseDN              = %{idp.authn.LDAP.baseDN:undefined}
          idp.attribute.resolver.LDAP.bindDN              = %{idp.authn.LDAP.bindDN:undefined}
          idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
          idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
          # The searchFilter is used to find user attributes from an LDAP source
          idp.attribute.resolver.LDAP.searchFilter        = (uid=$resolutionContext.principal)
          # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
          idp.attribute.resolver.LDAP.exportAttributes    = ### List space-separated of attributes to retrieve directly from the directory ###
          ```

     * Solution 3: plain LDAP
       * `vim /opt/shibboleth-idp/credentials/secrets.properties`
         
         ```properties
         # Default access to LDAP authn and attribute stores. 
         idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
         idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
         ```
         
       * `vim /opt/shibboleth-idp/conf/ldap.properties`

          The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP. 
          The list MUST contain the attribute chosen for the persistent-id generation (*idp.persistentId.sourceAttribute*).

          ```properties
          idp.authn.LDAP.authenticator = bindSearchAuthenticator
          idp.authn.LDAP.ldapURL = ldap://ldap.example.org
          idp.authn.LDAP.useStartTLS = false
          # List of attributes to request during authentication
          idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemaining
          idp.authn.LDAP.baseDN = ou=people,dc=example,dc=org
          idp.authn.LDAP.subtreeSearch = false
          idp.authn.LDAP.bindDN = cn=idpuser,ou=system,dc=example,dc=org
          # The userFilter is used to locate a directory entry to bind against for LDAP authentication.
          idp.authn.LDAP.userFilter = (uid={user})

          # LDAP attribute configuration, see attribute-resolver.xml
          # Note, this likely won't apply to the use of legacy V2 resolver configurations
          idp.attribute.resolver.LDAP.ldapURL             = %{idp.authn.LDAP.ldapURL}
          idp.attribute.resolver.LDAP.connectTimeout      = %{idp.authn.LDAP.connectTimeout:PT3S}
          idp.attribute.resolver.LDAP.responseTimeout     = %{idp.authn.LDAP.responseTimeout:PT3S}
          idp.attribute.resolver.LDAP.baseDN              = %{idp.authn.LDAP.baseDN:undefined}
          idp.attribute.resolver.LDAP.bindDN              = %{idp.authn.LDAP.bindDN:undefined}
          idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
          idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
          # The searchFilter is is used to find user attributes from an LDAP source
          idp.attribute.resolver.LDAP.searchFilter        = (uid=$resolutionContext.principal)
          # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
          idp.attribute.resolver.LDAP.exportAttributes    = ### List space-separated of attributes to retrieve directly from the directory ###
          ```

   * For Active Directory:
     * Solution 1: AD + STARTTLS:
       * `vim /opt/shibboleth-idp/credentials/secrets.properties`
        
         ```properties
         # Default access to LDAP authn and attribute stores. 
         idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
         idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
         ```
         
       * `vim /opt/shibboleth-idp/conf/ldap.properties`

          The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP. 
          The list MUST contain the attribute chosen for the persistent-id generation (*idp.persistentId.sourceAttribute*).

          ```properties
          idp.authn.LDAP.authenticator = bindSearchAuthenticator
          idp.authn.LDAP.ldapURL = ldap://ldap.example.org
          idp.authn.LDAP.useStartTLS = true
          idp.authn.LDAP.sslConfig = certificateTrust
          idp.authn.LDAP.trustCertificates = %{idp.home}/credentials/ldap-server.crt
          # List of attributes to request during authentication
          idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemaining
          idp.authn.LDAP.baseDN = CN=Users,DC=ad,DC=example,DC=org
          idp.authn.LDAP.subtreeSearch = false
          idp.authn.LDAP.bindDN = CN=idpuser,CN=Users,DC=ad,DC=example,DC=org
          # The userFilter is used to locate a directory entry to bind against for LDAP authentication.
          idp.authn.LDAP.userFilter = (sAMAccountName={user})

          # LDAP attribute configuration, see attribute-resolver.xml
          # Note, this likely won't apply to the use of legacy V2 resolver configurations
          idp.attribute.resolver.LDAP.ldapURL             = %{idp.authn.LDAP.ldapURL}
          idp.attribute.resolver.LDAP.connectTimeout      = %{idp.authn.LDAP.connectTimeout:PT3S}
          idp.attribute.resolver.LDAP.responseTimeout     = %{idp.authn.LDAP.responseTimeout:PT3S}
          idp.attribute.resolver.LDAP.baseDN              = %{idp.authn.LDAP.baseDN:undefined}
          idp.attribute.resolver.LDAP.bindDN              = %{idp.authn.LDAP.bindDN:undefined}
          idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
          idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
          # The searchFilter is is used to find user attributes from an LDAP source
          idp.attribute.resolver.LDAP.searchFilter        = (sAMAccountName=$resolutionContext.principal)
          # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
          idp.attribute.resolver.LDAP.exportAttributes    = ### List space-separated of attributes to retrieve directly from the directory ###
          ```

     * Solution 2: AD + TLS:
       * `vim /opt/shibboleth-idp/credentials/secrets.properties`
         
         ```properties
         # Default access to LDAP authn and attribute stores. 
         idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
         idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
         ```
         
       * `vim /opt/shibboleth-idp/conf/ldap.properties`

          The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP. 
          The list MUST contain the attribute chosen for the persistent-id generation (*idp.persistentId.sourceAttribute*).

          ```properties
          idp.authn.LDAP.authenticator = bindSearchAuthenticator
          idp.authn.LDAP.ldapURL = ldaps://ldap.example.org
          idp.authn.LDAP.useStartTLS = false
          idp.authn.LDAP.sslConfig = certificateTrust
          idp.authn.LDAP.trustCertificates = %{idp.home}/credentials/ldap-server.crt
          # List of attributes to request during authentication
          idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemaining
          idp.authn.LDAP.baseDN = CN=Users,DC=ad,DC=example,DC=org
          idp.authn.LDAP.subtreeSearch = false         
          idp.authn.LDAP.bindDN = CN=idpuser,CN=Users,DC=ad,DC=example,DC=org
          # The userFilter is used to locate a directory entry to bind against for LDAP authentication.
          idp.authn.LDAP.userFilter = (sAMAccountName={user})

          # LDAP attribute configuration, see attribute-resolver.xml
          # Note, this likely won't apply to the use of legacy V2 resolver configurations
          idp.attribute.resolver.LDAP.ldapURL             = %{idp.authn.LDAP.ldapURL}
          idp.attribute.resolver.LDAP.connectTimeout      = %{idp.authn.LDAP.connectTimeout:PT3S}
          idp.attribute.resolver.LDAP.responseTimeout     = %{idp.authn.LDAP.responseTimeout:PT3S}
          idp.attribute.resolver.LDAP.baseDN              = %{idp.authn.LDAP.baseDN:undefined}
          idp.attribute.resolver.LDAP.bindDN              = %{idp.authn.LDAP.bindDN:undefined}
          idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
          idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
          # The searchFilter is is used to find user attributes from an LDAP source
          idp.attribute.resolver.LDAP.searchFilter        = (sAMAccountName=$resolutionContext.principal)
          # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
          idp.attribute.resolver.LDAP.exportAttributes    = ### List space-separated of attributes to retrieve directly from the directory ###
          ```

     * Solution 3: plain AD
       * `vim /opt/shibboleth-idp/credentials/secrets.properties`
        
         ```properties
         # Default access to LDAP authn and attribute stores. 
         idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
         idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
         ```
         
       * `vim /opt/shibboleth-idp/conf/ldap.properties`

          The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP. 
          The list MUST contain the attribute chosen for the persistent-id generation (*idp.persistentId.sourceAttribute*).

          ```properties
          idp.authn.LDAP.authenticator = bindSearchAuthenticator
          idp.authn.LDAP.ldapURL = ldap://ldap.example.org
          idp.authn.LDAP.useStartTLS = false
          # List of attributes to request during authentication
          idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemaining
          idp.authn.LDAP.baseDN = CN=Users,DC=ad,DC=example,DC=org
          idp.authn.LDAP.subtreeSearch = false
          idp.authn.LDAP.bindDN = CN=idpuser,CN=Users,DC=ad,DC=example,DC=org
          # The userFilter is used to locate a directory entry to bind against for LDAP authentication.
          idp.authn.LDAP.userFilter = (sAMAccountName={user})

          # LDAP attribute configuration, see attribute-resolver.xml
          # Note, this likely won't apply to the use of legacy V2 resolver configurations
          idp.attribute.resolver.LDAP.ldapURL             = %{idp.authn.LDAP.ldapURL}
          idp.attribute.resolver.LDAP.connectTimeout      = %{idp.authn.LDAP.connectTimeout:PT3S}
          idp.attribute.resolver.LDAP.responseTimeout     = %{idp.authn.LDAP.responseTimeout:PT3S}
          idp.attribute.resolver.LDAP.baseDN              = %{idp.authn.LDAP.baseDN:undefined}
          idp.attribute.resolver.LDAP.bindDN              = %{idp.authn.LDAP.bindDN:undefined}
          idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
          idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
          # The searchFilter is is used to find user attributes from an LDAP source
          idp.attribute.resolver.LDAP.searchFilter        = (sAMAccountName=$resolutionContext.principal)
          # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
          idp.attribute.resolver.LDAP.exportAttributes    = ### List space-separated of attributes to retrieve directly from the directory ###
          ```

     **UTILITY FOR OPENLDAP ADMINISTRATOR:**
       * `slapcat | grep dn`
         * the baseDN ==> `ou=people,dc=example,dc=org` (branch containing the registered users)
         * the bindDN ==> `cn=idpuser,ou=system,dc=example,dc=org` (distinguished name for the user that can made queries on the LDAP)

3. Restart Jetty to apply the changes:
   * `systemctl restart jetty.service`

4. Check IdP Status:
   * `bash /opt/shibboleth-idp/bin/status.sh`

### Configure Shibboleth Identity Provider to release the persistent NameID

> Shibboleth Documentation reference: https://wiki.shibboleth.net/confluence/display/IDP4/PersistentNameIDGenerationConfiguration

SAML 2.0 (but not SAML 1.x) defines a kind of NameID called a "persistent" identifier that every SP receives for the IdP users.
This part will teach you how to release the "persistent" identifiers with a database (Stored Mode) or without it (Computed Mode).

By default, a transient NameID will always be released to the Service Provider if the persistent one is not requested.

#### Strategy A - Computed mode - Default & Recommended

1. Become ROOT: 
   * `sudo su -`

2. Enable the generation of the computed `persistent-id` with:
   * `vim /opt/shibboleth-idp/conf/saml-nameid.properties`
     
     The *sourceAttribute* MUST be an attribute, or a list of comma-separated attributes, that uniquely identify the subject of the generated `persistent-id`.
      
     The *sourceAttribute* MUST be **Stable**, **Permanent** and **Not-reassignable** attribute.

     ```properties
     # ... other things ...#
     # OpenLDAP has the UserID into "uid" attribute
     idp.persistentId.sourceAttribute = uid
     
     # Active Directory has the UserID into "sAMAccountName"
     #idp.persistentId.sourceAttribute = sAMAccountName
     # ... other things ...#
     
     # BASE64 will match Shibboleth V2 values, we recommend BASE32 encoding for new installs.
     idp.persistentId.encoding = BASE32
     idp.persistentId.generator = shibboleth.ComputedPersistentIdGenerator
     ```

   * `vim /opt/shibboleth-idp/conf/saml-nameid.xml`
     * Uncomment the line:

       ```xml
       <ref bean="shibboleth.SAML2PersistentGenerator" />
       ```

   * `vim /opt/shibboleth-idp/credentials/secrets.properties`

     ```properties
     idp.persistentId.salt = ### result of 'openssl rand -base64 36' ###
     ```

3. Restart Jetty to apply the changes:
   * `systemctl restart jetty.service`

4. Check IdP Status:
   * `bash /opt/shibboleth-idp/bin/status.sh`

#### Strategy B - Stored mode - using a database

1. Become ROOT:
   * `sudo su -`

2. Install required packages:
   * `yum install mariadb-server mysql-connector-java apache-commons-dbcp`

3. Activate MariaDB database service:
   * `systemctl start mariadb.service`

4. Address several security concerns in a default MariaDB installation (if it is not already done):
   * `mysql_secure_installation`

5. (OPTIONAL) MySQL DB Access without password:
   * `vim /root/.my.cnf`

     ```cnf
     [client]
     user=root
     password=##ROOT-DB-PASSWORD-CHANGEME##
     ```

6. Create `shibpid` table on `shibboleth` database.
   * `wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/db/shib-pid-db.sql -O /root/shib-pid-db.sql`
   * fill missing data on `shib-pid-db.sql` before import
   * `mysql -u root < shib-pid-db.sql`
   * `systemctl restart mariadb.service`

7. Rebuild IdP with the needed libraries:
   * `cd /opt/shibboleth-idp`
   * `ln -s /usr/share/java/mysql-connector-java.jar edit-webapp/WEB-INF/lib`
   * `ln -s /usr/share/java/commons-dbcp.jar edit-webapp/WEB-INF/lib`
   * `ln -s /usr/share/java/commons-pool.jar edit-webapp/WEB-INF/lib`
   * `bin/build.sh`

8. Enable Persistent Identifier's store:
   * `vim /opt/shibboleth-idp/conf/global.xml` 
     
     and add the following directives to the tail, just before the last **`</beans>`** tag:

     ```xml
     <!-- Bean to store persistent-id on 'shibboleth' database -->

     <bean id="MyDataSource"
           class="org.apache.commons.dbcp.BasicDataSource" destroy-method="close" lazy-init="true"
           p:driverClassName="com.mysql.jdbc.Driver"
           p:url="jdbc:mysql://localhost:3306/shibboleth?autoReconnect=true"
           p:username="###_SHIB-USERNAME-CHANGEME_###"
           p:password="###_SHIB-DB-USER-PASSWORD-CHANGEME_###"
           p:maxActive="10"
           p:maxIdle="5"
           p:maxWait="15000"
           p:testOnBorrow="true"
           p:validationQuery="select 1"
           p:validationQueryTimeout="5" />
     ```

     :warning: **IMPORTANT**:

     remember to change "**`###_SHIB-USERNAME-CHANGEME_###`**" and "**`###_SHIB-DB-USER-PASSWORD-CHANGEME_###`**" with your DB user and password data

9. Enable the generation of the `persistent-id`:
   * `vim /opt/shibboleth-idp/conf/saml-nameid.properties`

      The *sourceAttribute* MUST be an attribute, or a list of comma-separated attributes, that uniquely identify the subject of the generated `persistent-id`.
      
      The *sourceAttribute* MUST be **Stable**, **Permanent** and **Not-reassignable** attribute.
   
     ```properties
     # ... other things ...#
     # OpenLDAP has the UserID into "uid" attribute
     idp.persistentId.sourceAttribute = uid

     # Active Directory has the UserID into "sAMAccountName"
     #idp.persistentId.sourceAttribute = sAMAccountName
     
     # BASE64 will match Shibboleth V2 values, we recommend BASE32 encoding for new installs.
     idp.persistentId.encoding = BASE32
     # ... other things ...#
     idp.persistentId.generator = shibboleth.StoredPersistentIdGenerator
     # ... other things ...#
     idp.persistentId.dataSource = MyDataSource
     # ... other things ...#
     ```
     
   * `vim /opt/shibboleth-idp/credentials/secrets.properties`
     ```properties
     idp.persistentId.salt = ### result of 'openssl rand -base64 36'###
     ```

   * Enable the **SAML2PersistentGenerator**:
     * `vim /opt/shibboleth-idp/conf/saml-nameid.xml`
       * Uncomment the line:

         ```xml
         <ref bean="shibboleth.SAML2PersistentGenerator" />
         ```

     * `vim /opt/shibboleth-idp/conf/c14n/subject-c14n.xml`
       * Uncomment the line:

         ```xml
         <ref bean="c14n/SAML2Persistent" />
         ```
       
     * (OPTIONAL) `vim /opt/shibboleth-idp/conf/c14n/subject-c14n.properties`
       * Transform each letter of username, before storing in into the database, to Lowercase or Uppercase by setting the proper constant:
       
         ```bash
         # Simple username -> principal name c14n
         idp.c14n.simple.lowercase = true
         #idp.c14n.simple.uppercase = false
         idp.c14n.simple.trim = true

10. Restart Jetty to apply the changes:
    * `systemctl restart jetty.service`

11. Check IdP Status:
    * `bash /opt/shibboleth-idp/bin/status.sh`

### Configure the attribute resolver (sample)

1. Define which attributes your IdP can manage into your Attribute Resolver file. Here you can find a sample **attribute-resolver-sample.xml** as example:
    * Download the sample attribute resolver provided by IDEM GARR AAI Federation Operators (OpenLDAP / Active Directory compliant):
      * ```bash
        wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/attribute-resolver-v4-idem-sample.xml -O /opt/shibboleth-idp/conf/attribute-resolver.xml
        ```

        If you decide to use the Solutions plain LDAP/AD, remove or comment the following directives from your Attribute Resolver file:

        ```xml
        Line 1:  useStartTLS="%{idp.attribute.resolver.LDAP.useStartTLS:true}"
        Line 2:  trustFile="%{idp.attribute.resolver.LDAP.trustCertificates}"
        ```
    
    * Configure the right owner:
      * `chown jetty /opt/shibboleth-idp/conf/attribute-resolver.xml`

2. Restart Jetty to apply the changes:
   * `systemctl restart jetty.service`

3. Check IdP Status:
   * `bash /opt/shibboleth-idp/bin/status.sh`

### Configure Shibboleth Identity Provider to release the eduPersonTargetedID

eduPersonTargetedID is an abstracted version of the SAML V2.0 Name Identifier format of "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent".

> To be able to follow these steps, you need to have followed the previous steps on "persistent" NameID generation.

#### Strategy A - Computed mode - using the computed persistent NameID

1. Check to have the `<AttributeDefinition>` and the `<DataConnector>` into the `attribute-resolver.xml`:
   * `vim /opt/shibboleth-idp/conf/attribute-resolver.xml`
      
     ```xml

     <!-- ...other things ... -->

     <!--  AttributeDefinition for eduPersonTargetedID - Computed Mode  -->
 
     <AttributeDefinition xsi:type="SAML2NameID" nameIdFormat="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" id="eduPersonTargetedID">
         <InputDataConnector ref="computed" attributeNames="computedId" />
     </AttributeDefinition>

     <!-- ... other things... -->

     <!--  Data Connector for eduPersonTargetedID - Computed Mode  -->

     <DataConnector id="computed" xsi:type="ComputedId"
         generatedAttributeID="computedId"
         salt="%{idp.persistentId.salt}"
         algorithm="%{idp.persistentId.algorithm:SHA}"
         encoding="%{idp.persistentId.encoding:BASE32}">

         <InputDataConnector ref="myLDAP" attributeNames="%{idp.persistentId.sourceAttribute}" />

     </DataConnector>
     ```

3. Create the custom `eduPersonTargetedID.properties` file:
   * ```bash 
     wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/attributes/custom/eduPersonTargetedID.properties -O /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties
     ```

4. Restart Jetty to apply the changes:
   * `systemctl restart jetty.service`

5. Check IdP Status:
   * `bash /opt/shibboleth-idp/bin/status.sh`

#### Strategy B - Stored mode - using the persistent NameID database

1. Check to have the `<AttributeDefinition>` and the `<DataConnector>` into the `attribute-resolver.xml`:
   * `vim /opt/shibboleth-idp/conf/attribute-resolver.xml`
      
     ```xml

     <!-- ...other things ... -->

     <!--  AttributeDefinition for eduPersonTargetedID - Stored Mode  -->
 
     <AttributeDefinition xsi:type="SAML2NameID" nameIdFormat="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" id="eduPersonTargetedID">
         <InputDataConnector ref="stored" attributeNames="storedId" />
     </AttributeDefinition>

     <!-- ... other things... -->

     <!--  Data Connector for eduPersonTargetedID - Stored Mode  -->

     <DataConnector id="stored" xsi:type="StoredId"
        generatedAttributeID="storedId"
        salt="%{idp.persistentId.salt}"
        queryTimeout="0">

        <InputDataConnector ref="myLDAP" attributeNames="%{idp.persistentId.sourceAttribute}" />

        <BeanManagedConnection>MyDataSource</BeanManagedConnection>
     </DataConnector>
     ```

2. Create the custom `eduPersonTargetedID.properties` file:
   * ```bash 
     wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/attributes/custom/eduPersonTargetedID.properties -O /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties
     ```

3. Restart Jetty to apply the changes:
   * `systemctl restart jetty.service`

4. Check IdP Status:
   * `bash /opt/shibboleth-idp/bin/status.sh`

### Configure the attribute resolution with Attribute Registry

File(s): `conf/attribute-registry.xml`, `conf/attributes/default-rules.xml`, `conf/attribute-resolver.xml`, `conf/attributes/custom/`

1. Download `schac.xml` into the right location:
   * ```bash
     wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/attributes/schac.xml -O /opt/shibboleth-idp/conf/attributes/schac.xml
     ```

2. Change the `default-rules.xml` to include the new `schac.xml` file:
   * `vim /opt/shibboleth-idp/conf/attributes/default-rules.xml`
   
     ```xml
         <!-- ...other things ... -->
     
         <import resource="inetOrgPerson.xml" />
         <import resource="eduPerson.xml" />
         <import resource="eduCourse.xml" />
         <import resource="samlSubject.xml" />
         <import resource="schac.xml" />
     </beans>
     ```

### Configure Shibboleth IdP Logging

Enrich IDP logs with the authentication error occurred on LDAP:
   * ```bash
     sed -i '/^    <logger name="org.ldaptive".*/a \\n    <!-- Logs on LDAP user authentication - ADDED BY IDEM HOWTO -->' /opt/shibboleth-idp/conf/logback.xml
     ```

   * ```bash
     sed -i '/^    <!-- Logs on LDAP user authentication - ADDED BY IDEM HOWTO -->/a \ \ \ \ \<logger name="org.ldaptive.auth.Authenticator" level="INFO" />' /opt/shibboleth-idp/conf/logback.xml
     ```

### Translate IdP messages into preferred language

Translate the IdP messages in your language:
   * Get the files translated in your language from [Shibboleth page](https://wiki.shibboleth.net/confluence/display/IDP4/MessagesTranslation)
   * Put '`messages_XX.properties`' downloaded file into `/opt/shibboleth-idp/messages` directory
   * Restart Jetty to apply the changes with `systemctl restart jetty.service`

### Enrich IdP Login Page with the Institutional Logo

  1. Discover what images are publicly available by opening an URL similar to "https://idp.example.org/idp/images/" from a web browser.
  
  2. Copy the institutional logo into all placeholder found inside the `/opt/shibboleth-idp/edit-webapp/images` directory **without renaming them**.

  3. Rebuild IdP war file:
     * `cd /opt/shibboleth-idp/bin ; ./build.sh`

  4. Restart Jetty:
     * `sudo systemctl restart jetty.service`

### Enrich IdP Login Page with Information and Privacy Policy pages

1. Add the following two lines into `views/login.vm`:
   ```xml
   <li class="list-help-item"><a href="#springMessageText("idp.url.infoPage", '#')"><span class="item-marker">&rsaquo;</span> #springMessageText("idp.login.infoPage", "Information page")</a></li>
   <li class="list-help-item"><a href="#springMessageText("idp.url.privacyPage", '#')"><span class="item-marker">&rsaquo;</span> #springMessageText("idp.login.privacyPage", "Privacy Policy")</a></li>
   ```

   under the line containing the Anchor:

   ```xml
   <a href="#springMessageText("idp.url.helpdesk", '#')">
   ```

2. Add the new variables defined with lines added at point 1 into `messages*.properties` files linked to the view `view/login.vm`:

   * `messages/messages.properties`:

     ```properties
     idp.login.infoPage=Informations
     idp.url.infoPage=https://my.organization.it/english-idp-info-page.html
     idp.login.privacyPage=Privacy Policy
     idp.url.privacyPage=https://my.organization.it/english-idp-privacy-policy.html
     ```

   * `messages/messages_it.properties`:

     ```properties
     idp.login.infoPage=Informazioni
     idp.url.infoPage=https://my.organization.it/italian-idp-info-page.html
     idp.login.privacyPage=Privacy Policy
     idp.url.privacyPage=https://my.organization.it/italian-idp-privacy-policy.html
     ```
        
3. Rebuild IdP WAR file and Restart Jetty to apply changes:
   * `cd /opt/shibboleth-idp/bin ; ./build.sh`
   * `sudo systemctl restart jetty`

### Change default login page footer text

Change the content of `idp.footer` variable into `messages*.properties` files linked to the view `view/login.vm`:

   * `messages/messages.properties`:

     ```properties
     idp.footer=Footer text for english version of IdP login page
     ```

   * `messages/messages_it.properties`:

     ```properties
     idp.footer=Testo del Footer a pie di pagina per la versione italiana della pagina di login dell'IdP
     ```

### Change default "Forgot your password?" and "Need help?" endpoints

Change the content of `idp.url.password.reset` and `idp.url.helpdesk` variables into `messages*.properties` files linked to the view `view/login.vm`:

   * `messages/messages.properties`:

     ```properties
     idp.url.password.reset=CONTENT-FOR-FORGOT-YOUR-PASSWORD-LINK
     idp.url.helpdesk=CONTENT-FOR-NEED-HELP-LINK
     ```

   * `messages/messages_it.properties`:

     ```properties
     idp.url.password.reset=CONTENUTO-PER-LINK-PASSWORD-DIMENTICATA
     idp.url.helpdesk=CONTENUTO-PER-SERVE-AIUTO-LINK
     ```


### Disable SAML1 Deprecated Protocol

1. Modify the IdP metadata to enable only the SAML2 protocol:
   > The `<AttributeAuthorityDescriptor>` role is needed **ONLY IF** you have SPs that use AttributeQuery to request attributes to your IdP.
   > 
   > Shibboleth documentation reference: https://wiki.shibboleth.net/confluence/display/IDP4/SecurityAndNetworking#SecurityAndNetworking-AttributeQuery

   * `vim /opt/shibboleth-idp/metadata/idp-metadata.xml`

      ```xml
      - Remove completely the initial default comment
      
      <EntityDescriptor> Section:
        - Remove `validUntil` XML attribute.
	
      <IDPSSODescriptor> Section:
        - Remove completely the comment on <mdui:UIInfo>. 
          You will add it on the "IDEM Entity Registry", the web application provided by the IDEM GARR AAI to manage metadata.

        - Remove the endpoint:
          <ArtifactResolutionService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/ArtifactResolution" index="1"/>
          (and modify the index value of the next one to “1”)

        - Remove comment from SingleLogoutService endpoints

        - Between the last <SingleLogoutService> and the first <SingleSignOnService> endpoints add these 2 lines:
          <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</NameIDFormat>
          <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</NameIDFormat>

          (because the IdP installed with this guide will release transient NameID, by default, and persistent NameID if requested.)

        - Remove the endpoint: 
          <SingleSignOnService Binding="urn:mace:shibboleth:1.0:profiles:AuthnRequest" Location="https://idp.example.org/idp/profile/Shibboleth/SSO"/>

        - Remove all ":8443" from the existing URL (such port is not used anymore)

      <AttributeAuthorityDescriptor> Section (Remember what was said at the beginning of this step):
        - From the list "protocolSupportEnumeration" replace the value:
          - urn:oasis:names:tc:SAML:1.1:protocol
          with:
          - urn:oasis:names:tc:SAML:2.0:protocol

        - Uncomment:
          <AttributeService Binding="urn:oasis:names:tc:SAML:2.0:bindings:SOAP" Location="https://idp.example.org/idp/profile/SAML2/SOAP/AttributeQuery"/>

        - Remove the endpoint: 
          <AttributeService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/AttributeQuery"/>

        - Remove the comment starting with "If you uncomment..."

        - Remove all ":8443" from the existing URL (such port is not used anymore)
      ```
   
2. Check that the metadata is available on:
   * ht<span>tps://</span>idp.example.org/idp/shibboleth

### Secure cookies and other IDP data

> Shibboleth Documentation reference: https://wiki.shibboleth.net/confluence/display/IDP4/SecretKeyManagement

The default configuration of the IdP relies on a component called a "DataSealer" which in turn uses an AES secret key to secure cookies and certain other data for the IdPs own use. This key must never be shared with anybody else, and must be copied to every server node making up a cluster.
The Java "JCEKS" keystore file stores secret keys instead of public/private keys and certificates and a parallel file tracks the key version number.

These instructions will regularly update the secret key (and increase its version) and provide you the capability to push it to cluster nodes and continually maintain the secrecy of the key.

1. Download `updateIDPsecrets.sh` into the right location:
   * ```bash
     wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/updateIDPsecrets.sh -O /opt/shibboleth-idp/bin/updateIDPsecrets.sh
     ```

2. Provide the right privileges to the script:
   * `sudo chmod +x /opt/shibboleth-idp/bin/updateIDPsecrets.sh`

3. Create the CRON script to run it:
   * `sudo vim /etc/cron.daily/updateIDPsecrets`
     
     ```bash
     #!/bin/bash

     /opt/shibboleth-idp/bin/updateIDPsecrets.sh
     ```

4. Provide the right privileges to the script:
   * `sudo chmod +x /etc/cron.daily/updateIDPsecrets`

5. Confirm that the script will be run daily with (you should see your script in the command output):
   * `sudo run-parts --test /etc/cron.daily`
   
6. (OPTIONAL) Add the following properties to `conf/idp.properties` if you need to set different values than defaults:
   * `idp.sealer._count` - Number of earlier keys to keep (default 30)
   * `idp.sealer._sync_hosts` - Space separated list of hosts to scp the sealer files to (default generate locally)

### Configure Attribute Filter Policy to release attributes to Federated Resources

> Follow these steps **ONLY IF** your organization is connected to the [GARR Network](https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites)

1. Become ROOT:
   * `sudo su -`

2. Create the directory "`tmp/httpClientCache`" used by "`shibboleth.FileCachingHttpClient`":
   * `mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown jetty /opt/shibboleth-idp/tmp/httpClientCache`

3. Modify your `services.xml`:
   * `vim /opt/shibboleth-idp/conf/services.xml`

     and add the following two beans on the top of the file, under the first `<beans>` TAG, only one time:

     ```xml
     <bean id="MyHTTPClient" parent="shibboleth.FileCachingHttpClientFactory"
           p:connectionTimeout="PT30S"
           p:connectionRequestTimeout="PT30S"
           p:socketTimeout="PT30S"
           p:cacheDirectory="%{idp.home}/tmp/httpClientCache" />
     
     <bean id="IdemAttributeFilterFull" class="net.shibboleth.ext.spring.resource.FileBackedHTTPResource"
           c:client-ref="MyHTTPClient"
           c:url="https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/idem-attribute-filter-v4-full.xml"
           c:backingFile="%{idp.home}/conf/idem-attribute-filter-v4-full.xml"/>
     ```
     
     and enrich the "`AttributeFilterResources`" list with "`IdemAttributeFilterFull`":
     
     ```xml
     <!-- ...other things... -->

     <util:list id ="shibboleth.AttributeFilterResources">
         <value>%{idp.home}/conf/attribute-filter.xml</value>
         <ref bean="IdemAttributeFilterFull"/>
     </util:list>
     
     <!-- ...other things... -->
     ```

4. Restart Jetty to apply the changes:
   * `systemctl restart jetty.service`
   
5. Check IdP Status:
   * `bash /opt/shibboleth-idp/bin/status.sh`

### Register the IdP on the IDEM Test Federation

Follow these steps **ONLY IF** your organization is connected to the [GARR Network](https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites?key=all)

1. Register you IdP metadata on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
   * `https://registry.idem.garr.it/`

2. Configure the IdP to retrieve the Federation Metadata:

   1. **IDEM MDX (recommended): https://mdx.idem.garr.it/**
   
   2. IDEM MDS (legacy):
      * Retrieve the Federation Certificate used to verify signed metadata:
        *  ```bash
           wget https://md.idem.garr.it/certs/idem-signer-20241118.pem -O /opt/shibboleth-idp/metadata/federation-cert.pem
           ```

      * Check the validity:
        *  `cd /opt/shibboleth-idp/metadata`
        *  `openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout`
       
           (sha1: 0E:21:81:8E:06:02:D1:D9:D1:CF:3D:4C:41:ED:5F:F3:43:70:16:79)
        *  `openssl x509 -in federation-cert.pem -fingerprint -md5 -noout`

           (md5: 73:B7:29:FA:7C:AE:5C:E7:58:1F:10:0B:FC:EE:DA:A9)

      * `vim /opt/shibboleth-idp/conf/metadata-providers.xml`
   
        and add before the last `</MetadataProvider>` this piece of code:

        ```xml
        <!-- IDEM Test Federation -->
        <MetadataProvider
           id="URLMD-IDEM-Federation"
           xsi:type="FileBackedHTTPMetadataProvider"
           backingFile="%{idp.home}/metadata/idem-test-metadata-sha256.xml"
           metadataURL="http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml">

           <!--
               Verify the signature on the root element of the metadata aggregate using a trusted metadata signing certificate.
           -->
           <MetadataFilter xsi:type="SignatureValidation" requireSignedRoot="true" certificateFile="${idp.home}/metadata/federation-cert.pem"/>

           <!--
               Require a validUntil XML attribute on the root element and make sure its value is no more than 10 days into the future.
           -->
           <MetadataFilter xsi:type="RequiredValidUntil" maxValidityInterval="P10D"/>
   
           <!-- 
               Consume only SP in the metadata aggregate for Shibboleth IdP v3.x and 4.0:
           -->
	   <!--
           <MetadataFilter xsi:type="EntityRoleWhiteList">
             <RetainedRole>md:SPSSODescriptor</RetainedRole>
           </MetadataFilter>
           -->
		
           <!-- 
               Consume only SP in the metadata aggregate for Shibboleth IdP v4.1+:
           -->
           <MetadataFilter xsi:type="EntityRole">
             <RetainedRole>md:SPSSODescriptor</RetainedRole>
           </MetadataFilter>
        </MetadataProvider>
        ```

   3. Reload service with id `shibboleth.MetadataResolverService` to retrieve the Federation Metadata:
      *  `bash /opt/shibboleth-idp/bin/reload-service.sh -id shibboleth.MetadataResolverService`
    
3. Check that your IdP release at least eduPersonScopedAffiliation, eduPersonTargetedID and a saml2:NameID transient/persistent to the testing SP provided by IDEM:
   * `bash /opt/shibboleth-idp/bin/aacli.sh -n <USERNAME> -r https://sp.example.org/shibboleth --saml2` 
     
     (the command will have a `transient` NameID into the Subject of the assertion)

   * `bash /opt/shibboleth-idp/bin/aacli.sh -n <USERNAME> -r https://sp.aai-test.garr.it/shibboleth --saml2`

     (the command will have a `persistent` NameID into the Subject of the assertion)

4. Wait that your IdP Metadata is approved by an IDEM Federation Operator into the metadata stream and the next steps provided by the operator itself.

5. Follow the [instructions provided by IDEM](https://wiki.idem.garr.it/wiki/RegistraEntita).

### Appendix A: Enable Consent Module: Attribute Release + Terms of Use Consent

> Shibboleth Documentation reference: https://wiki.shibboleth.net/confluence/display/IDP4/ConsentConfiguration

The IdP includes the ability to require user consent to attribute release, as well as presenting a "terms of use" message prior to completing a login to a service, a simpler "static" form of consent.

1. Load Consent Module:
   * `bin/module.sh -t idp.intercept.Consent || bin/module.sh -e idp.intercept.Consent`

2. Enable Consent Module by editing `conf/relying-party.xml` with the right `postAuthenticationFlows`:
   * `<bean parent="SAML2.SSO" p:postAuthenticationFlows="attribute-release" />` - to enable only Attribute Release Consent
   * `<bean parent="SAML2.SSO" p:postAuthenticationFlows="#{ {'terms-of-use', 'attribute-release'} }" />` - to enable both

### Appendix B: Import persistent-id from a previous database

Follow these steps **ONLY IF** your need to import persistent-id database from another IdP

1. Become ROOT:
   * `sudo su -`

2. Create a DUMP of `shibpid` table from the previous DB `shibboleth` on the OLD IdP:
   * `cd /tmp`
   * ```bash
     mysqldump --complete-insert --no-create-db --no-create-info -u root -p shibboleth shibpid > /tmp/shibboleth_shibpid.sql
     ```

3. Move the `/tmp/shibboleth_shibpid.sql` of old IdP into `/tmp/shibboleth_shibpid.sql` on the new IdP.
 
4. Import the content of `/tmp/shibboleth_shibpid.sql` into database of the new IDP:
   * `cd /tmp ; mysql -u root -p shibboleth < /tmp/shibboleth_shibpid.sql`

5. Delete `/tmp/shibboleth_shibpid.sql`:
   * `rm /tmp/shibboleth_shibpid.sql`
   
### Appendix C: Useful logs to find problems

Follow this if you need to find a problem of your IdP.

1. Jetty Logs:
   * `cd /opt/jetty/logs`
   * `ls -l *.stderrout.log`

2. Shibboleth IdP Logs:
   * `cd /opt/shibboleth-idp/logs`
   * **Audit Log:** `vim idp-audit.log`
   * **Consent Log:** `vim idp-consent-audit.log`
   * **Warn Log:** `vim idp-warn.log`
   * **Process Log:** `vim idp-process.log`

### Appendix D: Connect an SP with the IdP

> Shibboleth Documentation Reference: 
> * https://wiki.shibboleth.net/confluence/display/IDP4/ChainingMetadataProvider
> * https://wiki.shibboleth.net/confluence/display/IDP4/FileBackedHTTPMetadataProvider
> * https://wiki.shibboleth.net/confluence/display/IDP4/AttributeFilterConfiguration
> * https://wiki.shibboleth.net/confluence/display/IDP4/AttributeFilterPolicyConfiguration

Follow these steps **IF** your organization **IS NOT** connected to the [GARR Network](https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites) or **IF** you need to connect directly a Shibboleth Service Provider.

1. Connect the SP to the IdP by adding its metadata on the `metadata-providers.xml` configuration file:

   * `vim /opt/shibboleth-idp/conf/metadata-providers.xml`
  
     ```bash
     <MetadataProvider id="HTTPMetadata"
                       xsi:type="FileBackedHTTPMetadataProvider"
                       backingFile="%{idp.home}/metadata/sp-metadata.xml"
                       metadataURL="https://sp.example.org/Shibboleth.sso/Metadata"
                       failFastInitialization="false"/>
     ```

2. Adding an `AttributeFilterPolicy` on the `conf/attribute-filter.xml` file:
   * ```bash
     wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP4/idem-example-arp.txt -O /opt/shibboleth-idp/conf/example-arp.txt
  
     cat /opt/shibboleth-idp/conf/example-arp.txt
     ```

   * copy and paste the content into `/opt/shibboleth-idp/conf/attribute-filter.xml` before the last element `</AttributeFilterPolicyGroup>`.
   
   * Make sure to change "### SP-ENTITYID ###" of the text pasted with the entityID of the Service Provider to connect with the Identity Provider installed.
  
3. Restart Jetty to apply changes:
   * `systemctl restart jetty.service`

### Utilities

* AACLI: Useful to understand which attributes will be released to the federated resources
  * `export JAVA_HOME=/usr/lib/jvm/java-11-amazon-corretto`
  * `bash /opt/shibboleth-idp/bin/aacli.sh -n <USERNAME> -r <ENTITYID-SP> --saml2`

* [The Mozilla Observatory](https://observatory.mozilla.org/):
  The Mozilla Observatory has helped over 240,000 websites by teaching developers, system administrators, and security professionals how to configure their sites safely and securely.

### Useful Documentation

* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631699/SpringConfiguration
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631633/ConfigurationFileSummary
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631710/LoggingConfiguration
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631711/AuditLoggingConfiguration
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631712/FTICKSLoggingConfiguration
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631635/MetadataConfiguration
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631611/PasswordAuthnConfiguration
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631549/AttributeResolverConfiguration
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631572/LDAPConnector
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1272054306/AttributeRegistryConfiguration
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1272054333/TranscodingRuleConfiguration
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631675/HTTPResource
* https://shibboleth.atlassian.net/wiki/spaces/CONCEPT/pages/948470554/SAMLKeysAndCertificates
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631799/SecretKeyManagement
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631671/NameIDGenerationConfiguration
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1285914730/GCMEncryption
* https://shibboleth.atlassian.net/wiki/spaces/KB/pages/1435927082/Switching+locale+on+the+login+page
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1265631851/WebInterfaces
* https://shibboleth.atlassian.net/wiki/spaces/IDP4/pages/1280180737/Cross-Site+Request+Forgery+CSRF+Protection

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
