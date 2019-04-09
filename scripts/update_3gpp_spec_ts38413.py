#!/usr/bin/env python
""" scripts to retrieve and extract asn.1 description from 3gpp specs """

import argparse
import enum
import os
import re
import sys
import ftplib
import StringIO
import subprocess
import tempfile
import urllib
import zipfile

class Ts3gpp(object):
    """ class to get 3gpp spec information and files """

    base_url = u"http://www.3gpp.org/ftp/Specs/archive/${series}_series/${series}.${mantissa}/${number}-${hexa_version}.zip"

    def __init__(self, number):
        self._number = str(number)

    @staticmethod
    def number_to_series(number):
        """ return series number as string """
        if number.__class__ == int:
            raise NotImplementedError
        elif number.__class__ == str:
            return number[0:2]
        raise NotImplementedError

    @staticmethod
    def number_to_dotted(number):
        """ return number as series and number separated by dot """
        if number.__class__ == int:
            raise NotImplementedError
        elif number.__class__ == str:
            return number[0:2] + "." + number[2:]
        raise NotImplementedError

    def number(self):
        """ return TS number """
        return self._number

    def series(self):
        """ return series of the TS number """
        return Ts3gpp.number_to_series(self._number)

    def dotted(self):
        """ return dotted representation of the TS number """
        return Ts3gpp.number_to_dotted(self._number)

    @staticmethod
    def string_to_file_version(string):
        """ return the version used for ts files for 3gpp

        >>> [ Ts3gpp.string_to_file_version(s) for s in [ "v15.2.3", "16.0.0", "0.0.3"] ]
        ['f23', 'g00', '003']

        """
        string = re.sub('[^0-9.]', '', string)

        def number_to_ord(number):
            number_as_int = int(number)
            if number_as_int > 36:
                raise ValueError
            if number_as_int < 10:
                return number
            return chr(ord('a') + number_as_int - 10)

        return "".join([number_to_ord(s) for s in string.split('.')])

    @staticmethod
    def file_version_to_string(string):
        """ return convert ts files version to major.minor.patch

        >>> [ Ts3gpp.file_version_to_string(s) for s in ['f23', 'g00', '003'] ]
        ['15.2.3', '16.0.0', '0.0.3']

        """

        def ord_to_number(char):
            if ord(char) >= ord('a'):
                return ord(char) - ord('a') + 10
            elif ord(char) >= ord('0') and ord(char) <= ord('9'):
                return ord(char) - ord('0')
            raise ValueError

        return ".".join([str(ord_to_number(s)) for s in string])


    @staticmethod
    def ftp_ls_to_versions(linearray):
        """ return a list of available versions for a given ts with the publication date

        >>> linearray = ['05-03-07  01:31PM                31300 36411-001.zip', \
         '06-19-07  01:56PM                30645 36411-002.zip', \
         '09-24-07  11:09AM                30028 36411-100.zip', \
         '12-11-07  08:02AM                28224 36411-200.zip', \
         '12-12-07  10:42AM                28971 36411-800.zip', \
         '12-16-08  08:28PM               145149 36411-810.zip', \
         '12-17-09  08:15PM               144027 36411-900.zip', \
         '12-21-10  01:15PM               158286 36411-a00.zip', \
         '06-24-11  02:14PM               157453 36411-a10.zip', \
         '09-22-12  04:35PM               157488 36411-b00.zip', \
         '09-19-14  08:46PM               160317 36411-c00.zip', \
         '12-22-15  11:31PM                33725 36411-d00.zip', \
         '03-24-17  11:29PM                34582 36411-e00.zip', \
         '06-22-18  05:24AM                34731 36411-f00.zip']
        >>> versions = Ts3gpp.ftp_ls_to_versions(linearray)
        >>> sorted(versions.iteritems())
        [('0.0.1', ('001', '05-03-07')), ('0.0.2', ('002', '06-19-07')), ('1.0.0', ('100', '09-24-07')), ('10.0.0', ('a00', '12-21-10')), ('10.1.0', ('a10', '06-24-11')), ('11.0.0', ('b00', '09-22-12')), ('12.0.0', ('c00', '09-19-14')), ('13.0.0', ('d00', '12-22-15')), ('14.0.0', ('e00', '03-24-17')), ('15.0.0', ('f00', '06-22-18')), ('2.0.0', ('200', '12-11-07')), ('8.0.0', ('800', '12-12-07')), ('8.1.0', ('810', '12-16-08')), ('9.0.0', ('900', '12-17-09'))]
        """

        versions = {}
        for line in linearray:
            date = line[0:8]
            file_version = line[-7:-4]
            version = Ts3gpp.file_version_to_string(file_version)
            versions[version] = (file_version, date)

        return versions


    def get_available_version_from_3gpp(self):
        """ return a list of available versions for a given ts with the publication date
        """

        ftp = ftplib.FTP("ftp.3gpp.org")
        ftp.login()
        ftp.cwd(u'/Specs/archive/{}_series/{}'.format(self.series(), self.dotted()))
        files = ftp.nlst('-l')
        ftp.close()

        versions = {}
        for line in files:
            date = line[0:8]
            file_version = line[-7:-4]
            version = Ts3gpp.file_version_to_string(file_version)
            versions[version] = (file_version, date)
        return versions

    def get_zip_archive(self, version):
        """ return the zip archive content of the ts """
        url = u'ftp://ftp.3gpp.org/Specs/archive/{}_series/{}/{}-{}.zip'.format(
            self.series(),
            self.dotted(),
            self.number(),
            Ts3gpp.string_to_file_version(version)
        )
        print "downloading " + url
        handle = urllib.urlopen(url)
        data = handle.read()
        handle.close()
        return data

    @staticmethod
    def unzip_and_convert_to_text(zipdata):
        """ unzip archive, and convert word document to text """
        print "unarchive zip"
        zip_file = zipfile.ZipFile(StringIO.StringIO(zipdata))
        docname = None
        for name in zip_file.namelist():
            if name[-4:] == ".doc":
                docname = name
        if docname is None:
            raise RuntimeError("No .doc found")
        print "found document : " + docname
        data = zip_file.read(docname)
        with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as tmp_doc_file:
            command = "soffice --headless --cat {}".format(tmp_doc_file.name)
            print "converting document to text using " + command
            tmp_doc_file.write(data)
            tmp_doc_file.flush()
            text = subprocess.check_output(command.split(" "))
        return text

    @staticmethod
    def text_to_asn1(output_dir, text):
        """ parse text file and outpout asn1 sections to output directory.
            asn.1 section must be delimited by ASN1START, ASN1STOP
        """

        print "extracting asn.1 specs"

        class State(enum.Enum):
            TEXT = 0
            ASN = 1

        if output_dir[-1:-1] != "/":
            output_dir += "/"

        title_search = re.compile("^([0-9.]+)\t(.*)$")
        asn1start_search = re.compile("^-- ASN1START$")
        asn1stop_search = re.compile("^-- ASN1STOP$")

        state = State.TEXT
        title = None
        file_output = None

        for line in text.split("\n"):
            if state == State.TEXT:
                res = title_search.match(line)
                if res is not None:
                    title = res.group(2)
                    continue
                res = asn1start_search.match(line)
                if res is not None:
                    filename = title + ".asn1"
                    file_output = open(output_dir + filename, "w")
                    print filename
                    file_output.write(line + "\n")
                    state = State.ASN
            elif state == State.ASN:
                file_output.write(line + "\n")
                res = asn1stop_search.match(line)
                if res is not None:
                    file_output.close()
                    state = State.TEXT

    def convert_ts_to_asn1(self, version, output_dir):
        zipcontent = self.get_zip_archive(version)
        ts_as_text = Ts3gpp.unzip_and_convert_to_text(zipcontent)
        Ts3gpp.text_to_asn1(output_dir, ts_as_text)

# === cli helpers ===

def dir_path(path):
    """ argparse type checker for directory """
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(u"readable_dir:{path} is not a valid path")

def versions_to_str(versions):
    string = ""
    for version, value in sorted(versions.iteritems()):
        string += "{}\t{}\n".format(version, value[1])
    return string

def get_version(ts):
    versions = ts.get_available_version_from_3gpp()
    print "Available versions :"
    print ""
    print versions_to_str(versions)
    print ""
    version = sorted(versions.keys())[-1]
    print "using last one : " + version
    return version

# === main ===

def main():
    """ program to retrieve TS specification and extract ASN.1 specs """
    parser = argparse.ArgumentParser(description=sys.argv[0])
    parser.add_argument('-o', '--output-directory', type=dir_path,
                        help='output directory for asn.1 files', default=".")
    parser.add_argument('ts', help='TS reference ', type=int)
    parser.add_argument('-v', '--version', help='TS version')

    args = parser.parse_args()

    ts3gpp = Ts3gpp(args.ts)

    version = ""
    if not args.version:
        version = get_version(ts3gpp)
    else:
        # TODO verify versions availabilyty
        version = args.version

    ts3gpp.convert_ts_to_asn1(version, args.output_directory)

if __name__ == '__main__':
    main()
