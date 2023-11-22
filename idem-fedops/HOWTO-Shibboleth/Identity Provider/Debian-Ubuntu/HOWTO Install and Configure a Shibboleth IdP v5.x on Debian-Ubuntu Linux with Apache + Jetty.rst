HOWTO Install and Configure a Shibboleth IdP v5.x on Debian-Ubuntu Linux with Apache + Jetty
============================================================================================

.. image:: https://wiki.idem.garr.it/IDEM_Approved.png
   :width: 120 px

Table of Contents
-----------------

#. `Requirements`_

   #. `Hardware`_
   #. `Software`_
   #. `Others`_

#. `Notes`_
#. `Configure the environment`_
#. `Configure APT Mirror`_
#. `Install Dependencies`_
#. `Install software requirements`_

   #. `Install Apache Web Server`_
   #. `Install Amazon Corretto JDK`_
   #. `Install Jetty Servlet Container`_

#. `Install Shibboleth Identity Provider`_
#. `Disable Jetty Directory Indexing`_
#. `Configure Apache Web Server`_
#. `Configure Jetty Context Descriptor for IdP`_
#. `Configure Apache2 as the front-end of Jetty`_
#. `Configure Shibboleth Identity Provider Storage Service`_

   #. `Strategy A - Default (HTML Local Storage, Encryption GCM, No Database) - Recommended`_
   #. `Strategy B - JDBC Storage Service - using a database`_

#. `Configure the Directory Connection`_

   #. `openLDAP directory connection`_
   #. `Active Directory connection`_

#. `Configure Shibboleth Identity Provider to release the persistent NameID`_

   #. `Strategy A - Computed mode (Default) - Recommended`_
   #. `Strategy B - Stored mode - using a database`_

#. `Configure the attribute resolver (sample)`_
#. `Configure Shibboleth Identity Provider to release the eduPersonTargetedID`_

   #. `Strategy A - Computed mode - using the computed persistent NameID - Recommended`_
   #. `Strategy B - Stored mode - using the persistent NameID database`_

#. `Configure Shibboleth IdP Logging`_
#. `Translate IdP messages into preferred language`_
#. `Enrich IdP Login Page with the Institutional Logo`_
#. `Enrich IdP Login Page with Information and Privacy Policy pages`_
#. `Change default login page footer text`_
#. `Change default "Forgot your password?" and "Need help?" endpoints`_
#. `Update IdP metadata`_
#. `Secure cookies and other IDP data`_
#. `Configure Attribute Filter Policy to release attributes to Federated Resources`_
#. `Register the IdP on the IDEM Test Federation`_
#. `Appendix A: Enable Consent Module: Attribute Release + Terms of Use Consent`_
#. `Appendix B: Import persistent-id from a previous database`_
#. `Appendix C: Useful logs to find problems`_
#. `Appendix D: Connect an SP with the IdP`_
#. `Utilities`_
#. `Useful Documentation`_
#. `Authors`_

Requirements
------------

Hardware
++++++++

* CPU: 2 Core (64 bit)
* RAM: 2 GB (with IDEM MDX), 4GB (without IDEM MDX)
* HDD: 10 GB
* OS: Debian 12 / Ubuntu 22.04

Software
++++++++

* Apache Web Server (*<= 2.4*)
* Jetty 11+ Servlet Container (*implementing Servlet API 5.0 or above*)
* Amazon Corretto JDK 17
* OpenSSL (*<= 3.0.2*)

Others
++++++

* SSL Credentials: HTTPS Certificate & Key
* Logo:

  * size: 80x60 px (or other that respect the aspect-ratio)
  * format: PNG
  * style: with a transparent background

* Favicon:

  * size: 16x16 px (or other that respect the aspect-ratio)
  * format: PNG
  * style: with a transparent background

[`TOC`_]

Notes
-----

This HOWTO uses ``example.org`` and ``idp.example.org`` as example values.

Please remember to **replace all occurencences** of:

* the ``example.org`` value with the IdP domain name
* the ``idp.example.org`` value with the Full Qualified Domain Name of the Identity Provider.

[`TOC`_]

Configure the environment
+++++++++++++++++++++++++

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Be sure that your firewall **is not blocking** the traffic on port **443** and **80** for the IdP server.

#. Set the IdP hostname:

   **!!!ATTENTION!!!**: Replace ``idp.example.org`` with your IdP Full Qualified Domain Name and ``<HOSTNAME>`` with the IdP hostname

   * .. code-block:: text

        echo "<YOUR-SERVER-IP-ADDRESS> idp.example.org <HOSTNAME>" >> /etc/hosts

   * .. code-block:: text

        hostnamectl set-hostname <HOSTNAME>

#. Set the variable ``JAVA_HOME`` into ``/etc/environment``:

   * .. code-block:: text

        echo 'JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto' > /etc/environment

   * .. code-block:: text

        source /etc/environment

   * .. code-block:: text

        export JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto

   * .. code-block:: text

        echo $JAVA_HOME

[`TOC`_]

Configure APT Mirror
--------------------

Debian Mirror List: https://www.debian.org/mirror/list

Ubuntu Mirror List: https://launchpad.net/ubuntu/+archivemirrors

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. (**only for italian institutions**) Change the default mirror to the GARR ones:

   * Debian 12 - Deb822 file format:

     .. code-block:: text

        bash -c 'cat > /etc/apt/sources.list.d/garr.sources <<EOF
        Types: deb deb-src
        URIs: https://debian.mirror.garr.it/debian/
        Suites: bookworm bookworm-updates bookworm-backports
        Components: main

        Types: deb deb-src
        URIs: https://debian.mirror.garr.it/debian-security/
        Suites: bookworm-security
        Components: main
        EOF'

   * Ubuntu:

     .. code-block:: text

        bash -c 'cat > /etc/apt/sources.list.d/garr.list <<EOF
        deb https://ubuntu.mirror.garr.it/ubuntu/ jammy main
        deb-src https://ubuntu.mirror.garr.it/ubuntu/ jammy main
        EOF'

#. Update packages:

   .. code-block:: text

      apt update && apt-get upgrade -y --no-install-recommends

[`TOC`_]

Install Dependencies
--------------------

.. code-block:: text

   sudo apt install fail2ban vim wget gnupg ca-certificates openssl ntp --no-install-recommends

[`TOC`_]

Install software requirements
-----------------------------

Install Apache Web Server
+++++++++++++++++++++++++

The Apache HTTP Server will be configured as a reverse proxy and it will be used for SSL offloading.

.. code-block:: text

   sudo apt install apache2

[`TOC`_]

Install Amazon Corretto JDK
+++++++++++++++++++++++++++

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Download the Public Key *B04F24E3.pub* into ``/tmp`` dir to verify the signature file from `Amazon`_.

#. Convert Public Key into "**amazon-corretto.gpg**":

   * .. code-block:: text

        gpg --no-default-keyring --keyring /tmp/temp-keyring.gpg --import /tmp/B04F24E3.pub

   * .. code-block:: text

        gpg --no-default-keyring --keyring /tmp/temp-keyring.gpg --export --output /etc/apt/keyrings/amazon-corretto.gpg

   * .. code-block:: text

        rm /tmp/temp-keyring.gpg /tmp/B04F24E3.pub /tmp/temp-keyring.gpg~

#. Create an APT source list for Amazon Corretto:

   * .. code-block:: text

        echo "deb [signed-by=/etc/apt/keyrings/amazon-corretto.gpg] https://apt.corretto.aws stable main" >> /etc/apt/sources.list.d/amazon-corretto.list

   * .. code-block:: text

        echo "#deb-src [signed-by=/etc/apt/keyrings/amazon-corretto.gpg] https://apt.corretto.aws stable main" >> /etc/apt/sources.list.d/amazon-corretto.list

#. Install Amazon Corretto:

   .. code-block:: text

      apt update ; apt install -y java-17-amazon-corretto-jdk

#. Check that Java is working:

   .. code-block:: text

      java --version

   Result: ``OpenJDK Runtime Environment Corretto-<VERSION>``

[`TOC`_]

Install Jetty Servlet Container
+++++++++++++++++++++++++++++++

