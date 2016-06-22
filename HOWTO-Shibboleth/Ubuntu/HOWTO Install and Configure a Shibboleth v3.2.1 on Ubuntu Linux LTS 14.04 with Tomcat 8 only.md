# HOWTO Install and Configure a Shibboleth IdP v3.2.1 on Ubuntu Linux LTS 14.04 with Tomcat 8 only

## Table of Contents

1. [Requirements Hardware](#requirements-hardware)
2. [Requirements Software](#requirements-software)
3. [Other Requirements](#other-requirements)
4. [Installation Instructions](#installation-instructions)
  1. [Install software requirements](#install-software-requirements)
  2. [Install Shibboleth Identity Provider v3.2.1](#install-shibboleth-identity-provider-v321)
5. [Configuration Instructions](#configuration-instructions)
  1. [Configure Apache Tomcat 8](#configure-apache-tomcat-8)
  2. [Configure Shibboleth Identity Provider v3.2.1 to release the persistent-id (Stored Mode)](#configure-shibboleth-identity-provider-v321-to-release-the-persistent-id-stored-mode)
  3. [Configure Attribute Filter for Research and Scholarship Entity Category](#configure-attribute-filter-for-research-and-scholarship-entity-category)


## Requirements Hardware

 * CPU: 2 Core
 * RAM: 4 GB
 * HDD: 20 GB

## Requirements Software

 * ca-certificates
 * ntp
 * openSSL >= 1.0.2
 * oracle-java8-installer 
 * oracle-java8-unlimited-jce-policy
 * Tomcat 8
 * Shibboleth Identity Provider

## Other Requirements

 * Place the HTTPS Server Certificate and the HTTTPS Server Key into the ```/tmp``` directory

## Installation Instructions

### Install software requirements

0. Become ROOT of the machine: 
  * ```sudo su -```

1. Install GIT and retrieve this repository: 
  * ```apt-get install git```
  * ```git clone https://github.com/malavolti/HOWTO-Install-and-Configure-Shibboleth-Identity-Provider.git /usr/local/src/HOWTO-Shib-IdP```

2. Install the packages required: 
  * ```apt-get install vim ntp```

3. Install Sun Java 8 Oracle:
  * ```apt-get install python-software-properties```
  * ```add-apt-repository ppa:webupd8team/java```
  * ```apt-get update```
  * ```apt-get install oracle-java8-installer oracle-java8-unlimited-jce-policy```

4. Configure the Sun Java Oracle:
  * ```update-alternatives --config java``` (copy the path without the ```/bin/java``` part)
  * ```update-alternatives --config javac```
  * ```vim /etc/environment```

5. Modify the machine environment: 
  * ``` vim /etc/environment ```

    ```
    JAVA_HOME=##PATH_COPIED##
    CATALINA_HOME=/opt/tomcat
    ```

6. Applied changes:
  * ```source /etc/environment```

7. Verify the changes applied:
  ```bash
  echo "JAVA_HOME="$JAVA_HOME ; echo "CATALINA_HOME="$CATALINA_HOME
  ```

8. Install openSSL >= 1.0.2:
  * ```apt-get install make ant gcc libapr1-dev libssl-dev```
  * ```cd /usr/local/src```
  * ```wget https://www.openssl.org/source/openssl-1.0.2g.tar.gz```
  * ```tar -xvzf openssl-1.0.2g.tar.gz```
  * ```cd openssl-1.0.2g/```
  * ```./config --prefix=/usr/```
  * ```make depend```
  * ```make && make install```
  * ```openssl version``` (useful to verify the installation)

9. Install Apache APR (Apache Portable Runtime):
  * ```cd /usr/local/src```
  * ```wget http://mirror.nohup.it/apache//apr/apr-1.5.2.tar.gz```
  * ```tar -xvzf apr-1.5.2.tar.gz```
  * ```cd apr-1.5.2 ; vim configure```
  * change the line **30206** by replace the value of ```$RM "$cfgfile"``` with ```"$RM" -f "$cfgfile"```
  * ```./configure```
  * ```make```
  * ```make test```
  * ```make install```

  The library APR will be installed into ```/usr/local/apr/lib``` directory

10. Install Apache Tomcat 8:
  * ```cd /usr/local/src/```
  * ```wget http://apache.panu.it/tomcat/tomcat-8/v8.0.33/bin/apache-tomcat-8.0.33.tar.gz```
  * ```mkdir /opt/tomcat```
  * ```tar xvf apache-tomcat-8*tar.gz -C /opt/tomcat --strip-components=1```
  * ```groupadd tomcat```
  * ```useradd -s /bin/false -g tomcat -d /opt/tomcat tomcat```
  * ```cd /opt/tomcat```
  * ```chgrp -R tomcat conf```
  * ```chmod g+rwx conf```
  * ```chmod g+r conf/*```

11. Create the init.d service for restarting Tomcat 8:
  * ```vim /etc/init.d/tomcat``` (and paste the content of the [daemon-tomcat](../blob/master/daemon-tomcat) file)
  * ```cd /usr/local/src```
  * ```chmod 755 /etc/init.d/tomcat```
  * ```update-rc.d tomcat defaults```
  * ```service tomcat start```

12. Ensure that your firewall/firewalls are not blocking the traffic on the port **443** and **8080**:

13. Open the Tomcat 8 Home Page (fix the URL before open on your browser):
  * ```http://idp.example.garr.it:8080``` and verify to see the Tomcat 8 Home Page

14. Move the HTTPS Certificate and Key to a new directory ```/opt/tomcat/ssl```:
  * ```mkdir /opt/tomcat/ssl```
  * ```mv /tmp/cert-server.pem /opt/tomcat/ssl/```
  * ```mv /tmp/key-server.pem /opt/tomcat/ssl/```
  * ```chmod 400 /opt/tomcat/ssl/key-server.pem```

15. Install the Tomcat Native:
  * ```cd /usr/local/src```
  * ```wget http://apache.panu.it/tomcat/tomcatconnectors/native/1.2.5/source/tomcat-native-1.2.5-src.tar.gz```
  * ```tar -xvzf tomcat-native-*-src.tar.gz```
  * ```cd /usr/local/src/tomcat-native-*-src/```
  * ```ant```
  * ```cd /usr/local/src/tomcat-native-*-src/native```
  * ```./configure --with-apr=/usr/local/apr --with-javahome=/usr/lib/jvm/java-8-oracle --with-ssl=yes --prefix=/opt/tomcat```
  * ```make && make install```

16. Create Tomcat 8 environment: 
  * ```touch /opt/tomcat/bin/setenv.sh ; vim touch /opt/tomcat/bin/setenv.sh```

    ```bash
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/apr/lib"
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/tomcat/lib"
    ```
    
  * ```service tomcat restart```

17. Enable the port **443** for the HTTPS by changing the **8443** connector into this one:
  * ```vim $CATALINA_HOME/conf/server.xml```

    ```xml
    ...
    <!-- Define a SSL/TLS HTTP/1.1 Connector on port 443
    This connector uses the NIO implementation that requires the JSSE
    style configuration. When using the APR/native implementation, the
    OpenSSL style configuration is required as described in the APR/native
    documentation -->
    <Connector
        protocol="org.apache.coyote.http11.Http11AprProtocol"
        port="443" maxThreads="200" maxPostSize="100000"
        scheme="https" secure="true" SSLEnabled="true"
        SSLCertificateFile="/opt/tomcat/ssl/cert-server.pem"
        SSLCertificateKeyFile="/opt/tomcat/ssl/key-server.pem"
        SSLVerifyClient="optional" SSLProtocol="TLSv1+TLSv1.1+TLSv1.2"/>
    ...
    ```

  * ```service tomcat restart```

18. Manage Tomcat with its GUI:

  * ```sudo su -```

  * ```vim $CATALINA_HOME/conf/tomcat-users.xml```
    ```xml
    <tomcat-users>
      ...
      <role rolename="manager-gui"/>
      <role rolename="admin-gui"/>
      <user username="admin" password="**password_administrator**" roles="admin-gui,manager-gui"/>
      <user username="manager" password="**password_manager**" roles="manager-gui"/>
    </tomcat-users>
    ```

  * Try to login on: https://idp.example.it/manager/html with the user "**manager**" and remove all default applications deployed and not directly involved with the IdP to improve the speed of Tomcat loading.

### Install Shibboleth Identity Provider v3.2.1

1. Become ROOT:
  * ```sudo su -```

2. Download the Shibboleth Identity Provider v3.2.1 package into ```/usr/local/src``` directory:
  * ```cd /usr/local/src```
  * ```wget http://shibboleth.net/downloads/identity-provider/latest/shibboleth-identity-provider-3.2.1.tar.gz```
  * ```tar -xzvf shibboleth-identity-provider-3.2.1.tar.gz```
  * ```cd shibboleth-identity-provider-3.2.1```

3. Install Shibboleth Identity Provider:

  * ```./bin/install.sh```
      ```bash
      root@idp:/usr/local/src/shibboleth-identity-provider-3.2.1# ./bin/install.sh
      Source (Distribution) Directory: [/usr/local/src/shibboleth-identity-provider-3.2.1]
      Installation Directory: [/opt/shibboleth-idp]

      Hostname: [localhost.localdomain]
      idp.example.it

      SAML EntityID: [https://idp.example.it/idp/shibboleth]
      Attribute Scope: [localdomain]
      example.it

      Backchannel PKCS12 Password: ###PASSWORD-FOR-BACKCHANNEL###
      Re-enter password:           ###PASSWORD-FOR-BACKCHANNEL###
      Cookie Encryption Key Password: ###PASSWORD-FOR-COOKIE-ENCRYPTION###
      Re-enter password:              ###PASSWORD-FOR-COOKIE-ENCRYPTION###
      ```
      (from now "**{idp.home}**" == ```/opt/shibboleth-idp/```)
  
4. Import JST library useful for IdP Status page:
  * ```cd /opt/shibboleth-idp/edit-webapp/WEB-INF/lib```
  * ```wget https://build.shibboleth.net/nexus/service/local/repositories/thirdparty/content/javax/servlet/jstl/1.2/jstl-1.2.jar```
  * ```cd /opt/shibboleth-idp/bin```
  * ```./build.sh -Didp.target.dir=/opt/shibboleth-idp```
 
5. (OPTIONAL) Enable the IdP Status Web page:
  * ```vim /opt/shibboleth-idp/conf/access-control.xml```

    ```xml
    <util:map id="shibboleth.AccessControlPolicies">
      <entry key="AccessByIPAddress">
        <bean parent="shibboleth.IPRangeAccessControl" p:allowedRanges="#{ {'127.0.0.1/32', '::1/128', 'my.idp.ip.address/24'} }" />
      </entry>
    </util:map>
    ```
  
6. Give the access to the tomcat user on some IdP directory:
  * ```chown -R tomcat /opt/shibboleth-idp/logs/```
  * ```chown -R tomcat /opt/shibboleth-idp/metadata/```
  * ```chown -R tomcat /opt/shibboleth-idp/credentials/```
  * ```chown -R tomcat /opt/shibboleth-idp/conf/```

## Configuration Instructions

### Configure Apache Tomcat 8

1. Become ROOT:
  * ```sudo su -```

2. Modify Tomcat ```$CATALINA_HOME/conf/server.xml``` by:
  * Disabling the Connector HTML (port=8080) by commenting out its code
  * Disabling the Connector AJP (port=8009) by commenting out its code

3. Configure Tomcat 8 environment:
  * Add the following line to the new file ```$CATALINA_HOME/bin/setenv.sh```

    ```export JAVA_OPTS="-Djava.awt.headless=true -XX:+DisableExplicitGC -XX:+UseParallelOldGC -Xms256m -Xmx2g -Djava.security.egd=file:/dev/./urandom"```
    
    (This settings configure the memory of the JVM that will host the IdP Web Application. 
    The Memory value depends on the phisical memory installed on the machine. 
    Set the "**Xmx**" (max heap space available to the JVM) at least to **2GB**)

4. Deploy the IdP Web Application on Tomcat 8 web container with a context file:
  * ```vim $CATALINA_HOME/conf/Catalina/localhost/idp.xml```

    ```xml
    <Context docBase="/opt/shibboleth-idp/war/idp.war"
             privileged="true"
             antiResourceLocking="false"
             swallowOutput="true"/>
    ```
    (Avoid to use the **idp.war** without unpack it if you want an improvement of the Tomcat load's time)

5. Modify the ```context.xml``` file to avoid errors on “*lack of persistence of the session objects*” created by the IdP:
  * ```vim $CATALINA_HOME/conf/context.xml``` and remove the comment to```<Manager pathname="" />```

6. Speed Up Tomcat 8 instance:
  * Find JAR that can be not scanned at boot of Tomcat with:
    * ```cd /opt/shibboleth-idp/```
    * ```ls webapp/WEB-INF/lib | awk '{print $1",\\"}'```
    * Add the output list return from the command to ```$CATALINA_HOME/conf/catalina.properties``` at tail of the voice ```tomcat.util.scan.StandardJarScanFilter.jarsToSkip```. **(Pay attention with commas!)**
    * Save the changes and restart tomcat:
      * ```service tomcat restart```

7. Modify your "**hosts**" file:
    * ```vim /etc/hosts```
  
      ```127.0.1.1 idp.example.it idp```

8. Try your IdP:
    1. If **YOU HAVE** followed the optional point 4.ii.5, then open a page like the following on your preferred browser:
      "```https://idp.example.garr.it/idp/status```" and, if you see the status of the IdP, you have installed correctly.

    2. If **YOU DON'T HAVE** followed the optional point 4.ii.5, then open a terminal and run the command 
    "```cd /opt/shibboleth-idp/bin ; ./status.sh```"
    and, if you see the status of the IdP, you have installed correctly.
  
### Configure Shibboleth Identity Provider v3.2.1 to release the persistent-id (Stored mode)

1. Become ROOT:
  * ```sudo su -```

2. Install **MySQL Connector Java** and **Tomcat JDBC** libraries used by Tomcat and Shibboleth for MySQL DB:
  * ```apt-get istall mysql-server libmysql-java```
  * ```cp /usr/share/java/mysql-connector-java.jar /opt/shibboleth-idp/editwebapp/WEB-INF/lib/```
  * ```cp /usr/share/java/mysql-connector-java.jar /usr/share/tomcat8/lib/```
  * ```cp /usr/share/tomcat8/lib/tomcat-jdbc.jar /opt/shibboleth-idp/editwebapp/WEB-INF/lib/```

3. Install the libraries **Common DBCP2**[[2]](http://commons.apache.org/proper/commons-dbcp/) used for generation of saml-id:
  * ```cd /usr/local/src/```
  * ```wget http://mirrors.muzzy.it/apache//commons/dbcp/binaries/commonsdbcp2-2.1.1-bin.tar.gz```
  * ```tar xzvf commons-dbcp2-2.1.1-bin.tar.gz ; cd commons-dbcp2-2.1.1/```
  * ```cp commons-dbcp2-2.1.1.jar /opt/shibboleth-idp/edit-webapp/WEBINF/lib/```
  
4. Install the libraries **Tomcat Common Pool**[[3]](http://commons.apache.org/proper/commons-pool/download_pool.cgi) used for the generation of saml-id:
  * ```cd /usr/local/src/```
  * ```wget http://mirror.nohup.it/apache//commons/pool/binaries/commonspool2-2.4.2-bin.tar.gz```
  * ```tar xzvf commons-pool2-2.4.2-bin.tar.gz ; cd commons-pool2-2.4.2/```
  * ```cp commons-pool2-2.4.2.jar /opt/shibboleth-idp/edit-webapp/WEBINF/lib/```

5. Rebuild the **idp.war** of Shibboleth with the new libraries:
  * ```cd /opt/shibboleth-idp/ ; ./bin/build.sh```

6. Create and prepare the "**shibboleth**" MySQL DB to host the values of the several **persistent-id** and **StorageRecords** to host other useful information about user consent:
  *  ```cd /usr/local/src/HOWTO-Shib-IdP```
  *  Modify the [shibboleth-db.sql](../master/shibboleth-db.sql) by changing the *username* and *password* of the user that has access to the "**shibboleth**" DB.
  *  ```mysql -u root -p##PASSWORD-DB## < ./shibboleth-db.sql```
  *  ```service mysql restart```

7. Enable the generation of the ```persistent-id``` (this replace the deprecated attribute *eduPersonTargetedID*)
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

        * Modify the ***DefaultRelyingParty*** to releasing of the "persistent-id" to all, ever:
          * ```vim /opt/shibboleth-idp/conf/relying-party.xml```

            ```xml
            <bean id="shibboleth.DefaultRelyingParty" parent="RelyingParty">
                <property name="profileConfigurations">
                  <list>
                      <bean parent="Shibboleth.SSO" p:postAuthenticationFlows="attributerelease" />
                      <ref bean="SAML1.AttributeQuery" />
                      <ref bean="SAML1.ArtifactResolution" />
                      <bean parent="SAML2.SSO" p:postAuthenticationFlows="attribute-release" p:nameIDFormatPrecedence="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" />
                      <ref bean="SAML2.ECP" />
                      <ref bean="SAML2.Logout" />
                      <ref bean="SAML2.AttributeQuery" />
                      <ref bean="SAML2.ArtifactResolution" />
                      <ref bean="Liberty.SSOS" />
                  </list>
                </property>
            </bean>
            ```

8. Enable **JPAStorageService** for the **StorageService** of the user consent:
  * ```vim /opt/shibboleth-idp/conf/global.xml``` and add to the tail of the file this piece code:

    ```xml
    <!-- A DataSource bean suitable for use in the idp.persistentId.dataSource property. -->
    <bean id="MyDataSource" class="org.apache.commons.dbcp.BasicDataSource"
          p:driverClassName="com.mysql.jdbc.Driver"
          p:url="jdbc:mysql://localhost:3306/shibboleth?autoReconnect=true"
          p:username="##USER_DB##"
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
    (and modify the "**USER_DB_NAME**" and "**PASSWORD**" of the "**shibboleth**" DB)

  * Modify the IdP configuration file:
    * ```vim /opt/shibboleth-idp/conf/idp.properties```

      ```xml
      idp.session.StorageService = shibboleth.JPAStorageService
      idp.consent.StorageService = shibboleth.JPAStorageService
      idp.replayCache.StorageService = shibboleth.JPAStorageService
      idp.artifact.StorageService = shibboleth.JPAStorageService
      ```
  
      (This will say to IdP to store the data collected by User Consent into the "**StorageRecords**" table)

9. Connect the openLDAP to the IdP to allow the authentication of the users:
  * ```vim /opt/shibboleth-idp/conf/ldap.properties```

    (with ***TLS** solutions we consider to have the LDAP certificate into ```/opt/shibboleth-idp/credentials```).

    *  Solution 1: LDAP + STARTTLS:

      ```xml
      idp.authn.LDAP.authenticator = bindSearchAuthenticator
      idp.authn.LDAP.ldapURL = ldap://ldap.example.it:389
      idp.authn.LDAP.useStartTLS = true
      idp.authn.LDAP.useSSL = false
      idp.authn.LDAP.sslConfig = certificateTrust
      idp.authn.LDAP.trustCertificates = %{idp.home}/credentials/ldap-server.crt
      idp.authn.LDAP.baseDN = ou=people,dc=example,dc=it
      idp.authn.LDAP.userFilter = (uid={user})
      idp.authn.LDAP.bindDN = cn=admin,dc=example,dc=it
      idp.authn.LDAP.bindDNCredential = ###LDAP ADMIN PASSWORD###
      ```

    * Solution 2: LDAP + TLS:

      ```xml
      idp.authn.LDAP.authenticator = bindSearchAuthenticator
      idp.authn.LDAP.ldapURL = ldaps://ldap.example.it:636
      idp.authn.LDAP.useStartTLS = false
      idp.authn.LDAP.useSSL = true
      idp.authn.LDAP.sslConfig = certificateTrust
      idp.authn.LDAP.trustCertificates = %{idp.home}/credentials/ldap-server.crt
      idp.authn.LDAP.baseDN = ou=people,dc=example,dc=it
      idp.authn.LDAP.userFilter = (uid={user})
      idp.authn.LDAP.bindDN = cn=admin,dc=example,dc=it
      idp.authn.LDAP.bindDNCredential = ###LDAP ADMIN PASSWORD###
      ```

    * Solution 3: plain LDAP
  
      ```xml
      idp.authn.LDAP.authenticator = bindSearchAuthenticator
      idp.authn.LDAP.ldapURL = ldap://ldap.example.it:389
      idp.authn.LDAP.useStartTLS = false
      idp.authn.LDAP.useSSL = false
      idp.authn.LDAP.baseDN = ou=people,dc=example,dc=it
      idp.authn.LDAP.userFilter = (uid={user})
      idp.authn.LDAP.bindDN = cn=admin,dc=example,dc=it
      idp.authn.LDAP.bindDNCredential = ###LDAP ADMIN PASSWORD###
      ```
      (If you decide to use the Solution 3, you have to remove the following code from your ```attribute-resolver-full.xml```:
      
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
          * the baseDN ==> ```ou=people, dc=example,dc=it``` (branch containing the registered users)
          * the bindDN ==> ```cn=admin,dc=example,dc=it``` (distinguished name for the user that can made queries on the LDAP)

10. Enrich IDP logs with the authentication error occurred on LDAP
  * ```vim /opt/shibboleth/conf/logback```

    ```xml
    <!-- Logs LDAP related messages -->
    <logger name="org.ldaptive" level="${idp.loglevel.ldap:-WARN}"/>
 
    <!-- Logs on LDAP user authentication -->
    <logger name="org.ldaptive.auth.Authenticator" level="INFO" />
    ```

11. Build the **attribute-resolver.xml** to define which attributes your IdP can release *(a Federation may distribute an attribute resolver compliant with its reccomendations, here we will give a basic configuration only)*:
  * ```vim /opt/shibboleth/conf/services.xml```

    ```xml
    <value>%{idp.home}/conf/attribute-resolver.xml</value>
 
    must become:
 
    <value>%{idp.home}/conf/attribute-resolver-full.xml</value>
    ```

  *  ```vim /opt/shibboleth-idp/conf/attribute-resolver-full.xml```
    * Remove comment from "**Schema: Core Schema attributes**"
    * Remove comment from "**Schema: InetOrgPerson attributes**"
    * Remove comment from "**Schema: eduPerson attributes**"

    (Obviously, this schemas are the default ones, but for new attributes, your LDAP could need some new schemas)
    
    * Remove the comment from the LDAP Data Connector configured previously on ```ldap.properties```

12. Translate the IdP messages in your language:
  * Get the files translated in your language from [Shibboleth page](https://wiki.shibboleth.net/confluence/display/IDP30/MessagesTranslation) for:
    * **login page** (authn-messages_it.properties)
    * **user consent/terms of use page** (consent-messages_it.properties)
    * **error pages** (error-messages_it.properties)
  
  * Put all the downloded files into ```/opt/shibboleth-idp/messages``` directory
    * Restart Tomcat by: ```service tomcat restart```

13. Enable the SAML2 support by changing the ```idp-metadata.xml``` and disabling the SAML v1.x deprecated support:
  * ```vim /opt/shibboleth-idp/metadata.xml```
    ```bash
    STRINGS TO REMOVE:
      – urn:oasis:names:tc:SAML:1.1:protocol
      – urn:mace:shibboleth:1.0
      – Entire endpoint with Binding="urn:oasis:names:tc:SAML:1.0:bindings:SOAPbinding" (and change the index in the right way)
      – <NameIDFormat>urn:mace:shibboleth:1.0:nameIdentifier</NameIDFormat>
      – Entire endpoint with Binding="urn:mace:shibboleth:1.0:profiles:AuthnRequest" (and change the index in the right way)
      – 8443 (everywhere, because we don't use it)
      
    IN THE ATTRIBUTE-AUTHORITY SECTION:
    – Replace "urn:oasis:names:tc:SAML:1.1:protocol" with "urn:oasis:names:tc:SAML:2.0:protocol"
    - Remove the comment from the AttributeService SAML2 and comment out the SAMLv1 one.
    ```

14. Register your IdP on your federation with the metadata found on:
  *  ```https://##idp.example.it##/idp/shibboleth```

15. Configure the IdP to retrieve the Federation Metadata:
  * ```cd /opt/shibboleth-idp/conf```
  * ```vim metadata-providers.xml```

    ```xml
    <MetadataProvider
          id="URLMD-Federation"
          xsi:type="FileBackedHTTPMetadataProvider"
          backingFile="%{idp.home}/federation-test-metadata-sha256.xml"
          metadataURL="https://www.exampleFed.it/metadata/federation-test-metadatasha256.xml">

          <!--
              Verify the signature on the root element of the metadata aggregate
              using a trusted metadata signing certificate.
          -->
          <MetadataFilter xsi:type="SignatureValidation" requireSignedRoot="true" certificateFile="${idp.home}/metadata/federation-cert.pem"/>
 
          <!--
              Require a validUntil XML attribute on the root element and make sure its value is no more than 14 days into the future. 
          -->
          <MetadataFilter xsi:type="RequiredValidUntil" maxValidityInterval="P14D"/>

          <!-- Consume all SP metadata in the aggregate -->
          <MetadataFilter xsi:type="EntityRoleWhiteList">
            <RetainedRole>md:SPSSODescriptor</RetainedRole>
          </MetadataFilter>
    </MetadataProvider>
    ```

  * Retrive the Federation Certificate used to verify its signed metadata:
    *  ```wget https://www.exampleFed.it/certificate/federation-cert.pem -O /opt/shibboleth-idp/metadata/federation-cert.pem```

  * Check the validity:
    *  ```cd /opt/shibboleth-idp/metadata```
    *  ```openssl x509 -in federation-cert.pem -fingerprint -sha1 -noout```
    *  ```openssl x509 -in federation-cert.pem -fingerprint -md5 -noout```
  
15. Reload service with id ```shibboleth.MetadataResolverService``` to retrieve the Federation Metadata:
  *  ```cd /opt/shibboleth-idp/bin```
  *  ```./reload-service.sh -id shibboleth.MetadataResolverService```

### Configure Attribute Filter for Research and Scholarship Entity Category

1. Retrieve the attribute filter Research and Scholarship compliant:
  *  Download the [R&S Attribute Filter](../blob/master/attribute-filter-rs.xml) inside ```cd /opt/shibboleth-idp/conf```
  
2. Modify your ```services.xml```:
  *  ```vim /opt/shibboleth-idp/conf/services.xml```

     ```xml
     <util:list id ="shibboleth.AttributeFilterResources">
        <value>%{idp.home}/conf/attribute-filter.xml</value>
        <value>%{idp.home}/conf/attribute-filter-rs.xml</value>
     </util:list>
     ```
3. Restart Tomcat to apply the changes:
    *  ```service tomcat8 restart```
