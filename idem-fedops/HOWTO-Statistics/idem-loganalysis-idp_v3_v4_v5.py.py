#!/usr/bin/env python

"""Parse Shibboleth Identity Provider audit logfile and generate simple stats."""
from __future__ import absolute_import, print_function
from fileinput import input as finput, hook_compressed as compr
from sys import exit as term
from os import linesep
from json import dumps
from optparse import OptionParser
from operator import itemgetter
from subprocess import check_output


def parse_files(files, options):
    """Build datastructures from lines"""
    lines = []
    for line in finput(files, openhook=compr):
        lines.append(line.rstrip().split("|"))

    db = {}
    db['rp'], db['users'], db['msgprof'], db['logins'] = {}, {}, {}, 0

    login_string = "sso"
    fields_position = [3, 4, 8]

    if options.shibidpv4 or options.shibidpv5:
        login_string = "success"
        fields_position = [4, 17, 3]

    # Audit log format we're trying to parse below:
    # datetime|req_bind|req_id|rp|msg_profile|idp|resp_bind|resp_id|user|authn_mech|attribs|name_id|assert_id|ip

    for event in lines:
        try:
            rp, msg_profile, user = list(event[i] for i in fields_position)
        except ValueError:
            print(linesep.join([
                "ERROR: Unsupported log file format or compressed logs with Python < 2.5",
                "See the documentation."]))
            term(-1)

        if rp:
            if msg_profile.lower().find(login_string) > -1:
                db['logins'] += 1

                # we almost always need to count rps:
                if len(rp) > 0:
                    if rp in db['rp']:
                        db['rp'][rp] += 1
                    else:
                        db['rp'][rp] = 1

                # only count users if asked to
                if len(user) > 0:
                    if options.uniqusers or options.xml or options.rrd or options.json:
                        if user in db['users']:
                            db['users'][user] += 1
                        else:
                            db['users'][user] = 1

        # only count message profiles and rps if asked to
        if options.msgprofiles:
            if msg_profile in db['msgprof']:
                if rp in db['msgprof'][msg_profile]:
                    db['msgprof'][msg_profile][rp] += 1
                else:
                    db['msgprof'][msg_profile][rp] = 1
            else:
                db['msgprof'][msg_profile] = {}
                db['msgprof'][msg_profile][rp] = 1
    return db


def basic_stats(db):
    """Collect basic statistics to be fed to output functions"""
    idp_version = check_output(['bash','/opt/shibboleth-idp/bin/version.sh']).strip().decode()
    rps = len(list(db['rp'].keys()))
    users = len(list(db['users'].keys()))
    logins = db['logins']
    return {"idp": idp_version, "rps": rps, "users": users, "logins": logins}


def xml_out(db):
    """XML output of basic stats"""
    stats = basic_stats(db)
    print('<?xml version="1.0"?>')
    print('<idp-audit rps="%d" logins="%d" users="%d">'
          % (stats['rps'], stats['logins'], stats['users']))
    for rp, i in list(db['rp'].items()):
        print('  <rp count="%d">%s</rp>' % (i, rp))
    print("</idp-audit>")


def rrd_out(db):
    """RRD output of basic stats"""
    stats = basic_stats(db)
    print("rp:%d l:%d u:%d" % (stats['rps'], stats['logins'], stats['users']))


def json_out(db, options):
    """JSON output of basic stats"""
    stats = {"stats": basic_stats(db)}
    stats['logins_per_rp'] = db['rp']
    if options.quiet:
        print(dumps(stats, separators=(',', ':')))
    else:
        print(dumps(stats, indent=2, separators=(',', ': ')))


def unique_rp(db):
    """Output unique relying parties"""
    for rp in sorted(db['rp'].keys()):
        print(rp)


def unique_rp_count(db, options):
    """Output number of unique relying parties"""
    rps = len(list(db['rp'].keys()))
    if options.quiet:
        print(rps)
    else:
        print("%d unique relying part%s" % (rps, ('y', 'ies')[rps != 1]))


