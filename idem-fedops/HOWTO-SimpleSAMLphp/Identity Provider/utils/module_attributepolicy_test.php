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

   /*SP di Test di IDEM*/
   'https://sp.aai-test.garr.it/shibboleth' => 
      [
       'eduPersonScopedAffiliation',
       'eduPersonTargetedID',
       'mail',
       'eduPersonPrincipalName',
       'displayName',
       'eduPersonOrcid',
       'sn',
       'givenName',
       'eduPersonEntitlement',
       'cn',
       'eduPersonOrgDN',
       'title',
       'telephoneNumber',
       'eduPersonOrgUnitDN',
       'schacPersonalTitle',
       'schacPersonalUniqueID',
       'schacHomeOrganization',
       'schacHomeOrganizationType',
       'schacUserPresenceID',
       'mobile',
       'schacMotherTongue',
       'preferredLanguage',
       'schacGender',
       'schacDateOfBirth',
       'schacPlaceOfBirth',
       'schacCountryOfCitizenship',
       'schacSn1',
       'schacSn2',
       'schacCountryOfResidence',
       'schacPersonalUniqueCode',
       'schacExpiryDate',
       'schacUserPrivateAttribute',
       'schacUserStatus',
       'schacProjectMembership',
       'schacProjectSpecificRole',
       'schacYearOfBirth',
       'eduPersonNickname',
       'eduPersonPrimaryAffiliation',
       'eduPersonPrimaryOrgUnitDN',
       'eduPersonAssurance',
       'eduPersonPrincipalNamePrior',
       'eduPersonUniqueId',
      ],

   'https://registry.idem.garr.it/shibboleth' =>
      [
       'givenName',
       'sn',
       'email',
       'eduPersonPrincipalName',
       'eduPersonTargetedID',
      ],
];

?>
