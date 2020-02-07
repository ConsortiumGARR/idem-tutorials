HOWTO Make Shibboleth IdP Highly Available with local containers
----------------------------------------------------------------


1. [Introduction](#introduction)
2. [Installation of the necessary software](#installation-of-the-necessary-software)
3. [LXC](#lxc)
5. [NginX](#nginx)
4. [Test](#test)
6. [Authors](#authors)
7. [Credits](#credits)

Introduction
------------

This HowTo discusses the main challenges of having a High availabile IdP service.
In this example we also purpose a strategy based on containers, with the help of LXC, and a passive TCP health check, with the help of NginX.

The same concept could be also developed with Docker as container/microservice solution and HAproxy as TCP Loadbalancer.

This HowTo works as-is with the idem-tutorials, probably the most demanding users will certainly want to manage shared session storage among the containers. If the session storage has been configured as showed in the `idem-tutorials` there's no need to deploy a centralized storage service.
This asset allows for example to block the communication on port 8080 of a container (iptables or comment it out in nginx configuration) modify the configuration of a ShibIdP, test this adequately. Then reintroduce the updated instance into the HA cluster. Then wait for further analysis, propagate this update also to the backup copy (rsync via hypervisor roots). Everything without any downtime.

:warning: WARNING: Mind That if the Shibboleth servers/containers doesn't have any JSESSIONID shared storage (Memcached) or user-agent localStorage (idem-tutorials) the users must login again on each HA takeover.
For avoiding this it's suggested to enable a [MemcachedStorageService](https://wiki.shibboleth.net/confluence/display/IDP30/StorageConfiguration) or another kind of storage (RDBMS).

:warning: WARNING: The community edition of NginX only offer to us a passive health check (TCP Layer 4) and not a fully compliant Layer 7 check. Please use Nginx plus or compile Nginx from source, enable a community health check plugin, or use HAproxy instead.

:warning: WARNING: Without a MDQ MetadataProvider each ShibIdP container will consume RAM to handle indipendently the EduGAIN Metadata. It's suggested to use a federation MDQ server or a [local setup of this]().

Installation of the necessary software
--------------------------------------

````
apt install lxc nginx
````

LXC
---

In this example we use an [ansible playbook](https://github.com/peppelinux/Ansible-Shibboleth-IDP-SP-Debian) for the IdP deployment but all the installation steps described in [idem-tutorials](https://github.com/ConsortiumGARR/idem-tutorials) can be executed by hands, obtaining a fully working IdP.
the installation of Apache2 is useless for this scope, we just have to install the servlet container (jetty) and Shibboleth IdP, and get it run on the desidered port.


````
CONTAINER_NAME=shib

lxc-create  -t download -n $CONTAINER_NAME -- -d debian -r buster -a amd64

# give optionally a static ip to the container or set a static lease into your dnsmasq local instance
echo "lxc.network.ipv4 = 10.0.3.201/24 10.0.3.255" >> /var/lib/lxc/$CONTAINER_NAME/config
echo "lxc.network.ipv4.gateway = 10.0.3.1" >> /var/lib/lxc/$CONTAINER_NAME/config

# configure the container with an "unconfined" profile, otherwise ntp processes can't start.
# see `man lxc.container.conf` to have a better acknowledge
echo "lxc.aa_profile = unconfined" >> /var/lib/lxc/$CONTAINER_NAME/config

lxc-start -n shib1
lxc-attach $CONTAINER_NAME -- apt install python3-pip libffi-dev libssl-dev \
                               libxml2-dev libxslt1-dev libjpeg-dev \
                               zlib1g-dev apt-utils iputils-ping tcpdump curl
````

If you want to setup the IdP manually or need to migrate an existing one, enter in the running container and do the things, step by step:
````
lxc-attach $CONTAINER_NAME
````

If you want instead to run the ansible-playbook remember to run only the desidered tasks, as showed in this example.
Copy and modify the playbook `playbook.yml` and `make_CA.3.sh` as showed in the example, then copy the playbook folder into the container rootfs tree. Using these tags only Jetty and Shibboleth IdP will be installed.
````
# cp your modified playbook
cp -R Ansible-Shibboleth-IDP-SP-Debian /var/lib/lxc/$CONTAINER_NAME/rootfs/root/

# run it
lxc-attach $CONTAINER_NAME -- pip3 install ansible
lxc-attach $CONTAINER_NAME -- bash -c "cd /root/Ansible-Shibboleth-IDP-SP-Debian && \
                              bash make_ca.production.sh && \
                              ansible-playbook -i "localhost," -c local \
                              playbook.production.yml --tag uninstall,common, idp_install, idp_configure"
````

#### Final steps

Once jetty socket is running in the container and `/opt/shibboleth-opt/logs/idp-process.log` give us a healty status of the service let's remove the installation files:
````
# if they are in /opt, otherwise ...
cd /opt
rm -R jetty-distribution-9.4.26.v20200117.tar.gz shibboleth-identity-provider-3.4.6  shibboleth-identity-provider-3.4.6.tar.gz java-1.8.0-amazon-corretto-jdk_8.232.09-1_amd64.deb
apt clean
apt autoremove
````

- Test a metadata download: `curl http://localhost:8080/idp/shibboleth`
- Test an attribute policy: `aacli -n $username -r $sp_entityID --saml2 -u http://localhost:8080/idp`
- Exit the container `exit` or `Ctrl+D`
- See container status with `lxc-ls -f`
- Clone the container (stop it first), or snapshot if they are on top of an LVM volume, `lxc-copy -n shib1 -N shib2`, change/set (dns or static) `shib2`'s ip before starting it `lxc-start shib2`
- Configure the containers for autorun at boottime `lxc.start.auto = 0` in `/var/lib/lxc/$CONTAINER_NAME/config
- Start the containers


NginX
-----

This is an example of a passive health check with NginX.
The commented health checks options can be enabled with NginX Plus edition or installing by hands (need compilation) the community plugin.

````
upstream shib_balancer {
        least_conn;
        server 10.0.3.101:8080 max_fails=1 fail_timeout=10s;
        server 10.0.3.102:8080 backup;
}

# not available in commutity edition
#match server_ok {
# something like:
#    status 200;
#    body !~ "maintenance";
# or:
#    send      "GET /idp/shibboleth HTTP/1.0\r\nHost: localhost\r\n\r\n";
#    expect ~* "200 OK";
#}

server {
    listen      80;
    server_name idp.testunical.it; # substitute your machine's IP address or FQDN

    access_log /var/log/nginx/idp.testunical.it.access.log;
    error_log  /var/log/nginx/idp.testunical.it.error.log error;

    return 301 https://$host$request_uri;
}

server {
    server_name idp.testunical.it;
    charset     utf-8;

    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/shib-balancer/idp.testunical.it-cert.pem;
    ssl_certificate_key /etc/ssl/certs/shib-balancer/idp.testunical.it-key.pem;

    access_log /var/log/nginx/idp.testunical.it.access.log;
    error_log  /var/log/nginx/idp.testunical.it.error.log error;

    # max upload size
    client_max_body_size 5M;   # adjust to your tastes

    location /idp {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 300;
        port_in_redirect off;

        # these fixes SAML message intended destination endpoint did not match the recipient endpoint
        # $scheme is https.
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;

        # HSTS
        add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; ";
        add_header X-Frame-Options "DENY";

        proxy_set_header X-Forwarded-Server $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://shib_balancer;

        # not available in commutity edition
        #health_check interval=5 passes=1 fails=1;
        #health_check match=server_ok;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
    root   /usr/local/nginx/html;
    }

}
````
Tests
----

Do your tests with a SP or a simple curl command like the following. It make a Http Request every second:
````
watch -n1 curl -v https://idp.testunical.it/idp/shibboleth -k | head
````

Now try stopping `lxc-stop shib1`, you'll see that your Http Requests will continue working without any problems.
Then start `shib1` and stop `shib2`, nothing change, shib2 is only a backup server.

Authors
-------
Giuseppe De Marco <giuseppe.demarco@unical.it>

Credits
-------
The Community.
