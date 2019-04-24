# libngapcodec

A C library to encode/decode NGAP message defined by 3gpp TS 38413

## Description

This is a static library for coding/decoding NGAP protocol.
It is based on the asn1c code generator and official 3gpp specs, without
modification on the asn descriptions.

## Build instructions

### static library

This library depends only on gcc and make in order to build it.

    $ sudo apt install make gcc

## Installation

### On system

    $ sudo make install

This installs files in the following folder:

| Folder | Description |
|-----------------------------------------|--------------------------------|
| /usr/local/lib/ngapcodec/<version>      | static library                 |
| /usr/local/include/ngapcodec-<version>  |  c headers                     |
| /usr/local/share/pkgconfig              |  pkg-config configuration file |
| /usr/local/share/libngapcodec/<version> |  asn1 description files        |

You can change the /usr/local prefix by setting the PREFIX variable with
the make command:

    $ sudo make install PREFIX=/usr

The Makefile support also the common DESTDIR variable in order to install to
another place.

### By building a debian package

install debian packaging tools :

    $ sudo apt install build-essential debhelper

build the debian package:

    $ dpkg-buildpackage -b
    dpkg-buildpackage: source package libngapcodec
    dpkg-buildpackage: source version 15.2.0-1
    dpkg-buildpackage: source distribution unstable
    dpkg-buildpackage: source changed by Frédéric Leroy <frederic.leroy@b-com.com>
    dpkg-buildpackage: host architecture amd64
     dpkg-source --before-build src
     fakeroot debian/rules clean
    [...]
    dpkg-deb: building package 'libngapcodec-dev' in '../libngapcodec-dev_15.2.0-1_amd64.deb'.
     dpkg-genchanges -b >../libngapcodec_15.2.0-1_amd64.changes
    dpkg-genchanges: binary-only upload (no source code included)
     dpkg-source --after-build src
    dpkg-buildpackage: binary-only upload (no source included)
    $

Then you can install it:

    $ sudo dpkg -i ../libngapcodec-dev_15.2.0-1_amd64.deb

## Example program

In order to compile the example, you need to install the pkg-config tool:

    $ sudo apt install pkg-config

Then just go in the example folder and launch make:

    $ make
    cc -DASN_PDU_COLLECTION -I. `pkg-config --cflags ngapcodec-15.2.0` -o converter-example.o -c converter-example.c
    cc -DASN_PDU_COLLECTION -I. `pkg-config --cflags ngapcodec-15.2.0` -o pdu_collection.o -c pdu_collection.c
    cc -DASN_PDU_COLLECTION -I. `pkg-config --cflags ngapcodec-15.2.0`  -o converter-example converter-example.o pdu_collection.o `pkg-config --static --libs ngapcodec-15.2.0`
    $

## Testing with the example program

The converte example program have many option to encode/decode pdu packets.
Here are it's help usage:

    $ ./converter-example -h
    Usage: ./converter-example [options] <datafile> ...
    Where options are:
      -iber        Input is in BER (Basic Encoding Rules) or DER
      -ioer        Input is in OER (Octet Encoding Rules)
      -iper        Input is in Unaligned PER (Packed Encoding Rules) (DEFAULT)
      -iaper        Input is in Aligned PER (Packed Encoding Rules)
      -ixer        Input is in XER (XML Encoding Rules)
      -oder        Output as DER (Distinguished Encoding Rules)
      -ooer        Output as Canonical OER (Octet Encoding Rules)
      -oper        Output as Unaligned PER (Packed Encoding Rules)
      -oaper       Output as Aligned PER (Packed Encoding Rules)
      -oxer        Output as XER (XML Encoding Rules) (DEFAULT)
      -otext       Output as plain semi-structured text
      -onull       Verify (decode) input, but do not output
      -per-nopad   Assume PER PDUs are not padded (-iper)
      -p <PDU>     Specify PDU type to decode
      -p list      List available PDUs
      -1           Decode only the first PDU in file
      -b <size>    Set the i/o buffer size (default is 8192)
      -c           Check ASN.1 constraints after decoding
      -d           Enable debugging (-dd is even better)
      -n <num>     Process files <num> times
      -s <size>    Set the stack usage limit (default is 30000)

