# HOWTO Get statistics data from Shibboleth IDP

1. Ensure to have installed Python (possibly > 2.5) on your IdP

2. Save the python script [idem-loganalysis-idp_v3.py](https://raw.githubusercontent.com/ConsortiumGARR/idem-tutorials/master/idem-fedops/HOWTO-Statistics/idem-loganalysis-idp_v3.py) into your HOME as `$HOME/loganalisys.py`

3. Extract the data for January 2021 and save the statistics into a file named `idp-<DOMAIN-NAME>-Jan-2021-sso-stats.json`:
   * Python 2.x: 
     ```bash
     zcat /opt/shibboleth-idp/logs/idp-audit-2020-09* | python $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-2020-09-sso-stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2020-10* | python $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-2020-10-sso-stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2020-11* | python $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-2020-11-sso-stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2020-12* | python $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-2020-12-sso-stats.json
     cat /opt/shibboleth-idp/logs/idp-audit-2021-01-* | python $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-2021-01-sso-stats.json
     ```
   * Python 3.x:
     ```bash
     zcat /opt/shibboleth-idp/logs/idp-audit-2020-09* | python3 $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-2020-09-sso-stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2020-10* | python3 $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-2020-10-sso-stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2020-11* | python3 $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-2020-11-sso-stats.json
     zcat /opt/shibboleth-idp/logs/idp-audit-2020-12* | python3 $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-2020-12-sso-stats.json
     cat /opt/shibboleth-idp/logs/idp-audit-2021-01-* | python3 $HOME/loganalisys.py -j - > idp-$(dnsdomainname)-2021-01-sso-stats.json
     ```
     
   Example JSON output (for one month):
   ```json
   {
    "stats": {
      "logins": 29,
      "rps": 8,
      "users": 3
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
