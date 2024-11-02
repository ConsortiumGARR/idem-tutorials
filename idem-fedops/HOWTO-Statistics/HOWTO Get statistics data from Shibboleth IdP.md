# HOWTO Get statistics data from Shibboleth IDP

### Instructions

1. Ensure to have installed Python (possibly > 2.5) on your IdP and to have the compliant format set for the `idp-audit.log` with:

   * Shibboleth IdP v4.x and v5.x:
     * `cat /opt/shibboleth-idp/conf/audit.xml | grep Shibboleth-Audit`

       ```xml  
       <entry key="Shibboleth-Audit" value="%a|%ST|%T|%u|%SP|%i|%ac|%t|%attr|%n|%f|%SSO|%XX|%XA|%b|%bb|%e|%S|%SS|%s|%UA" />
       ```

   * Shibboleth IdP v3.x (DEPRECATED):
     * `cat /opt/shibboleth-idp/conf/audit.xml | grep Shibboleth-Audit`

       ```xml  
       <entry key="Shibboleth-Audit" value="%T|%b|%I|%SP|%P|%IDP|%bb|%III|%u|%ac|%attr|%n|%i|" />
       ```

   These are the formats compliant with the script provided into this HOWTO.

2. Save the python script [idem-loganalysis-idp_v3_v4_v5.py](./idem-loganalysis-idp_v3_v4_v5.py) as `$HOME/loganalisys.py`, or just copy and paste the command below:

   * ```
     wget https://raw.githubusercontent.com/ConsortiumGARR/idem-tutorials/master/idem-fedops/HOWTO-Statistics/idem-loganalysis-idp_v3_v4_v5.py -O $HOME/loganalisys.py
     ```

3. Set the IDP_HOME env variable with:

   * `export IDP_HOME=/opt/shibboleth-idp`

     (replace the `/opt/shibboleth-idp` value with your Shibboleth IdP Home path)

4. Extract the data for each month and save the statistics in a corresponding JSON file:

   * Python 2.x - IdP v4.x / IdP v5.x: 
     ```bash
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-09* | python $HOME/loganalisys.py -j4 - > idp_$(dnsdomainname)_2024_09_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-10* | python $HOME/loganalisys.py -j4 - > idp_$(dnsdomainname)_2024_10_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-11* | python $HOME/loganalisys.py -j4 - > idp_$(dnsdomainname)_2024_11_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-12* | python $HOME/loganalisys.py -j4 - > idp_$(dnsdomainname)_2024_12_sso_stats.json
     ```

   * Python 3.x - IdP v4.x / IdP v5.x:
     ```bash
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-09* | python3 $HOME/loganalisys.py -j4 - > idp_$(dnsdomainname)_2024_09_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-10* | python3 $HOME/loganalisys.py -j4 - > idp_$(dnsdomainname)_2024_10_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-11* | python3 $HOME/loganalisys.py -j4 - > idp_$(dnsdomainname)_2024_11_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-12* | python3 $HOME/loganalisys.py -j4 - > idp_$(dnsdomainname)_2024_12_sso_stats.json
     ```

   * Python 2.x - IdP v3.x (DEPRECATED): 
     ```bash
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-09* | python $HOME/loganalisys.py -j - > idp_$(dnsdomainname)_2024_09_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-10* | python $HOME/loganalisys.py -j - > idp_$(dnsdomainname)_2024_10_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-11* | python $HOME/loganalisys.py -j - > idp_$(dnsdomainname)_2024_11_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-12* | python $HOME/loganalisys.py -j - > idp_$(dnsdomainname)_2024_12_sso_stats.json
     ```

   * Python 3.x - IdP v3.x (DEPRECATED):
     ```bash
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-09* | python3 $HOME/loganalisys.py -j - > idp_$(dnsdomainname)_2024_09_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-10* | python3 $HOME/loganalisys.py -j - > idp_$(dnsdomainname)_2024_10_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-11* | python3 $HOME/loganalisys.py -j - > idp_$(dnsdomainname)_2024_11_sso_stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2024-12* | python3 $HOME/loganalisys.py -j - > idp_$(dnsdomainname)_2024_12_sso_stats.json
     ```

4. Unset the IDP_HOME env variable with:

   * `unset IDP_HOME`


### Example JSON output (for one month)

```json
{
 "stats": {
   "logins": 29,
   "rps": 8,
   "users": 3
   "version": "5.0.0"
 },
 "logins_per_rp": {
   "https://filesender.garr.it/shibboleth": 5,
   "https://coco.release-check.edugain.org/shibboleth": 1,
   "https://sp-demo.idem.garr.it/shibboleth": 2,
   "https://rendez-vous.renater.fr/shibboleth": 1,
   "https://rns-ng.release-check.edugain.org/shibboleth": 1,
   "https://buponline.com/shibboleth": 2,
   "https://sp24-test.garr.it/shibboleth": 16,
   "https://noec.release-check.edugain.org/shibboleth": 1
 }
}
```
   
### UTILITY

See help message:

* Python 2.x: `python loganalisys.py -h`
* Python 3.x: `python3 loganalisys.py -h`

### Authors

#### Original Author

* Marco Malavolti (marco.malavolti@garr.it)

### Thanks

* Peter Schober original script: https://gitlab.com/peter-/shib-idp-auditlog
