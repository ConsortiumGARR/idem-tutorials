<?php
/*
 * AttributePolicy configuration file.
 *
 * Define the attributes to release:
 * - by default
 * - by EntityID
 * - by a regular expression based on EntityID
 *
*/

$config = [

   /* Default Policy */
   'default' => [],

   /*SP 2.4 di Test di IDEM*/
   'https://sp24-test.garr.it/shibboleth' => 
      [
       'uid',
       'sn',
       'givenName',
       'cn',
       'displayName',
       'schacDateOfBirth',
       'schacYearOfBirth',
       'schacPalceOfBirth',
       'schacPersonalUniqueID',
       'schacPersonalPosition',
       'schacPersonalTitle',
       'schacUserPresenceID',
       'schacHomeOrganization',
       'schacHomeOrganizationType',
       'schacMotherTongue',
       'street',
       'houseIdentifier',
       'locality',
       'preferredLanguage',
       'postalCode',
       'stateProvince',
       'countryName',
       'friendlyCountryName',
       'email',
       'telephoneNumber',
       'facsimileTelephoneNumber',
       'mobile',
       'orgainzationalUnit',
       'organizationName',
       'eduPersonOrgDN',
       'eduPersonOrgUnitDN',
       'eduPersonPrincipalName',
       'eduPersonEntitlement',
       'eduPersonAffiliation',
       'eduPersonScopedAffiliation',
       'eduPersonTargetedID',
       'title',
      ],

   'https://sp-test.garr.it/shibboleth' =>
      [
       'cn',
       'uid',
       'email',
       'sn',
       'organizationName',
       'organizationalUnit',
       'givenName',
       'preferredLanguage',
       'eduPersonAffiliation',
       'eduPersonEntitlement',
       'eduPersonOrgUnitDN',
       'eduPersonPrimaryAffiliation',
       'eduPersonPrincipalName',
       'eduPersonTargetedID',
       'eduPersonScopedAffiliation',
      ],

   'https://sp2-test.garr.it/shibboleth' =>
      [
       'cn',
       'uid',
       'email',
       'sn',
       'organizationName',
       'organizationalUnit',
       'givenName',
       'preferredLanguage',
       'eduPersonAffiliation',
       'eduPersonEntitlement',
       'eduPersonOrgUnitDN',
       'eduPersonPrimaryAffiliation',
       'eduPersonPrincipalName',
       'eduPersonTargetedID',
       'eduPersonScopedAffiliation',
      ],

   'https://registry.idem.garr.it/shibboleth' =>
      [
       'givenName',
       'sn',
       'email',
       'eduPersonPrincipalName',
       'eduPersonTargetedID',
      ],

   'https://sp-demo.aai-test.garr.it/shibboleth' =>
      [
       'cn',
       'uid',
       'email',
       'sn',
       'organizationName',
       'organizationalUnit',
       'givenName',
       'preferredLanguage',
       'eduPersonAffiliation',
       'eduPersonEntitlement',
       'eduPersonOrgUnitDN',
       'eduPersonPrimaryAffiliation',
       'eduPersonPrincipalName',
       'eduPersonTargetedID',
       'eduPersonScopedAffiliation',
      ],
];

?>