Jetty is a Web server and a Java Servlet container. It will be used to run the IdP application through its WAR file.

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. OPTIONAL - Install Servlet Jakarta API 5.0.0:

   * apt install liblogback-java => logback-classic-1.2.11.jar, logback-core-1.2.11.jar
   * apt install libservlet-api-java => servlet-api-4.0.1.jar
   * apt install libjakarta-servlet-api-java => jakarta-servlet-api-5.0.0.jar

   * .. code-block:: text

        apt install libjakarta-servlet-api-java --no-install-recommends

#. Download and Extract Jetty:

   * .. code-block:: text

        cd /usr/local/src

   * .. code-block:: text

        wget https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-home/11.0.18/jetty-home-11.0.18.tar.gz

   * .. code-block:: text

        tar xzvf jetty-home-11.0.18.tar.gz

#. Create the ``jetty-src`` folder as a symbolic link. It will be useful for future Jetty updates:

   .. code-block:: text

      ln -nsf jetty-home-11.0.18 jetty-src

#. Create the system user ``jetty`` that can run the web server (without home directory):

   .. code-block:: text

      useradd -r -M jetty

#. Create your custom Jetty configuration that overrides the default one and will survive upgrades:

   * .. code-block:: text

        mkdir -p /opt/jetty

   * .. code-block:: text

        wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/jetty-conf/start.ini -O /opt/jetty/start.ini

     (the ``start.ini`` provided is adapted to be used with `IDEM MDX`_ service)

#. Create the TMPDIR directory used by Jetty:

   * .. code-block:: text

        mkdir /opt/jetty/tmp ; chown jetty:jetty /opt/jetty/tmp

   * .. code-block:: text

        chown -R jetty:jetty /opt/jetty /usr/local/src/jetty-src

#. Create the Jetty Logs' folders:

   * .. code-block:: text

        mkdir /var/log/jetty

   * .. code-block:: text

        mkdir /opt/jetty/logs

   * .. code-block:: text

        chown jetty:jetty /var/log/jetty /opt/jetty/logs

#. Configure **/etc/default/jetty**:

   .. code-block:: bash

      bash -c 'cat > /etc/default/jetty <<EOF
      JETTY_HOME=/usr/local/src/jetty-src
      JETTY_BASE=/opt/jetty
      JETTY_USER=jetty
      JETTY_START_LOG=/var/log/jetty/start.log
      TMPDIR=/opt/jetty/tmp
      EOF'

#. Create the service loadable from command line:

   * .. code-block:: text

        cd /etc/init.d

   * .. code-block:: text

        ln -s /usr/local/src/jetty-src/bin/jetty.sh jetty

   * .. code-block:: text

        update-rc.d jetty defaults

   * .. code-block:: text

        sudo update-alternatives --config editor

     (enter ``2`` to select ``/usr/bin/vim.basic`` as editor)

   * Fix the wrong parameter from ``start`` to ``run``:

     .. code-block:: text

        systemctl edit --full jetty.service

     .. code-block:: text

        ExecStart=/etc/init.d/jetty run

#. Install & configure logback for all Jetty logging:

   * .. code-block:: text

        java -jar /usr/local/src/jetty-src/start.jar --add-module=logging-logback

     .. code-block:: text

        ALERT: There are enabled module(s) with licenses.
        ...
         Module: logging-logback
        ...
        Proceed (y/N)? y

   * .. code-block:: text

        mkdir /opt/jetty/etc

   * .. code-block:: text

        mkdir /opt/jetty/resources

   * .. code-block:: text

        wget "https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/jetty-conf/jetty-requestlog.xml" -O /opt/jetty/etc/jetty-requestlog.xml

   * .. code-block:: text

        wget "https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/jetty-conf/jetty-logging.properties" -O /opt/jetty/resources/jetty-logging.properties

#. Check if all settings are OK:

   * ``service jetty check``   (Jetty NOT running)
   * ``service jetty run``
   * ``service jetty check``   (Jetty running pid=XXXX)

   If you receive an error likes "*Job for jetty.service failed because the control process exited with error code. See "systemctl status jetty.service" and "journalctl -xe" for details.*", try this:

   * .. code-block:: text

        rm /var/run/jetty.pid

   * .. code-block:: text

        systemctl start jetty.service

[`TOC`_]

Install Shibboleth Identity Provider
------------------------------------

The Identity Provider (IdP) is responsible for user authentication and providing user information to the Service Provider (SP). It is located at the home organization, which is the organization which maintains the user's account.
It is a Java Web Application that can be deployed with its WAR file.

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Download the Shibboleth Identity Provider v5.x.y (replace '5.x.y' with the latest version found on the `Shibboleth download site`_):

   * .. code-block:: text

        cd /usr/local/src

   * .. code-block:: text

        wget http://shibboleth.net/downloads/identity-provider/5.x.y/shibboleth-identity-provider-5.x.y.tar.gz

   * .. code-block:: text

        tar -xzf shibboleth-identity-provider-5.*.tar.gz

#. Validate the package downloaded:

   * .. code-block:: text

        cd /usr/local/src

   * .. code-block:: text

        wget https://shibboleth.net/downloads/identity-provider/5.x.y/shibboleth-identity-provider-5.x.y.tar.gz.asc

   * .. code-block:: text

        wget https://shibboleth.net/downloads/PGP_KEYS

   * .. code-block:: text

        gpg --import /usr/local/src/PGP_KEYS

   * .. code-block:: text

        gpg --verify /usr/local/src/shibboleth-identity-provider-5.x.y.tar.gz.asc /usr/local/src/shibboleth-identity-provider-5.x.y.tar.gz

   If the verification contains also the name of Scott Cantor the package is valid.

