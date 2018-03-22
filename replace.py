#!/usr/bin/env python3

import re
import subprocess
import argparse

POSSIBLE_DEPTYPES = ["hostmakedepends", "makedepends", "depends",
                     "checkdepends"]


def get_pkglist(pkgs: str) -> str:
    """ Takes a whitespace-separated string of pkgs and iterates over them.

        as if they were a list then return them as a string
        for an explaination of each symbol see xgetdeps in the
        same repo.
        actions done for the symbols given:
        1. separate by whitespace
        2. if string vopt not found then add to pkglist list
        3. if string vopt found then check if | is not present
        4. if string | is not present then we replace ' with nothing
        5. replace all / and | with ' '
        6. replace vopt with $(vopt_if then append ) to the end of the string
        7. add to pkgvoptlist
        8. iterate over pkgvoptlist and append to pkglist
        9. join pkglist over ' ' and return it
    """

    from typing import List

    pkglist: List[str] = []
    pkgvoptlist: List[str] = []

    for pkg in pkgs.split(' '):
        if 'vopt' not in pkg:
            pkglist.append(pkg)
        else:
            if '|' not in pkg:
                pkg = pkg.replace("'", "")

            pkgvoptlist.append(pkg
                               .replace('/', ' ')
                               .replace('|', ' ')
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

        pkgs = get_pkglist(pkgs)

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