def login_count(db, options):
    """Output total number of logins"""
    logins = db['logins']
    if options.quiet:
        print(logins)
        print("%d login%s" % (logins, ('', 's')[logins != 1]))


def unique_users(db, options):
    """Output number of unique userids"""
    users = len(list(db['users'].keys()))
    if options.quiet:
        print(users)
    else:
        print("%d unique userid%s" % (users, ('', 's')[users != 1]))


def logins_per_rp_sorted(db, options):
    """Output sorted list of logins per relying party"""
    for rp, i in sorted(iter(list(db['rp'].items())), key=itemgetter(1), reverse=True):
        if options.quiet:
            print("%d %s" % (i, rp))
        else:
            print("%d\t | %s" % (i, rp))


def rp_per_msg_profile(db, options):
    """Output usage of SAML message profiles per relying party"""
    for mp, rps in list(db['msgprof'].items()):
        print(mp)
        for rp, i in sorted(iter(list(rps.items())), key=itemgetter(1), reverse=True):
            if options.quiet:
                print("%d %s" % (i, rp))
            else:
                print("%d\t | %s" % (i, rp))
        if not options.quiet:
            print()


def getopts():
    """Parse command line options and arguments"""
    parser = OptionParser("Usage: %prog [options] [files ...]")
    parser.add_option("-5", "--shibidpv5", action="store_true", help="Parse Shibboleth IdP V5 Audit logs")
    parser.add_option("-4", "--shibidpv4", action="store_true", help="Parse Shibboleth IdP V4 Audit logs")
    parser.add_option("-r", "--relyingparties", action="store_true", dest="uniqrp",
                      help="List of unique relying parties, sorted by name")
    parser.add_option("-c", "--rpcount", action="store_true",
                      help="Number of unique relying parties")
    parser.add_option("-u", "--users", action="store_true", dest="uniqusers",
                      help="Number of unique userids")
    parser.add_option("-l", "--logins", action="store_true", help="Number of logins")
    parser.add_option("-n", "--rploginssort", action="store_true",
                      help="Number of events per relying party, sorted numerically")
    parser.add_option("-m", "--msgprofiles", action="store_true",
                      help="Used SAML message profiles per relying party, sorted")
    parser.add_option("-q", "--quiet", action="store_true",
                      help="Suppress decorative output (or compact JSON)")
    parser.add_option("-x", "--xml", action="store_true", help="Output stats in XML")
    parser.add_option("-t", "--rrd", action="store_true", help="Output basic stats for RRD use")
    parser.add_option("-j", "--json", action="store_true", help="Output stats in JSON")

    # Parse options and do basic sanity checking
    (options, args) = parser.parse_args()
    if len(args) == 0:
        print("Missing filename(s). Specify '-' as filename to read from STDIN.%s" % linesep)
        parser.print_help()
        term(-1)

    # Make sure that at least one option is set, otherwise don't bother parsing any files
    for value in list(options.__dict__.values()):
        if value:
            db = parse_files(args, options)
            return (db, options)
    print("Missing option: At least one option needs to be supplied.%s" % linesep)
    parser.print_help()
    term(-1)


def main():
    """Run necessary procedures"""
    db, options = getopts()
    if options.uniqrp:
        unique_rp(db)
    if options.rpcount:
        unique_rp_count(db, options)
    if options.uniqusers:
        unique_users(db, options)
    if options.logins:
        login_count(db, options)
    if options.rploginssort:
        if not options.quiet:
            header = "logins\t | relyingPartyId"
            print(linesep + header + linesep + '-' * (len(header) + 1))
    if options.rploginssort:
        logins_per_rp_sorted(db, options)
    if options.msgprofiles:
        rp_per_msg_profile(db, options)
    if options.xml:
        xml_out(db)
    if options.rrd:
        rrd_out(db)
    if options.json:
        json_out(db, options)


if __name__ == "__main__":
    main()