#. Install Identity Provider Shibboleth:

   **NOTE**

   According to `NSA and NIST`_, **RSA with 3072 bit-modulus is the minimum** to protect up to TOP SECRET over than 2030.

   * .. code-block:: text

        cd /usr/local/src/shibboleth-identity-provider-5.*/bin

   * .. code-block:: text

        bash install.sh --hostName $(hostname -f)

   **!!! ATTENTION !!!**

   Replace the default value of *Attribute Scope* with the domain name of your institution.

   .. code-block:: bash

      Installation Directory: [/opt/shibboleth-idp] ?                                        (Press ENTER)
      SAML EntityID: [https://idp.example.org/idp/shibboleth] ?                              (Press ENTER)
      Attribute Scope: [example.org] ?                            (Digit your domain name and press ENTER)

   By starting from this point, the variable **idp.home** refers to the directory: ``/opt/shibboleth-idp``

[`TOC`_]

Disable Jetty Directory Indexing
--------------------------------

**!!! ATTENTION !!!**

Jetty has had vulnerabilities related to directory indexing (sigh) so we suggest disabling that feature at this point.

#. Create missing dir

   .. code-block:: text

      mkdir /opt/shibboleth-idp/edit-webapp/WEB-INF

#. Fix ``web.xml``:

   .. code-block:: text

      cp /opt/shibboleth-idp/dist/webapp/WEB-INF/web.xml /opt/shibboleth-idp/edit-webapp/WEB-INF/web.xml

#. Rebuild IdP war file:

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/build.sh

[`TOC`_]

Configure Apache Web Server
---------------------------

#. Create the DocumentRoot:

   * .. code-block:: text

        mkdir /var/www/html/$(hostname -f)

   * .. code-block:: text

        chown -R www-data: /var/www/html/$(hostname -f)

   * .. code-block:: text

        echo '<h1>It Works!</h1>' > /var/www/html/$(hostname -f)/index.html

#. Put SSL credentials in the right place:

   * HTTPS Server Certificate (Public Key) inside ``/etc/ssl/certs``
   * HTTPS Server Key (Private Key) inside ``/etc/ssl/private``
   * Add CA Cert into ``/etc/ssl/certs``

     * If you use GARR TCS or GEANT TCS:

   * .. code-block:: text

        wget -O /etc/ssl/certs/GEANT_OV_RSA_CA_4.pem https://crt.sh/?d=2475254782

   * .. code-block:: text

        wget -O /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt https://crt.sh/?d=924467857

   * .. code-block:: text

        cat /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt >> /etc/ssl/certs/GEANT_OV_RSA_CA_4.pem

   * .. code-block:: text

        rm /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt

     * If you use ACME (Let's Encrypt):

       .. code-block:: text

          ln -s /etc/letsencrypt/live/<SERVER_FQDN>/chain.pem /etc/ssl/certs/ACME-CA.pem

#. Configure the right privileges for the SSL Certificate and Key used by HTTPS:

   * .. code-block:: text

        chmod 400 /etc/ssl/private/$(hostname -f).key

   * .. code-block:: text

        chmod 644 /etc/ssl/certs/$(hostname -f).crt

   (``$(hostname -f)`` will provide your IdP Full Qualified Domain Name)

#. Enable the required Apache2 modules and the virtual hosts:

   * .. code-block:: text

        a2enmod proxy_http ssl headers alias include negotiation

   * .. code-block:: text

        a2dissite 000-default.conf default-ssl

   * .. code-block:: text

        systemctl restart apache2.service

[`TOC`_]

Configure Jetty Context Descriptor for IdP
------------------------------------------

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Configure the Jetty Context Descriptor:

   * .. code-block:: text

        mkdir /opt/jetty/webapps

   * .. code-block:: text

        wget "https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/jetty-conf/idp.xml" -O /opt/jetty/webapps/idp.xml

#. Make the **jetty** user owner of IdP main directories:

   * .. code-block:: text

        cd /opt/shibboleth-idp

   * .. code-block:: text

        chown -R jetty logs/ metadata/ credentials/ conf/ war/

#. Restart Jetty:

   .. code-block:: text

      systemctl restart jetty.service

[`TOC`_]

Configure Apache2 as the front-end of Jetty
-------------------------------------------

The Apache HTTP Server will be configured as a reverse proxy and it will be used for SSL offloading.

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Create the Virtualhost file (**please pay attention: you need to edit this file and customize it, check the initial comment of the file**):

   .. code-block:: text

      wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/apache-conf/idp.example.org.conf -O /etc/apache2/sites-available/$(hostname -f).conf

#. Enable the Apache2 virtual hosts created:

   * .. code-block:: text

        a2ensite $(hostname -f).conf

   * .. code-block:: text

        systemctl reload apache2.service

#. Check that IdP metadata is available on:

   ``https://idp.example.org/idp/shibboleth``

#. Verify the strength of your IdP's machine on SSLLabs_.

[`TOC`_]

Configure Shibboleth Identity Provider Storage Service
------------------------------------------------------

Shibboleth Documentation reference: `StorageConfiguration`_

The IdP provides a number of general-purpose storage facilities that can be used by core subsystems like session management and consent.

Strategy A - Default (HTML Local Storage, Encryption GCM, No Database) - Recommended
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The HTML Local Storage requires JavaScript be enabled because reading and writing to the client requires an explicit page be rendered.
Note that this feature is safe to enable globally. The implementation is written to check for this capability in each client, and to back off to cookies.
The default configuration generates encrypted assertions that a large percentage of non-Shibboleth SPs are going to be unable to decrypt, resulting a wide variety of failures and error messages.
Some old Shibboleth SPs or software running on old Operating Systems will also fail to work.

**!!! DO IT BECAUSE IT IS IMPORTANT !!!**

**(only for Italian Identity Federation IDEM members)**

The IDEM Federation Operators collect a list of Service Providers
that don't support the new default encryption algorithm and provide a solution on his wiki pages:

* `Idp4noGCMsps`_

If you don't change anything, the IdP stores data in a browser session cookie or HTML local storage and encrypt his assertions with AES-GCM encryption algorithm.

See the configuration files and the Shibboleth documentation for details.

Check IdP Status:

.. code-block:: text

   bash /opt/shibboleth-idp/bin/status.sh

Proceed with `Configure the Directory Connection`_

[`TOC`_]

Strategy B - JDBC Storage Service - using a database
++++++++++++++++++++++++++++++++++++++++++++++++++++

https://shibboleth.atlassian.net/wiki/spaces/IDPPLUGINS/pages/2989096970/JDBCStorageService

This Storage service will memorize User Consent data on a persistent SQL database.

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Install SQL database and needed libraries:

   * .. code-block:: text

        apt install default-mysql-server libmariadb-java libcommons-dbcp2-java libcommons-pool2-java --no-install-recommends

#. Install JDBCStorageService plugin:

   .. code-block:: text

      /opt/shibboleth-idp/bin/plugin.sh -I net.shibboleth.plugin.storage.jdbc

#. Activate MariaDB database service:

   .. code-block:: text

      systemctl start mariadb.service

#. Address several security concerns in a default MariaDB installation (if it is not already done):

   .. code-block:: text

      mysql_secure_installation

#. (OPTIONAL) MySQL DB Access without password:

   .. code-block:: text

      vim /root/.my.cnf

   .. code-block:: text

      [client]
      user=root
      password=##ROOT-DB-PASSWORD-CHANGEME##

#. Create ``StorageRecords`` table on the ``storagerecords`` database:

   * .. code-block:: text

        wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/db-conf/shib-sr-db.sql -O /root/shib-sr-db.sql

   fill missing datas on ``shib-sr-db.sql`` before import:

   * .. code-block:: text

        mysql -u root < /root/shib-sr-db.sql

   * .. code-block:: text

        systemctl restart mariadb.service

#. Rebuild IdP war file with the needed libraries:

   * .. code-block:: text

        mkdir /opt/shibboleth-idp/edit-webapp/WEB-INF/lib

   * .. code-block:: text

        ln -s /usr/share/java/mariadb-java-client.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib

   * .. code-block:: text

        ln -s /usr/share/java/commons-dbcp2.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib

   * .. code-block:: text

        ln -s /usr/share/java/commons-pool2.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib

   * .. code-block:: text

        bash /opt/shibboleth-idp/bin/build.sh

#. Configure JDBC Storage Service:

   .. code-block:: text

      vim /opt/shibboleth-idp/conf/global.xml

   and add the following directives to the tail, before the last ``</beans>`` tag:

   .. code-block:: xml+jinja

      <bean id="storagerecords.JDBCStorageService.DataSource"
            class="org.apache.commons.dbcp2.BasicDataSource" destroy-method="close" lazy-init="true"
            p:driverClassName="org.mariadb.jdbc.Driver"
            p:url="jdbc:mysql://localhost:3306/storagerecords?autoReconnect=true"
            p:username="###_SR-USERNAME-CHANGEME_###"
            p:password="###_SR-DB-USER-PASSWORD-CHANGEME_###"
            p:maxTotal="10"
            p:maxIdle="5"
            p:maxWaitMillis="15000"
            p:testOnBorrow="true"
            p:validationQuery="select 1"
            p:validationQueryTimeout="5" />

      <bean id="storagerecords.JDBCStorageService" parent="shibboleth.JDBCStorageService"
            p:dataSource-ref="storagerecords.JDBCStorageService.DataSource" />

   **!!! IMPORTANT !!!**:

   remember to change "**###_SR-USERNAME-CHANGEME_###**" and "**###_SR-DB-USER-PASSWORD-CHANGEME_###**" with your DB user and password data

#. Set the consent storage service to the JDBC storage service:

   .. code-block:: text

      vim /opt/shibboleth-idp/conf/idp.properties

   .. code-block:: text

      idp.consent.StorageService = storagerecords.JDBCStorageService

#. Restart Jetty to apply the changes:

   .. code-block:: text

      systemctl restart jetty.service

#. Check IdP Status:

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/status.sh

#. Proceed with `Configure the Directory Connection`_

[`TOC`_]

Configure the Directory Connection
----------------------------------

openLDAP directory connection
+++++++++++++++++++++++++++++

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Install useful packages:

   .. code-block:: text

      apt install ldap-utils

#. Check that you can reach the Directory from your IDP server:

   .. code-block:: text

      ldapsearch -x -h <LDAP-SERVER-FQDN-OR-IP> -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<IDPUSER-PASSWORD>' -b 'ou=people,dc=example,dc=org' '(uid=<USERNAME-USED-IN-THE-LOGIN-FORM>)'

   * the baseDN (``-b`` parameter) ==> ``ou=people,dc=example,dc=org`` (branch containing the registered users)
   * the bindDN (``-D`` parameter) ==> ``cn=idpuser,ou=system,dc=example,dc=org`` (distinguished name for the user that can made queries on the LDAP, read only is sufficient)
   * the searchFilter ``(uid=<USERNAME-USED-IN-THE-LOGIN-FORM>)`` corresponds to the ``(uid=$resolutionContext.principal)`` searchFilter configured into ``conf/ldap.properties``

#. Connect the openLDAP to the IdP to allow the authentication of the users:

   * Solution 1 - LDAP + STARTTLS:

     * Configure ``secrets.properties``:

       .. code-block:: text

          vim /opt/shibboleth-idp/credentials/secrets.properties

       .. code-block:: xml+jinja

          # Default access to LDAP authn and attribute stores.
          idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
          idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}

     * Configure ``ldap.properties``:

       The ``ldap.example.org`` have to be replaced with the FQDN of the LDAP server.

       The ``idp.authn.LDAP.baseDN`` and ``idp.authn.LDAP.bindDN`` have to be replaced with the right value.

       The property ``idp.attribute.resolver.LDAP.exportAttributes``
       **has to be added** into the file and configured with
       the list of attributes the IdP retrieves directly from LDAP.
       The list MUST contain the attribute chosen for the persistent-id generation
       (**idp.persistentId.sourceAttribute**).

       .. code-block:: text

          vim /opt/shibboleth-idp/conf/ldap.properties

       .. code-block:: xml+jinja

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

     * Paste the OpenLDAP certificate into ``/opt/shibboleth-idp/credentials/ldap-server.crt``.

     * Configure the right owner/group for the OpenLDAP certificate loaded:

       .. code-block:: text

          chown jetty:root /opt/shibboleth-idp/credentials/ldap-server.crt ; chmod 600 /opt/shibboleth-idp/credentials/ldap-server.crt

     * Restart Jetty to apply the changes:

       .. code-block:: text

          systemctl restart jetty.service

     * Check IdP Status:

       .. code-block:: text

          bash /opt/shibboleth-idp/bin/status.sh

     * Proceed with `Configure Shibboleth Identity Provider to release the persistent NameID`_

   * Solution 2 - LDAP + TLS:

     * Configure ``secrets.properties``:

       .. code-block:: text

          vim /opt/shibboleth-idp/credentials/secrets.properties

       .. code-block:: xml+jinja

          # Default access to LDAP authn and attribute stores.
          idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
          idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}

     * Configure ``ldap.properties``:

       The ``ldap.example.org`` have to be replaced with the FQDN of the LDAP server.

       The ``idp.authn.LDAP.baseDN`` and ``idp.authn.LDAP.bindDN`` have to be replaced with the right value.

       The property ``idp.attribute.resolver.LDAP.exportAttributes``
       **has to be added** into the file and configured with
       the list of attributes the IdP retrieves directly from LDAP.
       The list MUST contain the attribute chosen for the persistent-id generation
       (**idp.persistentId.sourceAttribute**).

       .. code-block:: text

          vim /opt/shibboleth-idp/conf/ldap.properties

       .. code-block:: xml+jinja

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
     * Paste the content of OpenLDAP certificate into ``/opt/shibboleth-idp/credentials/ldap-server.crt``

     * Configure the right owner/group to the OpenLDAP certificate loaded:

       .. code-block:: text

          chown jetty:root /opt/shibboleth-idp/credentials/ldap-server.crt ; chmod 600 /opt/shibboleth-idp/credentials/ldap-server.crt

     * Restart Jetty to apply the changes:

       .. code-block:: text

          systemctl restart jetty.service

     * Check IdP Status:

       .. code-block:: text

          bash /opt/shibboleth-idp/bin/status.sh

     * Proceed with `Configure Shibboleth Identity Provider to release the persistent NameID`_

   * Solution 3 - plain LDAP:

     * Configure ``secrets.properties``:

       .. code-block:: text

          vim /opt/shibboleth-idp/credentials/secrets.properties

       .. code-block:: xml+jinja

          # Default access to LDAP authn and attribute stores.
          idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
          idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}

     * Configure ``ldap.properties``:

       The ``ldap.example.org`` have to be replaced with the FQDN of the LDAP server.

       The ``idp.authn.LDAP.baseDN`` and ``idp.authn.LDAP.bindDN`` have to be replaced with the right value.

       The property ``idp.attribute.resolver.LDAP.exportAttributes``
       **has to be added** into the file and configured with
       the list of attributes the IdP retrieves directly from LDAP.
       The list MUST contain the attribute chosen for the persistent-id generation
       (**idp.persistentId.sourceAttribute**).

       .. code-block:: text

          vim /opt/shibboleth-idp/conf/ldap.properties

       .. code-block:: xml+jinja

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
     * Restart Jetty to apply the changes:

       .. code-block:: text

          systemctl restart jetty.service

     * Check IdP Status:

       .. code-block:: text

          bash /opt/shibboleth-idp/bin/status.sh

     * Proceed with `Configure Shibboleth Identity Provider to release the persistent NameID`_

