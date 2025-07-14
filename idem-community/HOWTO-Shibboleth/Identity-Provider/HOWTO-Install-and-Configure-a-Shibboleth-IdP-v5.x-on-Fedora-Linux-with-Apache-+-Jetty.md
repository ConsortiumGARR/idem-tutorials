# HOWTO Install and Configure a Shibboleth IdP v5.x on Fedora Linux with Apache + Jetty

## Table of Contents

1.  [Requirements](#requirements)
    1.  [Hardware](#hardware)
    2.  [Software](#software)
    3.  [Others](#others)
2.  [Notes](#notes)
3.  [Configure the environment](#configure-the-environment)
4.  [Install software requirements](#install-software-requirements)
5.  [Install Jetty 12 Servlet Container](#install-jetty-12-servlet-container)
6.  [Install Shibboleth Identity Provider](#install-shibboleth-identity-provider)
7.  [Disable Jetty Directory Indexing](#disable-jetty-directory-indexing)
8.  [Configure Apache Web Server](#configure-apache-web-server)
9. [Configure Jetty Context Descriptor for IdP](#configure-jetty-context-descriptor-for-idp)
10. [Configure Shibboleth Identity Provider Storage Service](#configure-shibboleth-identity-provider-storage-service)
    1.  [Default (HTML Local Storage, Encryption GCM, No Database)](#default-html-local-storage-encryption-gcm-no-database)
11. [Configure the Directory Connection](#configure-the-directory-connection)
    1.  [openLDAP directory connection](#openldap-directory-connection)
12. [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)
    1.  [Computed mode (Default & Recommended)](#computed-mode-default)
13. [Configure the attribute resolver (sample)](#configure-the-attribute-resolver-sample)
14. [Configure Shibboleth Identity Provider to release the eduPersonTargetedID](#configure-shibboleth-identity-provider-to-release-the-edupersontargetedid)
    1.  [Computed mode - using the computed persistent NameID](#computed-mode---using-the-computed-persistent-nameid)
15. [Configure Shibboleth IdP Logging](#configure-shibboleth-idp-logging)
16. [Translate IdP messages into preferred language](#translate-idp-messages-into-preferred-language)
17. [Enrich IdP Login Page with the Institutional Logo](#enrich-idp-login-page-with-the-institutional-logo)
18. [Enrich IdP Login Page with Information and Privacy Policy pages](#enrich-idp-login-page-with-information-and-privacy-policy-pages)
19. [Change default login page footer text](#change-default-login-page-footer-text)
20. [Change default "Forgot your password?" and "Need help?" endpoints](#change-default-forgot-your-password-and-need-help-endpoints)
21. [Update IdP metadata](#update-idp-metadata)
22. [Secure cookies and other IDP data](#secure-cookies-and-other-idp-data)
23. [Configure Attribute Filter Policy to release attributes to Federated Resources](#configure-attribute-filter-policy-to-release-attributes-to-federated-resources)
24. [Register the IdP on the IDEM Test Federation](#register-the-idp-on-the-idem-test-federation)
25. [Appendix A: Enable Consent Module (Attribute Release + Terms of Use Consent)](#appendix-a-enable-consent-module-attribute-release--terms-of-use-consent)
26. [Appendix B: Useful logs to find problems](#appendix-b-useful-logs-to-find-problems)
27. [Appendix C: Connect an SP with the IdP](#appendix-c-connect-an-sp-with-the-idp)
28. [Utilities](#utilities)
29. [Useful Documentation](#useful-documentation)
30. [Authors](#authors)

## Requirements

### Hardware

-   CPU: 1 Core (64 bit)
-   RAM: 3 GB (with IDEM MDX), 4GB (without IDEM MDX)
-   HDD: 20 GB
-   OS: Fedora Cloud base generic (>= 40)

### Software

-   Apache Web Server (*\>= 2.4*)
-   Jetty 12+ Servlet Container (*implementing Servlet API 5.0 or above*)
-   OpenJDK 24.0.0.0.36-1
-   OpenSSL (*\>= 3.2.1*)
-   Shibboleth Identity Provider (*\>= 5.1.3*)

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
-   Virtual Machine Image: fedora-cloud-base-generic.x86_64-40-1.14.qcow2

[[TOC](#table-of-contents)]

## Notes

This HOWTO uses `example.org` and `idp.example.org` as example values.

Please remember to **replace all occurencences** of:

-   the `example.org` value with the IdP domain name
-   the `idp.example.org` value with the Full Qualified Domain Name of the Identity Provider.

[[TOC](#table-of-contents)]

## Configure the environment

1. Modify your ```/etc/hosts```:
     ``` text
     vi /etc/hosts
     ```
  
     ```bash
     127.0.1.1 idp.example.org idp
     ```
   (*Replace ```idp.example.org``` with your IdP Full Qualified Domain Name*)

2. Be sure that your firewall **doesn't block** the traffic on port **443** (or you can't access to your IdP)

3. Define the costant ```JAVA_HOME```, ```IDP_HOME```, ```IDP_SRC```,  ```JETTY_HOME``` and ```JETTY_BASE```  inside ```/etc/profile```:
    ``` text
    vi /etc/profile
    ```

     ```bash
     export JAVA_HOME=/usr/lib/jvm/jre-24-openjdk
     export IDP_HOME=/opt/shibboleth-idp
     export IDP_SRC=/opt/shibboleth-idp-5.1.3
     export JETTY_HOME=/opt/jetty-src
     export JETTY_BASE=/opt/jetty
     ```
     ``` text
     source /etc/profile
     ```
  
5. Move the Certificate and the Key file for HTTPS server from ```/tmp/``` to ```/root/certificates```:
    ``` text
   mkdir /root/certificates
    ```
    ``` text
   mv /tmp/idp-cert-server.cer /root/certificates
    ```
    ``` text
   mv /tmp/idp-key-server.key /root/certificates
    ```
    ``` text
   mv /tmp/DigiCertCA.cer /root/certificates
    ```
    ``` text
   chmod 400 /root/certificates/idp-key-server.key
    ```
    ``` text
   chmod 644 /root/certificates/idp-cert-server.cer
    ```
    ``` text
   chmod 644 /root/certificates/DigiCertCA.cer
    ```

   (OPTIONAL) Create a Certificate and a Key self-signed for HTTPS if you don't have the official ones provided by DigiCert:
    ```openssl req -x509 -newkey rsa:4096 -keyout /root/certificates/idp-key-server.key -out /root/certificates/idp-cert-server.crt -nodes -days 1095```

[[TOC](#table-of-contents)]

## Install software requirements

1. Become ROOT:
   ``` text
   sudo su -
   ```

3. Install the packages required:

    ``` text
    dnf install java-latest-openjdk-devel mod_ssl httpd wget jakarta-servlet jakarta-server-pages
    ```
  
4. Disable SELinux:
    ``` text
    vi /etc/selinux/config
    ```
  
     ```
     # This file controls the state of SELinux on the system.
     # SELINUX= can take one of these three values:
     #       enforcing - SELinux security policy is enforced.
     #       permissive - SELinux prints warnings instead of enforcing.
     #       disabled - No SELinux policy is loaded.
     SELINUX=disabled
     ```
   ``` text
   reboot
   ```
   ``` text
   sudo su -
   ```
   check that the command ```getenforce``` returns **Disabled**.

[[TOC](#table-of-contents)]

### Install Jetty 12 Servlet Container

Jetty is a Web server and a Java Servlet container. It will be used to run the IdP application through its WAR file.

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Download and Extract Jetty:

    ``` text
    cd /opt
    ```

    ``` text
    wget https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-home/12.0.14/jetty-home-12.0.14.tar.gz
    ```

    ``` text
    tar xzvf jetty-home-12.0.14.tar.gz
    ```

3.  Create the `jetty-src` folder as a symbolic link. It will be useful for future Jetty updates:

    ``` text
    ln -s jetty-home-12.0.14 jetty-src
    ```

4.  Create the system user `jetty` that can run the web server (without home directory):

    ``` text
    useradd -r -m jetty
    ```
    (ignore the message: "useradd: failed to reset the lastlog entry of ...")

5.  Create your custom Jetty configuration that overrides the default one and will survive upgrades:

    ``` text
    mkdir /opt/jetty
    ```

6.  Create the TMPDIR directory used by Jetty:

    ``` text
    mkdir /opt/jetty/tmp ; chown jetty:jetty /opt/jetty/tmp
    ```

    ``` text
    chown -R jetty:jetty /opt/jetty /opt/jetty-src
    ```

7.  Create the Jetty Logs' folders:

    ``` text
    mkdir /var/log/jetty
    ```

    ``` text
    chown jetty:jetty /var/log/jetty
    ```

8. Configure **/etc/default/jetty**:

    ``` text
    update-alternatives --config java
    ```
    type: 2
   
    ``` bash
    bash -c 'cat > /etc/default/jetty <<EOF
    JETTY_HOME=/opt/jetty-src
    JETTY_BASE=/opt/jetty
    JETTY_PID=/opt/jetty/jetty.pid
    JETTY_USER=jetty
    JETTY_START_LOG=/var/log/jetty/start.log
    TMPDIR=/opt/jetty/tmp
    EOF'
    ```

9. Create the service loadable from command line:

    ``` text
    cp /opt/jetty-src/bin/jetty.service /etc/systemd/system/jetty.service
    ```

    ``` text
    vi /etc/systemd/system/jetty.service
    ```
    change section [Service] with:
    ``` text  
    Type=simple
    User=jetty
    Group=jetty
    ExecStart=/usr/bin/java -jar /opt/jetty-src/start.jar jetty.home=/opt/jetty-src jetty.base=/opt/jetty jetty.http.port=8080
    ExecStop=/bin/kill ${MAINPID}
    SuccessExitStatus=143
    ```

    ``` text
    systemctl daemon-reload
    ```

    ``` text
    systemctl enable jetty.service
    ```

10. Install & configure several Jetty modules:

    ```text
    cd /opt/jetty
    ```

    ``` text
    java -jar $JETTY_HOME/start.jar --create-startd --add-modules=server,http,ext
    ```

    ``` text
    systemctl start jetty
    ```

    ``` text
    java -jar $JETTY_HOME/start.jar --create-startd --add-modules=home-base-warning,console-capture
    ```

    ``` text
    vi start.d/console-capture.ini
    ```
    Set line: `jetty.console-capture.dir=/var/log/jetty`

    ``` text
    chown jetty:jetty /opt/jetty/logs
    ```
    
    ``` text
    systemctl restart jetty
    ```

    ``` text
    java -jar $JETTY_HOME/start.jar --create-startd --add-modules=ee10-deploy,ee10-websocket-jakarta,ee10-websocket-jetty,ee10-servlets,ee10-annotations,ee10-jstl,threadpool,requestlog,ee10-plus,http-forwarded,logging-logback
    ```
    Type y at request "Proceed (y/N)?"

    ``` text
    systemctl restart jetty
    ```

    ``` text
    wget "https://github.com/ConsortiumGARR/idem-tutorials/raw/master/idem-fedops/HOWTO-Shibboleth/Identity%20Provider/utils/jetty-11-logging.properties" -O /opt/jetty/resources/jetty-logging.properties
    ```

11. Check if all settings are OK:

    ``` text
    systemctl check jetty
    ```

    ``` text
    systemctl status jetty
    ```

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
        cd /opt
        ```

    -   ``` text
        wget https://shibboleth.net/downloads/identity-provider/5.1.3/shibboleth-identity-provider-5.1.3.tar.gz
        ```
    
3.  Validate the package downloaded:

    -   ``` text
        wget https://shibboleth.net/downloads/identity-provider/5.1.3/shibboleth-identity-provider-5.1.3.tar.gz.asc
        ```

    -   ``` text
        wget https://shibboleth.net/downloads/PGP_KEYS
        ```

    -   ``` text
        gpg --import /opt/PGP_KEYS
        ```

    -   ``` text
        gpg --verify /opt/shibboleth-identity-provider-5.1.3.tar.gz.asc /opt/shibboleth-identity-provider-5.1.3.tar.gz
        ```

    If the verification contains also the name of Scott Cantor the package is valid.

    -   ``` text
        tar -xzf shibboleth-identity-provider-5.1.3.tar.gz
        ```

5.  Install Identity Provider Shibboleth:

    **NOTE**

    According to [NSA and NIST](https://www.keylength.com/en/compare/), **RSA with 3072 bit-modulus is the minimum** to protect up to TOP SECRET over than 2030.

    -   ``` text
        cd /opt/shibboleth-identity-provider-5.1.3
        ```

    -   ``` text
        ./bin/install.sh --hostName $(hostname -f)
        ```

    **!!! ATTENTION !!!**

    Replace the default value of `Attribute Scope` with the domain name of your institution.

    ``` bash
    Installation Directory: [/opt/shibboleth-idp] ?                                        (Press ENTER)
    SAML EntityID: [https://idp.example.org/idp/shibboleth] ?                              (Press ENTER)
    Attribute Scope: [example.org] ?                            (Digit your domain name and press ENTER)
    ```

    By starting from this point, the variable **%{idp.home}** into some IdP configuration files refers to the directory: `/opt/shibboleth-idp`

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

4.  Rebuild IdP war file:

    ``` text
    bash /opt/shibboleth-idp/bin/build.sh
    ```

[[TOC](#table-of-contents)]

## Configure Apache Web Server

1. Modify the file ```/etc/httpd/conf.d/ssl.conf``` as follows:

   ```apache
   <VirtualHost _default_:443>
     ServerName idp.example.org:443
     ServerAdmin admin@example.org
     DocumentRoot /var/www/html
     ...
     SSLEngine On
     SSLProtocol all -SSLv3 -SSLv2 -TLSv1 -TLSv1.1
     SSLProxyProtocol all -SSLv3 -SSLv2 -TLSv1 -TLSv1.1

     SSLHonorCipherOrder on
    
     SSLCipherSuite "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305"
    
     SSLProxyCipherSuite PROFILE=SYSTEM
       
     # Enable HTTP Strict Transport Security with a 2 year duration
     <IfModule headers_module>
        Header set X-Frame-Options DENY
        Header set Strict-Transport-Security "max-age=63072000 ; includeSubDomains ; preload"
     </IfModule>
     ...
     SSLCertificateFile /root/certificates/idp-cert-server.cer
     SSLCertificateKeyFile /root/certificates/idp-key-server.key
     SSLCertificateChainFile /root/certificates/DigiCertCA.cer
     ...
   
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
   ```

2. Create the file ```/etc/httpd/conf.d/idp.conf``` as follows:

   ``` text
   SSLUseStapling on
   SSLStaplingResponderTimeout 5
   SSLStaplingReturnResponderErrors off
   SSLStaplingCache shmcb:/var/run/ocsp(128000)

   <VirtualHost *:80>
      ServerName "idp.example.org"
      Redirect permanent "/" "https://idp.example.org/"
   </VirtualHost>
   ```   

4. Enable and start Apache web server:

   ``` text
    systemctl enable httpd
    ```
   
   ``` text
    systemctl start httpd
    ```
   
  
5. Verify the strength of your IdP's machine on:
   * [**https://www.ssllabs.com/ssltest/analyze.html**](https://www.ssllabs.com/ssltest/analyze.html)


[[TOC](#table-of-contents)]

## Configure Jetty Context Descriptor for IdP

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Configure the Jetty Context Descriptor:

    ``` text
    wget "https://github.com/ConsortiumGARR/idem-tutorials/raw/master/idem-fedops/HOWTO-Shibboleth/Identity%20Provider/utils/idp.xml" -O /opt/jetty/webapps/idp.xml
    ```

    On `idp.xml` change the line:

    ```<Configure class="org.eclipse.jetty.webapp.WebAppContext">```

    with

    ```<Configure class="org.eclipse.jetty.ee10.webapp.WebAppContext">```


3.  Make the **jetty** user owner of IdP main directories:

    ``` text
    cd /opt/shibboleth-idp
    ```

    ``` text
    chown -R jetty logs/ metadata/ credentials/ conf/ war/
    ```

4.  Restart Jetty:

    ``` text
    systemctl restart jetty
    ```

[[TOC](#table-of-contents)]

## Configure Shibboleth Identity Provider Storage Service

Shibboleth Documentation reference: [StorageConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199509576/StorageConfiguration)

The IdP provides a number of general-purpose storage facilities that can be used by core subsystems like session management and consent.

### Default (HTML Local Storage, Encryption GCM, No Database)

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
bash /opt/shibboleth-idp/bin/status.sh -u http://localhost:8080/idp
```

Proceed with [Configure the Directory Connection](#configure-the-directory-connection)

[[TOC](#table-of-contents)]

## Configure the Directory Connection

### openLDAP directory connection

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Install useful packages:

    ``` text
    dnf install openldap-clients
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
            vi /opt/shibboleth-idp/credentials/secrets.properties
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
            vi /opt/shibboleth-idp/conf/ldap.properties
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
            systemctl restart jetty
            ```

        -   Check IdP Status:

            ``` text
            bash /opt/shibboleth-idp/bin/status.sh -u http://localhost:8080/idp
            ```

        -   Proceed with [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)

    -   Solution 2 - LDAP + TLS:

        -   Configure `secrets.properties`:

            ``` text
            vi /opt/shibboleth-idp/credentials/secrets.properties
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
            vi /opt/shibboleth-idp/conf/ldap.properties
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
            systemctl restart jetty
            ```

        -   Check IdP Status:

            ``` text
            bash /opt/shibboleth-idp/bin/status.sh -u http://localhost:8080/idp
            ```

        -   Proceed with [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)

    -   Solution 3 - plain LDAP:

        -   Configure `secrets.properties`:

            ``` text
            vi /opt/shibboleth-idp/credentials/secrets.properties
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
            vi /opt/shibboleth-idp/conf/ldap.properties
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
            systemctl restart jetty
            ```

        -   Check IdP Status:

            ``` text
            bash /opt/shibboleth-idp/bin/status.sh -u http://localhost:8080/idp
            ```

        -   Proceed with [Configure Shibboleth Identity Provider to release the persistent NameID](#configure-shibboleth-identity-provider-to-release-the-persistent-nameid)

[[TOC](#table-of-contents)]

## Configure Shibboleth Identity Provider to release the persistent NameID

DOC: [PersistentNameIDGenerationConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199507892/PersistentNameIDGenerationConfiguration)

SAML 2.0 (but not SAML 1.x) defines a kind of NameID called a "*persistent*" identifier that every SP receives for the IdP users.
This part will teach you how to release the "*persistent*" identifiers with a database (Stored Mode) or without it (Computed Mode).

By default, a transient NameID will always be released to the Service Provider if the persistent one is not requested.

### Computed mode (Default & Recommended)

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Enable the generation of the computed `persistent-id` with:

    -   ``` text
        vi /opt/shibboleth-idp/conf/saml-nameid.properties
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
        vi /opt/shibboleth-idp/conf/saml-nameid.xml
        ```

        Uncomment the line: `<ref bean="shibboleth.SAML2PersistentGenerator" />`

    -   ``` xml+jinja
        vi /opt/shibboleth-idp/credentials/secrets.properties
        ```

        ``` xml+jinja
        idp.persistentId.salt = ### result of command 'openssl rand -base64 36' ###
        ```

3.  Restart Jetty to apply the changes:

    ``` text
    systemctl restart jetty
    ```

4.  Check IdP Status:

    ``` text
    bash /opt/shibboleth-idp/bin/status.sh -u http://localhost:8080/idp
    ```

5.  Proceed with [Configure the attribute resolver (sample)](#configure-the-attribute-resolver-sample)

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
    wget https://conf.idem.garr.it/idem-attribute-resolver-shib-v5.xml -O /opt/shibboleth-idp/conf/attribute-resolver.xml
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
    systemctl restart jetty
    ```

5.  Check IdP Status:

    ``` text
    bash /opt/shibboleth-idp/bin/status.sh -u http://localhost:8080/idp
    ```

[[TOC](#table-of-contents)]

## Configure Shibboleth Identity Provider to release the eduPersonTargetedID

eduPersonTargetedID is an abstracted version of the SAML V2.0 Name Identifier format of `urn:oasis:names:tc:SAML:2.0:nameid-format:persistent`.

To be able to follow these steps, you need to have followed the previous steps on `persistent` NameID generation.

### Computed mode - using the computed persistent NameID

1.  Become ROOT:

    ``` text
    sudo su -
    ```

2.  Check to have the following `<AttributeDefinition>` and the `<DataConnector>` into the `attribute-resolver.xml`:

    ``` text
    vi /opt/shibboleth-idp/conf/attribute-resolver.xml
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
    wget https://github.com/ConsortiumGARR/idem-tutorials/raw/master/idem-fedops/HOWTO-Shibboleth/Identity%20Provider/utils/eduPersonTargetedID.properties -O /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties
    ```

4.  Set proper owner/group with:

    ``` text
    chown jetty:root /opt/shibboleth-idp/conf/attributes/custom/eduPersonTargetedID.properties
    ```

5.  Restart Jetty to apply the changes:

    ``` text
    systemctl restart jetty
    ```

6.  Check IdP Status:

    ``` text
    bash /opt/shibboleth-idp/bin/status.sh -u http://localhost:8080/idp
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
-   Restart Jetty to apply the changes with
    ``` text
    systemctl restart jetty
    ```

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
    sudo systemctl restart jetty
    ```

[[TOC](#table-of-contents)]

## Enrich IdP Login Page with Information and Privacy Policy pages

1.  Add the following two lines into `views/login.vm`:

    ``` text
    <li class="list-help-item"><a href="#springMessageText("idp.url.infoPage", '#')"><span class="item-marker">&rsaquo;</span> #springMessageText("idp.login.infoPage", "Information page")</a></li>
    <li class="list-help-item"><a href="#springMessageText("idp.url.privacyPage", '#')"><span class="item-marker">&rsaquo;</span> #springMessageText("idp.login.privacyPage", "Privacy Policy")</a></li>
    ```

    under the line containing the Anchor:  `<a href="#springMessageText("idp.url.helpdesk", '#')">`

2.  Add the new variables defined with lines added at point 1 into all `messages*.properties` files linked to the view `view/login.vm`:

    -   Move to the IdP Home:

        ``` text
        cd /opt/shibboleth-idp
        ```

    -   Modify `messages.properties`:

        ``` text
        vi messages/messages.properties
        ```

        ``` text
        idp.login.infoPage=Informations
        idp.url.infoPage=https://my.organization.it/english-idp-info-page.html
        idp.login.privacyPage=Privacy Policy
        idp.url.privacyPage=https://my.organization.it/english-idp-privacy-policy.html
        ```

    -   Modify `messages_it.properties`:

        ``` text
        vi messages/messages_it.properties
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
    vi messages/messages.properties
    ```

    ``` xml+jinja
    idp.footer=Footer text for english version of IdP login page
    ```

-   ``` text
    vi messages/messages_it.properties:
    ```

    ``` xml+jinja
    idp.footer=Testo del Footer a pie di pagina per la versione italiana della pagina di login dell'IdP
    ```

    Rebuild IdP WAR file and Restart Jetty to apply changes:

    -   ``` text
        bash /opt/shibboleth-idp/bin/build.sh
        ```

    -   ``` text
        sudo systemctl restart jetty
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
    vi messages/messages.properties
    ```

    ``` xml+jinja
    idp.url.password.reset=CONTENT-FOR-FORGOT-YOUR-PASSWORD-LINK
    idp.url.helpdesk=CONTENT-FOR-NEED-HELP-LINK
    ```

-   Modify `messages_it.properties`:

    ``` text
    vi messages/messages_it.properties
    ```

    ``` xml+jinja
    idp.url.password.reset=CONTENUTO-PER-LINK-PASSWORD-DIMENTICATA
    idp.url.helpdesk=CONTENUTO-PER-SERVE-AIUTO-LINK
    ```

    Rebuild IdP WAR file and Restart Jetty to apply changes:

    -   ``` text
        bash /opt/shibboleth-idp/bin/build.sh
        ```

    -   ``` text
        sudo systemctl restart jetty
        ```

[[TOC](#table-of-contents)]

## Update IdP metadata

**(only for italian identity federation IDEM members)**

1.  Modify the IdP metadata as follow:

    ``` text
    vi /opt/shibboleth-idp/metadata/idp-metadata.xml
    ```

    1.  Remove completely the initial default comment

    2.  From the v5.1.3, the installer miss a space between `<md:EntityDescriptor` and `entityID` into the first line, add this space

    3.  Remove completely the `<mdui:UIInfo>` element and its content too.

    4.  Add the `HTTP-Redirect` SingleLogoutService endpoints under the `SOAP` one:

        ``` xml+jinja
        <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://idp.example.org/idp/profile/SAML2/Redirect/SLO"/>
        ```

        (replace `idp.example.org` value with the Full Qualified Domain Name of the Identity Provider.)

    5.  Between the last `<SingleLogoutService>` and the first `<SingleSignOnService>` endpoints add:

        ``` xml+jinja
        <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</md:NameIDFormat>
        <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</md:NameIDFormat>
        ```

        (because the IdP installed with this guide will release transient NameID, by default, and persistent NameID if requested.)

3.  Check that the metadata is available on `/idp/shibboleth` location:

    ``` text
    https://idp.example.org/idp/shibboleth
    ```

[[TOC](#table-of-contents)]

## Secure cookies and other IDP data

DOC: [SecretKeyManagement](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501624/SecretKeyManagement)

The default configuration of the IdP relies on a component called a "DataSealer" which in turn uses an AES secret key to secure cookies and certain other data for the IdPs own use. 
This key must never be shared with anybody else, and must be copied to every server node making up a cluster.
The Java "JCEKS" keystore file stores secret keys instead of public/private keys and certificates and a parallel file tracks the key version number.

These instructions will regularly update the secret key (and increase its version) and provide you the capability to push it to cluster nodes and continually maintain the secrecy of the key.

1.  Download `updateIDPsecrets.sh` into the right location:

    ``` text
    wget https://github.com/ConsortiumGARR/idem-tutorials/raw/master/idem-fedops/HOWTO-Shibboleth/Identity%20Provider/utils/updateIDPsecrets.sh -O /opt/shibboleth-idp/bin/updateIDPsecrets.sh
    ```

2.  Provide the right privileges to the script:

    ``` text
    sudo chmod +x /opt/shibboleth-idp/bin/updateIDPsecrets.sh
    ```

3.  Install Cron:

    ``` text
    sudo dnf install crontabs
    ```

4.  Create the CRON script to run it:

    ``` text
    sudo vi /etc/cron.daily/updateIDPsecrets
    ```

    ``` text
    #!/bin/bash

    /opt/shibboleth-idp/bin/updateIDPsecrets.sh
    ```

5.  Provide the right privileges to the script:

    ``` text
    sudo chmod +x /etc/cron.daily/updateIDPsecrets
    ```

6.  Confirm that the script will be run daily with (you should see your script in the command output):

    ``` text
    sudo run-parts --test /etc/cron.daily
    ```

7.  (OPTIONAL) Add the following properties to `conf/idp.properties` if you need to set different values than defaults:

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
    vi /opt/shibboleth-idp/conf/services.xml
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
          c:url="https://conf.idem.garr.it/idem-attribute-filter-shib-v5-full.xml"
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
    bash /opt/shibboleth-idp/bin/status.sh -u http://localhost:8080/idp
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
    systemctl restart jetty
    ```

[[TOC](#table-of-contents)]

## Appendix B: Useful logs to find problems

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

    -   **Audit Log:** `vi idp-audit.log`
    -   **Consent Log:** `vi idp-consent-audit.log`
    -   **Warn Log:** `vi idp-warn.log`
    -   **Process Log:** `vi idp-process.log`

[[TOC](#table-of-contents)]

## Appendix C: Connect an SP with the IdP

DOC:

-   [ChainingMetadataProvider](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199506765/ChainingMetadataProvider)
-   [FileBackedHTTPMetadataProvider](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199506865/FileBackedHTTPMetadataProvider)
-   [AttributeFilterConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501794/AttributeFilterConfiguration)
-   [AttributeFilterPolicyConfiguration](https://shibboleth.atlassian.net/wiki/spaces/IDP5/pages/3199501835/AttributeFilterPolicyConfiguration)

Follow these steps **IF** your organization **IS NOT** connected to the [GARR Network](https://www.garr.it/en/infrastructures/network-infrastructure/connected-organizations-and-sites).

1.  Connect the SP to the IdP by adding its metadata on the `metadata-providers.xml` configuration file:

    ``` text
    vi /opt/shibboleth-idp/conf/metadata-providers.xml
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
        wget https://github.com/ConsortiumGARR/idem-tutorials/raw/master/idem-fedops/HOWTO-Shibboleth/Identity%20Provider/utils/idem-example-arp.txt -O /opt/shibboleth-idp/conf/example-arp.txt
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

Alessandro Enea <alessandro.enea@ilc.cnr.it>

This guide is an adaptation of the guide for Debian-Ubuntu by Marco Malavolti (<marco.malavolti@garr.it>):<br/>
[HOWTO-Install-and-Configure-a-Shibboleth-IdP-v5.x-on-Debian-Ubuntu-Linux-with-Apache-+-Jetty](https://github.com/ConsortiumGARR/idem-tutorials/blob/master/idem-fedops/HOWTO-Shibboleth/Identity%20Provider/Debian-Ubuntu/HOWTO-Install-and-Configure-a-Shibboleth-IdP-v5.x-on-Debian-Ubuntu-Linux-with-Apache-%2B-Jetty.md)

[[TOC](#table-of-contents)]
