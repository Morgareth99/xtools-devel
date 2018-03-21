#!/usr/bin/env python3

import re
import subprocess
import argparse

POSSIBLE_DEPTYPES = ["hostmakedepends", "makedepends", "depends",
                     "checkdepends"]


def get_pkglist(pkgs: str) -> str:
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
    p = argparse.ArgumentParser(description="trim dependencies of templates.")
    p.add_argument('pkgname', metavar='template', type=str,
                   help='name of the package to be trimmed')
    p.add_argument('deptypes', metavar='deptypes', type=str,
                   help='single white-space separated string of deptypes')
    p.add_argument('pkgs', metavar='pkgs', type=str,
                   help='single white-space separated string of packages')
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

    pkgs = args.pkgs.replace('\n', ' ')  # this might be unecessary

    with open(filepath, 'r') as file_in:
        mod = file_in.read()

    deptypes = args.deptypes.split(" ")

    for deptype in deptypes:
        if deptype not in POSSIBLE_DEPTYPES:
            continue

        pkgs = (get_pkglist(pkgs))

        regex = deptype + '=\"(.*\\n){0,}?.*\"'
        mod = re.sub(r'^%s' % regex, deptype + '="' + pkgs + '"',
                     str(mod), flags=re.MULTILINE)

        print(deptype + '="' + pkgs + '"')

    file_in.close()

    if args.replace:
        with open(filepath, 'w') as file_out:
            file_out.write(mod)
            file_out.close()


if __name__ == "__main__":
    main()