[`TOC`_]

Active Directory connection
+++++++++++++++++++++++++++

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Install useful packages:

   .. code-block:: text

      apt install ldap-utils

#. Check that you can reach the Directory from your IDP server:

   .. code-block:: text

      ldapsearch -x -h <AD-SERVER-FQDN-OR-IP> -D 'CN=idpuser,CN=Users,DC=ad,DC=example,DC=org' -w '<IDPUSER-PASSWORD>' -b 'CN=Users,DC=ad,DC=example,DC=org' '(sAMAccountName=<USERNAME-USED-IN-THE-LOGIN-FORM>)'

   * the baseDN (``-b`` parameter) ==> ``CN=Users,DC=ad,DC=example,DC=org`` (branch containing the registered users)
   * the bindDN (``-D`` parameter) ==> ``CN=idpuser,CN=Users,DC=ad,DC=example,DC=org`` (distinguished name for the user that can made queries on the LDAP, read only is sufficient)
   * the searchFilter ``(sAMAccountName=<USERNAME-USED-IN-THE-LOGIN-FORM>)`` corresponds to the ``(sAMAccountName=$resolutionContext.principal)`` searchFilter configured into ``conf/ldap.properties``

#. Connect the Active Directory to the IdP to allow the authentication of the users:

   * Solution 1 - AD + STARTTLS:

     * Configure ``secrets.properties``:

       .. code-block:: text

          vim /opt/shibboleth-idp/credentials/secrets.properties

       .. code-block:: xml+jinja

          # Default access to LDAP authn and attribute stores.
          idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
          idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}

     * Configure ``ldap.properties``:

       The ``ldap.example.org`` have to be replaced with the FQDN of the LDAP server.

       The ``idp.authn.LDAP.baseDN`` and ``idp.authn.LDAP.bindDN`` have to be replaced with the right value.

       The property ``idp.attribute.resolver.LDAP.exportAttributes``
       **has to be added** into the file and configured with
       the list of attributes the IdP retrieves directly from LDAP.
       The list MUST contain the attribute chosen for the persistent-id generation
       (**idp.persistentId.sourceAttribute**).

       .. code-block:: text

          vim /opt/shibboleth-idp/conf/ldap.properties

       .. code-block:: xml+jinja

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
     * Paste the content of OpenLDAP certificate into ``/opt/shibboleth-idp/credentials/ldap-server.crt``

     * Configure the right owner/group to the OpenLDAP certificate loaded:

       .. code-block:: text

          chown jetty:root /opt/shibboleth-idp/credentials/ldap-server.crt ; chmod 600 /opt/shibboleth-idp/credentials/ldap-server.crt

     * Restart Jetty to apply the changes:

       .. code-block:: text

          systemctl restart jetty.service

     * Check IdP Status:

       .. code-block:: text

          bash /opt/shibboleth-idp/bin/status.sh

     * Proceed with `Configure Shibboleth Identity Provider to release the persistent NameID`_

   * Solution 2: AD + TLS:

     * Configure ``secrets.properties``:

       .. code-block:: text

          vim /opt/shibboleth-idp/credentials/secrets.properties

       .. code-block:: xml+jinja

          # Default access to LDAP authn and attribute stores.
          idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
          idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}

     * Configure ``ldap.properties``:

       The ``ldap.example.org`` have to be replaced with the FQDN of the LDAP server.

       The ``idp.authn.LDAP.baseDN`` and ``idp.authn.LDAP.bindDN`` have to be replaced with the right value.

       The property ``idp.attribute.resolver.LDAP.exportAttributes``
       **has to be added** into the file and configured with
       the list of attributes the IdP retrieves directly from LDAP.
       The list MUST contain the attribute chosen for the persistent-id generation
       (**idp.persistentId.sourceAttribute**).

       .. code-block:: text

          vim /opt/shibboleth-idp/conf/ldap.properties

       .. code-block:: xml+jinja

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

     * Paste the content of OpenLDAP certificate into ``/opt/shibboleth-idp/credentials/ldap-server.crt``

     * Configure the right owner/group to the OpenLDAP certificate loaded:

       .. code-block:: text

          chown jetty:root /opt/shibboleth-idp/credentials/ldap-server.crt ; chmod 600 /opt/shibboleth-idp/credentials/ldap-server.crt

     * Restart Jetty to apply the changes:

       .. code-block:: text

          systemctl restart jetty.service

     * Check IdP Status:

       .. code-block:: text

          bash /opt/shibboleth-idp/bin/status.sh

     * Proceed with `Configure Shibboleth Identity Provider to release the persistent NameID`_

   * Solution 3 - plain AD:

     * Configure ``secrets.properties``:

       .. code-block:: text

          vim /opt/shibboleth-idp/credentials/secrets.properties

       .. code-block:: xml+jinja

          # Default access to LDAP authn and attribute stores.
          idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
          idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}

     * Configure ``ldap.properties``:

       The ``ldap.example.org`` have to be replaced with the FQDN of the LDAP server.

       The ``idp.authn.LDAP.baseDN`` and ``idp.authn.LDAP.bindDN`` have to be replaced with the right value.

       The property ``idp.attribute.resolver.LDAP.exportAttributes``
       **has to be added** into the file and configured with
       the list of attributes the IdP retrieves directly from LDAP.
       The list MUST contain the attribute chosen for the persistent-id generation
       (**idp.persistentId.sourceAttribute**).

       .. code-block:: text

          vim /opt/shibboleth-idp/conf/ldap.properties

       .. code-block:: xml+jinja

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

     * Restart Jetty to apply the changes:

       .. code-block:: text

          systemctl restart jetty.service

     * Check IdP Status:

       .. code-block:: text

          bash /opt/shibboleth-idp/bin/status.sh

     * Proceed with `Configure Shibboleth Identity Provider to release the persistent NameID`_

