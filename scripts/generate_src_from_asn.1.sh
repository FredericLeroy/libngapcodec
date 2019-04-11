#!/bin/bash

set -e

export ASN1C_PREFIX=Ngap_

asn1c \
    -pdu=all \
    -fcompound-names \
    -fno-include-deps \
    -findirect-choice \
    -gen-PER \
    -D src \
    asn.1/*.asn1

#sed -e 's/libasncodec/libngap/g' \
#    -i \
#    src/Makefile.am.libasncodec
