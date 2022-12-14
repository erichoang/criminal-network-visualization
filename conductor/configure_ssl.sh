#!/bin/bash

### SUBJECT OPTIONS ###
SCRIPT_DIR=$(dirname "$0")
CONFIG_OUTPUT="$SCRIPT_DIR/openssl.conf"
KEY_OUTPUT="$SCRIPT_DIR/sna-api.key"
CERTIFICATE_OUTPUT="$SCRIPT_DIR/sna-api.cert"
DHPARAM_OUTPUT="$SCRIPT_DIR/dhparam.pem"

if [ ! -e "$DHPARAM_OUTPUT" ]; then
    openssl dhparam -out $DHPARAM_OUTPUT 2048
fi

if [ -e "$KEY_OUTPUT" ] && [ -e "$CERTIFICATE_OUTPUT" ]; then
    exit 0
fi

COUNTRY_NAME=${COUNTRY:="GE"}
STATE_NAME=${STATE:="Niedersachsen"}
LOCALITY_NAME=${LOCALITY:="Hannover"}
ORGANISATION_NAME=${ORGANISATION:="l3s"}
COMMON_NAME=${NAME:="www.sna.de"}

### SET DNS ###

DOMAIN_NAMES=(${DOMAINS//;/ })
DNS_COUNTER=0
DOMAINS_STRING=""

for domain in "${DOMAIN_NAMES[@]}"; do
    ((DNS_COUNTER+=1))
    DOMAINS_STRING="$DOMAINS_STRING\nDNS.$DNS_COUNTER   = $domain"
done

if [ -n $DISABLE_LOCALHOST ]; then
    ((DNS_COUNTER+=1))
    DOMAINS_STRING="$DOMAINS_STRING\nDNS.$DNS_COUNTER   = localhost"
    ((DNS_COUNTER+=1))
    DOMAINS_STRING="$DOMAINS_STRING\nDNS.$DNS_COUNTER   = localhost.localdomain"
    ((DNS_COUNTER+=1))
    DOMAINS_STRING="$DOMAINS_STRING\nDNS.$DNS_COUNTER   = 127.0.0.1"
    ((DNS_COUNTER+=1))
    DOMAINS_STRING="$DOMAINS_STRING\nDNS.$DNS_COUNTER   = ::1"
fi

### FILL TEMPLATE ###

CONFIG_TEMPLATE="[ req ]
default_bits        = 2048
default_keyfile     = server-key.pem
req_extensions      = req_ext
x509_extensions     = x509_ext
string_mask         = utf8only
distinguished_name  = subj_name

[ subj_name ]

C = $COUNTRY_NAME
ST = $STATE_NAME
L = $LOCALITY_NAME
O = $ORGANISATION_NAME
CN = $COMMON_NAME

# Section x509_ext is used when generating a self-signed certificate. I.e., openssl req -x509 ...
[ x509_ext ]

subjectKeyIdentifier        = hash
authorityKeyIdentifier    = keyid,issuer

# You only need digitalSignature below. *If* you don't allow
#   RSA Key transport (i.e., you use ephemeral cipher suites), then
#   omit keyEncipherment because that's key transport.
basicConstraints        = CA:FALSE
keyUsage            = digitalSignature, keyEncipherment
subjectAltName          = @alternate_names
nsComment           = 'OpenSSL Generated Certificate'

# RFC 5280, Section 4.2.1.12 makes EKU optional
#   CA/Browser Baseline Requirements, Appendix (B)(3)(G) makes me confused
#   In either case, you probably only need serverAuth.
extendedKeyUsage    = serverAuth, clientAuth

# Section req_ext is used when generating a certificate signing request. I.e., openssl req ...
[ req_ext ]

subjectKeyIdentifier        = hash

basicConstraints        = CA:FALSE
keyUsage            = digitalSignature, keyEncipherment
subjectAltName          = @alternate_names
nsComment           = 'OpenSSL Generated Certificate'

# RFC 5280, Section 4.2.1.12 makes EKU optional
#   CA/Browser Baseline Requirements, Appendix (B)(3)(G) makes me confused
#   In either case, you probably only need serverAuth.
extendedKeyUsage    = serverAuth, clientAuth

[ alternate_names ]

$DOMAINS_STRING"

### GENERATE CERTIFICATES ###

echo -e "$CONFIG_TEMPLATE" >> $CONFIG_OUTPUT

openssl req -config $CONFIG_OUTPUT -new -x509 -sha256 -newkey rsa:4096 -nodes \
    -keyout $KEY_OUTPUT -days 365 -out $CERTIFICATE_OUTPUT -subj "/C=$COUNTRY_NAME/ST=$STATE_NAME/L=$LOCALITY_NAME/O=$ORGANISATION_NAME/CN=$COMMON_NAME"