### Decoding an aper pdu packet to xer format:

Here is an example to decode a pdu packet to xer :

    $ ./converter-example -iaper -pInitialUEMessage ../test/aper/pdu-InitialUEMessage.aper
    <InitialUEMessage>
        <protocolIEs>
            <InitialUEMessage-IEs>
                <id>38</id>
                <criticality><reject/></criticality>
                <value>
                    <NAS-PDU>
                        7E 00 41 07 00 0E 09 02 F8 98 00 00 00 00 10 00
                        00 00 00 00
                    </NAS-PDU>
                </value>
            </InitialUEMessage-IEs>
        </protocolIEs>
    </InitialUEMessage>
    $

### Encoding a xer pdu packet to aper:

    $ ./converter-example -c -ixer -pInitialUEMessage ../test/xer/pdu-InitialUEMessage.xer -oaper > packet.aper
    $

You can now check that the generated packet is identical to the aper sample:

    $ md5sum packet.aper ../test/aper/pdu-InitialUEMessage.aper
    bdd412c7ff4d2d67478ab4df1ee2871b  packet.aper
    bdd412c7ff4d2d67478ab4df1ee2871b  ../test/aper/pdu-InitialUEMessage.aper
    $


## Changing revision of the 3gpp spec

### Preparing version number in build infrastructure

In order to change the spec version, you need to update the version numbers in
the following files:

* Makefile : _VERSION=..._ at the top of the file
* debian/changelog : _libngapcodec (..._ on the first line
* example/Makefile: _PKGCONFIGPACKAGE=ngapcodec-..._

### Retrieve asn1c specification

In the _script_ folder script, update_3gpp_spec_ts38413.py can download and extract asn1
specification from official 3gpp specification site.

It needs _python_ and _libreoffice_ installed on your system in order to convert Microsoft word
document to text file.

If for example you want to extract asn specification from the 15.2.0 version of
TS38413, and put it in the asn.1 folder, use this command:

    $ ./scripts/update_3gpp_spec_ts38413.py -v 15.2.0 -o asn.1 38413
    downloading ftp://ftp.3gpp.org/Specs/archive/38_series/38.413/38413-f20.zip
    unarchive zip
    found document : 38413-f20.doc
    converting document to text using soffice --headless --cat /tmp/tmpshG_kL.doc
    extracting asn.1 specs
    Elementary Procedure Definitions.asn1
    PDU Definitions.asn1
    Information Element Definitions.asn1
    Common Definitions.asn1
    Constant Definitions.asn1
    Container Definitions.asn1
    $

It is preferable to empty the asn.1 folder before using this command.

### Set up asn1c compiler

In order to generate C files you need the appropriate asn1c compiler with the
following support:

* aper coding/decoding
* asn1 constants support
* prefix support

This library have been generated with the following fork of asn1c compiler
https://github.com/velichkov/asn1c on branch s1ap.

Just follow the instruction of asn1c to build and install it on your system.

### generate C files from .asn1 files

In the _script_ folder script, generate_src_from_asn.1.sh convert asn1 files to
C source files.

The process is to empty the _src_ folder and then generates the new files:

    $ rm src/*
    $ ./scripts/generate_src_from_asn.1.sh
    WARNING: Parameterized type maxProtocolIEs expected for maxProtocolIEs at line
    123 in asn.1/Container Definitions.asn1
    [...]
    Generated pdu_collection.c
    Generated src/Makefile.am.asn1convert
    Generated Ngap_asn_constant.h
    $

It produces a lot of output and may produce a lot of warning.
Don't worry !

Once this is done, you can build the new library:

    $ make
    cc  -DASN_PDU_COLLECTION -I. -Iinclude/asn1c -o src/Ngap_Criticality.o -c src/Ngap_Criticality.c
    [...]
    $

If there are any errors to compile the library, you need to fix it manually.

### What to do after ?

Now you have your library supporting a new version of your spec.
You can install it as explained above.

Ideally, you can commit your changes to a new release branch.
