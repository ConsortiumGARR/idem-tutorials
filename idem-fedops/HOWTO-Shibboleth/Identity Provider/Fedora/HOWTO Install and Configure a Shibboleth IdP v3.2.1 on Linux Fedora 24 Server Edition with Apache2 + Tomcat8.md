# HOWTO Install and Configure a Shibboleth IdP v3.2.1 on Linux Fedora 24 Server Edition (minimal) with Apache2 + Tomcat8

<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />

## Index

1. [Requirements Hardware](#requirements-hardware)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Other Requirements](#other-requirements)
4. [Installation Instructions](#installation-instructions)
   1. [Install software requirements](#install-software-requirements)
   2. [Configure the environment](#configure-the-environment)
   3. [Install Shibboleth Identity Provider 3.2.1](#install-shibboleth-identity-provider-v321)
5. [Configuration Instructions](#configuration-instructions)
   1. [Configure SSL on Apache2 (Tomcat 8 front-end)](#configure-ssl-on-apache2-tomcat-8-front-end)
   2. [Configure Apache Tomcat 8](#configure-apache-tomcat-8)
   3. [Speed up Tomcat 8 startup](#speed-up-tomcat-8-startup)
   4. [Configure Shibboleth Identity Provider v3.2.1 to release the persistent-id (Stored Mode)](#configure-shibboleth-identity-provider-v321-to-release-the-persistent-id-stored-mode)
   5. [Configure Attribute Filters to release the mandatory attributes to the default IDEM Resources](#configure-attribute-filters-to-release-the-mandatory-attributes-to-the-default-idem-resources)
   6. [Configure Attribute Filters to release the mandatory attributes to the IDEM Production Resources](#configure-attribute-filters-to-release-the-mandatory-attributes-to-the-idem-production-resources)
   7. [Configure Attribute Filters for Research and Scholarship and Data Protection Code of Conduct Entity Category](#configure-attribute-filters-for-research-and-scholarship-and-data-protection-code-of-conduct-entity-category)
6. [Appendix A: Import metadata from previous IDP v2.x](#appendix-a-import-metadata-from-previous-idp-v2x)
7. [Appendix B: Import persistent-id from a previous database](#appendix-b-import-persistent-id-from-a-previous-database)
8. [Appendix C: Useful logs to find problems](#appendix-c-useful-logs-to-find-problems)
9. [Appendix D: Issues](#appendix-d-issues)
10. [Authors](#authors)


## Requirements Hardware 

 * CPU: 2 Core
 * RAM: 4 GB
 * HDD: 20 GB

## Software that will be installed

 * ca-certificates
 * ntp
 * vim-enhanced
 * java-1.8.0-openjdk
 * java-1.8.0-openjdk-devel
 * tomcat
 * httpd (Apache >= 2.4)
 * expat
 * openssl
 * mariadb-server
 * mysql-connector-java
 * apache-commons-dbcp
 * apache-commons-pool

## Other Requirements

 * Place the HTTPS Server Certificate and the HTTPS Server Key inside ```/tmp``` directory

## Installation Instructions

### Install software requirements

1. Become ROOT:
   * ```sudo su -```

2. Install the packages required: 
   * ```dnf install vim-enhanced java-1.8.0-openjdk java-1.8.0-openjdk-devel ca-certificates openssl httpd mod_ssl expat wget tar ntp```
  
3. Disable SELinux:
   * ```vim /etc/selinux/config```
  
     ```
     # This file controls the state of SELinux on the system.
     # SELINUX= can take one of these three values:
     #       enforcing - SELinux security policy is enforced.
     #       permissive - SELinux prints warnings instead of enforcing.
     #       disabled - No SELinux policy is loaded.
     SELINUX=disabled
     ```
   * ```reboot```
   * ```sudo su -```
   * check that the command ```getenforce``` returns **Disabled**.

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
     JAVA_HOME=/usr/lib/jvm/jre
     IDP_SRC=/usr/local/src/shibboleth-identity-provider-3.2.1
     ```
   * ```source /etc/environment```
   * ```export JAVA_HOME=/usr/lib/jvm/jre```
   * ```export IDP_SRC=/usr/local/src/shibboleth-identity-provider-3.2.1```
  
4. Move the Certificate and the Key file for HTTPS server from ```/tmp/``` to ```/root/certificates```:
   * ```mkdir /root/certificates```
   * ```mv /tmp/idp-cert-server.crt /root/certificates```
   * ```mv /tmp/idp-key-server.key /root/certificates```
   * ```mv /tmp/DigiCertCA.crt /root/certificates```
   * ```chmod 400 /root/certificates/idp-key-server.key```
   * ```chmod 644 /root/certificates/idp-cert-server.crt```
   * ```chmod 644 /root/certificates/DigiCertCA.crt```

   (OPTIONAL) Create a Certificate and a Key self-signed for HTTPS if you don't have the official ones provided by DigiCert:
   * ```openssl req -x509 -newkey rsa:4096 -keyout /root/certificates/idp-key-server.key -out /root/certificates/idp-cert-server.crt -nodes -days 1095```

5. Configure **/etc/tomcat/tomcat.conf**:
   * ```update-alternatives --config java``` (copy the path without /bin/java)
   * ```update-alternatives --config javac```
   * ```vim /etc/tomcat/tomcat.conf```
  
     ```bash
     JAVA_OPTS="-Djavax.sql.DataSource.Factory=org.apache.commons.dbcp.BasicDataSourceFactory -Djava.awt.headless=true -XX:+DisableExplicitGC -XX:+UseParallelOldGC -Xms256m -Xmx2g -Djava.security.egd=file:/dev/./urandom"
     ```

     (This settings configure the memory of the JVM that will host the IdP Web Application. 
     The Memory value depends on the phisical memory installed on the machine. 
     Set the "**Xmx**" (max heap space available to the JVM) at least to **2GB**)

### Install Shibboleth Identity Provider v3.2.1

1. Become ROOT: 
   * ```sudo su -```

2. Download the Shibboleth Identity Provider v3.2.1:
   * ```cd /usr/local/src```
   * ```wget http://shibboleth.net/downloads/identity-provider/3.2.1/shibboleth-identity-provider-3.2.1.tar.gz```
   * ```tar -xzvf shibboleth-identity-provider-3.2.1.tar.gz```
   * ```cd shibboleth-identity-provider-3.2.1```

3. Run the installer ```install.sh```:
   * ```./bin/install.sh```
  
   ```bash
   root@idp:/usr/local/src/shibboleth-identity-provider-3.2.1# ./bin/install.sh
   Source (Distribution) Directory: [/usr/local/src/shibboleth-identity-provider-3.2.1]
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

4. Import the JST libraries to visualize the IdP ```status``` page:
   * ```cd /opt/shibboleth-idp/edit-webapp/WEB-INF/lib```
   * ```wget https://build.shibboleth.net/nexus/service/local/repositories/thirdparty/content/javax/servlet/jstl/1.2/jstl-1.2.jar```
   * ```cd /opt/shibboleth-idp/bin ; ./build.sh -Didp.target.dir=/opt/shibboleth-idp```

5. Change the owner to enable **tomcat8** user to access on the following directories:
   * ```chown -R tomcat /opt/shibboleth-idp/logs/```
   * ```chown -R tomcat /opt/shibboleth-idp/metadata/```
   * ```chown -R tomcat /opt/shibboleth-idp/credentials/```
   * ```chown -R tomcat /opt/shibboleth-idp/conf/```

## Configuration Instructions

### Configure SSL on Apache2 (Tomcat 8 front-end)

1. Modify the file ```/etc/httpd/conf.d/ssl.conf``` as follows:

   ```apache
   #
   # When we also provide SSL we have to listen to the 
   # the HTTPS port in addition.
   #
   Listen 443 https
   ...
   <VirtualHost _default_:443>
     ServerName idp.example.org:443
     ServerAdmin admin@example.org
     DocumentRoot /var/www/html
     ...
     SSLEngine On
     SSLProtocol all -SSLv2 -SSLv3 -TLSv1
    
     SSLCipherSuite "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA:kEDH+AESGCM:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES256-SHA256:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA256:ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA256:AES256-GCM-SHA384:!3DES:!DES:!DHE-RSA-AES128-GCM-SHA256:!DHE-RSA-AES256-SHA:!EDE3:!EDH-DSS-CBC-SHA:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC-SHA:!EDH-RSA-DES-CBC3-SHA:!EXP-EDH-DSS-DES-CBC-SHA:!EXP-EDH-RSA-DES-CBC-SHA:!EXPORT:!MD5:!PSK:!RC4-SHA:!aNULL:!eNULL"
    
     SSLHonorCipherOrder on
    
     # Disable SSL Compression
     SSLCompression Off
     # Enable HTTP Strict Transport Security with a 2 year duration
     Header always set Strict-Transport-Security "max-age=63072000;includeSubDomains"
     ...
     SSLCertificateFile /root/certificates/idp-cert-server.crt
     SSLCertificateKeyFile /root/certificates/idp-key-server.key
     SSLCertificateChainFile /root/certificates/DigiCertCA.crt
     ...
   </VirtualHost>
   ```

2. Configure Apache2 to open port **80** only for localhost:
   * ```vim /etc/httpd/conf/httpd.conf```

     ```apache
     # Listen: Allows you to bind Apache to specific IP addresses and/or
     # ports, instead of the default. See also the <VirtualHost>
     # directive.
     #
     # Change this to Listen on specific IP addresses as shown below to 
     # prevent Apache from glomming onto all bound IP addresses.
     #
     #Listen 12.34.56.78:80
     Listen 127.0.0.1:80
     ```

3. Enable **SSL** and **headers** Apache2 modules:
   * ```service httpd restart```
  
4. Verify the strength of your IdP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

### Configure Apache Tomcat 8

1. Become ROOT: 
   * ```sudo su -```

2. Change ```server.xml```:
   * ```vim /etc/tomcat/server.xml```

     Comment out the Connector 8080 (HTTP):
    
     ```apache
     <!-- A "Connector" represents an endpoint by which requests are received
          and responses are returned. Documentation at :
          Java HTTP Connector: /docs/config/http.html (blocking & non-blocking)
          Java AJP  Connector: /docs/config/ajp.html
          APR (HTTP/AJP) Connector: /docs/apr.html
          Define a non-SSL/TLS HTTP/1.1 Connector on port 8080
     -->
     <!--
     <Connector port="8080" protocol="HTTP/1.1"
                connectionTimeout="20000"
                URIEncoding="UTF-8"
                redirectPort="8443" />
     -->
     ```

     Enable the Connector 8009 (AJP):

     ```apache
     <!-- Define an AJP 1.3 Connector on port 8009 -->
     <Connector port="8009" protocol="AJP/1.3" redirectPort="443" address="127.0.0.1" enableLookups="false" tomcatAuthentication="false"/>
     ```
    
     Check the integrity of XML files just edited with:
     ```xmlwf -e UTF-8 /etc/tomcat/server.xml```

3. Create and change the file ```idp.xml```:
   * ```sudo vim /etc/tomcat/Catalina/localhost/idp.xml```

     ```apache
     <Context docBase="/opt/shibboleth-idp/war/idp.war"
              privileged="true"
              antiResourceLocking="false"
              swallowOutput="true"/>
     ```

4. Create the Apache2 configuration file for IdP:
   * ```vim /etc/httpd/conf.d/idp.conf```
  
     ```apache
     ProxyPreserveHost On
     RequestHeader set X-Forwarded-Proto "https"

     <Proxy ajp://localhost:8009>
       Require all granted
     </Proxy>
  
     ProxyPass /idp ajp://localhost:8009/idp retry=5
     ProxyPassReverse /idp ajp://localhost:8009/idp retry=5
     ```

5. Restart Apache2:
   * ```service httpd restart```
  
6. Modify **context.xml** to prevent error of *lack of persistence of the session objects* created by the IdP :
   * ```vim /etc/tomcat/context.xml```

     and remove the comment from:

     ```<Manager pathname="" />```
    
7. Restart Tomcat 8:
   * ```service tomcat restart```

8. Verify if the IdP works by opening this page on your browser:
   * ```https://idp.example.org/idp/shibboleth``` (you should see the IdP metadata)

### Speed up Tomcat 8 startup

1. Become ROOT: 
   * ```sudo su -```
  
2. Find out the JARs that can be skipped from the scanning:
   * ```cd /opt/shibboleth-idp/```
   * ```ls webapp/WEB-INF/lib | awk '{print $1",\\"}'```
  
3. Insert the output list into ```/etc/tomcat/catalina.properties``` at the tail of ```tomcat.util.scan.StandardJarScanFilter.jarsToSkip```

4. Restart Tomcat 8:
   * ```service tomcat restart```

### Configure Shibboleth Identity Provider v3.2.1 to release the persistent-id (Stored mode)

1. Become ROOT of the machine: 
   * ```sudo su -```
  
2. Test IdP by opening a terminal and running these commands:
   * ```cd /opt/shibboleth-idp/bin```
   * ```./status.sh``` (You should see some informations about the IdP installed)

3. Install **MySQL Connector Java** and **Tomcat JDBC** libraries used by Tomcat and Shibboleth for MySQL DB:
   * ```dnf install mariadb-server mysql-connector-java apache-commons-dbcp apache-commons-pool```
   * ```cd /usr/share/tomcat/lib/```
   * ```ln -s ../../java/mysql-java-connector.jar mysql-connector-java.jar```
   * ```ln -s ../../java/commons-pool.jar commons-pool.jar```
   * ```ln -s ../../java/commons-dbcp.jar commons-dbcp.jar```

4. Rebuild the **idp.war** of Shibboleth with the new libraries:
   * ```cd /opt/shibboleth-idp/ ; ./bin/build.sh```

5. Create and prepare the "**shibboleth**" MySQL DB to host the values of the several **persistent-id** and **StorageRecords** MySQL DB to host other useful information about user consent:
   * Modify the [shibboleth-db.sql](../utils/shibboleth-db.sql) by changing the *username* and *password* of the user that has write access to the "**shibboleth**" DB.
   * Import the SQL modified to your MySQL Server:
     ```mysql -u root -p##PASSWORD-DB## < ./shibboleth-db.sql```
   * Restart mysql service:
     ```service mariadb restart```

6. Enable the generation of the ```persistent-id``` (this replace the deprecated attribute *eduPersonTargetedID*)
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

7. Enable **JPAStorageService** for the **StorageService** of the user consent:
   * ```vim /opt/shibboleth-idp/conf/global.xml``` and add this piece of code to the tail:

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
     (and modify the "**USER_DB_NAME**" and "**PASSWORD**" for your "**shibboleth**" DB)

   * Modify the IdP configuration file:
     * ```vim /opt/shibboleth-idp/conf/idp.properties```

       ```xml
       idp.consent.StorageService = shibboleth.JPAStorageService
       idp.replayCache.StorageService = shibboleth.JPAStorageService
       idp.artifact.StorageService = shibboleth.JPAStorageService
       ```
 
       (This will indicate to IdP to store the data collected by User Consent into the "**StorageRecords**" table)

8. Connect the openLDAP to the IdP to allow the authentication of the users:
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
       (If you decide to use the Solution 3, you have to remove (or comment out) the following code from your ```attribute-resolver-full.xml```:
      
       ```xml
       </dc:FilterTemplate>
       <!--
       <dc:StartTLSTrustCredential id="LDAPtoIdPCredential" xsi:type="sec:X509ResourceBacked">
         <sec:Certificate>%
           {idp.attribute.resolver.LDAP.trustCertificates}</sec:Certificate>
         </dc:StartTLSTrustCredential>
       -->
       </resolver:DataConnector>
       ```

       **UTILITY FOR OPENLDAP ADMINISTRATOR:**
         * ```ldapsearch -H ldap:// -x -b "dc=example,dc=it" -LLL dn```
           * the baseDN ==> ```ou=people, dc=example,dc=org``` (branch containing the registered users)
           * the bindDN ==> ```cn=admin,dc=example,dc=org``` (distinguished name for the user that can made queries on the LDAP)


9. Enrich IDP logs with the authentication error occurred on LDAP:
   * ```vim /opt/shibboleth-idp/conf/logback.xml```

     ```xml
     <!-- Logs LDAP related messages -->
     <logger name="org.ldaptive" level="${idp.loglevel.ldap:-WARN}"/>
 
     <!-- Logs on LDAP user authentication -->
     <logger name="org.ldaptive.auth.Authenticator" level="INFO" />
     ```

10. Build the **attribute-resolver.xml** to define which attributes your IdP can manage. Here you can find the **attribute-resolver-v3-idem.xml** provided by IDEM GARR AAI:
    * Download the attribute resolver provided by IDEM GARR AAI:
      ```wget http://www.garr.it/idem-conf/attribute-resolver-v3-idem.xml -O /opt/shibboleth-idp/conf/attribute-resolver-v3-idem.xml```

    * Modify ```services.xml``` file:
      ```vim /opt/shibboleth-idp/conf/services.xml```

      ```xml
      <value>%{idp.home}/conf/attribute-resolver.xml</value>
      ```
    
      must become:
 
      ```xml
      <value>%{idp.home}/conf/attribute-resolver-v3-idem.xml</value>
      ```

    * Configure the LDAP Data Connector to be compliant to the values put on ```ldap.properties```. (See above suggestions)

11. Translate the IdP messages in your language:
    * Get the files translated in your language from [Shibboleth page](https://wiki.shibboleth.net/confluence/display/IDP30/MessagesTranslation) for:
      * **login page** (authn-messages_it.properties)
      * **user consent/terms of use page** (consent-messages_it.properties)
      * **error pages** (error-messages_it.properties)
    * Put all the downloded files into ```/opt/shibboleth-idp/messages``` directory
    * Restart Tomcat8: 
      ```service tomcat restart```

12. Enable the SAML2 support by changing the ```idp-metadata.xml``` and disabling the SAML v1.x deprecated support:
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

        – Replace the endpoint:
          <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</NameIDFormat>
          with:
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
          <AttributeService Binding="urn:oasis:names:tc:SAML:2.0:bindings:SOAP" Location="https://idp.mi.garr.it/idp/profile/SAML2/SOAP/AttributeQuery"/>
        - Remove the endpoint: 
          <AttributeService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/AttributeQuery"/>

        - Remove all ":8443" from the existing URL (such port is not used anymore)
      ```

13. Obtain your IdP metadata here:
    *  ```https://idp.example.org/idp/shibboleth```

14. Register you IdP on IDEM Entity Registry:
    * ```https://registry.idem.garr.it/```

15. Configure the IdP to retrieve the Federation Metadata:
    * ```cd /opt/shibboleth-idp/conf```
    * ```vim metadata-providers.xml```

      ```xml
      <MetadataProvider
            id="URLMD-IDEM-Federation"
            xsi:type="FileBackedHTTPMetadataProvider"
            backingFile="%{idp.home}/metadata/idem-test-metadata-sha256.xml"
            metadataURL="http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml">

            <!--
                Verify the signature on the root element of the metadata aggregate
                using a trusted metadata signing certificate.
            -->
            <MetadataFilter xsi:type="SignatureValidation" requireSignedRoot="true" certificateFile="${idp.home}/metadata/federation-cert.pem"/>
 
            <!--
                Require a validUntil XML attribute on the root element and
                make sure its value is no more than 10 days into the future.
            -->
            <MetadataFilter xsi:type="RequiredValidUntil" maxValidityInterval="P10D"/>
   
            <!-- Consume all SP metadata in the aggregate -->
            <MetadataFilter xsi:type="EntityRoleWhiteList">
              <RetainedRole>md:SPSSODescriptor</RetainedRole>
            </MetadataFilter>
      </MetadataProvider>
      ```

    * Retrieve the Federation Certificate used to verify its signed metadata:
      *  ```wget https://md.idem.garr.it/certs/idem-signer-20220121.pem -O /opt/shibboleth-idp/metadata/federation-cert.pem```

    * Check the validity:
      *  ```cd /opt/shibboleth-idp/metadata```
      *  ```openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout```
       
         (sha1: D1:68:6C:32:A4:E3:D4:FE:47:17:58:E7:15:FC:77:A8:44:D8:40:4D)
      *  ```openssl x509 -in federation-cert.pem -fingerprint -md5 -noout```

         (md5: 48:3B:EE:27:0C:88:5D:A3:E7:0B:7C:74:9D:24:24:E0)
  
16. Reload service with id ```shibboleth.MetadataResolverService``` to retrieve the Federation Metadata:
    *  ```cd /opt/shibboleth-idp/bin```
    *  ```./reload-service.sh -id shibboleth.MetadataResolverService```

17. The day after the IDEM Federation Operators approval the IdP entity on the IDEM Entity Registry, check if you can login with your IdP on the following services:
    * https://sp-demo.aai-test.garr.it/secure   (Service Provider provided for testing the IDEM Test Federation)
    * https://sp24-test.garr.it/secure (Service Provider provided for testing the IDEM Test Federation, IDEM Production Federation and eduGAIN)

### Configure Attribute Filters to release the mandatory attributes to the default IDEM Resources

1. Make sure that you have the "```tmp/httpClientCache```" used by "```shibboleth.FileCachingHttpClient```":
   * ```mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown tomcat8 /opt/shibboleth-idp/tmp/httpClientCache```

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

### Configure Attribute Filters to release the mandatory attributes to the IDEM Production Resources

1. Make sure that you have the "```tmp/httpClientCache```" used by "```shibboleth.FileCachingHttpClient```":
   * ```mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown tomcat8 /opt/shibboleth-idp/tmp/httpClientCache```

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
   * ```mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown tomcat8 /opt/shibboleth-idp/tmp/httpClientCache```

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

### Appendix A: Import metadata from previous IDP v2.x

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

5. Restart Tomcat8:
   * ```service tomcat restart```
  
6. Don't forget to update your IdP Metadata on [IDEM Entity Registry](https://registry.idem.garr.it/rr3) to apply changes on the federation IDEM! For any help write to idem-help@garr.it


### Appendix B: Import persistent-id from a previous database

1. Create a DUMP of `shibpid` table from the previous DB `userdb` on the OLD IdP:
   * ```cd /tmp```
   * ```mysqldump --complete-insert --no-create-db --no-create-info -u root -p userdb shibpid > /tmp/userdb_shibpid.sql```

2. Move the ```/tmp/userdb_shibpid.sql``` of old IdP into ```/tmp/userdb_shibpid.sql``` on the new IdP.
 
3. Import the content of ```/tmp/userdb_shibpid.sql``` into the DB of the new IDP:
   * ```cd /tmp ; mysql -u root -p shibboleth < /tmp/userdb_shibpid.sql```

4. Delete ```/tmp/userdb_shibpid.sql```:
   * ```rm /tmp/userdb_shibpid.sql```

### Appendix C: Useful logs to find problems

1. Tomcat8 Logs:
   * ```cd /var/log/tomcat/```
   * ```vim catalina.out```

2. Shibboleth IdP Logs:
   * ```cd /opt/shibboleth-idp/logs```
   * **Audit Log:** ```vim idp-audit.log```
   * **Consent Log:** ```vim idp-consent-audit.log```
   * **Warn Log:** ```vim idp-warn.log```
   * **Process Log:** ```vim idp-process.log```

### Appendix D: Issues

1. The ```<ResultCache>```, an LDAP Data Connector child element, in IdP versions before 3.3.0 has a serious security issue, as described in [security advisory 20161027](http://shibboleth.net/community/advisories/secadv_20161027.txt). 
  
   **If you are using a vulnerable version of the IdP then you should not use this element in new deployments, and you should remove it from existing deployments.**

   The <ResultCache> element can be used safely starting with IdP version 3.3.0.
  
### Authors

 * Alessandro Enea (alessandro.enea@ilc.cnr.it)
 * Marco Malavolti (marco.malavolti@garr.it)
