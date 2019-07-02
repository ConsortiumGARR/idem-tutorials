# HOWTO Install and Configure a Shibboleth IdP v3.4.4 on Debian 9 Linux with Apache2 + Jetty9 

[comment]: # (<img width="120px" src="https://wiki.idem.garr.it/IDEM_Approved.png" />)

## Table of Contents

1. [Requirements Hardware](#requirements-hardware)
2. [Software that will be installed](#software-that-will-be-installed)
3. [Other Requirements](#other-requirements)
4. [Installation Instructions](#installation-instructions)
   1. [Install software requirements](#install-software-requirements)
   2. [Configure the environment](#configure-the-environment)
   3. [Install Jetty 9 Web Server](#install-jetty-9-web-server)
   4. [Install Shibboleth Identity Provider 3.4.4](#install-shibboleth-identity-provider-v344)
5. [Configuration Instructions](#configuration-instructions)
   1. [Configure SSL on Apache2 (front-end of Jetty)](#configure-ssl-on-apache2-front-end-of-jetty)
   2. [Configure Jetty](#configure-jetty)
   3. [Configure Shibboleth Identity Provider StorageRecords (User Consent)](#configure-shibboleth-identity-provider-storagerecords-user-consent)
      1. [Default - Not Recommended](#default---not-recommended)
      2. [HTML Local Storage - Recommended](#html-local-storage---recommended)
      3. [JPA Storage Service - using a database](#jpa-storage-service---using-a-database)
   4. [Configure Shibboleth Identity Provider to release the persistent-id](#configure-shibboleth-identity-provider-to-release-the-persistent-id)
      1. [Computed mode - Default & Recommended](#computed-mode---default-recommended)
      2. [Stored Mode](#stored-mode)
   5. [Configure Logout](#configure-logout)
   6. [Configure the directory (openLDAP) connection](#configure-the-directory-openldap-connection)
   7. [Configure IdP Logging](#configure-idp-logging)
   8. [Translate IdP messages into preferred language](#translate-idp-messages-into-preferred-language)
   9. [Disable SAML1 Deprecated Protocol](#disable-saml1-deprecated-protocol)
   10. [Register the IdP on the Federation](#register-the-idp-on-the-federation)
   11. [Configure Attribute Filters to release the mandatory attributes to the IDEM Default  Resources](#configure-attribute-filters-to-release-the-mandatory-attributes-to-the-idem-default-resources)
   12. [Configure Attribute Filters to release the mandatory attributes to the IDEM Production Resources](#configure-attribute-filters-to-release-the-mandatory-attributes-to-the-idem-production-resources)
   13. [Configure Attribute Filters for Research and Scholarship and Data Protection Code of Conduct Entity Category](#configure-attribute-filters-for-research-and-scholarship-and-data-protection-code-of-conduct-entity-category)
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
 * mysql-server (if Stored mode is used)
 * libmysql-java (if Stored mode is used)
 * libcommons-dbcp-java (if Stored mode is used)
 * libcommons-pool-java (if Stored mode is used)

## Other Requirements

 * Put HTTPS credentials in the right place:
   * HTTPS Server Certificate (Public Key) inside `/etc/ssl/certs` 
   * HTTPS Server Key (Private Key) inside `/etc/ssl/private`
   * HTTPS Certification Authority Certificate is already provided by Debian packages

## Installation Instructions

### Install software requirements

1. Become ROOT:
   * `sudo su -`

2. Change the default mirror with the GARR ones:
   * `sed -i 's/deb.debian.org/debian.mirror.garr.it/g' /etc/apt/sources.list`
   * `apt update && apt-get upgrade -y --no-install-recommends`
  
3. Install the packages required: 
   * `apt install vim default-jdk ca-certificates openssl apache2 ntp expat --no-install-recommends`

4. Check that Java is working:
   * `update-alternatives --config java`

### Configure the environment

1. Modify your `/etc/hosts`:
   * `vim /etc/hosts`
  
     `127.0.1.1 idp.example.org idp`

     (Replace `127.0.1.1` with the *IdP's private IP* and `idp.example.org` with your IdP *Full Qualified Domain Name*)

2. Be sure that your firewall **doesn't block** the traffic on port **443** (or you can't access to your IdP)

3. Define the costant `JAVA_HOME` inside `/etc/environment`:
   * `vim /etc/environment`

     `JAVA_HOME=/usr/lib/jvm/default-java/jre`

   * `source /etc/environment`

4. Put the Certificate and Key used by HTTPS into the `/etc/ssl` directory and set the right privileges:
   * `chmod 400 /etc/ssl/private/idp.example.org.key`
   * `chmod 644 /etc/ssl/certs/idp.example.org.crt`

   (OPTIONAL) Create a Certificate and a Key self-signed for HTTPS if you don't have the official ones provided by a Certification Authority like DigiCert:
   * `openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/idp.example.org.key -out /etc/ssl/certs/idp.example.org.crt -nodes -days 1095`

5. Configure **/etc/default/jetty**:
   * `vim /etc/default/jetty`
  
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
   * `sudo su -`

2. Download and Extract Jetty:
   * `cd /usr/local/src`
   * `wget http://central.maven.org/maven2/org/eclipse/jetty/jetty-distribution/9.4.19.v20190610/jetty-distribution-9.4.19.v20190610.tar.gz`
   * `tar xzvf jetty-distribution-9.4.19.v20190610.tar.gz`

3. Create an useful-for-updates `jetty-src` folder:
   * `ln -s jetty-distribution-9.4.19.v20190610 jetty-src`

4. Create the user `jetty` that can run the web server:
   * `useradd -r -m jetty`

5. Create your custom Jetty configuration that override the default ones:
   * `mkdir /opt/jetty`
   * `cd /opt/jetty`
   * `vim /opt/jetty/start.ini`

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
   * `mkdir /opt/jetty/tmp ; chown jetty:jetty /opt/jetty/tmp`
   * `chown -R jetty:jetty /opt/jetty/ /usr/local/src/jetty-src`

7. Create the service loadable from command line:
   * `cd /etc/init.d`
   * `ln -s /usr/local/src/jetty-src/bin/jetty.sh jetty`
   * `update-rc.d jetty defaults`

8. Create the Jetty Log's folder:
   * `mkdir /var/log/jetty`
   * `mkdir /opt/jetty/logs`
   * `chown jetty:jetty /var/log/jetty /opt/jetty/logs`

9. Check if all settings are OK:
   * `service jetty check`   (Jetty NOT running)
   * `service jetty start`
   * `service jetty check`   (Jetty running pid=XXXX)
  
   If you receive an error likes "*Job for jetty.service failed because the control process exited with error code. See "systemctl status jetty.service" and "journalctl -xe" for details.*", try this: 
     * `rm /var/run/jetty.pid`
     * `systemctl start jetty`

10. Check if the Apache Welcome page is available:
    * https://idp.example.org

### Install Shibboleth Identity Provider v3.4.4

1. Become ROOT:
   * `sudo su -`

2. Download the Shibboleth Identity Provider v3.4.4:
   * `cd /usr/local/src`
   * `wget http://shibboleth.net/downloads/identity-provider/3.4.4/shibboleth-identity-provider-3.4.4.tar.gz`
   * `tar -xzvf shibboleth-identity-provider-3.4.4.tar.gz`

3. Import the JST libraries to visualize the IdP `status` page:
   * `cd /usr/local/src/shibboleth-identity-provider-3.4.4/webapp/WEB-INF/lib`
   * `wget https://build.shibboleth.net/nexus/service/local/repositories/thirdparty/content/javax/servlet/jstl/1.2/jstl-1.2.jar`

4. Run the installer `install.sh`:
   * `cd /usr/local/src/shibboleth-identity-provider-3.4.4`
   * `./bin/install.sh`
  
   ```bash
   root@idp:/usr/local/src/shibboleth-identity-provider-3.4.4# ./bin/install.sh
   Source (Distribution) Directory: [/usr/local/src/shibboleth-identity-provider-3.4.4]
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
  
   From this point the variable **idp.home** refers to the directory: `/opt/shibboleth-idp`

5. Change the owner to enable **jetty** user to access on the following directories:
   * `cd /opt/shibboleth-idp`
   * `chown -R jetty logs/ metadata/ credentials/ conf/ system/ war/`

## Configuration Instructions

### Configure SSL on Apache2 (front-end of Jetty)

1. Create the server's directory:
   * `mkdir /var/www/html/idp.example.org`
   * `sudo chown -R www-data: /var/www/html/idp.example.org`

2. Create a new Virtualhost file `/etc/apache2/sites-available/idp.example.org-ssl.conf` as follows:

   ```apache
   <IfModule mod_ssl.c>
      SSLStaplingCache shmcb:/var/run/ocsp(128000)
      <VirtualHost _default_:443>
        ServerName idp.example.org:443
        ServerAdmin admin@example.org
        DocumentRoot /var/www/html/idp.example.org
        
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
        
        SSLCertificateFile /etc/ssl/certs/idp.example.org.crt
        SSLCertificateKeyFile /etc/ssl/private/idp.example.org.key
        SSLCACertificateFile /etc/ssl/certs/ca-certificates.crt

        <IfModule mod_proxy.c>
           ProxyPreserveHost On
           RequestHeader set X-Forwarded-Proto "https"
           ProxyPass /idp http://localhost:8080/idp retry=5
           ProxyPassReverse /idp http://localhost:8080/idp retry=5

           <Location /idp>
              Require all granted
           </Location>
        </IfModule>
      </VirtualHost>
   </IfModule>
   ```
   
3. Configure Apache2 to redirect all on HTTPS:
   * `vim /etc/apache2/sites-available/idp.example.org.conf`
   
   ```apache
   <VirtualHost *:80>
        ServerName "idp.example.org"
        Redirect permanent "/" "https://idp.example.org/"
   </VirtualHost>
   ```

4. Enable **proxy_http**, **SSL** and **headers** Apache2 modules:
   * `a2enmod proxy_http ssl headers alias include negotiation`
   * `a2ensite idp.example.org-ssl.conf`
   * `a2ensite idp.example.org.conf`
   * `a2dissite 000-default.conf`
   * `systemctl restart apache2.service`

5. Verify the strength of your IdP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)

6. **OPTIONAL STEPS**:
   If you want to host your IdP's Information/Privacy pages on the IdP itself, follow the next steps:
  
   1. Create all needed files with:
      * `vim /var/www/html/idp.example.org/info_page.html`

         ```bash
         <html>
            <head><title>Information Page</title></head>
            <body>
               <h1>Put here IdP Information page content</h1>
            </body>
         </html>
         ```

      * `vim /var/www/html/idp.example.org/privacy_page.html`

         ```bash
         <html>
            <head><title>Privacy Page</title></head>
            <body>
               <h1>Put here IdP Privacy page content</h1>
            </body>
         </html>
         ```

      * `touch /var/www/html/idp.example.org/logo80x60.png`

      * `touch /var/www/html/idp.example.org/favicon16x16.png`

   2. Replace them with the correct content.

### Configure Jetty

1. Become ROOT: 
   * `sudo su -`

2. Configure IdP Context Descriptor
   * `mkdir /opt/jetty/webapps`
   * `vim /opt/jetty/webapps/idp.xml`

     ```bash
     <Configure class="org.eclipse.jetty.webapp.WebAppContext">
       <Set name="war"><SystemProperty name="idp.home"/>/war/idp.war</Set>
       <Set name="contextPath">/idp</Set>
       <Set name="extractWAR">false</Set>
       <Set name="copyWebDir">false</Set>
       <Set name="copyWebInf">true</Set>
     </Configure>
     ```

3. Restart Jetty:
   * `systemctl restart jetty`

4. Check that IdP metadata is available on:
   * https://idp.example.org/idp/shibboleth

5. Enable IdP Status page for the IdP local IP:
   * `vim /opt/shibboleth-idp/conf/access-control.xml`
     
     ```bash
     <bean id="AccessByIPAddress" parent="shibboleth.IPRangeAccessControl"
		     p:allowedRanges="#{ {'127.0.0.1/32', '::1/128', '192.168.XX.YY/32'} }" />
     ```

7. Restart Jetty:
   * `systemctl restart jetty`

8. Check IdP Status:
   * `export JAVA_HOME=/usr/lib/jvm/default-java`
   * `cd /opt/shibboleth-idp/bin`
   * `./status.sh -u https://idp.example.org/idp`

### Configure Shibboleth Identity Provider StorageRecords (User Consent)

#### Default - Not Recommended

If you don't change anything you will use cookies that can store an extremely small number of records.

#### HTML Local Storage - Recommended

1. Become ROOT: 
   * `sudo su -`

2. Enable HTML Local Storage:
   * `vim /opt/shibboleth-idp/conf/idp.properties`
   
     ```bash
     idp.storage.htmlLocalStorage = true
     ```
3. Restart Jetty to apply changes:
   * `systemctl restart jetty.service`

4. Check that metadata is available on:
   * https://idp.example.org/idp/shibboleth

5. Check IdP Status:
   * `export JAVA_HOME=/usr/lib/jvm/default-java`
   * `cd /opt/shibboleth-idp/bin`
   * `./status.sh -u https://idp.example.org/idp`

#### JPA Storage Service - using a database

1. Become ROOT: 
   * `sudo su -`

2. Rebuild IdP with the needed libraries:

   * `apt install mysql-server libmysql-java libcommons-dbcp-java libcommons-pool-java --no-install-recommends`

   * `cd /opt/shibboleth-idp`

   * `ln -s /usr/share/java/mysql-connector-java.jar edit-webapp/WEB-INF/lib`

   * `ln -s /usr/share/java/commons-dbcp.jar edit-webapp/WEB-INF/lib`

   * `ln -s /usr/share/java/commons-pool.jar edit-webapp/WEB-INF/lib`

   * `bin/build.sh`

3. Create `StorageRegords` table on `shibboleth` database.

   * `vim shib-ss-db.sql`:

     ```bash
     SET NAMES 'utf8';

     SET CHARACTER SET utf8;

     CREATE DATABASE IF NOT EXISTS storageservice CHARACTER SET=utf8;

     GRANT ALL PRIVILEGES ON storageservice.* TO root@localhost IDENTIFIED BY '##ROOT-DB-PASSWORD-CHANGEME##';
     GRANT ALL PRIVILEGES ON storageservice.* TO ##USERNAME-CHANGEME##@localhost IDENTIFIED BY '##USER-PASSWORD-CHANGEME##';

     FLUSH PRIVILEGES;

     USE storageservice;

     CREATE TABLE IF NOT EXISTS StorageRecords
     (
     context VARCHAR(255) NOT NULL,
     id VARCHAR(255) NOT NULL,
     expires BIGINT(20) DEFAULT NULL,
     value LONGTEXT NOT NULL,
     version BIGINT(20) NOT NULL,
     PRIMARY KEY (context, id)
     );

     quit
     ```

   * `mysql -u root -p < shib-ss-db.sql`

   * `systemctl restart mysql`

4. Enable JPA Storage Service:

   * `vim /opt/shibboleth-idp/conf/global.xml` and add this piece of code to the tail (before **`</beans>`** tag):

     ```bash
     <!-- Add bean to store info on StorageRecords database -->

     <bean id="storageservice.JPAStorageService" class="org.opensaml.storage.impl.JPAStorageService"
           p:cleanupInterval="%{idp.storage.cleanupInterval:PT10M}"
           c:factory-ref="storageservice.JPAStorageService.entityManagerFactory"/>

     <bean id="storageservice.JPAStorageService.entityManagerFactory"
           class="org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean">
           <property name="packagesToScan" value="org.opensaml.storage.impl"/>
           <property name="dataSource" ref="storageservice.JPAStorageService.DataSource"/>
           <property name="jpaVendorAdapter" ref="storageservice.JPAStorageService.JPAVendorAdapter"/>
           <property name="jpaDialect">
             <bean class="org.springframework.orm.jpa.vendor.HibernateJpaDialect" />
           </property>
     </bean>

     <bean id="storageservice.JPAStorageService.DataSource"
           class="org.apache.commons.dbcp.BasicDataSource" destroy-method="close" lazy-init="true"
           p:driverClassName="com.mysql.jdbc.Driver"
           p:url="jdbc:mysql://localhost:3306/storageservice?autoReconnect=true"
           p:username="##USERNAME-CHANGEME##"
           p:password="##USER-PASSWORD-CHANGEME##"
           p:maxActive="10"
           p:maxIdle="5"
           p:maxWait="15000"
           p:testOnBorrow="true"
           p:validationQuery="select 1"
           p:validationQueryTimeout="5" />

     <bean id="storageservice.JPAStorageService.JPAVendorAdapter" class="org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter">
         <property name="database" value="MYSQL" />
     </bean>
     ```
     (and modify the "**##USERNAME-CHANGEME##**" and "**##USER-PASSWORD-CHANGEME##**" for your "**storageservice**" DB)

5. Modify the IdP properties properly:
   * `vim /opt/shibboleth-idp/conf/idp.properties`

     ```xml
     idp.consent.StorageService = storageservice.JPAStorageService
     ```
  
     (This will indicate to IdP to store the data collected by User Consent into the "**StorageRecords**" table)

6. Restart Jetty to apply changes:
   * `systemctl restart jetty.service`

7. Check that metadata is available on:
   * https://idp.example.org/idp/shibboleth

8. Check IdP Status:
   * `export JAVA_HOME=/usr/lib/jvm/default-java`
   * `cd /opt/shibboleth-idp/bin`
   * `./status.sh -u https://idp.example.org/idp`

### Configure Shibboleth Identity Provider to release the persistent-id

#### Computed mode - Default & Recommended

1. Become ROOT: 
   * `sudo su -`

2. Enable the generation of the computed `persistent-id` (this replace the deprecated attribute *eduPersonTargetedID*) with:
   * `vim /opt/shibboleth-idp/conf/saml-nameid.properties`
     (the *sourceAttribute* MUST BE an attribute, or a list of comma-separated attributes, that uniquely identify the subject of the generated `persistent-id`. It MUST BE: **Stable**, **Permanent** and **Not-reassignable**)

     ```xml
     idp.persistentId.sourceAttribute = uid
     ...
     idp.persistentId.salt = ### result of 'openssl rand -base64 36'###
     ```

   * `vim /opt/shibboleth-idp/conf/saml-nameid.xml`
     * Remove the comment for the line:

       ```xml
       <ref bean="shibboleth.SAML2PersistentGenerator" />
       ```

   * `vim /opt/shibboleth-idp/conf/c14n/subject-c14n.xml`
     * Remove the comment to the bean called "**c14n/SAML2Persistent**".

3. Restart Jetty:
   * `systemctl restart jetty.service`

4. Check that metadata is available on:
   * https://idp.example.org/idp/shibboleth

5. Check IdP Status:
   * `export JAVA_HOME=/usr/lib/jvm/default-java`
   * `cd /opt/shibboleth-idp/bin`
   * `./status.sh -u https://idp.example.org/idp`

#### Stored mode

1. Become ROOT: 
   * `sudo su -`

2. Rebuild IdP with the needed libraries:

   * `apt install mysql-server libmysql-java libcommons-dbcp-java libcommons-pool-java --no-install-recommends`

   * `cd /opt/shibboleth-idp`

   * `ln -s /usr/share/java/mysql-connector-java.jar edit-webapp/WEB-INF/lib`

   * `ln -s /usr/share/java/commons-dbcp.jar edit-webapp/WEB-INF/lib`

   * `ln -s /usr/share/java/commons-pool.jar edit-webapp/WEB-INF/lib`

   * `bin/build.sh`

3. Create `shibpid` table on `shibboleth` database.

   * `vim shib-pid-db.sql`:

     ```bash
     SET NAMES 'utf8';

     SET CHARACTER SET utf8;

     CREATE DATABASE IF NOT EXISTS shibboleth CHARACTER SET=utf8;

     GRANT ALL PRIVILEGES ON shibboleth.* TO root@localhost IDENTIFIED BY '##ROOT-DB-PASSWORD-CHANGEME##';
     GRANT ALL PRIVILEGES ON shibboleth.* TO ##USERNAME-CHANGEME##@localhost IDENTIFIED BY '##USER-PASSWORD-CHANGEME##';

     FLUSH PRIVILEGES;

     USE shibboleth;

     CREATE TABLE IF NOT EXISTS shibpid
     (
     localEntity VARCHAR(1024) NOT NULL,
     peerEntity VARCHAR(1024) NOT NULL,
     persistentId VARCHAR(50) NOT NULL,
     principalName VARCHAR(255) NOT NULL,
     localId VARCHAR(255) NOT NULL,
     peerProvidedId VARCHAR(255) NULL,
     creationDate TIMESTAMP NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
     deactivationDate TIMESTAMP NULL default NULL,
     PRIMARY KEY (localEntity(255), peerEntity(255), persistentId(50))
     );

     quit
     ```

   * `mysql -u root -p < shib-pid-db.sql`

   * `systemctl restart mysql`

4. Enable Persistent Identifier's store:

   * `vim /opt/shibboleth-idp/conf/global.xml` and add this piece of code to the tail (before **`</beans>`** tag):

     ```bash
     <!-- Add bean to store persistent-id on shibboleth database -->

     <bean id="shibboleth.JPAStorageService.DataSource"
           class="org.apache.commons.dbcp.BasicDataSource" destroy-method="close" lazy-init="true"
           p:driverClassName="com.mysql.jdbc.Driver"
           p:url="jdbc:mysql://localhost:3306/shibboleth?autoReconnect=true"
           p:username="##USERNAME-CHANGEME##"
           p:password="##USER-PASSWORD-CHANGEME##"
           p:maxActive="10"
           p:maxIdle="5"
           p:maxWait="15000"
           p:testOnBorrow="true"
           p:validationQuery="select 1"
           p:validationQueryTimeout="5" />
     ```
     (and modify the "**##USERNAME-CHANGEME##**" and "**##USER-PASSWORD-CHANGEME##**" for your "**shibboleth**" DB)

5. Enable the generation of the `persistent-id` (this replace the deprecated attribute *eduPersonTargetedID*)
   * `vim /opt/shibboleth-idp/conf/saml-nameid.properties`
     (the *sourceAttribute* MUST BE an attribute, or a list of comma-separated attributes, that uniquely identify the subject of the generated `persistent-id`. It MUST BE: **Stable**, **Permanent** and **Not-reassignable**)

     ```xml
     idp.persistentId.sourceAttribute = uid
     ...
     idp.persistentId.salt = ### result of 'openssl rand -base64 36'###
     ...
     idp.persistentId.generator = shibboleth.StoredPersistentIdGenerator
     ...
     idp.persistentId.dataSource = shibboleth.JPAStorageService.DataSource
     ```

   * Enable the **SAML2PersistentGenerator**:
     * `vim /opt/shibboleth-idp/conf/saml-nameid.xml`
       * Remove the comment from the line containing:

         ```xml
         <ref bean="shibboleth.SAML2PersistentGenerator" />
         ```

     * `vim /opt/shibboleth-idp/conf/c14n/subject-c14n.xml`
       * Remove the comment to the bean called "**c14n/SAML2Persistent**".

6. Restart Jetty to apply changes:
   * `systemctl restart jetty.service`

7. Check that metadata is available on:
   * https://idp.example.org/idp/shibboleth

8. Check IdP Status:
   * `export JAVA_HOME=/usr/lib/jvm/default-java`
   * `cd /opt/shibboleth-idp/bin`
   * `./status.sh -u https://idp.example.org/idp`

### Configure Logout

1. Become ROOT: 
   * `sudo su -`

2. Enable Shibboleth Logout:
   * `vim /opt/shibboleth-idp/conf/idp.properties`
   
     ```bash
     idp.session.trackSPSessions = true
     idp.session.secondaryServiceIndex = true
     ```

3. Restart Jetty to apply changes:
   * `systemctl restart jetty.service`

4. Check that metadata is available on:
   * https://idp.example.org/idp/shibboleth

5. Check IdP Status:
   * `export JAVA_HOME=/usr/lib/jvm/default-java`
   * `cd /opt/shibboleth-idp/bin`
   * `./status.sh -u https://idp.example.org/idp`

### Configure the Directory (openLDAP) Connection

1. Connect the openLDAP to the IdP to allow the authentication of the users:
   * `vim /opt/shibboleth-idp/conf/ldap.properties`

     (with **TLS** solutions we consider to have the LDAP certificate into `/opt/shibboleth-idp/credentials`).

     * Solution 1: LDAP + STARTTLS

       ```xml
       idp.authn.LDAP.authenticator = bindSearchAuthenticator
       idp.authn.LDAP.ldapURL = ldap://ldap.example.org:389
       idp.authn.LDAP.useStartTLS = true
       idp.authn.LDAP.useSSL = false
       idp.authn.LDAP.sslConfig = certificateTrust
       idp.authn.LDAP.trustCertificates = %{idp.home}/credentials/ldap-server.crt
       idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemainig
       idp.authn.LDAP.baseDN = ou=people,dc=example,dc=org
       idp.authn.LDAP.userFilter = (uid={user})
       idp.authn.LDAP.bindDN = uid=idpuser,ou=system,dc=example,dc=org
       idp.authn.LDAP.bindDNCredential = ###LDAP_ADMIN_PASSWORD###
       ```

     * Solution 2: LDAP + TLS

       ```xml
       idp.authn.LDAP.authenticator = bindSearchAuthenticator
       idp.authn.LDAP.ldapURL = ldaps://ldap.example.org:636
       idp.authn.LDAP.useStartTLS = false
       idp.authn.LDAP.useSSL = true
       idp.authn.LDAP.sslConfig = certificateTrust
       idp.authn.LDAP.trustCertificates = %{idp.home}/credentials/ldap-server.crt
       idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemainig
       idp.authn.LDAP.baseDN = ou=people,dc=example,dc=org
       idp.authn.LDAP.userFilter = (uid={user})
       idp.authn.LDAP.bindDN = uid=idpuser,ou=system,dc=example,dc=org
       idp.authn.LDAP.bindDNCredential = ###LDAP_ADMIN_PASSWORD###
       ```

     * Solution 3: plain LDAP

       ```xml
       idp.authn.LDAP.authenticator = bindSearchAuthenticator
       idp.authn.LDAP.ldapURL = ldap://ldap.example.org:389
       idp.authn.LDAP.useStartTLS = false
       idp.authn.LDAP.useSSL = false
       idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemainig
       idp.authn.LDAP.baseDN = ou=people,dc=example,dc=org
       idp.authn.LDAP.userFilter = (uid={user})
       idp.authn.LDAP.bindDN = uid=idpuser,ou=system,dc=example,dc=org
       idp.authn.LDAP.bindDNCredential = ###LDAP_ADMIN_PASSWORD###
       ```
       (If you decide to use the Solution 3, you have to remove (or comment out) the following code from your Attribute Resolver file:
      
       ```xml
       Line 1:  useStartTLS="%{idp.attribute.resolver.LDAP.useStartTLS:true}"
       Line 2:  trustFile="%{idp.attribute.resolver.LDAP.trustCertificates}"
       ```

       **UTILITY FOR OPENLDAP ADMINISTRATOR:**
         * `ldapsearch -H ldap:// -x -b "dc=example,dc=it" -LLL dn`
           * the baseDN ==> `ou=people, dc=example,dc=org` (branch containing the registered users)
           * the bindDN ==> `cn=admin,dc=example,dc=org` (distinguished name for the user that can made queries on the LDAP)

2. Configure your "attribute-resolver.xml" to define and support attributes:
   * `cd /opt/shibboleth-idp/conf`
   
   * `cp attribute-resolver.xml attribute-resolver.xml.orig`

   * `cp attribute-resolver-full.xml attribute-resolver.xml`

   * `vim attribute-resolver.xml`
     * Remove comment for all schemas supported by your OpenLDAP
     * Remove comment for the Example LDAP Connector
     * Save

     Here you can find the **attribute-resolver-v3_4-idem.xml** provided by IDEM GARR AAI as example:
       * Download the attribute resolver provided by IDEM GARR AAI:
         `wget http://www.garr.it/idem-conf/attribute-resolver-v3_4-idem.xml -O /opt/shibboleth-idp/conf/attribute-resolver-v3_4-idem.xml`
	 
     **Pay attention on `<DataConnector id="myStoredId"`. You have to put the right bean ID into `<BeanManagedConnection>` or IdP will not work. You have to put there the ID of the `BasicDataSource` bean**

3. Restart Jetty to apply changes:
   * `systemctl restart jetty.service`

4. Check to be able to retrieve user's info:
   * `export JAVA_HOME=/usr/lib/jvm/default-java`
   * `cd /opt/shibboleth-idp/bin`
   * `./aacli.sh -n user1 -r https://sp24-test.garr.it/shibboleth --saml2 -u https://idp.example.org/idp`

5. Check IdP Status:
   * `export JAVA_HOME=/usr/lib/jvm/default-java`
   * `cd /opt/shibboleth-idp/bin`
   * `./status.sh -u https://idp.example.org/idp`

### Configure IdP Logging

Enrich IDP logs with the authentication error occurred on LDAP:
   * sed -i '/^    <logger name="org.ldaptive".*/a \\n    <!-- Logs on LDAP user authentication - ADDED -->' /opt/shibboleth-idp/conf/logback.xml
   * sed -i '/^    <!-- Logs on LDAP user authentication - ADDED -->/a \ \ \ \ \<logger name="org.ldaptive.auth.Authenticator" level="INFO" />' /opt/shibboleth-idp/conf/logback.xml

### Translate IdP messages into preferred language

Translate the IdP messages in your language:
   * Get the files translated in your language from [Shibboleth page](https://wiki.shibboleth.net/confluence/display/IDP30/MessagesTranslation)
   * Put 'messages_XX.properties' downloaded file into `/opt/shibboleth-idp/messages` directory
   * Restart Jetty to apply changes: 
      `systemctl restart jetty.service`

### Disable SAML1 Deprecated Protocol

1. Modify IdP metadata to enable only the SAML2 protocol:
   * `vim /opt/shibboleth-idp/metadata/idp-metadata.xml`

      ```bash
      <IDPSSODescriptor> SECTION:
        - From the list of "protocolSupportEnumeration" remove:
          - urn:oasis:names:tc:SAML:1.1:protocol
          - urn:mace:shibboleth:1.0

        - Remove the endpoint:
          <ArtifactResolutionService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/ArtifactResolution" index="1"/>
          (and modify the index value of the next one to “1”)

        - Before the </IDPSSODescriptor> add:
          <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</NameIDFormat>
          <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</NameIDFormat>

          (because the IdP installed with this guide will release transient, by default, and persistent SAML NameIDs)

        - Remove the endpoint: 
          <SingleSignOnService Binding="urn:mace:shibboleth:1.0:profiles:AuthnRequest" Location="https://idp.example.org/idp/profile/Shibboleth/SSO"/>

        - Remove all ":8443" from the existing URL (such port is not used anymore)

      <AttributeAuthorityDescriptor> Section:
        - From the list "protocolSupportEnumeration" replace the value of:
          - urn:oasis:names:tc:SAML:1.1:protocol
          with
          - urn:oasis:names:tc:SAML:2.0:protocol

        - Remove the endpoint: 
          <AttributeService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/AttributeQuery"/>

        - Remove the comment from:
          <AttributeService Binding="urn:oasis:names:tc:SAML:2.0:bindings:SOAP" Location="https://idp.example.org/idp/profile/SAML2/SOAP/AttributeQuery"/>

        - Remove all ":8443" from the existing URL (such port is not used anymore)
      ```

2. Restart Jetty to apply changes: 
   * `systemctl restart jetty.service`

3. Obtain your IdP metadata on:
   *  `https://idp.example.org/idp/shibboleth`

### Register the IdP on the Federation

1. Register you IdP metdata on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):
   * `https://registry.idem.garr.it/`

2. Configure the IdP to retrieve the Federation Metadata:
   * `cd /opt/shibboleth-idp/conf`
   * `vim metadata-providers.xml`

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
     *  `wget https://md.idem.garr.it/certs/idem-signer-20220121.pem -O /opt/shibboleth-idp/metadata/federation-cert.pem`

   * Check the validity:
     *  `cd /opt/shibboleth-idp/metadata`
     *  `openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout`
       
        (sha1: D1:68:6C:32:A4:E3:D4:FE:47:17:58:E7:15:FC:77:A8:44:D8:40:4D)
     *  `openssl x509 -in federation-cert.pem -fingerprint -md5 -noout`

        (md5: 48:3B:EE:27:0C:88:5D:A3:E7:0B:7C:74:9D:24:24:E0)
  
3. Reload service with id `shibboleth.MetadataResolverService` to retrieve the Federation Metadata:
    *  `cd /opt/shibboleth-idp/bin`
    *  `./reload-service.sh -id shibboleth.MetadataResolverService -u https://idp.example.org/idp`

4. The day after the IDEM Federation Operators approval your entity on IDEM Entity Registry, check if you can login with your IdP on the following services:
    * https://sp-test.garr.it/secure   (Service Provider provided for testing the IDEM Test Federation)
    * https://sp24-test.garr.it/secure (Service Provider provided for testing the IDEM Test Federation and IDEM Production Federation)

    or check which attributes are released to them with AACLI:

    * `cd /opt/shibboleth-idp/bin`
    * `./aacli.sh -n user1 -r https://sp24-test.garr.it/shibboleth --saml2 -u https://idp.example.org/idp`


### Configure Attribute Filters to release the mandatory attributes to the IDEM Default Resources:

1. Become ROOT:
   * `sudo su -`

2. Make sure to you have "`tmp/httpClientCache`" used by "`shibboleth.FileCachingHttpClient`":
   * `mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown jetty /opt/shibboleth-idp/tmp/httpClientCache`

3. Modify your `services.xml`:
   * `vim /opt/shibboleth-idp/conf/services.xml`

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

4. Restart Jetty to apply changes:
   *  `systemctl restart jetty.service`

### Configure Attribute Filters to release the mandatory attributes to the IDEM Production Resources:

1. Make sure that you have the "`tmp/httpClientCache`" used by "`shibboleth.FileCachingHttpClient`":
   * `mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown jetty /opt/shibboleth-idp/tmp/httpClientCache`

2. Modify your `services.xml`:
   * `vim /opt/shibboleth-idp/conf/services.xml`

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

3. Restart Jetty to apply changes:
   *  `systemctl restart jetty.service`

### Configure Attribute Filters for Research and Scholarship and Data Protection Code of Conduct Entity Category

1. Make sure that you have the "`tmp/httpClientCache`" used by "`shibboleth.FileCachingHttpClient`":
   * `mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown jetty /opt/shibboleth-idp/tmp/httpClientCache`

2. Modify your `services.xml`:
   * `vim /opt/shibboleth-idp/conf/services.xml`

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

3. Restart Jetty to apply changes:
   *  `systemctl restart jetty.service`

### Appendix A: Import metadata from previous IDP v2.x ###

1. Store into /tmp directory the following files:
   * `idp-metadata.xml`
   * `idp.crt`
   * `idp.key`

2. Follow the steps on your IdP v3.x:
   * `sudo su -`
   * `mv /tmp/idp-metadata.xml /opt/shibboleth-idp/metadata`
   * `mv /tmp/idp.crt /tmp/idp.key /opt/shibboleth-idp/credentials`
   * `cd /opt/shibboleth-idp/credentials/`
   * `rm idp-encryption.crt idp-backchannel.crt idp-encryption.key idp-signing.crt idp-signing.key`
   * `ln -s idp.crt idp-encryption.crt`
   * `ln -s idp.key idp-encryption.key`
   * `ln -s idp.key idp-signing.key`
   * `ln -s idp.crt idp-signing.crt`
   * `ln -s idp.crt idp-backchannel.crt`
   * `openssl pkcs12 -export -in idp-encryption.crt -inkey idp-encryption.key -out idp-backchannel.p12 -password pass:#YOUR.BACKCHANNEL.CERT.PASSWORD#`

3. Check that *idp.entityID* property value on *idp.properties* file is equal to the previous entityID value into *idp-metadata.xml*.

4. Modify IdP metadata to enable only the SAML2 protocol:
   * `vim /opt/shibboleth-idp/metadata/idp-metadata.xml`
 
      ```bash
      <IDPSSODescriptor> SECTION:
        – From the list of "protocolSupportEnumeration" remove:
          - urn:oasis:names:tc:SAML:1.1:protocol
          - urn:mace:shibboleth:1.0

        – Remove the endpoint:
          <ArtifactResolutionService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/ArtifactResolution" index="1"/>
          (and modify the index value of the next one to “1”)

        – Before the </IDPSSODescriptor> add:
          <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</NameIDFormat>
          <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</NameIDFormat>

          (because the IdP installed with this guide will release transient, by default, and persistent SAML NameIDs)

        - Remove the endpoint: 
          <SingleSignOnService Binding="urn:mace:shibboleth:1.0:profiles:AuthnRequest" Location="https://idp.example.org/idp/profile/Shibboleth/SSO"/>
       
        - Remove all ":8443" from the existing URL (such port is not used anymore)

      <AttributeAuthorityDescriptor> Section:
        - From the list "protocolSupportEnumeration" replace the value of:
          - urn:oasis:names:tc:SAML:1.1:protocol
          with
          - urn:oasis:names:tc:SAML:2.0:protocol

        - Remove the endpoint: 
          <AttributeService Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAP-binding" Location="https://idp.example.org:8443/idp/profile/SAML1/SOAP/AttributeQuery"/>

        - Remove the comment from:
          <AttributeService Binding="urn:oasis:names:tc:SAML:2.0:bindings:SOAP" Location="https://idp.example.org/idp/profile/SAML2/SOAP/AttributeQuery"/>

        - Remove all ":8443" from the existing URL (such port is not used anymore)
      ```

5. Restart Jetty:
   * `systemctl restart jetty.service`
  
6. Don't forget to update your IdP Metadata on [IDEM Entity Registry](https://registry.idem.garr.it/rr3) to apply changes on the federation IDEM! For any help write to idem-help@garr.it

### Appendix B: Import persistent-id from a previous database ###

1. Become ROOT:
   * `sudo su -`

2. Create a DUMP of `shibpid` table from the previous DB `userdb` on the OLD IdP:
   * `cd /tmp`
   * `mysqldump --complete-insert --no-create-db --no-create-info -u root -p userdb shibpid > /tmp/userdb_shibpid.sql`

3. Move the `/tmp/userdb_shibpid.sql` of old IdP into `/tmp/userdb_shibpid.sql` on the new IdP.
 
4. Import the content of `/tmp/userdb_shibpid.sql` into the DB of the new IDP:
   * `cd /tmp ; mysql -u root -p shibboleth < /tmp/userdb_shibpid.sql`

5. Delete `/tmp/userdb_shibpid.sql`:
   * `rm /tmp/userdb_shibpid.sql`

### Appendix C: Useful logs to find problems

1. Jetty Logs:
   * `cd /opt/jetty/logs`
   * `ls -l *.stderrout.log`

2. Shibboleth IdP Logs:
   * `cd /opt/shibboleth-idp/logs`
   * **Audit Log:** `vim idp-audit.log`
   * **Consent Log:** `vim idp-consent-audit.log`
   * **Warn Log:** `vim idp-warn.log`
   * **Process Log:** `vim idp-process.log`

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