[`TOC`_]

Configure Shibboleth Identity Provider to release the persistent NameID
-----------------------------------------------------------------------

DOC: `PersistentNameIDGenerationConfiguration`_

SAML 2.0 (but not SAML 1.x) defines a kind of NameID called a "*persistent*" identifier that every SP receives for the IdP users.
This part will teach you how to release the "*persistent*" identifiers with a database (Stored Mode) or without it (Computed Mode).

By default, a transient NameID will always be released to the Service Provider if the persistent one is not requested.

Strategy A - Computed mode (Default) - Recommended
++++++++++++++++++++++++++++++++++++++++++++++++++

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Enable the generation of the computed ``persistent-id`` with:

   * .. code-block:: text

        vim /opt/shibboleth-idp/conf/saml-nameid.properties

     The *sourceAttribute* MUST be an attribute, or a list of comma-separated attributes, that uniquely identify the subject of the generated ``persistent-id``.

     The *sourceAttribute* MUST be a **Stable**, **Permanent** and **Not-reassignable** directory attribute.

     .. code-block:: xml+jinja

        # ... other things ...#
        # OpenLDAP has the UserID into "uid" attribute
        idp.persistentId.sourceAttribute = uid

        # Active Directory has the UserID into "sAMAccountName"
        #idp.persistentId.sourceAttribute = sAMAccountName
        # ... other things ...#

   * .. code-block:: text

        vim /opt/shibboleth-idp/conf/saml-nameid.xml

     Uncomment the line:

     .. code-block:: xml+jinja

        <ref bean="shibboleth.SAML2PersistentGenerator" />

   * .. code-block:: xml+jinja

        vim /opt/shibboleth-idp/credentials/secrets.properties

     .. code-block:: xml+jinja

        idp.persistentId.salt = ### result of command 'openssl rand -base64 36' ###

#. Restart Jetty to apply the changes:

   .. code-block:: text

      systemctl restart jetty.service

#. Check IdP Status:

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/status.sh

#. Proceed with `Configure the attribute resolver (sample)`_

[`TOC`_]

Strategy B - Stored mode - using a database
+++++++++++++++++++++++++++++++++++++++++++

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Install SQL database and needed libraries:

   * .. code-block:: text

        apt install default-mysql-server libmariadb-java libcommons-dbcp2-java libcommons-pool2-java --no-install-recommends

#. Install JDBCStorageService plugin:

   .. code-block:: text

      /opt/shibboleth-idp/bin/plugin.sh -I net.shibboleth.plugin.storage.jdbc

#. Activate MariaDB database service:

   .. code-block:: text

      systemctl start mariadb.service

#. Address several security concerns in a default MariaDB installation (if it is not already done):

   .. code-block:: text

      mysql_secure_installation

#. (OPTIONAL) MySQL DB Access without password:

   .. code-block:: text

      vim /root/.my.cnf

   .. code-block:: text

      [client]
      user=root
      password=##ROOT-DB-PASSWORD-CHANGEME##

#. Create ``shibpid`` table on ``shibboleth`` database:

   * .. code-block:: text

        wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/db-conf/shib-pid-db.sql -O /root/shib-pid-db.sql

   fill missing data on ``shib-pid-db.sql`` before import:

   * .. code-block:: text

        mysql -u root < /root/shib-pid-db.sql

   * .. code-block:: text

        systemctl restart mariadb.service

#. Rebuild IdP war file with the needed libraries:

   * .. code-block:: text

        mkdir /opt/shibboleth-idp/edit-webapp/WEB-INF/lib

   * .. code-block:: text

        ln -s /usr/share/java/mariadb-java-client.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib

   * .. code-block:: text

        ln -s /usr/share/java/commons-dbcp2.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib

   * .. code-block:: text

        ln -s /usr/share/java/commons-pool2.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib

   * .. code-block:: text

        bash /opt/shibboleth-idp/bin/build.sh

#. Configure JDBC Storage Service:

   .. code-block:: text

      vim /opt/shibboleth-idp/conf/global.xml

   and add the following directives to the tail, before the last ``</beans>`` tag:

   .. code-block:: xml+jinja

      <bean id="shibpid.JDBCStorageService.DataSource"
            class="org.apache.commons.dbcp2.BasicDataSource" destroy-method="close" lazy-init="true"
            p:driverClassName="org.mariadb.jdbc.Driver"
            p:url="jdbc:mysql://localhost:3306/shibpid?autoReconnect=true"
            p:username="###_SHIBPID-USERNAME-CHANGEME_###"
            p:password="###_SHIBPID-DB-USER-PASSWORD-CHANGEME_###"
            p:maxTotal="10"
            p:maxIdle="5"
            p:maxWaitMillis="15000"
            p:testOnBorrow="true"
            p:validationQuery="select 1"
            p:validationQueryTimeout="5" />

   **!!! IMPORTANT !!!**

   remember to change "**###_SHIBPID-USERNAME-CHANGEME_###**" and "**###_SHIBPID-DB-USER-PASSWORD-CHANGEME_###**" with your DB user and password data

#. Enable the generation of the ``persistent-id``:

   * .. code-block:: text

        vim /opt/shibboleth-idp/conf/saml-nameid.properties

     The *sourceAttribute* MUST be an attribute, or a list of comma-separated attributes, that uniquely identify the subject of the generated ``persistent-id``.

     The *sourceAttribute* MUST be a **Stable**, **Permanent** and **Not-reassignable** directory attribute.

     .. code-block:: xml+jinja

        # ... other things ...#
        # OpenLDAP has the UserID into "uid" attribute
        idp.persistentId.sourceAttribute = uid

        # Active Directory has the UserID into "sAMAccountName"
        #idp.persistentId.sourceAttribute = sAMAccountName

        # ... other things ...#
        idp.persistentId.generator = shibboleth.StoredPersistentIdGenerator
        # ... other things ...#
        idp.persistentId.dataSource = shibpid.JDBCStorageService.DataSource
        # ... other things ...#

   * .. code-block:: text

        vim /opt/shibboleth-idp/credentials/secrets.properties

     .. code-block:: text

        idp.persistentId.salt = ### result of command 'openssl rand -base64 36'###

   * Enable the **SAML2PersistentGenerator**:

     * .. code-block:: text

          vim /opt/shibboleth-idp/conf/saml-nameid.xml

       Uncomment the line:

       .. code-block:: xml+jinja

          <ref bean="shibboleth.SAML2PersistentGenerator" />

     * .. code-block:: text

          vim /opt/shibboleth-idp/conf/c14n/subject-c14n.xml

       Uncomment the line:

       .. code-block:: xml+jinja

          <ref bean="c14n/SAML2Persistent" />

     * (OPTIONAL) Transform each letter of username, before storing in into the database, to Lowercase or Uppercase by setting the proper constant:

       .. code-block:: text

          vim /opt/shibboleth-idp/conf/c14n/subject-c14n.properties

       .. code-block:: xml+jinja

          # Simple username -> principal name c14n
          idp.c14n.simple.lowercase = true
          #idp.c14n.simple.uppercase = false
          idp.c14n.simple.trim = true

