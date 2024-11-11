# HOWTO Install and Configure a Shibboleth IdP v5.x on Debian-Ubuntu Linux with Apache + Jetty

<img src="https://wiki.idem.garr.it/IDEM_Approved.png" width="120" alt="image" />

## Table of Contents

1.  [Requirements](#requirements)
    1.  [Hardware](#hardware)
    2.  [Software](#software)
    3.  [Others](#others)
2.  [Notes](#notes)
3.  [Configure the environment](#configure-the-environment)
4.  [Configure APT Mirror](#configure-apt-mirror)
5.  [Install Dependencies](#install-dependencies)
6.  [Install software requirements](#install-software-requirements)
    1.  [Install Apache Web Server](#install-apache-web-server)
    2.  [Install Amazon Corretto JDK](#install-amazon-corretto-jdk)
    3.  [Install Jetty Servlet Container](#install-jetty-servlet-container)
7.  [Install Shibboleth Identity Provider](#install-shibboleth-identity-provider)
8.  [Disable Jetty Directory Indexing](#disable-jetty-directory-indexing)
9.  [Configure Apache Web Server](#configure-apache-web-server)
10. [Configure Jetty Context Descriptor for IdP](#configure-jetty-context-descriptor-for-idp)
11. [Configure Apache2 as the front-end of Jetty](#configure-apache2-as-the-front-end-of-jetty)
12. [Configure Shibboleth Identity Provider Storage Service](#configure-shibboleth-identity-provider-storage-service)
    1.  [Strategy A - Default (HTML Local Storage, Encryption GCM, No Database) - Recommended](#strategy-a---default-html-local-storage-encryption-gcm-no-database---recommended)
    2.  [Strategy B - JDBC Storage Service - using a database](#strategy-b---jdbc-storage-service---using-a-database)
13. [Configure the Directory Connection](#configure-the-directory-connection)
    1.  [openLDAP directory connection](#openldap-directory-connection)
    2.  [Active Directory connection](#active-directory-connection)
14. [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)
    1.  [Strategy A - Computed mode (Default) - Recommended](#strategy-a---computed-mode-default---recommended)
    2.  [Strategy B - Stored mode - using a database](#strategy-b---stored-mode---using-a-database)
15. [Configure the attribute resolver (sample)](#configure-the-attribute-resolver-sample)
16. [Configure Shibboleth Identity Provider to release the eduPersonTargetedID](#configure-shibboleth-identity-provider-to-release-the-edupersontargetedid)
    1.  [Strategy A - Computed mode - using the computed persistent NameID - Recommended](#strategy-a---computed-mode---using-the-computed-persistent-nameid---recommended)
    2.  [Strategy B - Stored mode - using the persistent NameID database](#strategy-b---stored-mode---using-the-persistent-nameid-database)
17. [Configure Shibboleth IdP Logging](#configure-shibboleth-idp-logging)
18. [Translate IdP messages into preferred language](#translate-idp-messages-into-preferred-language)
19. [Enrich IdP Login Page with the Institutional Logo](#enrich-idp-login-page-with-the-institutional-logo)
20. [Enrich IdP Login Page with Information and Privacy Policy pages](#enrich-idp-login-page-with-information-and-privacy-policy-pages)
21. [Change default login page footer text](#change-default-login-page-footer-text)
22. [Change default "Forgot your password?" and "Need help?" endpoints](#change-default-forgot-your-password-and-need-help-endpoints)
23. [Update IdP metadata](#update-idp-metadata)
24. [Secure cookies and other IDP data](#secure-cookies-and-other-idp-data)
25. [Configure Attribute Filter Policy to release attributes to Federated Resources](#configure-attribute-filter-policy-to-release-attributes-to-federated-resources)
26. [Register the IdP on the IDEM Test Federation](#register-the-idp-on-the-idem-test-federation)
27. [Appendix A: Enable Consent Module (Attribute Release + Terms of Use Consent)](#appendix-a-enable-consent-module-attribute-release--terms-of-use-consent)
28. [Appendix B: Import persistent-id from a previous database](#appendix-b-import-persistent-id-from-a-previous-database)
29. [Appendix C: Useful logs to find problems](#appendix-c-useful-logs-to-find-problems)
30. [Appendix D: Connect an SP with the IdP](#appendix-d-connect-an-sp-with-the-idp)
31. [Utilities](#utilities)
32. [Useful Documentation](#useful-documentation)
33. [Authors](#authors)

## Requirements

### Hardware

-   CPU: 2 Core (64 bit)
-   RAM: 2 GB (with IDEM MDX), 4GB (without IDEM MDX)
-   HDD: 10 GB
-   OS: Debian (>= 12) / Ubuntu LTS (>= 22.04)

### Software

-   Apache Web Server (*\>= 2.4*)
-   Jetty 11+ Servlet Container (*implementing Servlet API 5.0 or above*)
-   Amazon Corretto JDK 17
-   OpenSSL (*\>= 3.0.2*)
-   Shibboleth Identity Provider (*\>= 5.0.0*)

### Others

-   SSL Credentials: HTTPS Certificate & Private Key
-   Logo:
    -   size: 80x60 px (or other that respect the aspect-ratio)
    -   format: PNG
    -   style: with a transparent background
-   Favicon:
    -   size: 16x16 px (or other that respect the aspect-ratio)
    -   format: PNG
    -   style: with a transparent background

[[TOC](#table-of-contents)]

## Notes

This HOWTO uses `example.org` and `idp.example.org` as example values.

Please remember to **replace all occurencences** of:

-   the `example.org` value with the IdP domain name
-   the `idp.example.org` value with the Full Qualified Domain Name of the Identity Provider.

[[TOC](#table-of-contents)]

## Configure the environment

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Be sure that your firewall **is not blocking** the traffic on port **443** and **80** for the IdP server.

3.  Set the IdP hostname:

    **!!!ATTENTION!!!**: Replace `idp.example.org` with your IdP Full Qualified Domain Name and `<HOSTNAME>` with the IdP hostname

    -   ``` text
        echo "<YOUR-SERVER-IP-ADDRESS> idp.example.org <HOSTNAME>" >> /etc/hosts
        ```

    -   ``` text
        hostnamectl set-hostname <HOSTNAME>
        ```

4.  Set the variable `JAVA_HOME` into `/etc/environment`:

    -   ``` text
        echo 'JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto' > /etc/environment
        ```

    -   ``` text
        source /etc/environment
        ```

    -   ``` text
        export JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto
        ```

    -   ``` text
        echo $JAVA_HOME
        ```

[[TOC](#table-of-contents)]

## Configure APT Mirror

Debian Mirror List: <https://www.debian.org/mirror/list>

Ubuntu Mirror List: <https://launchpad.net/ubuntu/+archivemirrors>

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  (**only for italian institutions**) Change the default mirror to the GARR ones:

    -   Debian 12 - Deb822 file format:

        ``` text
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
        ```

    -   Ubuntu:

        ``` text
        bash -c 'cat > /etc/apt/sources.list.d/garr.list <<EOF
        deb https://ubuntu.mirror.garr.it/ubuntu/ jammy main
        deb-src https://ubuntu.mirror.garr.it/ubuntu/ jammy main
        EOF'
        ```

3.  Update packages:

    ``` text
    apt update && apt-get upgrade -y --no-install-recommends
    ```

[[TOC](#table-of-contents)]

## Install Dependencies

``` text
sudo apt install fail2ban vim wget gnupg ca-certificates openssl ntp --no-install-recommends
```

[[TOC](#table-of-contents)]

## Install software requirements

### Install Apache Web Server

The Apache HTTP Server will be configured as a reverse proxy and it will be used for SSL offloading.

``` text
sudo apt install apache2
```

[[TOC](#table-of-contents)]

### Install Amazon Corretto JDK

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Download the Public Key *B04F24E3.pub* into `/tmp` dir to verify the signature file from [Amazon](https://docs.aws.amazon.com/corretto/latest/corretto-17-ug/downloads-list.html#signature).

3.  Convert Public Key into "**amazon-corretto.gpg**":

    -   ``` text
        gpg --no-default-keyring --keyring /tmp/temp-keyring.gpg --import /tmp/B04F24E3.pub
        ```

    -   ``` text
        gpg --no-default-keyring --keyring /tmp/temp-keyring.gpg --export --output /etc/apt/keyrings/amazon-corretto.gpg
        ```

    -   ``` text
        rm /tmp/temp-keyring.gpg /tmp/B04F24E3.pub /tmp/temp-keyring.gpg~
        ```

4.  Create an APT source list for Amazon Corretto:

    -   ``` text
        echo "deb [signed-by=/etc/apt/keyrings/amazon-corretto.gpg] https://apt.corretto.aws stable main" >> /etc/apt/sources.list.d/amazon-corretto.list
        ```

    -   ``` text
        echo "#deb-src [signed-by=/etc/apt/keyrings/amazon-corretto.gpg] https://apt.corretto.aws stable main" >> /etc/apt/sources.list.d/amazon-corretto.list
        ```

5.  Install Amazon Corretto:

    ``` text
    apt update ; apt install -y java-17-amazon-corretto-jdk
    ```

6.  Check that Java is working:

    ``` text
    java --version
    ```

    Result: `OpenJDK Runtime Environment Corretto-<VERSION>`

[[TOC](#table-of-contents)]

### Install Jetty Servlet Container

Jetty is a Web server and a Java Servlet container. It will be used to run the IdP application through its WAR file.

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Download and Extract Jetty:

    -   ``` text
        cd /usr/local/src
        ```

    -   ``` text
        wget https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-home/11.0.19/jetty-home-11.0.19.tar.gz
        ```

    -   ``` text
        tar xzvf jetty-home-11.0.19.tar.gz
        ```

3.  Create the `jetty-src` folder as a symbolic link. It will be useful for future Jetty updates:

    ``` text
    ln -nsf jetty-home-11.0.19 jetty-src
    ```

4.  Create the system user `jetty` that can run the web server (without home directory):

    ``` text
    useradd -r -M jetty
    ```

5.  Create your custom Jetty configuration that overrides the default one and will survive upgrades:

    -   ``` text
        mkdir -p /opt/jetty
        ```

    -   ``` text
        wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/jetty-conf/start.ini -O /opt/jetty/start.ini
        ```

        (the `start.ini` provided is adapted to be used with [IDEM MDX](https://mdx.idem.garr.it/) service)

6.  Create the TMPDIR directory used by Jetty:

    -   ``` text
        mkdir /opt/jetty/tmp ; chown jetty:jetty /opt/jetty/tmp
        ```

    -   ``` text
        chown -R jetty:jetty /opt/jetty /usr/local/src/jetty-src
        ```

7.  Create the Jetty Logs' folders:

    -   ``` text
        mkdir /var/log/jetty
        ```

    -   ``` text
        mkdir /opt/jetty/logs
        ```

    -   ``` text
        chown jetty:jetty /var/log/jetty /opt/jetty/logs
        ```

8. Configure **/etc/default/jetty**:

    ``` bash
    bash -c 'cat > /etc/default/jetty <<EOF
    JETTY_HOME=/usr/local/src/jetty-src
    JETTY_BASE=/opt/jetty
    JETTY_PID=/opt/jetty/jetty.pid
    JETTY_USER=jetty
    JETTY_START_LOG=/var/log/jetty/start.log
    TMPDIR=/opt/jetty/tmp
    EOF'
    ```

9. Create the service loadable from command line:

    -   ``` text
        cd /etc/init.d
        ```

    -   ``` text
        ln -s /usr/local/src/jetty-src/bin/jetty.sh jetty
        ```

    -   ``` text
        sudo update-alternatives --config editor
        ```

        (select `/usr/bin/vim.basic` or what do you prefer as editor)


    -   ``` text
        cp /usr/local/src/jetty-src/bin/jetty.service /etc/systemd/system/jetty.service
        ```

    -   Fix the `PIDFile` parameter with the `JETTY_PID` path:

        -   ``` text
            systemctl edit --full jetty.service
            ```

            ``` text
            PIDFile=/opt/jetty/jetty.pid
            ```

    -   ``` text
        systemctl daemon-reload
        ```

    -   ``` text
        systemctl enable jetty.service
        ```

10. Install Servlet Jakarta API 5.0.0:

    -   ``` text
        apt install libjakarta-servlet-api-java
        ```

11. Install & configure LogBack for all Jetty logging:

    -   ```text
        cd /opt/jetty
        ```

    -   ``` text
        java -jar /usr/local/src/jetty-src/start.jar --add-module=logging-logback
        ```

    -   ``` text
        mkdir /opt/jetty/etc
        ```

    -   ``` text
        mkdir /opt/jetty/resources
        ```

    -   ``` text
        wget "https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/jetty-conf/jetty-requestlog.xml" -O /opt/jetty/etc/jetty-requestlog.xml
        ```

    -   ``` text
        wget "https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/jetty-conf/jetty-logging.properties" -O /opt/jetty/resources/jetty-logging.properties
        ```

12. Check if all settings are OK:

    -   `service jetty check` (Jetty NOT running)
    -   `service jetty start`
    -   `service jetty check` (Jetty running pid=XXXX)

    If you receive an error likes "*Job for jetty.service failed because the control process exited with error code. See "systemctl status jetty.service" and "journalctl -xe" for details.*", try this:

    -   ``` text
        rm /opt/jetty/jetty.pid
        ```

    -   ``` text
        systemctl start jetty.service
        ```

[[TOC](#table-of-contents)]

## Install Shibboleth Identity Provider

The Identity Provider (IdP) is responsible for user authentication and providing user information to the Service Provider (SP). 
It is located at the home organization, which is the organization which maintains the,user's account. 
It is a Java Web Application that can be deployed with its WAR file.

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Download the Shibboleth Identity Provider v5.x.y (replace '5.x.y' with the latest version found on the [Shibboleth download site](https://shibboleth.net/downloads/identity-provider/)):

    -   ``` text
        cd /usr/local/src
        ```

    -   ``` text
        wget http://shibboleth.net/downloads/identity-provider/5.x.y/shibboleth-identity-provider-5.x.y.tar.gz
        ```

    -   ``` text
        tar -xzf shibboleth-identity-provider-5.*.tar.gz
        ```

3.  Validate the package downloaded:

    -   ``` text
        cd /usr/local/src
        ```

    -   ``` text
        wget https://shibboleth.net/downloads/identity-provider/5.x.y/shibboleth-identity-provider-5.x.y.tar.gz.asc
        ```

    -   ``` text
        wget https://shibboleth.net/downloads/PGP_KEYS
        ```

    -   ``` text
        gpg --import /usr/local/src/PGP_KEYS
        ```

    -   ``` text
        gpg --verify /usr/local/src/shibboleth-identity-provider-5.x.y.tar.gz.asc /usr/local/src/shibboleth-identity-provider-5.x.y.tar.gz
        ```

    If the verification contains also the name of Scott Cantor the package is valid.

4.  Install Identity Provider Shibboleth:

    **NOTE**

    According to [NSA and NIST](https://www.keylength.com/en/compare/), **RSA with 3072 bit-modulus is the minimum** to protect up to TOP SECRET over than 2030.

    -   ``` text
        cd /usr/local/src/shibboleth-identity-provider-5.*/bin
        ```

    -   ``` text
        bash install.sh --hostName $(hostname -f)
        ```

    **!!! ATTENTION !!!**

    Replace the default value of `Attribute Scope` with the domain name of your institution.

    ``` bash
    Installation Directory: [/opt/shibboleth-idp] ?                                        (Press ENTER)
    SAML EntityID: [https://idp.example.org/idp/shibboleth] ?                              (Press ENTER)
    Attribute Scope: [example.org] ?                            (Digit your domain name and press ENTER)
    ```

    By starting from this point, the variable **%{idp.home}** into some IdP configuration files refers to the directory: `/opt/shibboleth-idp`

    From the v5.1.3, the installer miss a space between `<md:EntityDescriptor` and `entityID` into the `/opt/shibboleth-idp/idp-metadata.xml`. **Make sure to add it before procede.**

[[TOC](#table-of-contents)]

## Disable Jetty Directory Indexing

**!!! ATTENTION !!!**

Jetty has had vulnerabilities related to directory indexing (sigh) so we suggest disabling that feature at this point.

1.  Create missing directory:

    ``` text
    mkdir /opt/shibboleth-idp/edit-webapp/WEB-INF
    ```

2.  Fix `web.xml`:

    ``` text
    cp /opt/shibboleth-idp/dist/webapp/WEB-INF/web.xml /opt/shibboleth-idp/edit-webapp/WEB-INF/web.xml
    ```

3.  Rebuild IdP war file:

    ``` text
    bash /opt/shibboleth-idp/bin/build.sh
    ```

[[TOC](#table-of-contents)]

## Configure Apache Web Server

1.  Create the DocumentRoot:

    -   ``` text
        mkdir /var/www/html/$(hostname -f)
        ```

    -   ``` text
        chown -R www-data: /var/www/html/$(hostname -f)
        ```

    -   ``` text
        echo '<h1>It Works!</h1>' > /var/www/html/$(hostname -f)/index.html
        ```

2.  Put SSL credentials in the right place:

    -   HTTPS Server Certificate (Public Key) inside `/etc/ssl/certs`

    -   HTTPS Server Key (Private Key) inside `/etc/ssl/private`

    -   Add CA Cert into `/etc/ssl/certs`
        -   If you use GARR TCS or GEANT TCS:

            -   ``` text
                wget -O /etc/ssl/certs/GEANT_OV_RSA_CA_4.pem https://crt.sh/?d=2475254782
                ```
        
            -   ``` text
                wget -O /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt https://crt.sh/?d=924467857
                ```
        
            -   ``` text
                cat /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt >> /etc/ssl/certs/GEANT_OV_RSA_CA_4.pem
                ```
        
            -   ``` text
                rm /etc/ssl/certs/SectigoRSAOrganizationValidationSecureServerCA.crt
                ```

        -   If you use ACME (Let's Encrypt):

            ``` text
            ln -s /etc/letsencrypt/live/<SERVER_FQDN>/chain.pem /etc/ssl/certs/ACME-CA.pem
            ```

3.  Configure the right privileges for the SSL Certificate and Key used by HTTPS:

    -   ``` text
        chmod 400 /etc/ssl/private/$(hostname -f).key
        ```

    -   ``` text
        chmod 644 /etc/ssl/certs/$(hostname -f).crt
        ```

    (`$(hostname -f)` will provide your IdP Full Qualified Domain Name)

4.  Enable the required Apache2 modules and the virtual hosts:

    -   ``` text
        a2enmod proxy_http ssl headers alias include negotiation
        ```

    -   ``` text
        a2dissite 000-default.conf default-ssl
        ```

    -   ``` text
        systemctl restart apache2.service
        ```

[[TOC](#table-of-contents)]

## Configure Jetty Context Descriptor for IdP

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Configure the Jetty Context Descriptor:

    -   ``` text
        mkdir /opt/jetty/webapps
        ```

    -   ``` text
        wget "https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/jetty-conf/idp.xml" -O /opt/jetty/webapps/idp.xml
        ```

3.  Make the **jetty** user owner of IdP main directories:

    -   ``` text
        cd /opt/shibboleth-idp
        ```

    -   ``` text
        chown -R jetty logs/ metadata/ credentials/ conf/ war/
        ```

4.  Restart Jetty:

    ``` text
    service jetty restart
    ```

[[TOC](#table-of-contents)]

## Configure Apache2 as the front-end of Jetty

The Apache HTTP Server will be configured as a reverse proxy and it will be used for SSL offloading.

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Create the Virtualhost file:

    ``` text
    wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/apache-conf/idp.example.org.conf -O /etc/apache2/sites-available/$(hostname -f).conf
    ```

    (do not change `idp.example.org` with the FQDN of the IdP on the GitHub URL provided)

3.  Edit the Virtualhost file (**PLEASE PAY ATTENTION! you need to edit this file and customize it, check the initial comment of the file**):

    ``` text
    vim /etc/apache2/sites-available/$(hostname -f).conf
    ```

4.  Enable the Apache2 virtual hosts created:

    -   ``` text
        a2ensite $(hostname -f).conf
        ```

    -   ``` text
        systemctl reload apache2.service
        ```

5.  Check that IdP metadata is available on:

    `https://idp.example.org/idp/shibboleth`

6.  Verify the strength of your IdP's machine on [SSLLabs](https://www.ssllabs.com/ssltest/analyze.html).

[[TOC](#table-of-contents)]

## Configure Shibboleth Identity Provider Storage Service

Shibboleth Documentation reference: [StorageConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509576/StorageConfiguration)

The IdP provides a number of general-purpose storage facilities that can be used by core subsystems like session management and consent.

### Strategy A - Default (HTML Local Storage, Encryption GCM, No Database) - Recommended

The HTML Local Storage requires JavaScript be enabled because reading and writing to the client requires an explicit page be rendered.
Note that this feature is safe to enable globally. 
The implementation is written to check for this capability in each client, and to back off to cookies.
The default configuration generates encrypted assertions that a large percentage of non-Shibboleth SPs are going to be unable to decrypt, resulting a wide variety of failures and error messages. 
Some old Shibboleth SPs or software running on old Operating Systems will also fail to work.

**!!! DO IT BECAUSE IT IS IMPORTANT !!!**

**(only for Italian Identity Federation IDEM members)**

The IDEM Federation Operators collect a list of Service Providers that don't support the new default encryption algorithm and provide a solution on his wiki pages:

-   [Idp4noGCMsps](https://wiki.idem.garr.it/wiki/Idp4noGCMsps)

If you don't change anything, the IdP stores data in a browser session cookie or HTML local storage and encrypt his assertions with AES-GCM encryption algorithm.

See the configuration files and the Shibboleth documentation for details.

Check IdP Status:

``` text
bash /opt/shibboleth-idp/bin/status.sh
```

Proceed with [Configure the Directory Connection](#configure-the-directory-connection)

[[TOC](#table-of-contents)]

### Strategy B - JDBC Storage Service - using a database

<https://shibboleth.atlassian.net/wiki/spaces/IDPPLUGINS/pages/2989096970/JDBCStorageService>

This Storage service will memorize User Consent data on a persistent SQL database.

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Install SQL database and needed libraries:

    ``` text
    apt install default-mysql-server libmariadb-java libcommons-dbcp2-java libcommons-pool2-java --no-install-recommends
    ```

3.  Install JDBCStorageService plugin:

    ``` text
    /opt/shibboleth-idp/bin/plugin.sh -I net.shibboleth.plugin.storage.jdbc
    ```

4.  Activate MariaDB database service:

    ``` text
    systemctl start mariadb.service
    ```

5.  Address several security concerns in a default MariaDB installation
    (if it is not already done):

    ``` text
    mysql_secure_installation
    ```

6.  (OPTIONAL) MySQL DB Access without password:

    ``` text
    vim /root/.my.cnf
    ```

    ``` text
    [client]
    user=root
    password=##ROOT-DB-PASSWORD-CHANGEME##
    ```

7.  Create `StorageRecords` table on the `storagerecords` database:

    ``` text
    wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/db-conf/shib-sr-db.sql -O /root/shib-sr-db.sql
    ```

    fill missing datas on the `shib-sr-db.sql` file before import:

    -   ``` text
        mysql -u root < /root/shib-sr-db.sql
        ```

    -   ``` text
        systemctl restart mariadb.service
        ```

8.  Rebuild IdP war file with the needed libraries:

    -   ``` text
        mkdir /opt/shibboleth-idp/edit-webapp/WEB-INF/lib
        ```

    -   ``` text
        ln -s /usr/share/java/mariadb-java-client.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib
        ```

    -   ``` text
        ln -s /usr/share/java/commons-dbcp2.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib
        ```

    -   ``` text
        ln -s /usr/share/java/commons-pool2.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib
        ```

    -   ``` text
        bash /opt/shibboleth-idp/bin/build.sh
        ```

9.  Configure JDBC Storage Service:

    ``` text
    vim /opt/shibboleth-idp/conf/global.xml
    ```

    and add the following directives to the tail, before the last `</beans>` tag:

    ``` xml+jinja
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
    ```

    **!!! IMPORTANT !!!**:

    remember to change "**\###\_SR-USERNAME-CHANGEME\_###**" and "**\###\_SR-DB-USER-PASSWORD-CHANGEME\_###**" with your DB user and password data.

10. Set the consent storage service to the JDBC storage service:

    * ``` text
      vim /opt/shibboleth-idp/conf/idp.properties
      ```

      ``` text
      idp.consent.StorageService = storagerecords.JDBCStorageService
      ```

11. Restart Jetty to apply the changes:

    ``` text
    service jetty restart
    ```

12. Check IdP Status:

    ``` text
    bash /opt/shibboleth-idp/bin/status.sh
    ```

13. Proceed with [Configure the Directory Connection](#configure-the-directory-connection)

[[TOC](#table-of-contents)]

## Configure the Directory Connection

### openLDAP directory connection

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Install useful packages:

    ``` text
    apt install ldap-utils
    ```

3.  Check that you can reach the Directory from your IDP server:

    ``` text
    ldapsearch -x -H ldap://<LDAP-SERVER-FQDN-OR-IP> -D 'cn=idpuser,ou=system,dc=example,dc=org' -w '<IDPUSER-PASSWORD>' -b 'ou=people,dc=example,dc=org' '(uid=<USERNAME-USED-IN-THE-LOGIN-FORM>)'
    ```

    -   the baseDN (`-b` parameter) ==\> `ou=people,dc=example,dc=org`
        (branch containing the registered users)
    -   the bindDN (`-D` parameter) ==\>
        `cn=idpuser,ou=system,dc=example,dc=org` (distinguished name for
        the user that can made queries on the LDAP, read only is
        sufficient)
    -   the searchFilter `(uid=<USERNAME-USED-IN-THE-LOGIN-FORM>)`
        corresponds to the `(uid=$resolutionContext.principal)`
        searchFilter configured into `conf/ldap.properties`

4.  Connect the openLDAP to the IdP to allow the authentication of the users:

    -   Solution 1 - LDAP + STARTTLS:

        -   Configure `secrets.properties`:

            ``` text
            vim /opt/shibboleth-idp/credentials/secrets.properties
            ```

            ``` xml+jinja
            # Default access to LDAP authn and attribute stores.
            idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
            idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
            ```

        -   Configure `ldap.properties`:

            The `ldap.example.org` have to be replaced with the FQDN of the LDAP server.

            The `idp.authn.LDAP.baseDN` and `idp.authn.LDAP.bindDN` have to be replaced with the right value.

            The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP.
            The list MUST contain the attribute chosen for the persistent-id generation (**idp.persistentId.sourceAttribute**).

            ``` text
            vim /opt/shibboleth-idp/conf/ldap.properties
            ```

            ``` xml+jinja
            idp.authn.LDAP.authenticator = bindSearchAuthenticator
            idp.authn.LDAP.ldapURL = ldap://ldap.example.org
            idp.authn.LDAP.useStartTLS = true
            idp.authn.LDAP.sslConfig = certificateTrust
            idp.authn.LDAP.trustCertificates = /opt/shibboleth-idp/credentials/ldap-server.crt
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
           
            # The userFilter is used to locate a directory entry to bind against for LDAP authentication.
            idp.authn.LDAP.userFilter = (uid={user})
            
            idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
            idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
            
            # The 'searchFilter' is is used to find user attributes from an LDAP source
            idp.attribute.resolver.LDAP.searchFilter        = (uid=$resolutionContext.principal)
            
            # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
            # The 'exportAttributes' contains a list space-separated of attributes to retrieve directly from the directory service.
            idp.attribute.resolver.LDAP.exportAttributes    = uid cn sn givenName mail eduPersonAffiliation
            ```

        -   Paste the OpenLDAP certificate into `/opt/shibboleth-idp/credentials/ldap-server.crt`.

        -   Configure the right owner/group for the OpenLDAP certificate loaded:

            ``` text
            chown jetty:root /opt/shibboleth-idp/credentials/ldap-server.crt ; chmod 600 /opt/shibboleth-idp/credentials/ldap-server.crt
            ```

        -   Restart Jetty to apply the changes:

            ``` text
            service jetty restart
            ```

        -   Check IdP Status:

            ``` text
            bash /opt/shibboleth-idp/bin/status.sh
            ```

        -   Proceed with [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)

    -   Solution 2 - LDAP + TLS:

        -   Configure `secrets.properties`:

            ``` text
            vim /opt/shibboleth-idp/credentials/secrets.properties
            ```

            ``` xml+jinja
            # Default access to LDAP authn and attribute stores.
            idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
            idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
            ```

        -   Configure `ldap.properties`:

            The `ldap.example.org` have to be replaced with the FQDN of the LDAP server.

            The `idp.authn.LDAP.baseDN` and `idp.authn.LDAP.bindDN` have to be replaced with the right value.

            The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP.
            The list MUST contain the attribute chosen for the persistent-id generation (**idp.persistentId.sourceAttribute**).

            ``` text
            vim /opt/shibboleth-idp/conf/ldap.properties
            ```

            ``` xml+jinja
            idp.authn.LDAP.authenticator = bindSearchAuthenticator
            idp.authn.LDAP.ldapURL = ldaps://ldap.example.org
            idp.authn.LDAP.useStartTLS = false
            idp.authn.LDAP.sslConfig = certificateTrust
            idp.authn.LDAP.trustCertificates = /opt/shibboleth-idp/credentials/ldap-server.crt
            # List of attributes to request during authentication
            idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemaining
            idp.authn.LDAP.baseDN = ou=people,dc=example,dc=org
            idp.authn.LDAP.subtreeSearch = false
            idp.authn.LDAP.bindDN = cn=idpuser,ou=system,dc=example,dc=org
           
            # The userFilter is used to locate a directory entry to bind against for LDAP authentication.
            idp.authn.LDAP.userFilter = (uid={user})
            
            idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
            idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
            
            # The 'searchFilter' is is used to find user attributes from an LDAP source
            idp.attribute.resolver.LDAP.searchFilter        = (uid=$resolutionContext.principal)
            
            # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
            # The 'exportAttributes' contains a list space-separated of attributes to retrieve directly from the directory service.
            idp.attribute.resolver.LDAP.exportAttributes    = uid cn sn givenName mail eduPersonAffiliation
            ```

        -   Paste the content of OpenLDAP certificate into `/opt/shibboleth-idp/credentials/ldap-server.crt`

        -   Configure the right owner/group to the OpenLDAP certificate loaded:

            ``` text
            chown jetty:root /opt/shibboleth-idp/credentials/ldap-server.crt ; chmod 600 /opt/shibboleth-idp/credentials/ldap-server.crt
            ```

        -   Restart Jetty to apply the changes:

            ``` text
            service jetty restart
            ```

        -   Check IdP Status:

            ``` text
            bash /opt/shibboleth-idp/bin/status.sh
            ```

        -   Proceed with [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)

    -   Solution 3 - plain LDAP:

        -   Configure `secrets.properties`:

            ``` text
            vim /opt/shibboleth-idp/credentials/secrets.properties
            ```

            ``` xml+jinja
            # Default access to LDAP authn and attribute stores.
            idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
            idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
            ```

        -   Configure `ldap.properties`:

            The `ldap.example.org` have to be replaced with the FQDN of the LDAP server.

            The `idp.authn.LDAP.baseDN` and `idp.authn.LDAP.bindDN` have to be replaced with the right value.

            The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP.
            The list MUST contain the attribute chosen for the persistent-id generation (**idp.persistentId.sourceAttribute**).

            ``` text
            vim /opt/shibboleth-idp/conf/ldap.properties
            ```

            ``` xml+jinja
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
            
            idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
            idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
            
            # The 'searchFilter' is is used to find user attributes from an LDAP source
            idp.attribute.resolver.LDAP.searchFilter        = (uid=$resolutionContext.principal)
            
            # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
            # The 'exportAttributes' contains a list space-separated of attributes to retrieve directly from the directory service.
            idp.attribute.resolver.LDAP.exportAttributes    = uid cn sn givenName mail eduPersonAffiliation
            ```

        -   Restart Jetty to apply the changes:

            ``` text
            service jetty restart
            ```

        -   Check IdP Status:

            ``` text
            bash /opt/shibboleth-idp/bin/status.sh
            ```

        -   Proceed with [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)

[[TOC](#table-of-contents)]

### Active Directory connection

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Install useful packages:

    ``` text
    apt install ldap-utils
    ```

3.  Check that you can reach the Directory from your IDP server:

    ``` text
    ldapsearch -x -H ldap://<AD-SERVER-FQDN-OR-IP> -D 'CN=idpuser,CN=Users,DC=ad,DC=example,DC=org' -w '<IDPUSER-PASSWORD>' -b 'CN=Users,DC=ad,DC=example,DC=org' '(sAMAccountName=<USERNAME-USED-IN-THE-LOGIN-FORM>)'
    ```

    -   the baseDN (`-b` parameter) ==\> `CN=Users,DC=ad,DC=example,DC=org` (branch containing the registered users)
    -   the bindDN (`-D` parameter) ==\> `CN=idpuser,CN=Users,DC=ad,DC=example,DC=org` (distinguished name for the user that can make queries on the LDAP, read only is sufficient)
    -   the searchFilter `(sAMAccountName=<USERNAME-USED-IN-THE-LOGIN-FORM>)` corresponds to the `(sAMAccountName=$resolutionContext.principal)` searchFilter configured into `conf/ldap.properties`

4.  Connect the Active Directory to the IdP to allow the authentication of the users:

    -   Solution 1 - AD + STARTTLS:

        -   Configure `secrets.properties`:

            ``` text
            vim /opt/shibboleth-idp/credentials/secrets.properties
            ```

            ``` xml+jinja
            # Default access to LDAP authn and attribute stores.
            idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
            idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
            ```

        -   Configure `ldap.properties`:

            The `ldap.example.org` have to be replaced with the FQDN of the LDAP server.

            The `idp.authn.LDAP.baseDN` and `idp.authn.LDAP.bindDN` have to be replaced with the right value.

            The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP.
            The list MUST contain the attribute chosen for the persistent-id generation (**idp.persistentId.sourceAttribute**).

            ``` text
            vim /opt/shibboleth-idp/conf/ldap.properties
            ```

            ``` xml+jinja
            idp.authn.LDAP.authenticator = bindSearchAuthenticator
            idp.authn.LDAP.ldapURL = ldap://ldap.example.org
            idp.authn.LDAP.useStartTLS = true
            idp.authn.LDAP.sslConfig = certificateTrust
            idp.authn.LDAP.trustCertificates = /opt/shibboleth-idp/credentials/ldap-server.crt
            # List of attributes to request during authentication
            idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemaining
            idp.authn.LDAP.baseDN = CN=Users,DC=ad,DC=example,DC=org
            idp.authn.LDAP.subtreeSearch = false
            idp.authn.LDAP.bindDN = CN=idpuser,CN=Users,DC=ad,DC=example,DC=org
           
            # The userFilter is used to locate a directory entry to bind against for LDAP authentication.
            idp.authn.LDAP.userFilter = (sAMAccountName={user})
            
            idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
            idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
            
            # The 'searchFilter' is is used to find user attributes from an LDAP source
            idp.attribute.resolver.LDAP.searchFilter        = (sAMAccountName=$resolutionContext.principal)
            
            # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
            # The 'exportAttributes' contains a list space-separated of attributes to retrieve directly from the directory service.
            idp.attribute.resolver.LDAP.exportAttributes    = sAMAccountName cn sn givenName mail eduPersonAffiliation
            ```

        -   Paste the content of OpenLDAP certificate into `/opt/shibboleth-idp/credentials/ldap-server.crt`

        -   Configure the right owner/group to the OpenLDAP certificate loaded:

            ``` text
            chown jetty:root /opt/shibboleth-idp/credentials/ldap-server.crt ; chmod 600 /opt/shibboleth-idp/credentials/ldap-server.crt
            ```

        -   Restart Jetty to apply the changes:

            ``` text
            service jetty restart
            ```

        -   Check IdP Status:

            ``` text
            bash /opt/shibboleth-idp/bin/status.sh
            ```

        -   Proceed with [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)

    -   Solution 2: AD + TLS:

        -   Configure `secrets.properties`:

            ``` text
            vim /opt/shibboleth-idp/credentials/secrets.properties
            ```

            ``` xml+jinja
            # Default access to LDAP authn and attribute stores.
            idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
            idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
            ```

        -   Configure `ldap.properties`:

            The `ldap.example.org` have to be replaced with the FQDN of the LDAP server.

            The `idp.authn.LDAP.baseDN` and `idp.authn.LDAP.bindDN` have to be replaced with the right value.

            The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP.
            The list MUST contain the attribute chosen for the persistent-id generation (**idp.persistentId.sourceAttribute**).

            ``` text
            vim /opt/shibboleth-idp/conf/ldap.properties
            ```

            ``` xml+jinja
            idp.authn.LDAP.authenticator = bindSearchAuthenticator
            idp.authn.LDAP.ldapURL = ldaps://ldap.example.org
            idp.authn.LDAP.useStartTLS = false
            idp.authn.LDAP.sslConfig = certificateTrust
            idp.authn.LDAP.trustCertificates = /opt/shibboleth-idp/credentials/ldap-server.crt
            # List of attributes to request during authentication
            idp.authn.LDAP.returnAttributes = passwordExpirationTime,loginGraceRemaining
            idp.authn.LDAP.baseDN = CN=Users,DC=ad,DC=example,DC=org
            idp.authn.LDAP.subtreeSearch = false
            idp.authn.LDAP.bindDN = CN=idpuser,CN=Users,DC=ad,DC=example,DC=org
           
            # The userFilter is used to locate a directory entry to bind against for LDAP authentication.
            idp.authn.LDAP.userFilter = (sAMAccountName={user})
            
            idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
            idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
            
            # The 'searchFilter' is is used to find user attributes from an LDAP source
            idp.attribute.resolver.LDAP.searchFilter        = (sAMAccountName=$resolutionContext.principal)
            
            # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
            # The 'exportAttributes' contains a list space-separated of attributes to retrieve directly from the directory service.
            idp.attribute.resolver.LDAP.exportAttributes    = sAMAccountName cn sn givenName mail eduPersonAffiliation
            ```

        -   Paste the content of OpenLDAP certificate into `/opt/shibboleth-idp/credentials/ldap-server.crt`

        -   Configure the right owner/group to the OpenLDAP certificate loaded:

            ``` text
            chown jetty:root /opt/shibboleth-idp/credentials/ldap-server.crt ; chmod 600 /opt/shibboleth-idp/credentials/ldap-server.crt
            ```

        -   Restart Jetty to apply the changes:

            ``` text
            service jetty restart
            ```

        -   Check IdP Status:

            ``` text
            bash /opt/shibboleth-idp/bin/status.sh
            ```

        -   Proceed with [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)

    -   Solution 3 - plain AD:

        -   Configure `secrets.properties`:

            ``` text
            vim /opt/shibboleth-idp/credentials/secrets.properties
            ```

            ``` xml+jinja
            # Default access to LDAP authn and attribute stores.
            idp.authn.LDAP.bindDNCredential              = ###IDPUSER_PASSWORD###
            idp.attribute.resolver.LDAP.bindDNCredential = %{idp.authn.LDAP.bindDNCredential:undefined}
            ```

        -   Configure `ldap.properties`:

            The `ldap.example.org` have to be replaced with the FQDN of the LDAP server.

            The `idp.authn.LDAP.baseDN` and `idp.authn.LDAP.bindDN` have to be replaced with the right value.

            The property `idp.attribute.resolver.LDAP.exportAttributes` **has to be added** into the file and configured with the list of attributes the IdP retrieves directly from LDAP.
            The list MUST contain the attribute chosen for the persistent-id generation (**idp.persistentId.sourceAttribute**).

            ``` text
            vim /opt/shibboleth-idp/conf/ldap.properties
            ```

            ``` xml+jinja
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
            
            idp.attribute.resolver.LDAP.useStartTLS         = %{idp.authn.LDAP.useStartTLS:true}
            idp.attribute.resolver.LDAP.trustCertificates   = %{idp.authn.LDAP.trustCertificates:undefined}
            
            # The 'searchFilter' is is used to find user attributes from an LDAP source
            idp.attribute.resolver.LDAP.searchFilter        = (sAMAccountName=$resolutionContext.principal)
            
            # List of attributes produced by the Data Connector that should be directly exported as resolved IdPAttributes without requiring any <AttributeDefinition>
            # The 'exportAttributes' contains a list space-separated of attributes to retrieve directly from the directory service.
            idp.attribute.resolver.LDAP.exportAttributes    = sAMAccountName cn sn givenName mail eduPersonAffiliation
            ```

        -   Restart Jetty to apply the changes:

            ``` text
            service jetty restart
            ```

        -   Check IdP Status:

            ``` text
            bash /opt/shibboleth-idp/bin/status.sh
            ```

        -   Proceed with [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)

[[TOC](#table-of-contents)]

## Configure Shibboleth Identity Provider to release the persistent NameID

DOC: [PersistentNameIDGenerationConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199507892/PersistentNameIDGenerationConfiguration)

SAML 2.0 (but not SAML 1.x) defines a kind of NameID called a "*persistent*" identifier that every SP receives for the IdP users.
This part will teach you how to release the "*persistent*" identifiers with a database (Stored Mode) or without it (Computed Mode).

By default, a transient NameID will always be released to the Service Provider if the persistent one is not requested.

### Strategy A - Computed mode (Default) - Recommended

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Enable the generation of the computed `persistent-id` with:

    -   ``` text
        vim /opt/shibboleth-idp/conf/saml-nameid.properties
        ```

        The *sourceAttribute* MUST be an attribute, or a list of comma-separated attributes, that uniquely identify the subject of the generated `persistent-id`.

        The *sourceAttribute* MUST be a **Stable**, **Permanent** and **Not-reassignable** directory attribute.

        ``` xml+jinja
        # ... other things ...#
        # OpenLDAP has the UserID into "uid" attribute
        idp.persistentId.sourceAttribute = uid

        # Active Directory has the UserID into "sAMAccountName"
        #idp.persistentId.sourceAttribute = sAMAccountName
        # ... other things ...#
        ```

    -   ``` text
        vim /opt/shibboleth-idp/conf/saml-nameid.xml
        ```

        Uncomment the line:

        ``` xml+jinja
        <ref bean="shibboleth.SAML2PersistentGenerator" />
        ```

    -   ``` xml+jinja
        vim /opt/shibboleth-idp/credentials/secrets.properties
        ```

        ``` xml+jinja
        idp.persistentId.salt = ### result of command 'openssl rand -base64 36' ###
        ```

3.  Restart Jetty to apply the changes:

    ``` text
    service jetty restart
    ```

4.  Check IdP Status:

    ``` text
    bash /opt/shibboleth-idp/bin/status.sh
    ```

5.  Proceed with [Configure the attribute resolver (sample)](#configure-the-attribute-resolver-sample)

[[TOC](#table-of-contents)]

### Strategy B - Stored mode - using a database

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Install SQL database and needed libraries:

    ``` text
    apt install default-mysql-server libmariadb-java libcommons-dbcp2-java libcommons-pool2-java --no-install-recommends
    ```

3.  Install JDBCStorageService plugin:

    ``` text
    /opt/shibboleth-idp/bin/plugin.sh -I net.shibboleth.plugin.storage.jdbc
    ```

4.  Activate MariaDB database service:

    ``` text
    systemctl start mariadb.service
    ```

5.  Address several security concerns in a default MariaDB installation (if it is not already done):

    ``` text
    mysql_secure_installation
    ```

6.  (OPTIONAL) MySQL DB Access without password:

    ``` text
    vim /root/.my.cnf
    ```

    ``` text
    [client]
    user=root
    password=##ROOT-DB-PASSWORD-CHANGEME##
    ```

7.  Create `shibpid` table on `shibboleth` database:

    ``` text
    wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/db-conf/shib-pid-db.sql -O /root/shib-pid-db.sql
    ```

    fill missing data on `shib-pid-db.sql` before import:

    -   ``` text
        mysql -u root < /root/shib-pid-db.sql
        ```

    -   ``` text
        systemctl restart mariadb.service
        ```

8.  Rebuild IdP war file with the needed libraries:

    -   ``` text
        mkdir /opt/shibboleth-idp/edit-webapp/WEB-INF/lib
        ```

    -   ``` text
        ln -s /usr/share/java/mariadb-java-client.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib
        ```

    -   ``` text
        ln -s /usr/share/java/commons-dbcp2.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib
        ```

    -   ``` text
        ln -s /usr/share/java/commons-pool2.jar /opt/shibboleth-idp/edit-webapp/WEB-INF/lib
        ```

    -   ``` text
        bash /opt/shibboleth-idp/bin/build.sh
        ```

9.  Configure JDBC Storage Service:

    ``` text
    vim /opt/shibboleth-idp/conf/global.xml
    ```

    and add the following directives to the tail, before the last `</beans>` tag:

    ``` xml+jinja
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
    ```

    **!!! IMPORTANT !!!**

    remember to change "**\###\_SHIBPID-USERNAME-CHANGEME\_###**" and "**\###\_SHIBPID-DB-USER-PASSWORD-CHANGEME\_###**" with your DB user and password data.

10. Enable the generation of the `persistent-id`:

    -   ``` text
        vim /opt/shibboleth-idp/conf/saml-nameid.properties
        ```

        The *sourceAttribute* MUST be an attribute, or a list of comma-separated attributes, that uniquely identify the subject of the generated `persistent-id`.

        The *sourceAttribute* MUST be a **Stable**, **Permanent** and **Not-reassignable** directory attribute.

        ``` xml+jinja
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
        ```

    -   ``` text
        vim /opt/shibboleth-idp/credentials/secrets.properties
        ```

        ``` text
        idp.persistentId.salt = ### result of command 'openssl rand -base64 36'###
        ```

    -   Enable the **SAML2PersistentGenerator**:

        -   ``` text
            vim /opt/shibboleth-idp/conf/saml-nameid.xml
            ```

            Uncomment the line:

            ``` xml+jinja
            <ref bean="shibboleth.SAML2PersistentGenerator" />
            ```

        -   ``` text
            vim /opt/shibboleth-idp/conf/c14n/subject-c14n.xml
            ```

            Uncomment the line:

            ``` xml+jinja
            <ref bean="c14n/SAML2Persistent" />
            ```

        -   (OPTIONAL) Transform each letter of username, before storing in into the database, to Lowercase or Uppercase by setting the proper constant:

            ``` text
            vim /opt/shibboleth-idp/conf/c14n/subject-c14n.properties
            ```

            ``` xml+jinja
            # Simple username -> principal name c14n
            idp.c14n.simple.lowercase = true
            #idp.c14n.simple.uppercase = false
            idp.c14n.simple.trim = true
            ```

11. Restart Jetty to apply the changes:

    ``` text
    service jetty restart
    ```

12. Check IdP Status:

    ``` text
    bash /opt/shibboleth-idp/bin/status.sh
    ```

13. Proceed with [Configure the attribute resolver (sample)](#configure-the-attribute-resolver-sample)

[[TOC](#table-of-contents)]

## Configure the attribute resolver (sample)

The attribute resolver contains attribute definitions and data connectors that collect information from a variety of sources,
combine and transform it, and produce a final collection of IdPAttribute objects, 
which are an internal representation of user data not specific to SAML or any other supported identity protocol.

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Download the sample attribute resolver provided by IDEM GARR AAI Federation Operators (OpenLDAP / Active Directory compliant):

    ``` text
    wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/conf/attribute-resolver-v5-idem-sample.xml -O /opt/shibboleth-idp/conf/attribute-resolver.xml
    ```

    If you decide to use the plain text LDAP/AD solution, **remove or comment** the following directives from your Attribute Resolver file:

    ``` xml+jinja
    Line 1:  useStartTLS="%{idp.attribute.resolver.LDAP.useStartTLS:true}"
    Line 2:  trustFile="%{idp.attribute.resolver.LDAP.trustCertificates}"
    ```

3.  Configure the right owner:

    ``` text
    chown jetty /opt/shibboleth-idp/conf/attribute-resolver.xml
    ```

4.  Restart Jetty to apply the changes:

    ``` text
    service jetty restart
    ```

5.  Check IdP Status:

    ``` text
    bash /opt/shibboleth-idp/bin/status.sh
    ```

[[TOC](#table-of-contents)]

## Configure Shibboleth Identity Provider to release the eduPersonTargetedID

eduPersonTargetedID is an abstracted version of the SAML V2.0 Name Identifier format of `urn:oasis:names:tc:SAML:2.0:nameid-format:persistent`.

To be able to follow these steps, you need to have followed the previous steps on `persistent` NameID generation.

### Strategy A - Computed mode - using the computed persistent NameID - Recommended

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Check to have the following `<AttributeDefinition>` and the `<DataConnector>` into the `attribute-resolver.xml`:

    ``` text
    vim /opt/shibboleth-idp/conf/attribute-resolver.xml
    ```

    ``` xml+jinja
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
    ```

3.  Create the custom `eduPersonTargetedID.properties` file:

    ``` text
    wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/conf/attributes/custom/eduPersonTargetedID.properties -O /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties
    ```

4.  Set proper owner/group with:

    ``` text
    chown jetty:root /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties
    ```

5.  Restart Jetty to apply the changes:

    ``` text
    service jetty restart
    ```

6.  Check IdP Status:

    ``` text
    bash /opt/shibboleth-idp/bin/status.sh
    ```

7.  Proceed with [Configure Shibboleth IdP Logging](#configure-shibboleth-idp-logging)

[[TOC](#table-of-contents)]

### Strategy B - Stored mode - using the persistent NameID database

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Check to have the following `<AttributeDefinition>` and the
    `<DataConnector>` into the `attribute-resolver.xml`:

    ``` text
    vim /opt/shibboleth-idp/conf/attribute-resolver.xml`
    ```

    ``` xml+jinja
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

        <BeanManagedConnection>shibpid.JDBCStorageService.DataSource</BeanManagedConnection>
    </DataConnector>
    ```

3.  Create the custom `eduPersonTargetedID.properties` file:

    ``` text
    wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/conf/attributes/custom/eduPersonTargetedID.properties -O /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties
    ```

4.  Set proper owner/group with:

    ``` text
    chown jetty:root /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties
    ```

5.  Restart Jetty to apply the changes:

    ``` text
    service jetty restart
    ```

6.  Check IdP Status:

    ``` text
    bash /opt/shibboleth-idp/bin/status.sh
    ```

7.  Proceed with [Configure Shibboleth IdP Logging](#configure-shibboleth-idp-logging)

[[TOC](#table-of-contents)]

## Configure Shibboleth IdP Logging

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Enrich IDP logs with the authentication error occurred on LDAP:

    ``` text
    sed -i '/^    <logger name="org.ldaptive".*/a \\n    <!-- Logs on LDAP user authentication - ADDED BY IDEM HOWTO -->' /opt/shibboleth-idp/conf/logback.xml

    sed -i '/^    <!-- Logs on LDAP user authentication - ADDED BY IDEM HOWTO -->/a \ \ \ \ \<logger name="org.ldaptive.auth.Authenticator" level="INFO" />' /opt/shibboleth-idp/conf/logback.xml
    ```

[[TOC](#table-of-contents)]

## Translate IdP messages into preferred language

Translate the IdP messages in your language:

-   Get the files translated in your language from [MessagesTranslation](https://shibboleth.atlassian.net/wiki/x/BwJwSw)
-   Put `messages_XX.properties` downloaded file into `/opt/shibboleth-idp/messages` directory
-   Restart Jetty to apply the changes with `service jetty restart`

[[TOC](#table-of-contents)]

## Enrich IdP Login Page with the Institutional Logo

1.  Discover what images are publicly available by opening an URL similar to "<https://idp.example.org/idp/images/>" from a web browser.

2.  Copy the institutional logo into all placeholder found inside the `/opt/shibboleth-idp/edit-webapp/images` directory **without renaming them**.

3.  Rebuild IdP war file:

    ``` text
    bash /opt/shibboleth-idp/bin/build.sh
    ```

4.  Restart Jetty:

    ``` text
    sudo service jetty restart
    ```

[[TOC](#table-of-contents)]

## Enrich IdP Login Page with Information and Privacy Policy pages

1.  Add the following two lines into `views/login.vm`:

    ``` text
    <li class="list-help-item"><a href="#springMessageText("idp.url.infoPage", '#')"><span class="item-marker">&rsaquo;</span> #springMessageText("idp.login.infoPage", "Information page")</a></li>
    <li class="list-help-item"><a href="#springMessageText("idp.url.privacyPage", '#')"><span class="item-marker">&rsaquo;</span> #springMessageText("idp.login.privacyPage", "Privacy Policy")</a></li>
    ```

    under the line containing the Anchor:

    ``` text
    <a href="#springMessageText("idp.url.helpdesk", '#')">
    ```

2.  Add the new variables defined with lines added at point 1 into all `messages*.properties` files linked to the view `view/login.vm`:

    -   Move to the IdP Home:

        ``` text
        cd /opt/shibboleth-idp
        ```

    -   Modify `messages.properties`:

        ``` text
        vim messages/messages.properties
        ```

        ``` text
        idp.login.infoPage=Informations
        idp.url.infoPage=https://my.organization.it/english-idp-info-page.html
        idp.login.privacyPage=Privacy Policy
        idp.url.privacyPage=https://my.organization.it/english-idp-privacy-policy.html
        ```

    -   Modify `messages_it.properties`:

        ``` text
        vim messages/messages_it.properties
        ```

        ``` text
        idp.login.infoPage=Informazioni
        idp.url.infoPage=https://my.organization.it/italian-idp-info-page.html
        idp.login.privacyPage=Privacy Policy
        idp.url.privacyPage=https://my.organization.it/italian-idp-privacy-policy.html
        ```

3.  Rebuild IdP WAR file and Restart Jetty to apply changes:

    -   ``` text
        bash /opt/shibboleth-idp/bin/build.sh
        ```

    -   ``` text
        sudo systemctl restart jetty
        ```

[[TOC](#table-of-contents)]

## Change default login page footer text

Change the content of `idp.footer` variable into all `messages*.properties` files linked to the view `view/login.vm`:

-   ``` text
    cd /opt/shibboleth-idp
    ```

-   ``` text
    vim messages/messages.properties
    ```

    ``` xml+jinja
    idp.footer=Footer text for english version of IdP login page
    ```

-   ``` text
    vim messages/messages_it.properties:
    ```

    ``` xml+jinja
    idp.footer=Testo del Footer a pie di pagina per la versione italiana della pagina di login dell'IdP
    ```

[[TOC](#table-of-contents)]

## Change default "Forgot your password?" and "Need help?" endpoints

Change the content of `idp.url.password.reset` and `idp.url.helpdesk` variables into `messages*.properties` files linked to the view `view/login.vm`:

-   Move to the IdP Home:

    ``` text
    cd /opt/shibboleth-idp
    ```

-   Modify `messages.properties`:

    ``` text
    vim messages/messages.properties
    ```

    ``` xml+jinja
    idp.url.password.reset=CONTENT-FOR-FORGOT-YOUR-PASSWORD-LINK
    idp.url.helpdesk=CONTENT-FOR-NEED-HELP-LINK
    ```

-   Modify `messages_it.properties`:

    ``` text
    vim messages/messages_it.properties
    ```

    ``` xml+jinja
    idp.url.password.reset=CONTENUTO-PER-LINK-PASSWORD-DIMENTICATA
    idp.url.helpdesk=CONTENUTO-PER-SERVE-AIUTO-LINK
    ```

[[TOC](#table-of-contents)]

## Update IdP metadata

**(only for italian identity federation IDEM members)**

1.  Modify the IdP metadata as follow:

    ``` text
    vim /opt/shibboleth-idp/metadata/idp-metadata.xml
    ```

    1.  Remove completely the initial default comment

    2.  Remove completely the `<mdui:UIInfo>` element and its content too.

    3.  Add the `HTTP-Redirect` SingleLogoutService endpoints under the `SOAP` one:

        ``` xml+jinja
        <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://idp.example.org/idp/profile/SAML2/Redirect/SLO"/>
        ```

        (replace `idp.example.org` value with the Full Qualified Domain Name of the Identity Provider.)

    4.  Between the last `<SingleLogoutService>` and the first `<SingleSignOnService>` endpoints add:

        ``` xml+jinja
        <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</md:NameIDFormat>
        <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</md:NameIDFormat>
        ```

        (because the IdP installed with this guide will release transient NameID, by default, and persistent NameID if requested.)

2.  Check that the metadata is available on `/idp/shibboleth` location:

`https://idp.example.org/idp/shibboleth`

[[TOC](#table-of-contents)]

## Secure cookies and other IDP data

DOC: [SecretKeyManagement](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501624/SecretKeyManagement)

The default configuration of the IdP relies on a component called a "DataSealer" which in turn uses an AES secret key to secure cookies and certain other data for the IdPs own use. 
This key must never be shared with anybody else, and must be copied to every server node making up a cluster.
The Java "JCEKS" keystore file stores secret keys instead of public/private keys and certificates and a parallel file tracks the key version number.

These instructions will regularly update the secret key (and increase its version) and provide you the capability to push it to cluster nodes and continually maintain the secrecy of the key.

1.  Download `updateIDPsecrets.sh` into the right location:

    ``` text
    wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/bin/updateIDPsecrets.sh -O /opt/shibboleth-idp/bin/updateIDPsecrets.sh
    ```

2.  Provide the right privileges to the script:

    ``` text
    sudo chmod +x /opt/shibboleth-idp/bin/updateIDPsecrets.sh
    ```

4.  Install Cron:

    ``` text
    sudo apt install cron
    ```

5.  Create the CRON script to run it:

    ``` text
    sudo vim /etc/cron.daily/updateIDPsecrets
    ```

    ``` text
    #!/bin/bash

    /opt/shibboleth-idp/bin/updateIDPsecrets.sh
    ```

6.  Provide the right privileges to the script:

    ``` text
    sudo chmod +x /etc/cron.daily/updateIDPsecrets
    ```

7.  Confirm that the script will be run daily with (you should see your script in the command output):

    ``` text
    sudo run-parts --test /etc/cron.daily
    ```

8.  (OPTIONAL) Add the following properties to `conf/idp.properties` if you need to set different values than defaults:

    -   `idp.sealer._count` - Number of earlier keys to keep (default "30")
    -   `idp.sealer._sync_hosts` - Space separated list of hosts to scp the sealer files to (default generate locally)

[[TOC](#table-of-contents)]

## Configure Attribute Filter Policy to release attributes to Federated Resources

Follow these steps **ONLY IF** your organization is connected to the [GARR Network](https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites).

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Create the directory `tmp/httpClientCache` used by `shibboleth.FileCachingHttpClient`:

    ``` text
    mkdir -p /opt/shibboleth-idp/tmp/httpClientCache ; chown jetty /opt/shibboleth-idp/tmp/httpClientCache
    ```

3.  Modify your `services.xml`:

    ``` text
    vim /opt/shibboleth-idp/conf/services.xml
    ```

    and add the following two beans on the top of the file, under the first `<beans>` TAG, only one time:

    ``` xml+jinja
    <bean id="MyHTTPClient" parent="shibboleth.FileCachingHttpClientFactory"
          p:connectionTimeout="PT30S"
          p:connectionRequestTimeout="PT30S"
          p:socketTimeout="PT30S"
          p:cacheDirectory="%{idp.home}/tmp/httpClientCache" />

    <bean id="IdemAttributeFilterFull" class="net.shibboleth.ext.spring.resource.FileBackedHTTPResource"
          c:client-ref="MyHTTPClient"
          c:url="https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/conf/idem-attribute-filter-v5-full.xml"
          c:backingFile="%{idp.home}/conf/idem-attribute-filter-full.xml"/>
    ```

    and enrich the `AttributeFilterResources` list with `IdemAttributeFilterFull`:

    ``` xml+jinja
    <!-- ...other things... -->

    <util:list id ="shibboleth.AttributeFilterResources">
        <value>%{idp.home}/conf/attribute-filter.xml</value>
        <ref bean="IdemAttributeFilterFull"/>
    </util:list>

    <!-- ...other things... -->
    ```

4.  Restart Jetty to apply the changes:

    ``` text
    systemctl restart jetty
    ```

5.  Check IdP Status:

    ``` text
    bash /opt/shibboleth-idp/bin/status.sh
    ```

[[TOC](#table-of-contents)]

## Register the IdP on the IDEM Test Federation

Follow these steps **ONLY IF** your organization is connected to the [GARR Network](https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites).

1.  Register you IdP metadata on IDEM Entity Registry (your entity have to be approved by an IDEM Federation Operator before become part of IDEM Test Federation):

    <https://registry.idem.garr.it/>

2.  Configure the IdP to retrieve the Federation Metadata through **IDEM MDX**: <https://mdx.idem.garr.it/>

3.  Check that your IdP release at least eduPersonScopedAffiliation, eduPersonTargetedID and a saml2:NameID transient/persistent to the testing SP provided by IDEM:

    ``` text
    bash /opt/shibboleth-idp/bin/aacli.sh -n <USERNAME> -r https://sp.example.org/shibboleth --saml2
    ```

    (the command will have a `transient` NameID into the Subject of the assertion)

    ``` text
    bash /opt/shibboleth-idp/bin/aacli.sh -n <USERNAME> -r https://sp.aai-test.garr.it/shibboleth --saml2
    ```

    (the command will have a `persistent` NameID into the Subject of the assertion)

4.  Wait that your IdP Metadata is approved by an IDEM Federation Operator into the IDEM Test Federation metadata stream and the next steps provided by the operator itself.

[[TOC](#table-of-contents)]

## Appendix A: Enable Consent Module (Attribute Release + Terms of Use Consent)

DOC: [ConsentConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509862/ConsentConfiguration)

The IdP includes the ability to require user consent to attribute release, as well as presenting a "terms of use" message prior to completing a login to a service, a simpler "static" form of consent.

1.  Move to IdP home dir:

    ``` text
    cd /opt/shibboleth-idp
    ```

2.  Load Consent Module:

    ``` text
    bin/module.sh -t idp.intercept.Consent || bin/module.sh -e idp.intercept.Consent
    ```

3.  Enable Consent Module by editing the `DefaultRelyingParty` on `conf/relying-party.xml` with the right `postAuthenticationFlows`:

    -   `<bean parent="SAML2.SSO" p:postAuthenticationFlows="attribute-release" />` - to enable only Attribute Release Consent
    -   `<bean parent="SAML2.SSO" p:postAuthenticationFlows="#{ {'terms-of-use', 'attribute-release'} }" />` - to enable both

    (instead of `<ref bean="SAML2.SSO" />`)

4.  Restart Jetty:

    ``` text
    service jetty restart
    ```

[[TOC](#table-of-contents)]

## Appendix B: Import persistent-id from a previous database

Follow these steps **ONLY IF** your need to import persistent-id database from another IdP

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Create a DUMP of `shibpid` table from the previous DB `shibboleth` on the OLD IdP:

    ``` text
    cd /tmp

    mysqldump --complete-insert --no-create-db --no-create-info -u root -p shibboleth shibpid > /tmp/shibboleth_shibpid.sql
    ```

3.  Copy the `/tmp/shibboleth_shibpid.sql` from the old IdP into `/tmp/shibboleth_shibpid.sql` on the new IdP.

4.  Import the content of `/tmp/shibboleth_shibpid.sql` into database of the new IDP:

    ``` text
    cd /tmp ; mysql -u root -p shibpid < /tmp/shibboleth_shibpid.sql
    ```

5.  Delete `/tmp/shibboleth_shibpid.sql`:

    ``` text
    rm /tmp/shibboleth_shibpid.sql
    ```

[[TOC](#table-of-contents)]

## Appendix C: Useful logs to find problems

Follow this if you need to find a problem of your IdP.

1.  Jetty Logs:

    ``` text
    cd /opt/jetty/logs

    ls -l *.stderrout.log
    ```

2.  Shibboleth IdP Logs:

    ``` text
    cd /opt/shibboleth-idp/logs
    ```

    -   **Audit Log:** `vim idp-audit.log`
    -   **Consent Log:** `vim idp-consent-audit.log`
    -   **Warn Log:** `vim idp-warn.log`
    -   **Process Log:** `vim idp-process.log`

[[TOC](#table-of-contents)]

## Appendix D: Connect an SP with the IdP

DOC:

-   [ChainingMetadataProvider](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199506765/ChainingMetadataProvider)
-   [FileBackedHTTPMetadataProvider](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199506865/FileBackedHTTPMetadataProvider)
-   [AttributeFilterConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501794/AttributeFilterConfiguration)
-   [AttributeFilterPolicyConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501835/AttributeFilterPolicyConfiguration)

Follow these steps **IF** your organization **IS NOT** connected to the [GARR Network](https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites).

1.  Connect the SP to the IdP by adding its metadata on the `metadata-providers.xml` configuration file:

    ``` text
    vim /opt/shibboleth-idp/conf/metadata-providers.xml
    ```

    ``` xml+jinja
    <MetadataProvider id="HTTPMetadata"
                      xsi:type="FileBackedHTTPMetadataProvider"
                      backingFile="%{idp.home}/metadata/sp-metadata.xml"
                      metadataURL="https://sp.example.org/Shibboleth.sso/Metadata"
                      failFastInitialization="false"/>
    ```

2.  Adding an `AttributeFilterPolicy` on the `conf/attribute-filter.xml` file:

    -   ``` text
        wget https://registry.idem.garr.it/idem-conf/shibboleth/IDP5/conf/idem-example-arp.txt -O /opt/shibboleth-idp/conf/example-arp.txt
        ```

    -   ``` text
        cat /opt/shibboleth-idp/conf/example-arp.txt
        ```

    -   Copy and paste the content into `/opt/shibboleth-idp/conf/attribute-filter.xml` before the last element `</AttributeFilterPolicyGroup>`.

    -   Make sure to change the value of the placeholder **\### SP-ENTITYID \###** on the text pasted with the entityID of the Service Provider to connect with the Identity Provider installed.

3.  Restart Jetty to apply changes:

    ``` text
    systemctl restart jetty
    ```

[[TOC](#table-of-contents)]

## Utilities

-   AACLI: Useful to understand which attributes will be released to the federated resources
    -   `export JAVA_HOME=/usr/lib/jvm/java-11-amazon-corretto`
    -   `bash /opt/shibboleth-idp/bin/aacli.sh -n <USERNAME> -r <ENTITYID-SP> --saml2`
-   [The Mozilla Observatory](https://observatory.mozilla.org/): The Mozilla Observatory has helped over 240,000 websites by teaching developers, system administrators, and security professionals how to configure their sites safely and securely.

[[TOC](#table-of-contents)]

### Useful Documentation

-   [SpringConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199508919/SpringConfiguration)
-   [ConfigurationFileSummary](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199506590/ConfigurationFileSummary)
-   [LoggingConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509659/LoggingConfiguration)
-   [AuditLoggingConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509698/AuditLoggingConfiguration)
-   [FTICKSLoggingConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509739/FTICKSLoggingConfiguration)
-   [MetadataConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199506698/MetadataConfiguration)
-   [PasswordAuthnConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199505587/PasswordAuthnConfiguration)
-   [AttributeResolverConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199502864/AttributeResolverConfiguration)
-   [AttributeFilter](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199511838/AttributeFilter)
-   [LDAPConnector](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199503855/LDAPConnector)
-   [AttributeRegistryConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199510514/AttributeRegistryConfiguration)
-   [TranscodingRuleConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199510553/TranscodingRuleConfiguration)
-   [HTTPResource](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199507990/HTTPResource)
-   [SAMLKeysAndCertificates](https://shibboleth.atlassian.net/wiki/spaces/CONCEPT/pages/948470554/SAMLKeysAndCertificates)
-   [SecretKeyManagement](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501624/SecretKeyManagement)
-   [NameIDGenerationConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199507810/NameIDGenerationConfiguration)
-   [GCMEncryption](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501202/GCMEncryption)
-   [Switching locale on the login page](https://shibboleth.atlassian.net/wiki/spaces/KB/pages/1435927082/Switching+locale+on+the+login+page)
-   [WebInterfaces](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199511365/WebInterfaces)
-   [Cross-Site Request Forgery CSRF Protection](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501137/Cross-Site+Request+Forgery+CSRF+Protection)

[[TOC](#table-of-contents)]

### Authors

#### Original Author

Marco Malavolti (<marco.malavolti@garr.it>)

[[TOC](#table-of-contents)]
