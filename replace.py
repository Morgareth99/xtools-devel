#!/usr/bin/env python3

import re
import sys
import subprocess

POSSIBLE_DEPTYPES = ["hostmakedepends", "makedepends", "depends",
                     "checkdepends"]


def get_pkglist(pkgs):
    pkglist = []
    pkgvoptlist = []

    for pkg in pkgs.split(' '):
        if 'vopt' not in pkg:
            pkglist.append(pkg)
        else:
            pkgvoptlist.append(pkg
                               .replace('_', ' ')
                               .replace('vopt', '$(vopt_if') + ')')

    for vpkg in pkgvoptlist:
        pkglist.append(vpkg)

    return ' '.join(pkglist)


def main():
    if len(sys.argv) < 2:
        print('no template provided')
        sys.exit(1)
    elif len(sys.argv) < 3:
        print('no deptype ... provided')
        sys.exit(1)
    elif len(sys.argv) < 4:
        print('no replace string provided')
        sys.exit(1)

    filepath = 'srcpkgs/' + sys.argv[1] + '/template'
    xdistdir = subprocess.run('xdistdir', stdout=subprocess.PIPE)
    filepath = xdistdir.stdout.decode('utf-8').replace('\n', '/') + filepath

    pkgs = sys.argv[3].replace('\n', ' ')

    with open(filepath, 'r') as file_in:
        mod = file_in.read()

    deptypes = sys.argv[2].split(" ")

    for deptype in deptypes:
        if deptype not in POSSIBLE_DEPTYPES:
            continue

        pkgs = (get_pkglist(pkgs))

        regex = deptype + '=\"(.*\\n){0,}?.*\"'
        mod = re.sub(r'^%s' % regex, deptype + '="' + pkgs + '"',
                     str(mod), flags=re.MULTILINE)

        print(deptype + '="' + pkgs + '"')

    file_in.close()

    with open(filepath, 'w') as file_out:
        file_out.write(mod)
        file_out.close()


if __name__ == "__main__":
    main()
