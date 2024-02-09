# HOWTO Get statistics data from SimpleSAMLphp IdP

**This HOWTO is applicable for those who have enabled the Authentication Process Filter "[statistics:StatisticsWithAttribute](https://simplesamlphp.org/docs/contrib_modules/statistics/authproc_statisticswithattribute.html)" but not the [SimpleSAMLphp statistics module](https://simplesamlphp.org/docs/contrib_modules/statistics/statistics.html) on the Identity Provider.**

To determine if your SimpleSAMLphp installation has the required Authentication Process Filter enabled, which is required by this HOWTO, check the following files:

* `config/config.php`
* `metadata/saml20-idp-hosted.php`

Those who already use SimpleSAMLphp statistics module and `statistics:StatisticsWithAttribute` authentication process **do not need to follow this HOWTO**.

## Instructions

1. Follow the steps provided here: https://github.com/ConsortiumGARR/ssp-statistics-parser

2. By considering only the "**AlignedMonth**" of "**SSO to service**",
   generate a files named `idp-$(dnsdomainname)-sso-stat-<YEAR><MONTH>.json` (es.: `idp-garr.it-sso-stat-202009.json`)
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