#. Restart Jetty to apply the changes:

   .. code-block:: text

      systemctl restart jetty.service

#. Check IdP Status:

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/status.sh

#. Proceed with `Configure the attribute resolver (sample)`_

[`TOC`_]

Configure the attribute resolver (sample)
-----------------------------------------

The attribute resolver contains attribute definitions and data connectors
that collect information from a variety of sources, combine and transform it,
and produce a final collection of IdPAttribute objects,
which are an internal representation of user data not specific to SAML
or any other supported identity protocol.

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Download the sample attribute resolver provided by IDEM GARR AAI Federation Operators (OpenLDAP / Active Directory compliant):

   .. code-block:: text

      wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/conf/attribute-resolver-v5-idem-sample.xml -O /opt/shibboleth-idp/conf/attribute-resolver.xml

   If you decide to use the plain text LDAP/AD solution, **remove or comment** the following directives from your Attribute Resolver file:

   .. code-block:: xml+jinja

      Line 1:  useStartTLS="%{idp.attribute.resolver.LDAP.useStartTLS:true}"
      Line 2:  trustFile="%{idp.attribute.resolver.LDAP.trustCertificates}"

#. Configure the right owner:

   .. code-block:: text

      chown jetty /opt/shibboleth-idp/conf/attribute-resolver.xml

#. Restart Jetty to apply the changes:

   .. code-block:: text

      systemctl restart jetty.service

#. Check IdP Status:

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/status.sh

[`TOC`_]

Configure Shibboleth Identity Provider to release the eduPersonTargetedID
-------------------------------------------------------------------------

eduPersonTargetedID is an abstracted version of the SAML V2.0 Name Identifier format of ``urn:oasis:names:tc:SAML:2.0:nameid-format:persistent``.

To be able to follow these steps, you need to have followed the previous steps on ``persistent`` NameID generation.

Strategy A - Computed mode - using the computed persistent NameID - Recommended
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Check to have the following ``<AttributeDefinition>`` and the ``<DataConnector>`` into the ``attribute-resolver.xml``:

   .. code-block:: text

      vim /opt/shibboleth-idp/conf/attribute-resolver.xml`

   .. code-block:: xml+jinja

      <!-- ...other things ... -->

      <!--  AttributeDefinition for eduPersonTargetedID - Computed Mode  -->
      <!--
            WARN [DEPRECATED:173] - xsi:type 'SAML2NameID'
            This feature is at-risk for removal in a future version

       NOTE: eduPersonTargetedID is DEPRECATED and should not be used.
      -->
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

#. Create the custom ``eduPersonTargetedID.properties`` file:

   .. code-block:: text

      wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/conf/attributes/custom/eduPersonTargetedID.properties -O /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties

#. Set proper owner/group with:

   .. code-block:: text

      chown jetty:root /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties

#. Restart Jetty to apply the changes:

   .. code-block:: text

      systemctl restart jetty.service

#. Check IdP Status:

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/status.sh

#. Proceed with `Configure Shibboleth IdP Logging`_

[`TOC`_]

Strategy B - Stored mode - using the persistent NameID database
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Check to have the following ``<AttributeDefinition>`` and the ``<DataConnector>`` into the ``attribute-resolver.xml``:

   .. code-block:: text

      vim /opt/shibboleth-idp/conf/attribute-resolver.xml`

   .. code-block:: xml+jinja

      <!-- ...other things ... -->

      <!--  AttributeDefinition for eduPersonTargetedID - Stored Mode  -->
      <!--
            WARN [DEPRECATED:173] - xsi:type 'SAML2NameID'
            This feature is at-risk for removal in a future version

       NOTE: eduPersonTargetedID is DEPRECATED and should not be used.
      -->
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

#. Create the custom ``eduPersonTargetedID.properties`` file:

   .. code-block:: text

      wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/conf/attributes/custom/eduPersonTargetedID.properties -O /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties

#. Set proper owner/group with:

   .. code-block:: text

      chown jetty:root /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties

#. Restart Jetty to apply the changes:

   .. code-block:: text

      systemctl restart jetty.service

#. Check IdP Status:

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/status.sh

#. Proceed with `Configure Shibboleth IdP Logging`_

[`TOC`_]

Configure Shibboleth IdP Logging
--------------------------------

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Enrich IDP logs with the authentication error occurred on LDAP:

   .. code-block:: text

      sed -i '/^    <logger name="org.ldaptive".*/a \\n    <!-- Logs on LDAP user authentication - ADDED BY IDEM HOWTO -->' /opt/shibboleth-idp/conf/logback.xml

      sed -i '/^    <!-- Logs on LDAP user authentication - ADDED BY IDEM HOWTO -->/a \ \ \ \ \<logger name="org.ldaptive.auth.Authenticator" level="INFO" />' /opt/shibboleth-idp/conf/logback.xml

[`TOC`_]

Translate IdP messages into preferred language
----------------------------------------------

Translate the IdP messages in your language:

* Get the files translated in your language from `MessagesTranslation`_
* Put ``messages_XX.properties`` downloaded file into ``/opt/shibboleth-idp/messages`` directory
* Restart Jetty to apply the changes with ``systemctl restart jetty.service``

[`TOC`_]

Enrich IdP Login Page with the Institutional Logo
-------------------------------------------------

#. Discover what images are publicly available by opening an URL similar to "https://idp.example.org/idp/images/" from a web browser.

#. Copy the institutional logo into all placeholder found inside the ``/opt/shibboleth-idp/edit-webapp/images`` directory **without renaming them**.

#. Rebuild IdP war file:

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/build.sh

#. Restart Jetty:

   .. code-block:: text

      sudo systemctl restart jetty.service

[`TOC`_]

Enrich IdP Login Page with Information and Privacy Policy pages
---------------------------------------------------------------

#. Add the following two lines into ``views/login.vm``:

   .. code-block:: text

      <li class="list-help-item"><a href="#springMessageText("idp.url.infoPage", '#')"><span class="item-marker">&rsaquo;</span> #springMessageText("idp.login.infoPage", "Information page")</a></li>
      <li class="list-help-item"><a href="#springMessageText("idp.url.privacyPage", '#')"><span class="item-marker">&rsaquo;</span> #springMessageText("idp.login.privacyPage", "Privacy Policy")</a></li>

   under the line containing the Anchor:

   .. code-block:: text

      <a href="#springMessageText("idp.url.helpdesk", '#')">

#. Add the new variables defined with lines added at point 1 into all ``messages*.properties`` files linked to the view ``view/login.vm``:

   * Move to the IdP Home:

     .. code-block:: text

        cd /opt/shibboleth-idp

   * Modify ``messages.properties``:

     .. code-block:: text

        vim messages/messages.properties

     .. code-block:: text

        idp.login.infoPage=Informations
        idp.url.infoPage=https://my.organization.it/english-idp-info-page.html
        idp.login.privacyPage=Privacy Policy
        idp.url.privacyPage=https://my.organization.it/english-idp-privacy-policy.html

   * Modify ``messages_it.properties``:

     .. code-block:: text

        vim messages/messages_it.properties

     .. code-block:: text

        idp.login.infoPage=Informazioni
        idp.url.infoPage=https://my.organization.it/italian-idp-info-page.html
        idp.login.privacyPage=Privacy Policy
        idp.url.privacyPage=https://my.organization.it/italian-idp-privacy-policy.html

