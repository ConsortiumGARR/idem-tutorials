# HOWTO Get statistics data from SimpleSAMLphp IdP

**This HOWTO is applicable for those who have enabled the Authentication Process Filter "[statistics:StatisticsWithAttribute](https://simplesamlphp.org/docs/contrib_modules/statistics/authproc_statisticswithattribute.html)" on the Identity Provider.**

To determine if your SimpleSAMLphp instance has the required Authentication Process Filter enabled, required by this HOWTO, check your `metadata/saml20-idp-hosted.php` and find out the following `authproc`:

```php
45 => [
    'class' => 'core:StatisticsWithAttribute',
    'attributename' => 'realm',
    'type' => 'saml20-idp-SSO',
],
```

## Instructions

Follow the steps provided [here](https://github.com/ConsortiumGARR/ssp-loganalysis/tree/main?tab=readme-ov-file#ssp-loganalysisphp).


## Authors
 * Marco Malavolti (marco.malavolti@garr.it)
