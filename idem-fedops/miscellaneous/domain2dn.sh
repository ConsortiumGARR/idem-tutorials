################################################
#                                              #
# Bash Script useful to convert                #
# a domain name into a LDAP distinguished name #
#                                              #
################################################

#!/usr/bin/env bash

LDAP_DC_ARRAY=()
LDAP_DC=""

echo "Enter your domain name (e.g.: example.org):"
read DOMAIN

DCS=$(echo $DOMAIN | tr "." "\n")

for dc in $DCS
do
    LDAP_DC_ARRAY+=("dc=$dc")
done

# Iterate the loop to read and print each array element
for value in "${LDAP_DC_ARRAY[@]}"
do
     LDAP_DC+="$value"
     if [[ "$value" != ${LDAP_DC_ARRAY[-1]} ]]; then
        LDAP_DC+=","
     fi
done

echo $LDAP_DC