#. Rebuild IdP WAR file and Restart Jetty to apply changes:

   * .. code-block:: text

        bash /opt/shibboleth-idp/bin/build.sh

   * .. code-block:: text

        sudo systemctl restart jetty

[`TOC`_]

Change default login page footer text
-------------------------------------

Change the content of ``idp.footer`` variable into all ``messages*.properties`` files linked to the view ``view/login.vm``:

* .. code-block:: text

     cd /opt/shibboleth-idp

* .. code-block:: text

     vim messages/messages.properties

  .. code-block:: xml+jinja

     idp.footer=Footer text for english version of IdP login page

* .. code-block:: text

     vim messages/messages_it.properties:

  .. code-block:: xml+jinja

     idp.footer=Testo del Footer a pie di pagina per la versione italiana della pagina di login dell'IdP

[`TOC`_]

Change default "Forgot your password?" and "Need help?" endpoints
-----------------------------------------------------------------

Change the content of ``idp.url.password.reset`` and ``idp.url.helpdesk`` variables into ``messages*.properties`` files linked to the view ``view/login.vm``:

* Move to the IdP Home:

  .. code-block:: text

     cd /opt/shibboleth-idp

* Modiy ``messages.properties``:

  .. code-block:: text

     vim messages/messages.properties

  .. code-block:: xml+jinja

     idp.url.password.reset=CONTENT-FOR-FORGOT-YOUR-PASSWORD-LINK
     idp.url.helpdesk=CONTENT-FOR-NEED-HELP-LINK

* Modiy ``messages_it.properties``:

  .. code-block:: text

     vim messages/messages_it.properties

  .. code-block:: xml+jinja

     idp.url.password.reset=CONTENUTO-PER-LINK-PASSWORD-DIMENTICATA
     idp.url.helpdesk=CONTENUTO-PER-SERVE-AIUTO-LINK

[`TOC`_]

Update IdP metadata
-------------------

**(only for italian identity federation IDEM members)**

#. Modify the IdP metadata as follow:

   .. code-block:: text

      vim /opt/shibboleth-idp/metadata/idp-metadata.xml

   #. Remove completely the initial default comment

   #. Remove completely the comment containing ``<mdui:UIInfo>`` element from ``<IDPSSODescriptor>`` Section.

   #. Add the ``HTTP-Redirect`` and ``HTTP-Post`` SingleLogoutService endpoints under the ``SOAP`` one:

      .. code-block:: xml+jinja

         <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://idp.example.org/idp/profile/SAML2/Redirect/SLO"/>
         <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://idp.example.org/idp/profile/SAML2/POST/SLO"/>

      (replace ``idp.example.org`` value with the Full Qualified Domain Name of the Identity Provider.)

   #. Between the last ``<SingleLogoutService>`` and the first ``<SingleSignOnService>`` endpoints add:

      .. code-block:: xml+jinja

         <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</md:NameIDFormat>
         <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</md:NameIDFormat>

      (because the IdP installed with this guide will release transient NameID, by default, and persistent NameID if requested.)

#. Check that the metadata is available on ``/idp/shibboleth`` location:

``https://idp.example.org/idp/shibboleth``

[`TOC`_]

Secure cookies and other IDP data
---------------------------------

DOC: `SecretKeyManagement`_

The default configuration of the IdP relies on a component called a "DataSealer" which in turn uses an AES secret key to secure cookies and certain other data for the IdPs own use. This key must never be shared with anybody else, and must be copied to every server node making up a cluster.
The Java "JCEKS" keystore file stores secret keys instead of public/private keys and certificates and a parallel file tracks the key version number.

These instructions will regularly update the secret key (and increase its version) and provide you the capability to push it to cluster nodes and continually maintain the secrecy of the key.

#. Download ``updateIDPsecrets.sh`` into the right location:

   .. code-block:: text

      wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/bin/updateIDPsecrets.sh -O /opt/shibboleth-idp/bin/updateIDPsecrets.sh

#. Provide the right privileges to the script:

   .. code-block:: text

      sudo chmod +x /opt/shibboleth-idp/bin/updateIDPsecrets.sh

#. Create the CRON script to run it:

   .. code-block:: text

      sudo vim /etc/cron.daily/updateIDPsecrets

   .. code-block:: text

      #!/bin/bash

      /opt/shibboleth-idp/bin/updateIDPsecrets.sh

#. Provide the right privileges to the script:

   .. code-block:: text

      sudo chmod +x /etc/cron.daily/updateIDPsecrets

#. Confirm that the script will be run daily with (you should see your script in the command output):

   .. code-block:: text

      sudo run-parts --test /etc/cron.daily

#. (OPTIONAL) Add the following properties to ``conf/idp.properties`` if you need to set different values than defaults:

   * ``idp.sealer._count`` - Number of earlier keys to keep (default 30)
   * ``idp.sealer._sync_hosts`` - Space separated list of hosts to scp the sealer files to (default generate locally)

[`TOC`_]

Configure Attribute Filter Policy to release attributes to Federated Resources
------------------------------------------------------------------------------

Follow these steps **ONLY IF** your organization is connected to the `GARR Network`_.

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Create the directory ``tmp/httpClientCache`` used by ``shibboleth.FileCachingHttpClient``:

   .. code-block:: text

      mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown jetty /opt/shibboleth-idp/tmp/httpClientCache

#. Modify your ``services.xml``:

   .. code-block:: text

      vim /opt/shibboleth-idp/conf/services.xml

   and add the following two beans on the top of the file, under the first ``<beans>`` TAG, only one time:

   .. code-block:: xml+jinja

      <bean id="MyHTTPClient" parent="shibboleth.FileCachingHttpClientFactory"
            p:connectionTimeout="PT30S"
            p:connectionRequestTimeout="PT30S"
            p:socketTimeout="PT30S"
            p:cacheDirectory="%{idp.home}/tmp/httpClientCache" />

      <bean id="IdemAttributeFilterFull" class="net.shibboleth.ext.spring.resource.FileBackedHTTPResource"
            c:client-ref="MyHTTPClient"
            c:url="https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/conf/idem-attribute-filter-v5-full.xml"
            c:backingFile="%{idp.home}/conf/idem-attribute-filter-full.xml"/>

   and enrich the ``AttributeFilterResources`` list with ``IdemAttributeFilterFull``:

   .. code-block:: xml+jinja

      <!-- ...other things... -->

      <util:list id ="shibboleth.AttributeFilterResources">
          <value>%{idp.home}/conf/attribute-filter.xml</value>
          <ref bean="IdemAttributeFilterFull"/>
      </util:list>

      <!-- ...other things... -->

#. Restart Jetty to apply the changes:

   .. code-block:: text

      systemctl restart jetty.service

#. Check IdP Status:

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/status.sh

[`TOC`_]

Register the IdP on the IDEM Test Federation
--------------------------------------------

Follow these steps **ONLY IF** your organization is connected to the `GARR Network`_.

#. Register you IdP metadata on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):

   https://registry.idem.garr.it/

#. Configure the IdP to retrieve the Federation Metadata through **IDEM MDX**: https://mdx.idem.garr.it/

#. Check that your IdP release at least eduPersonScopedAffiliation, eduPersonTargetedID and a saml2:NameID transient/persistent to the testing SP provided by IDEM:

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/aacli.sh -n <USERNAME> -r https://sp.example.org/shibboleth --saml2

   (the command will have a ``transient`` NameID into the Subject of the assertion)

   .. code-block:: text

      bash /opt/shibboleth-idp/bin/aacli.sh -n <USERNAME> -r https://sp.aai-test.garr.it/shibboleth --saml2

   (the command will have a ``persistent`` NameID into the Subject of the assertion)

#. Wait that your IdP Metadata is approved by an IDEM Federation Operator into the IDEM Test Federation metadata stream and the next steps provided by the operator itself.

[`TOC`_]

Appendix A: Enable Consent Module: Attribute Release + Terms of Use Consent
---------------------------------------------------------------------------

DOC: `ConsentConfiguration`_

The IdP includes the ability to require user consent to attribute release,
as well as presenting a "terms of use" message prior to completing a login to a service,
a simpler "static" form of consent.

#. Move to IdP home dir:

   .. code-block:: text

      cd /opt/shibboleth-idp

#. Load Consent Module:

   .. code-block:: text

      bin/module.sh -t idp.intercept.Consent || bin/module.sh -e idp.intercept.Consent

