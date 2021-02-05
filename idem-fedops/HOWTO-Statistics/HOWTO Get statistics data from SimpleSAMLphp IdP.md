# HOWTO Get statistics data from SimpleSAMLphp IdP

This HOWTO is needed for those SimpleSAMLphp IdP that did not collect access statistics with `statistics` module of SSP.
Who already use `statistics` module, do not need this.

## Instructions

1. Follow the steps provided here: https://github.com/ConsortiumGARR/ssp-statistics-parser

2. By considering only the "AlignedMonth" of "SSP to service",
   generate a files named `idp-$(dnsdomainname)-sso-stat-<YEAR><MONTH>.json` (es.: idp-garr.it-sso-stat-202009.json)
   for each month requested with the JSON format:

   ```json
   {
    "logins_per_rp": {
      "https://sp24-test.garr.it/shibboleth": 2,
      "https://filesender.garr.it/shibboleth": 1,
      "https://sp-demo.aai.garr.it/shibboleth": 3
    }
   }
   ```

## Authors
 * Marco Malavolti (marco.malavolti@garr.it)
