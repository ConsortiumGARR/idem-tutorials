# HOWTO Install and Configure a Shibboleth IdP v3.3.2 on Ubuntu Linux LTS 16.04 with Apache2 + Jetty9 

<img width="120px" src="https://wiki.idem.garrservices.it/IDEM_Approved.png" />

## Table of Contents

1. [Requirements Hardware](#requirements-hardware)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Other Requirements](#other-requirements)
4. [Installation Instructions](#installation-instructions)
   1. [Install software requirements](#install-software-requirements)
   2. [Configure the environment](#configure-the-environment)
   3. [Install Jetty 9 Web Server](#install-jetty-9-web-server)
   4. [Install Shibboleth Identity Provider 3.3.2](#install-shibboleth-identity-provider-v321)
5. [Configuration Instructions](#configuration-instructions)
   1. [Configure SSL on Apache2 (Jetty front-end)](#configure-ssl-on-apache2-jetty-front-end)
   2. [Configure Jetty](#configure-jetty)
   3. [Configure Shibboleth Identity Provider v3.3.2 to release the persistent-id (Stored Mode)](#configure-shibboleth-identity-provider-v321-to-release-the-persistent-id-stored-mode)
   4. [Configure Attribute Filters to release the mandatory attributes to the IDEM Default  Resources](#configure-attribute-filters-to-release-the-mandatory-attributes-to-the-idem-default-resources)
   5. [Configure Attribute Filters to release the mandatory attributes to the IDEM Production Resources](#configure-attribute-filters-to-release-the-mandatory-attributes-to-the-idem-production-resources)
   6. [Configure Attribute Filters for Research and Scholarship and Data Protection Code of Conduct Entity Category](#configure-attribute-filters-for-research-and-scholarship-and-data-protection-code-of-conduct-entity-category)
6. [Appendix A: Import metadata from previous IDP v2.x](#appendix-a-import-metadata-from-previous-idp-v2x)
7. [Appendix B: Import persistent-id from a previous database](#appendix-b-import-persistent-id-from-a-previous-database)
8. [Appendix C: Useful logs to find problems](#appendix-c-useful-logs-to-find-problems)
9. [Authors](#authors)


## Requirements Hardware

 * CPU: 2 Core
 * RAM: 4 GB
 * HDD: 20 GB

## Software that will be installed

 * ca-certificates
 * ntp
 * vim
 * default-jdk (openjdk 1.8.0)
 * jetty 9.4.x
 * apache2 (>= 2.4)
 * expat
 * openssl
 * mysql-server
 * libmysql-java
 * libcommons-dbcp-java
 * libcommons-pool-java
 * libjstl1.1-java

## Other Requirements

 * Put HTTPS credentials in the right place:
   * HTTPS Server Certificate (Public Key) inside ```/etc/ssl/certs``` 
   * HTTPS Server Key (Private Key) inside ```/etc/ssl/private```
   * HTTPS Certification Authority Certificate is already provided by Ubuntu packages

## Installation Instructions

### Install software requirements

1. Become ROOT:
   * ```sudo su -```

2. Change the default mirror with the GARR ones:
   * ```nano /etc/apt/sources.list```
   * CTRL+W (search)
   * CTRL+R (replace)
   * Text to search: '```archive.ubuntu.com```'
   * Text to replace: '```mi.mirror.garr.it```'
   * CTRL+X (save and exit)
   * ```apt-get update && apt-get upgrade```
  
3. Install the packages required: 
   * ```apt-get install vim default-jdk ca-certificates openssl apache2 ntp expat --no-install-recommends```

4. Check that Java is working:
   * ```update-alternatives --config java```

### Configure the environment

1. Modify your ```/etc/hosts```:
   * ```vim /etc/hosts```
  
     ```bash
     127.0.1.1 idp.example.org idp
     ```
   (*Replace ```idp.example.org``` with your IdP Full Qualified Domain Name*)

2. Be sure that your firewall **doesn't block** the traffic on port **443** (or you can't access to your IdP)

3. Define the costant ```JAVA_HOME``` and ```IDP_SRC``` inside ```/etc/environment```:
   * ```vim /etc/environment```

     ```bash
     JAVA_HOME=/usr/lib/jvm/default-java/jre
     IDP_SRC=/usr/local/src/shibboleth-identity-provider-3.3.2
     ```
   * ```source /etc/environment```
   * ```export JAVA_HOME=/usr/lib/jvm/default-java/jre```
   * ```export IDP_SRC=/usr/local/src/shibboleth-identity-provider-3.3.2```
  
4. Move the Certificate and the Key file for HTTPS server from ```/tmp/``` to ```/root/certificates```:
   * ```chmod 400 /etc/ssl/private/idp-key-server.key```
   * ```chmod 644 /etc/ssl/certs/idp-cert-server.crt```

   (OPTIONAL) Create a Certificate and a Key self-signed for HTTPS if you don't have the official ones provided by DigiCert:
   * ```openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/idp-key-server.key -out /etc/ssl/certs/idp-cert-server.crt -nodes -days 1095```

5. Configure **/etc/default/jetty**:
   * ```vim /etc/default/jetty```
  
     ```bash
     JETTY_HOME=/usr/local/src/jetty-src
     JETTY_BASE=/opt/jetty
     JETTY_USER=jetty
     JETTY_START_LOG=/var/log/jetty/start.log
     TMPDIR=/opt/jetty/tmp
     JAVA_OPTIONS="-Djava.awt.headless=true -XX:+DisableExplicitGC -XX:+UseParallelOldGC -Xms256m -Xmx2g -Djava.security.egd=file:/dev/./urandom -Didp.home=/opt/shibboleth-idp"
     ```

     (This settings configure the memory of the JVM that will host the IdP Web Application. 
     The Memory value depends on the phisical memory installed on the machine. 
     Set the "**Xmx**" (max heap space available to the JVM) at least to **2GB**)

### Install Jetty 9 Web Server

1. Become ROOT: 
   * ```sudo su -```

2. Download and Extract Jetty:
   * ```cd /usr/local/src```
   * ```wget http://central.maven.org/maven2/org/eclipse/jetty/jetty-distribution/9.4.9.v20180320/jetty-distribution-9.4.9.v20180320.tar.gz```
   * ```tar xzvf jetty-distribution-9.4.9.v20180320.tar.gz```

3. Create an useful-for-updates `jetty-src` folder:
   * ```ln -s jetty-distribution-9.4.9.v20180320 jetty-src```

4. Create the user `jetty` that can run the web server:
   * ```useradd -r -m jetty```

5. Create your custom Jetty configuration that override the default ones:
   * ```mkdir /opt/jetty```
   * ```cd /opt/jetty```
   * ```vim /opt/jetty/start.ini```

     ```bash
     #===========================================================
     # Jetty Startup
     #
     # Starting Jetty from this {jetty.home} is not recommended.
     #
     # A proper {jetty.base} directory should be configured, instead
     # of making changes to this {jetty.home} directory.
     #
     # See documentation about {jetty.base} at
     # http://www.eclipse.org/jetty/documentation/current/startup.html
     #
     # A demo-base directory has been provided as an example of
     # this sort of setup.
     #
     # $ cd demo-base
     # $ java -jar ../start.jar
     #
     #===========================================================

     # To disable the warning message, comment the following line
     --module=home-base-warning

     # ---------------------------------------
     # Module: ext
     --module=ext

     # ---------------------------------------
     # Module: server
     --module=server

     ### ThreadPool configuration
     ## Minimum number of threads
     jetty.threadPool.minThreads=10

     ## Maximum number of threads
     jetty.threadPool.maxThreads=200

     ## Thread idle timeout (in milliseconds)
     jetty.threadPool.idleTimeout=60000

     ## Response content buffer size (in bytes)
     jetty.httpConfig.outputBufferSize=32768

     ## Max request headers size (in bytes)
     jetty.httpConfig.requestHeaderSize=8192

     ## Max response headers size (in bytes)
     jetty.httpConfig.responseHeaderSize=8192

     ## Whether to send the Server: header
     jetty.httpConfig.sendServerVersion=true

     ## Whether to send the Date: header
     jetty.httpConfig.sendDateHeader=false

     ## Dump the state of the Jetty server, components, and webapps after startup
     	jetty.server.dumpAfterStart=false

     ## Dump the state of the Jetty server, components, and webapps before shutdown
     jetty.server.dumpBeforeStop=false

     # ---------------------------------------
     # Module: jsp
     --module=jsp

     # ---------------------------------------
     # Module: resources
     --module=resources

     # ---------------------------------------
     # Module: deploy
     --module=deploy

     # ---------------------------------------
     # Module: jstl
     --module=jstl

     # ---------------------------------------
     # Module: websocket
     --module=websocket

     # ---------------------------------------
     # Module: http
     --module=http

     ### HTTP Connector Configuration

     ## Connector host/address to bind to
     jetty.http.host=localhost

     ## Connector port to listen on
     jetty.http.port=8080

     ## Connector idle timeout in milliseconds
     jetty.http.idleTimeout=30000

     # ---------------------------------------
     # Module: annotations
     --module=annotations

     # Module: console-capture
     --module=console-capture

     jetty.console-capture.dir=/var/log/jetty

     # ---------------------------------------
     # Module: requestlog
     --module=requestlog

     # ---------------------------------------
     # Module: servlets
     --module=servlets

     # ---------------------------------------
     # Module: plus
     --module=plus

     # ---------------------------------------
     # Mwdule: http-forwarded
     --module=http-forwarded
     ```

6. Create the TMPDIR directory used by Jetty:
   * ```mkdir /opt/jetty/tmp ; chown jetty:jetty /opt/jetty/tmp```
   * ```chown -R jetty:jetty /opt/jetty/ /usr/local/src/jetty-src```

7. Create the service loadable from command line:
   * ```cd /etc/init.d```
   * ```ln -s /usr/local/src/jetty-src/bin/jetty.sh jetty```
   * ```update-rc.d jetty defaults```

8. Create the Jetty Log's folder:
   * ```mkdir /var/log/jetty```
   * ```mkdir /opt/jetty/logs```
   * ```chown jetty:jetty /var/log/jetty /opt/jetty/logs```

9. Check if all settings are OK:
   * ```service jetty check```
   * ```service jetty start```
  
   (If you receive an error likes "*Job for jetty.service failed because the control process exited with error code. See "systemctl status jetty.service" and "journalctl -xe" for details.*", try this: 
     * ```rm /var/run/jetty.pid```
     * ```service jetty start```

### Install Shibboleth Identity Provider v3.3.2

1. Become ROOT:
   * ```sudo su -```

2. Install needed libraries for Shibboleth:
   * ```apt-get install libmysql-java libcommons-dbcp-java libcommons-pool-java libjstl1.1-java --no-install-recommends```

3. Download the Shibboleth Identity Provider v3.3.2:
   * ```cd /usr/local/src```
   * ```wget http://shibboleth.net/downloads/identity-provider/3.3.2/shibboleth-identity-provider-3.3.2.tar.gz```
   * ```tar -xzvf shibboleth-identity-provider-3.3.2.tar.gz```
   * ```cd shibboleth-identity-provider-3.3.2```

4. Link the needed libraries:
   * ```cd shibboleth-identity-provider-3.3.2```
   * ```ln -s /usr/share/java/mysql-connector-java.jar webapp/WEB-INF/lib```
   * ```ln -s /usr/share/java/commons-dbcp.jar webapp/WEB-INF/lib```
   * ```ln -s /usr/share/java/commons-pool.jar webapp/WEB-INF/lib```
   * ```ln -s /usr/share/java/jstl1.1.jar webapp/WEB-INF/lib```

5. Run the installer ```install.sh```:
   * ```./bin/install.sh```
  
   ```bash
   root@idp:/usr/local/src/shibboleth-identity-provider-3.3.2# ./bin/install.sh
   Source (Distribution) Directory: [/usr/local/src/shibboleth-identity-provider-3.3.2]
   Installation Directory: [/opt/shibboleth-idp]
   Hostname: [localhost.localdomain]
   idp.example.org
   SAML EntityID: [https://idp.example.org/idp/shibboleth]
   Attribute Scope: [localdomain]
   example.org
   Backchannel PKCS12 Password: ###PASSWORD-FOR-BACKCHANNEL###
   Re-enter password:           ###PASSWORD-FOR-BACKCHANNEL###
   Cookie Encryption Key Password: ###PASSWORD-FOR-COOKIE-ENCRYPTION###
   Re-enter password:              ###PASSWORD-FOR-COOKIE-ENCRYPTION###
   ```
  
   From this point the variable **idp.home** refers to the directory: ```/opt/shibboleth-idp```

6. Change the owner to enable **jetty** user to access on the following directories:
   * ```cd /opt/shibboleth-idp```
   * ```chown -R jetty logs/ metadata/ credentials/ conf/ system/ war/```

## Configuration Instructions

### Configure SSL on Apache2 (Jetty front-end)

1. Modify the file ```/etc/apache2/sites-available/default-ssl.conf``` as follows:

   ```apache
   <IfModule mod_ssl.c>
      SSLStaplingCache        shmcb:/var/run/ocsp(128000)
      <VirtualHost _default_:443>
        ServerName idp.example.org:443
        ServerAdmin admin@example.org
        DocumentRoot /var/www/html
        ...
        SSLEngine On
        
        SSLProtocol All -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
        SSLCipherSuite "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH"

        SSLHonorCipherOrder on

        # Disable SSL Compression
        SSLCompression Off
        
        # OCSP Stapling, only in httpd/apache >= 2.3.3
        SSLUseStapling          on
        SSLStaplingResponderTimeout 5
        SSLStaplingReturnResponderErrors off
        
        # Enable HTTP Strict Transport Security with a 2 year duration
        Header always set Strict-Transport-Security "max-age=63072000;includeSubDomains;preload"
        ...
        SSLCertificateFile /root/certificates/idp-cert-server.crt
        SSLCertificateKeyFile /root/certificates/idp-key-server.key
        ...
      </VirtualHost>
   </IfModule>
   ```

2. Enable **proxy_http**, **SSL** and **headers** Apache2 modules:
   * ```a2enmod proxy_http ssl headers alias include negotiation```
   * ```a2ensite default-ssl.conf```
   * ```service apache2 restart```

3. Configure Apache2 to redirect all on HTTPS:
   * ```vim /etc/apache2/sites-enabled/000-default.conf```
   
   ```apache
   <VirtualHost *:80>
        ServerName "idp.example.org"
        Redirect permanent "/" "https://idp.example.org/"
   </VirtualHost>
   ```
  
4. Verify the strength of your IdP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

### Configure Jetty

1. Become ROOT: 
   * ```sudo su -```

2. Create the Apache2 configuration file for IdP:
   * ```vim /etc/apache2/sites-available/idp.conf```
  
     ```apache
     <IfModule mod_proxy.c>
         ProxyPreserveHost On
         RequestHeader set X-Forwarded-Proto "https"
         ProxyPass /idp http://localhost:8080/idp retry=5
         ProxyPassReverse /idp http://localhost:8080/idp retry=5

         <Location /idp>
            Require all granted
         </Location>
     </IfModule>
     ```

3. Enable the new site:
   * ```cd /etc/apache2/sites-available/ ; a2ensite idp.conf```
   * ```service apache2 reload```

4. Configure IdP Context Descriptor
   * ```mkdir /opt/jetty/webapps```
   * ```vim /opt/jetty/webapps/idp.xml```

     ```bash
     <Configure class="org.eclipse.jetty.webapp.WebAppContext">
       <Set name="war"><SystemProperty name="idp.home"/>/war/idp.war</Set>
       <Set name="contextPath">/idp</Set>
       <Set name="extractWAR">false</Set>
       <Set name="copyWebDir">false</Set>
       <Set name="copyWebInf">true</Set>
     </Configure>
     ```

5. Restart Jetty:
   * ```service jetty restart```

### Configure Shibboleth Identity Provider v3.3.2 to release the persistent-id (Stored mode)

1. Become ROOT of the machine: 
   * ```sudo su -```
  
2. Test IdP by opening a terminal and running these commands:
   * ```cd /opt/shibboleth-idp/bin```
   * ```./status.sh``` (You should see some informations about the IdP installed)

3. Install **MySQL Database Server**:
   * ```apt-get install mysql-server --no-install-recommends```

4. Create and prepare the "**shibboleth**" MySQL DB to host the values of the several **persistent-id** and **StorageRecords** MySQL DB to host other useful information about user consent:
   * Modify the [shibboleth-db.sql](../utils/shibboleth-db.sql) by changing the *username* and *password* of the user that has write access to the "**shibboleth**" DB.

   * Import the SQL modified to your MySQL Server:
    ```mysql -u root -p < shibboleth-db.sql```

   * Restart mysql service:
    ```service mysql restart```

5. Enable the generation of the ```persistent-id``` (this replace the deprecated attribute *eduPersonTargetedID*)
   * ```vim /opt/shibboleth-idp/conf/saml-nameid.properties```
     (the *sourceAttribute* MUST BE an attribute, or a list of comma-separated attributes, that uniquely identify the subject of the generated ```persistent-id```. It MUST BE: **Stable**, **Permanent** and **Not-reassignable**)

     ```xml
     idp.persistentId.sourceAttribute = uid
     ...
     idp.persistentId.salt = ### result of 'openssl rand -base64 36'###
     ...
     idp.persistentId.generator = shibboleth.StoredPersistentIdGenerator
     ...
     idp.persistentId.dataSource = MyDataSource
     ...
     idp.persistentId.computed = shibboleth.ComputedPersistentIdGenerator
     ```

   * Enable the **SAML2PersistentGenerator**:
     * ```vim /opt/shibboleth-idp/conf/saml-nameid.xml```
       * Remove the comment from the line containing:

         ```xml
         <ref bean="shibboleth.SAML2PersistentGenerator" />
         ```

     * ```vim /opt/shibboleth-idp/conf/c14n/subject-c14n.xml```
       * Remove the comment to the bean called "**c14n/SAML2Persistent**".

6. Enable **JPAStorageService** for the **StorageService** of the user consent:
   * ```vim /opt/shibboleth-idp/conf/global.xml``` and add this piece of code to the tail (before **`</beans>`** tag):

     ```xml
     <!-- A DataSource bean suitable for use in the idp.persistentId.dataSource property. -->
     <bean id="MyDataSource" class="org.apache.commons.dbcp.BasicDataSource"
           p:driverClassName="com.mysql.jdbc.Driver"
           p:url="jdbc:mysql://localhost:3306/shibboleth?autoReconnect=true"
           p:username="##USER_DB_NAME##"
           p:password="##PASSWORD##"
           p:maxActive="10"
           p:maxIdle="5"
           p:maxWait="15000"
           p:testOnBorrow="true"
           p:validationQuery="select 1"
           p:validationQueryTimeout="5" />

     <bean id="shibboleth.JPAStorageService" class="org.opensaml.storage.impl.JPAStorageService"
           p:cleanupInterval="%{idp.storage.cleanupInterval:PT10M}"
           c:factory-ref="shibboleth.JPAStorageService.entityManagerFactory"/>

     <bean id="shibboleth.JPAStorageService.entityManagerFactory"
           class="org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean">
           <property name="packagesToScan" value="org.opensaml.storage.impl"/>
           <property name="dataSource" ref="MyDataSource"/>
           <property name="jpaVendorAdapter" ref="shibboleth.JPAStorageService.JPAVendorAdapter"/>
           <property name="jpaDialect">
             <bean class="org.springframework.orm.jpa.vendor.HibernateJpaDialect" />
           </property>
     </bean>

     <bean id="shibboleth.JPAStorageService.JPAVendorAdapter" class="org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter">
           <property name="database" value="MYSQL" />
     </bean>
     ```
     (and modify the "**##USER_DB_NAME##**" and "**##PASSWORD##**" for your "**shibboleth**" DB)

   * Modify the IdP configuration file:
     * ```vim /opt/shibboleth-idp/conf/idp.properties```

       ```xml
       idp.session.StorageService = shibboleth.JPAStorageService
       idp.consent.StorageService = shibboleth.JPAStorageService
       idp.replayCache.StorageService = shibboleth.JPAStorageService
       idp.artifact.StorageService = shibboleth.JPAStorageService
       ```
  
       (This will indicate to IdP to store the data collected by User Consent into the "**StorageRecords**" table)

7. Connect the openLDAP to the IdP to allow the authentication of the users:
   * ```vim /opt/shibboleth-idp/conf/ldap.properties```

     (with **TLS** solutions we consider to have the LDAP certificate into ```/opt/shibboleth-idp/credentials```).

     * Solution 1: LDAP + STARTTLS:

       ```xml
       idp.authn.LDAP.authenticator = bindSearchAuthenticator
       idp.authn.LDAP.ldapURL = ldap://ldap.example.org:389
       idp.authn.LDAP.useStartTLS = true
       idp.authn.LDAP.useSSL = false
       idp.authn.LDAP.sslConfig = certificateTrust
       idp.authn.LDAP.trustCertificates = %{idp.home}/credentials/ldap-server.crt
       idp.authn.LDAP.baseDN = ou=people,dc=example,dc=org
       idp.authn.LDAP.userFilter = (uid={user})
       idp.authn.LDAP.bindDN = cn=admin,dc=example,dc=org
       idp.authn.LDAP.bindDNCredential = ###LDAP_ADMIN_PASSWORD###
       ```

     * Solution 2: LDAP + TLS:

       ```xml
       idp.authn.LDAP.authenticator = bindSearchAuthenticator
       idp.authn.LDAP.ldapURL = ldaps://ldap.example.org:636
       idp.authn.LDAP.useStartTLS = false
       idp.authn.LDAP.useSSL = true
       idp.authn.LDAP.sslConfig = certificateTrust
       idp.authn.LDAP.trustCertificates = %{idp.home}/credentials/ldap-server.crt
       idp.authn.LDAP.baseDN = ou=people,dc=example,dc=org
       idp.authn.LDAP.userFilter = (uid={user})
       idp.authn.LDAP.bindDN = cn=admin,dc=example,dc=org
       idp.authn.LDAP.bindDNCredential = ###LDAP_ADMIN_PASSWORD###
       ```

     * Solution 3: plain LDAP

       ```xml
       idp.authn.LDAP.authenticator = bindSearchAuthenticator
       idp.authn.LDAP.ldapURL = ldap://ldap.example.org:389
       idp.authn.LDAP.useStartTLS = false
       idp.authn.LDAP.useSSL = false
       idp.authn.LDAP.baseDN = ou=people,dc=example,dc=org
       idp.authn.LDAP.userFilter = (uid={user})
       idp.authn.LDAP.bindDN = cn=admin,dc=example,dc=org
       idp.authn.LDAP.bindDNCredential = ###LDAP_ADMIN_PASSWORD###
       ```
       (If you decide to use the Solution 3, you have to remove (or comment out) the following code from your Attribute Resolver file:
      
       ```xml
       </FilterTemplate>
       <!--
       <StartTLSTrustCredential id="LDAPtoIdPCredential" xsi:type="sec:X509ResourceBacked">
         <sec:Certificate>%
           {idp.attribute.resolver.LDAP.trustCertificates}</sec:Certificate>
         </StartTLSTrustCredential>
       -->
       </DataConnector>
       ```

       **UTILITY FOR OPENLDAP ADMINISTRATOR:**
         * ```ldapsearch -H ldap:// -x -b "dc=example,dc=it" -LLL dn```
           * the baseDN ==> ```ou=people, dc=example,dc=org``` (branch containing the registered users)
           * the bindDN ==> ```cn=admin,dc=example,dc=org``` (distinguished name for the user that can made queries on the LDAP)


8. Enrich IDP logs with the authentication error occurred on LDAP:
   * ```vim /opt/shibboleth-idp/conf/logback.xml```

     ```xml
     <!-- Logs LDAP related messages -->
     <logger name="org.ldaptive" level="${idp.loglevel.ldap:-WARN}"/>
 
     <!-- Logs on LDAP user authentication -->
     <logger name="org.ldaptive.auth.Authenticator" level="INFO" />
     ```

9. Define which attributes your IdP can manage into your Attribute Resolver file. Here you can find the **attribute-resolver-v3_3-idem.xml** provided by IDEM GARR AAI as example:
    * Download the attribute resolver provided by IDEM GARR AAI:
      ```wget http://www.garr.it/idem-conf/attribute-resolver-v3_3-idem.xml -O /opt/shibboleth-idp/conf/attribute-resolver-v3_3-idem.xml```

    * Modify ```services.xml``` file:
      ```vim /opt/shibboleth-idp/conf/services.xml```

      ```xml
      <value>%{idp.home}/conf/attribute-resolver.xml</value>
      ```
    
      must become:
 
      ```xml
      <value>%{idp.home}/conf/attribute-resolver.xml</value>
      <value>%{idp.home}/conf/attribute-resolver-v3_3-idem.xml</value>
      ```

  * Configure the LDAP Data Connector to be compliant to the values put in ```ldap.properties```. (See above suggestions)

10. Translate the IdP messages in your language:
    * Get the files translated in your language from [Shibboleth page](https://wiki.shibboleth.net/confluence/display/IDP30/MessagesTranslation) for:
      * **login page** (authn-messages_it.properties)
      * **user consent/terms of use page** (consent-messages_it.properties)
      * **error pages** (error-messages_it.properties)
    * Put all downloaded files into ```/opt/shibboleth-idp/messages``` directory
    * Restart Jetty: 
      ```service jetty restart```

11. Enable the SAML2 support by changing the ```idp-metadata.xml``` and disabling the SAML v1.x deprecated support:
    * ```vim /opt/shibboleth-idp/metadata/idp-metadata.xml```
      ```bash
      <IDPSSODescriptor> SECTION:
        – From the list of "protocolSupportEnumeration" remove:
          - urn:oasis:names:tc:SAML:1.1:protocol
          - urn:mace:shibboleth:1.0

        – Remove the endpoint:
          <ArtifactResolutionService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/ArtifactResolution" index="1"/>
          (and modify the index value of the next one to “1”)

        – Remove the endpoint:
          <NameIDFormat>urn:mace:shibboleth:1.0:nameIdentifier</NameIDFormat>

        – Add under the line:
          <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</NameIDFormat>
          this line:
          <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</NameIDFormat>
          (because the IdP installed with this guide releases persistent SAML NameIDs)

        - Remove the endpoint: 
          <SingleSignOnService Binding="urn:mace:shibboleth:1.0:profiles:AuthnRequest" Location="https://idp.example.org/idp/profile/Shibboleth/SSO"/>        
        - Remove all ":8443" from the existing URL (such port is not used anymore)

      <AttributeAuthorityDescriptor> Section:
        – From the list "protocolSupportEnumeration" replace the value of:
          - urn:oasis:names:tc:SAML:1.1:protocol
          with
          - urn:oasis:names:tc:SAML:2.0:protocol

        - Remove the comment from:
          <AttributeService Binding="urn:oasis:names:tc:SAML:2.0:bindings:SOAP" Location="https://idp.example.org/idp/profile/SAML2/SOAP/AttributeQuery"/>
        - Remove the endpoint: 
          <AttributeService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/AttributeQuery"/>

        - Remove all ":8443" from the existing URL (such port is not used anymore)
      ```

12. Obtain your IdP metadata here:
    *  ```https://idp.example.org/idp/shibboleth```

13. Register you IdP on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
    * ```https://registry.idem.garr.it/```

14. Configure the IdP to retrieve the Federation Metadata:
    * ```cd /opt/shibboleth-idp/conf```
    * ```vim metadata-providers.xml```

      ```xml
      <MetadataProvider
            id="URLMD-IDEM-Federation"
            xsi:type="FileBackedHTTPMetadataProvider"
            backingFile="%{idp.home}/metadata/idem-test-metadata-sha256.xml"
            metadataURL="http://www.garr.it/idem-metadata/idem-test-metadata-sha256.xml">

            <!--
                Verify the signature on the root element of the metadata aggregate
                using a trusted metadata signing certificate.
            -->
            <MetadataFilter xsi:type="SignatureValidation" requireSignedRoot="true" certificateFile="${idp.home}/metadata/federation-cert.pem"/>

            <!--
                Require a validUntil XML attribute on the root element and make sure its value is no more than 5 days into the future. 
            -->
            <MetadataFilter xsi:type="RequiredValidUntil" maxValidityInterval="P5D"/>

            <!-- Consume all SP metadata in the aggregate -->
            <MetadataFilter xsi:type="EntityRoleWhiteList">
              <RetainedRole>md:SPSSODescriptor</RetainedRole>
            </MetadataFilter>
      </MetadataProvider>
      ```

    * Retrieve the Federation Certificate used to verify its signed metadata:
      *  ```wget https://www.idem.garr.it/documenti/doc_download/321-idem-metadata-signer-2019 -O /opt/shibboleth-idp/metadata/federation-cert.pem```

    * Check the validity:
      *  ```cd /opt/shibboleth-idp/metadata```
      *  ```openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout```
       
         (sha1: 2F:F8:24:78:6A:A9:2D:91:29:19:2F:7B:33:33:FF:59:45:C1:7C:C8)
      *  ```openssl x509 -in federation-cert.pem -fingerprint -md5 -noout```

         (md5: AA:A7:CD:41:2D:3E:B7:F6:02:8A:D3:62:CD:21:F7:DE)
  
15. Reload service with id ```shibboleth.MetadataResolverService``` to retrieve the Federation Metadata:
    *  ```cd /opt/shibboleth-idp/bin```
    *  ```./reload-service.sh -id shibboleth.MetadataResolverService```

16. The day after the IDEM Federation Operators approval your entity on IDEM Entity Registry, check if you can login with your IdP on the following services:
    * https://sp-test.garr.it/secure   (Service Provider provided for testing the IDEM Test Federation)
    * https://sp24-test.garr.it/secure (Service Provider provided for testing the IDEM Test Federation and IDEM Production Federation)


### Configure Attribute Filters to release the mandatory attributes to the IDEM Default Resources:

1. Make sure that you have the "```tmp/httpClientCache```" used by "```shibboleth.FileCachingHttpClient```":
   * ```mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown jetty /opt/shibboleth-idp/tmp/httpClientCache```

2. Modify your ```services.xml```:
   * ```vim /opt/shibboleth-idp/conf/services.xml```

     ```xml
     <bean id="IDEM-Default-Filter" class="net.shibboleth.ext.spring.resource.FileBackedHTTPResource"
           c:client-ref="shibboleth.FileCachingHttpClient"
           c:url="http://www.garr.it/idem-conf/attribute-filter-v3-idem.xml"
           c:backingFile="%{idp.home}/conf/attribute-filter-v3-idem.xml"/>
          
     <util:list id ="shibboleth.AttributeFilterResources">
         <value>%{idp.home}/conf/attribute-filter.xml</value>
         <ref bean="IDEM-Default-Filter"/>
     </util:list>
     ```

3. Reload service with id ```shibboleth.AttributeFilterService``` to refresh the Attribute Filter followed by the IdP:
   *  ```cd /opt/shibboleth-idp/bin```
   *  ```./reload-service.sh -id shibboleth.AttributeFilterService```

### Configure Attribute Filters to release the mandatory attributes to the IDEM Production Resources:

1. Make sure that you have the "```tmp/httpClientCache```" used by "```shibboleth.FileCachingHttpClient```":
   * ```mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown jetty /opt/shibboleth-idp/tmp/httpClientCache```

2. Modify your ```services.xml```:
   * ```vim /opt/shibboleth-idp/conf/services.xml```

     ```xml
     <bean id="IDEM-Production-Filter" class="net.shibboleth.ext.spring.resource.FileBackedHTTPResource"
           c:client-ref="shibboleth.FileCachingHttpClient"
           c:url="http://www.garr.it/idem-conf/attribute-filter-v3-required.xml"
           c:backingFile="%{idp.home}/conf/attribute-filter-v3-required.xml"/>
     ...
     <util:list id ="shibboleth.AttributeFilterResources">
         <value>%{idp.home}/conf/attribute-filter.xml</value>
         <ref bean="IDEM-Default-Filter"/>
         <ref bean="IDEM-Production-Filter"/>
     </util:list>
     ```

3. Reload service with id ```shibboleth.AttributeFilterService``` to refresh the Attribute Filter followed by the IdP:
   *  ```cd /opt/shibboleth-idp/bin```
   *  ```./reload-service.sh -id shibboleth.AttributeFilterService```

### Configure Attribute Filters for Research and Scholarship and Data Protection Code of Conduct Entity Category

1. Make sure that you have the "```tmp/httpClientCache```" used by "```shibboleth.FileCachingHttpClient```":
   * ```mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown jetty /opt/shibboleth-idp/tmp/httpClientCache```

2. Modify your ```services.xml```:
   * ```vim /opt/shibboleth-idp/conf/services.xml```

     ```xml
     <bean id="ResearchAndScholarship" class="net.shibboleth.ext.spring.resource.FileBackedHTTPResource"
           c:client-ref="shibboleth.FileCachingHttpClient"
           c:url="http://www.garr.it/idem-conf/attribute-filter-v3-rs.xml"
           c:backingFile="%{idp.home}/conf/attribute-filter-v3-rs.xml"/>
          
     <bean id="CodeOfConduct" class="net.shibboleth.ext.spring.resource.FileBackedHTTPResource"
           c:client-ref="shibboleth.FileCachingHttpClient"
           c:url="http://www.garr.it/idem-conf/attribute-filter-v3-coco.xml"
           c:backingFile="%{idp.home}/conf/attribute-filter-v3-coco.xml"/>
    
     <util:list id ="shibboleth.AttributeFilterResources">
         <value>%{idp.home}/conf/attribute-filter.xml</value>
         <ref bean="IDEM-Default-Filter"/>
         <ref bean="IDEM-Production-Filter"/>
         <ref bean="ResearchAndScholarship"/>
         <ref bean="CodeOfConduct"/>
      </util:list>
      ```

3. Reload service with id ```shibboleth.AttributeFilterService``` to refresh the Attribute Filter followed by the IdP:
   *  ```cd /opt/shibboleth-idp/bin```
   *  ```./reload-service.sh -id shibboleth.AttributeFilterService```

### Appendix A: Import metadata from previous IDP v2.x ###

1. Store into /tmp directory the following files:
   * ```idp-metadata.xml```
   * ```idp.crt```
   * ```idp.key```

2. Follow the steps on your IdP v3.x:
   * ```sudo su -```
   * ```mv /tmp/idp-metadata.xml /opt/shibboleth-idp/metadata```
   * ```mv /tmp/idp.crt /tmp/idp.key /opt/shibboleth-idp/credentials```
   * ```cd /opt/shibboleth-idp/credentials/```
   * ```rm idp-encryption.crt idp-backchannel.crt idp-encryption.key idp-signing.crt idp-signing.key```
   * ```ln -s idp.crt idp-encryption.crt```
   * ```ln -s idp.key idp-encryption.key```
   * ```ln -s idp.key idp-signing.key```
   * ```ln -s idp.crt idp-signing.crt```
   * ```ln -s idp.crt idp-backchannel.crt```
   * ```openssl pkcs12 -export -in idp-encryption.crt -inkey idp-encryption.key -out idp-backchannel.p12 -password pass:#YOUR.BACKCHANNEL.CERT.PASSWORD#```

3. Check if the *idp.entityID* property value is equal to the entityID value inside the *idp-metadata.xml* on the file `/opt/shibboleth-idp/conf/idp.properties`.

4. Enable the SAML2 support by changing the ```idp-metadata.xml``` and disabling the SAML v1.x deprecated support:
   * ```vim /opt/shibboleth-idp/metadata/idp-metadata.xml```
 
     ```bash
     <IDPSSODescriptor> SECTION:
       – From the list of "protocolSupportEnumeration" remove:
         - urn:oasis:names:tc:SAML:1.1:protocol
         - urn:mace:shibboleth:1.0

       – Remove the endpoint:
         <ArtifactResolutionService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/ArtifactResolution" index="1"/>
         (and modify the index value of the next one to “1”)

       – Remove the endpoint:
         <NameIDFormat>urn:mace:shibboleth:1.0:nameIdentifier</NameIDFormat>

       – Add under the line:
         <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</NameIDFormat>
         this line:
         <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</NameIDFormat>
         (because the IdP installed with this guide releases persistent SAML NameIDs)

       - Remove the endpoint: 
         <SingleSignOnService Binding="urn:mace:shibboleth:1.0:profiles:AuthnRequest" Location="https://idp.example.org/idp/profile/Shibboleth/SSO"/>        
       - Remove all ":8443" from the existing URL (such port is not used anymore)

     <AttributeAuthorityDescriptor> Section:
       – From the list "protocolSupportEnumeration" replace the value of:
         - urn:oasis:names:tc:SAML:1.1:protocol
         with
         - urn:oasis:names:tc:SAML:2.0:protocol

       - Remove the comment from:
         <AttributeService Binding="urn:oasis:names:tc:SAML:2.0:bindings:SOAP" Location="https://idp.example.org/idp/profile/SAML2/SOAP/AttributeQuery"/>
       - Remove the endpoint: 
         <AttributeService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/AttributeQuery"/>

       - Remove all ":8443" from the existing URL (such port is not used anymore)
     ```

5. Restart Jetty:
   * ```service jetty restart```
  
6. Don't forget to update your IdP Metadata on [IDEM Entity Registry](https://registry.idem.garr.it/rr3) to apply changes on the federation IDEM! For any help write to idem-help@garr.it


### Appendix B: Import persistent-id from a previous database ###

1. Create a DUMP of `shibpid` table from the previous DB `userdb` on the OLD IdP:
   * ```cd /tmp```
   * ```mysqldump --complete-insert --no-create-db --no-create-info -u root -p userdb shibpid > /tmp/userdb_shibpid.sql```

2. Move the ```/tmp/userdb_shibpid.sql``` of old IdP into ```/tmp/userdb_shibpid.sql``` on the new IdP.
 
3. Import the content of ```/tmp/userdb_shibpid.sql``` into the DB of the new IDP:
   * ```cd /tmp ; mysql -u root -p shibboleth < /tmp/userdb_shibpid.sql```

4. Delete ```/tmp/userdb_shibpid.sql```:
   * ```rm /tmp/userdb_shibpid.sql```

### Appendix C: Useful logs to find problems

1. Jetty Logs:
   * ```cd /opt/jetty/logs```
   * ```ls -l *.stderrout.log```

2. Shibboleth IdP Logs:
   * ```cd /opt/shibboleth-idp/logs```
   * **Audit Log:** ```vim idp-audit.log```
   * **Consent Log:** ```vim idp-consent-audit.log```
   * **Warn Log:** ```vim idp-warn.log```
   * **Process Log:** ```vim idp-process.log```

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