#. Enable Consent Module by editing ``conf/relying-party.xml`` with the right ``postAuthenticationFlows``:

   * ``<bean parent="SAML2.SSO" p:postAuthenticationFlows="attribute-release" />`` - to enable only Attribute Release Consent
   * ``<bean parent="SAML2.SSO" p:postAuthenticationFlows="#{ {'terms-of-use', 'attribute-release'} }" />`` - to enable both

#. Restart Jetty:

   .. code-block:: text

      sudo systemctl restart jetty.service

[`TOC`_]

Appendix B: Import persistent-id from a previous database
---------------------------------------------------------

Follow these steps **ONLY IF** your need to import persistent-id database from another IdP

#. Become ROOT:

   .. code-block:: text

      sudo su -

#. Create a DUMP of ``shibpid`` table from the previous DB ``shibboleth`` on the OLD IdP:

   .. code-block:: text

      cd /tmp

      mysqldump --complete-insert --no-create-db --no-create-info -u root -p shibboleth shibpid > /tmp/shibboleth_shibpid.sql

#. Copy the ``/tmp/shibboleth_shibpid.sql`` from the old IdP into ``/tmp/shibboleth_shibpid.sql`` on the new IdP.

#. Import the content of ``/tmp/shibboleth_shibpid.sql`` into database of the new IDP:

   .. code-block:: text

      cd /tmp ; mysql -u root -p shibpid < /tmp/shibboleth_shibpid.sql

#. Delete ``/tmp/shibboleth_shibpid.sql``:

   .. code-block:: text

      rm /tmp/shibboleth_shibpid.sql

[`TOC`_]

Appendix C: Useful logs to find problems
----------------------------------------

Follow this if you need to find a problem of your IdP.

#. Jetty Logs:

   .. code-block:: text

      cd /opt/jetty/logs

      ls -l *.stderrout.log

#. Shibboleth IdP Logs:

   .. code-block:: text

      cd /opt/shibboleth-idp/logs

   * **Audit Log:** ``vim idp-audit.log``
   * **Consent Log:** ``vim idp-consent-audit.log``
   * **Warn Log:** ``vim idp-warn.log``
   * **Process Log:** ``vim idp-process.log``

[`TOC`_]

Appendix D: Connect an SP with the IdP
--------------------------------------

DOC:

* `ChainingMetadataProvider`_
* `FileBackedHTTPMetadataProvider`_
* `AttributeFilterConfiguration`_
* `AttributeFilterPolicyConfiguration`_

Follow these steps **IF** your organization **IS NOT** connected to the `GARR Network`_.

#. Connect the SP to the IdP by adding its metadata on the ``metadata-providers.xml`` configuration file:

   .. code-block:: text

      vim /opt/shibboleth-idp/conf/metadata-providers.xml

   .. code-block:: xml+jinja

     <MetadataProvider id="HTTPMetadata"
                       xsi:type="FileBackedHTTPMetadataProvider"
                       backingFile="%{idp.home}/metadata/sp-metadata.xml"
                       metadataURL="https://sp.example.org/Shibboleth.sso/Metadata"
                       failFastInitialization="false"/>

#. Adding an ``AttributeFilterPolicy`` on the ``conf/attribute-filter.xml`` file:

   * .. code-block:: text

        wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/conf/idem-example-arp.txt -O /opt/shibboleth-idp/conf/example-arp.txt

   * .. code-block:: text

        cat /opt/shibboleth-idp/conf/example-arp.txt

   * Copy and paste the content into ``/opt/shibboleth-idp/conf/attribute-filter.xml`` before the last element ``</AttributeFilterPolicyGroup>``.

   * Make sure to change the value of the placeholder **### SP-ENTITYID ###** on the text pasted with the entityID of the Service Provider to connect with the Identity Provider installed.

#. Restart Jetty to apply changes:

   .. code-block:: text

      systemctl restart jetty.service

[`TOC`_]

Utilities
---------

* AACLI: Useful to understand which attributes will be released to the federated resources

  * ``export JAVA_HOME=/usr/lib/jvm/java-11-amazon-corretto``
  * ``bash /opt/shibboleth-idp/bin/aacli.sh -n <USERNAME> -r <ENTITYID-SP> --saml2``

* `The Mozilla Observatory`_:
  The Mozilla Observatory has helped over 240,000 websites by teaching developers, system administrators, and security professionals how to configure their sites safely and securely.

[`TOC`_]

Useful Documentation
++++++++++++++++++++

* `SpringConfiguration`_
* `ConfigurationFileSummary`_
* `LoggingConfiguration`_
* `AuditLoggingConfiguration`_
* `FTICKSLoggingConfiguration`_
* `MetadataConfiguration`_
* `PasswordAuthnConfiguration`_
* `AttributeResolverConfiguration`_
* `AttributeFilter`_
* `LDAPConnector`_
* `AttributeRegistryConfiguration`_
* `TranscodingRuleConfiguration`_
* `HTTPResource`_
* `SAMLKeysAndCertificates`_
* `SecretKeyManagement`_
* `NameIDGenerationConfiguration`_
* `GCMEncryption`_
* `Switching locale on the login page`_
* `WebInterfaces`_
* `Cross-Site Request Forgery CSRF Protection`_

[`TOC`_]

Authors
+++++++

Original Author
***************

Marco Malavolti (marco.malavolti@garr.it)

[`TOC`_]

.. _Amazon: https://docs.aws.amazon.com/corretto/latest/corretto-17-ug/downloads-list.html#signature
.. _SSLLabs: https://www.ssllabs.com/ssltest/analyze.html
.. _StorageConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509576/StorageConfiguration
.. _Idp4noGCMsps: https://wiki.idem.garr.it/wiki/Idp4noGCMsps
.. _MessagesTranslation: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501275/MessagesTranslation
.. _GARR Network: https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites
.. _The Mozilla Observatory: https://observatory.mozilla.org/
.. _Shibboleth download site: https://shibboleth.net/downloads/identity-provider/
.. _NSA and NIST: https://www.keylength.com/en/compare/
.. _PersistentNameIDGenerationConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199507892/PersistentNameIDGenerationConfiguration
.. _SecretKeyManagement: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501624/SecretKeyManagement
.. _ConsentConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509862/ConsentConfiguration
.. _ChainingMetadataProvider: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199506765/ChainingMetadataProvider
.. _FileBackedHTTPMetadataProvider: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199506865/FileBackedHTTPMetadataProvider
.. _AttributeFilterConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501794/AttributeFilterConfiguration
.. _AttributeFilterPolicyConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501835/AttributeFilterPolicyConfiguration
.. _AttributeFilter: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199511838/AttributeFilter
.. _SpringConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199508919/SpringConfiguration
.. _ConfigurationFileSummary: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199506590/ConfigurationFileSummary
.. _LoggingConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509659/LoggingConfiguration
.. _AuditLoggingConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509698/AuditLoggingConfiguration
.. _FTICKSLoggingConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509739/FTICKSLoggingConfiguration
.. _MetadataConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199506698/MetadataConfiguration
.. _PasswordAuthnConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199505587/PasswordAuthnConfiguration
.. _AttributeResolverConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199502864/AttributeResolverConfiguration
.. _LDAPConnector: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199503855/LDAPConnector
.. _AttributeRegistryConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199510514/AttributeRegistryConfiguration
.. _TranscodingRuleConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199510553/TranscodingRuleConfiguration
.. _HTTPResource: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199507990/HTTPResource
.. _SAMLKeysAndCertificates: https://shibboleth.atlassian.net/wiki/spaces/CONCEPT/pages/948470554/SAMLKeysAndCertificates
.. _NameIDGenerationConfiguration: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199507810/NameIDGenerationConfiguration
.. _GCMEncryption: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501202/GCMEncryption
.. _Switching locale on the login page: https://shibboleth.atlassian.net/wiki/spaces/KB/pages/1435927082/Switching+locale+on+the+login+page
.. _WebInterfaces: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199511365/WebInterfaces
.. _Cross-Site Request Forgery CSRF Protection: https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501137/Cross-Site+Request+Forgery+CSRF+Protection
.. _IDEM MDX: https://mdx.idem.garr.it/
.. _TOC: `Table of Contents`_
