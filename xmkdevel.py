#!/usr/bin/env python3

import argparse
import subprocess
import os.path
import sys
from typing import List


def checkfile(pkgstring: str, filelist: str) -> str:
    solib: bool = False
    alib: bool = False

    paths: List[str] = ['/usr/include',
                        '/usr/lib/pkgconfig',
                        '/usr/share/pkgconfig',
                        '/usr/lib/cmake',
                        '/usr/share/cmake',
                        '/usr/share/aclocal',
                        '/usr/share/man/man3',
                        '/usr/share/info',
                        '/usr/share/gtk-doc',
                        '/usr/share/git-1.0',
                        '/usr/lib/gitrepository-1.0']

    for path in paths:
        if path in filelist:
            pkgstring += "\t\tvmove " + path + "\n"

    for line in filelist.split('\n'):
        if line.split(' ->', 1)[0].endswith('.so') and not solib:
            pkgstring += "\t\tvmove \"/usr/lib/*.so\"\n"
            solib = True

        if line.split(' ->', 1)[0].endswith('.a') and not alib:
            pkgstring += "\t\tvmove \"/usr/lib/*.a\"\n"
            alib = True

    return pkgstring


def main():
    p = argparse.ArgumentParser(description="create -devel packages.")
    p.add_argument('pkgname', metavar='pkgname', type=str,
                   help='name of the package to create the devel package')
    p.add_argument('develname', metavar='develname', type=str,
                   help='name of the devel package without -devel suffix')
    p.add_argument('filelist', metavar='filelist', type=str,
                   help='newline separated list of files in main package')
    p.add_argument('-i', dest='replace', action='store_true', default=False,
                   help='replace dependencies in template')

    args = p.parse_args()

    """
        Create a path by taking xdistdir and add srcpkgs/ the pkgname and
        /template
    """
    filepath = 'srcpkgs/' + args.pkgname + '/template'
    xdistdir = subprocess.run('xdistdir', stdout=subprocess.PIPE)
    filepath = xdistdir.stdout.decode('utf-8').replace('\n', '/') + filepath

    devname = args.develname + '-devel'

    if not os.path.isfile(filepath):
        print("Invalid filepath: %s" % filepath)
        sys.exit(2)

    pkgstring = """
$1-devel_package() {
\tshort_desc+=" - development files"
\tdepends="$2-${version}_${revision}
\tpkg_install() {\n""".replace("$1",
                                 args.develname).replace("$2",
                                                         args.pkgname)

    with open(filepath, 'r') as file_in:
        f = file_in.read()

        if args.replace:
            if f.find(devname) != -1:
                print('package already made for the name: %s' % devname)
                sys.exit(2)

    file_in.close()

    pkgstring = checkfile(pkgstring, args.filelist)

    pkgstring += "\t}\n"
    pkgstring += "}\n"

    print(pkgstring)

    if args.replace:
        with open(filepath, "a") as file_out:
            file_out.write(pkgstring)
            file_out.close()


if __name__ == "__main__":
    main()
