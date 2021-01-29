# HOWTO Obtain useful data for statistics purposes from Shibboleth IdP Audit logs

1. Ensure to have installed Python (possibly > 2.5) on your IdP

2. Save the python script [idem-loganalysis-idp_v3.py](./idem-loganalysis-idp_v3.py) into your HOME as `$HOME/loganalisys.py`

3. Save the statistics into a file named `idp-<DOMAIN-NAME>-sso-stats.json`:
   * Python 2.x: 
     ```bash
     zcat /opt/shibboleth-idp/logs/idp-audit-2020-[09-10-11-12]* /opt/shibboleth-idp/logs/idp-audit-2021-01-* | python $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-sso-stats.json
     ```
   * Python 3.x:
     ```bash
     zcat /opt/shibboleth-idp/logs/idp-audit-2020-[09-10-11-12]* /opt/shibboleth-idp/logs/idp-audit-2021-01-* | python3 $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-sso-stats.json
     ```
   
### UTILITY

See help message:

* Python 2.x: `python loganalisys.py -h`
* Python 3.x: `python3 loganalisys.py -h`

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
