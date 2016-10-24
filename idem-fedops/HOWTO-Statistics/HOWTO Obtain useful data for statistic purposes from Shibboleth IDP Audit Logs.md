# HOWTO OBTAIN USEFUL DATA FOR STATISTIC PURPOSES FROM SHIBBOLETH IDP AUDIT LOGS

1. Ensure to have installed Python (possibly > 2.5) on your IdP

2. Save the python script [idem-loganalysis-idp-v2_v3.py](./idem-loganalysis-idp-v2_v3.py) into a file "loganalysis.py"

3. Obtain the statistics from your logs:
  * Number of logins done in september 2016: 
    
    ```zcat /opt/shibboleth-idp/logs/idp-audit-2016-09-*.gz | python loganalysis.py -l -```
    
    Returns:
    
    ```22 logins```
  
  * Number of logins done from the users in september 2016: 
  
    ```zcat /opt/shibboleth-idp/logs/idp-audit-2016-09-*.gz | python loganalysis.py -a -```

    Returns:
    
    ```
    21       | malavolti
    1        | lalla
    ```
  
  * Number of logins done for each SP in september 2016: 
  
    ```zcat /opt/shibboleth-idp/logs/idp-audit-2016-09-*.gz | python loganalysis.py -n -```

    Returns:
    
    ```
    logins   | relyingPartyId
    -------------------------
    21       | https://sp24-test.garr.it/shibboleth
    1        | https://met.refeds.org/saml2/metadata/
    ```
