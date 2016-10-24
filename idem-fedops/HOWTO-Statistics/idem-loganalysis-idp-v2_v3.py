#!/usr/bin/python

# Copyright 2010 University Corporation for Advanced Internet Development, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Parse Shibboleth 2.x or 3.x Identity Provider audit logfile and generate simple stats.
   Audit log file format: https://wiki.shibboleth.net/confluence/display/SHIB2/IdPLogging"""

import sys
import fileinput
import os
from optparse import OptionParser
from operator import itemgetter

def parseFiles(files,options):
    """Build datastructures from lines."""
    lines = []
    if sys.version_info < (2, 5):
        for line in fileinput.input(files):
            lines.append(line.rstrip().split("|"))
    else:
        for line in fileinput.input(files, openhook=fileinput.hook_compressed):
            lines.append(line.rstrip().split("|"))

    db = {}
    db['rp'], db['users'], db['msgprof'], db['logins'] = {},{},{},0

    for event in lines:
        login = False
        try:
            datetime,reqBind,reqId,rp,msgProfile,idp,respBind,respId,user,authnMeth,relAttribs,nameId,assertIds,EOL = event
        except ValueError:
            print """ERROR: Unsupported log file format or using compressed log files with Python < 2.5.%sSee the documentation in the Shibboleth wiki.""" % os.linesep
            sys.exit(-1)

        if ('/sso/' in  msgProfile.lower() or msgProfile.lower().endswith(":sso")) and user != '':
            db['logins'] += 1
            login = True

        # we almost always need to cound rps:
        if db['rp'].has_key(rp):
            db['rp'][rp] += 1
        else:
            db['rp'][rp] = 1

        # only count users if asked to
        if (options.uniqusers or options.allusers) and login:
            if db['users'].has_key(user):
               db['users'][user] += 1
            else:
               db['users'][user] = 1

        # only count message profiles and rps if asked to
        if options.msgprofiles:
            if db['msgprof'].has_key(msgProfile):
                if db['msgprof'][msgProfile].has_key(rp):
                   db['msgprof'][msgProfile][rp] += 1
                else:
                   db['msgprof'][msgProfile][rp] = 1
            else:
                db['msgprof'][msgProfile] = {}
                db['msgprof'][msgProfile][rp] = 1
    return db

def uniqueRps(db):
    """Output unique relying parties."""
    for rp in sorted(db['rp'].keys()):
        print rp

def uniqueRpCount(db,options):
    """Output number of unique relying parties."""
    rps = len(db['rp'].keys())
    if options.quiet:
        print rps
    else:
        print "%d unique relying part%s" % (rps, ('y', 'ies')[rps!=1])

def allUsers(db):
    """Output useridss and number of logins."""
    for curuser,logins in sorted(db['users'].items(), reverse=True, key=lambda (k,v): (v,k)):
        if curuser == '':
            print "[WARN] curuser == '' --- %d\t | %s" % (logins, curuser)
        if not curuser == '':
            print "%d\t | %s" % (logins, curuser)

def loginCount(db,options):
    """Output total number of logins."""
    logins = db['logins']
    if not options.quiet:
        print "%d login%s" % (logins, ('', 's')[logins!=1])
    else:
        print logins

def uniqueUsers(db,options):
    """Output number of unique userids."""
    users = len(db['users'].keys())
    if not options.quiet:
        print "%d unique userid%s" % (users, ('', 's')[users!=1])
    else:
        print users

def loginsPerRp(db,options):
    """Output list of logins per relying party."""
    for rp,i in db['rp'].items():
        if options.quiet:
            print "%d %s" % (i, rp)
        else:
            print "%d\t | %s" % (i, rp)

def loginsPerRpSorted(db,options):
    """Output sorted list of logins per relying party."""
    for rp,i in sorted(db['rp'].iteritems(), key=itemgetter(1), reverse=True):
        if options.quiet:
            print "%d %s" % (i, rp)
        else:
            print "%d\t | %s" % (i, rp)

def rpPerMessageProfile(db,options):
    """Output usage of SAML message profiles per relying party."""
    for mp,rps in db['msgprof'].items():
        print mp
        for rp,i in sorted(rps.iteritems(), key=itemgetter(1), reverse=True):
            if options.quiet:
                print "%d %s" % (i, rp)
            else:
                print "%d\t | %s" % (i, rp)
        if not options.quiet:
            print

def main():
    """Parse command line options and arguments and their contents."""
    parser = OptionParser()
    usage = "usage: %prog [options] [files ...]"
    parser = OptionParser(usage)
    parser.add_option("-r", "--relyingparties", help="list of unique relying parties, sorted by name",
                      action="store_true", dest="uniqrp")
    parser.add_option("-c", "--rpcount", help="number of unique relying parties",
                      action="store_true")
    parser.add_option("-u", "--users", help="number of unique userids",
                      action="store_true", dest="uniqusers")
    parser.add_option("-a", "--allusers", help="number of logins per userid",
                      action="store_true", dest="allusers")
    parser.add_option("-l", "--logins", help="number of logins",
                      action="store_true")
    parser.add_option("-p", "--rplogins", help="number of events per relying party, by name",
                      action="store_true")
    parser.add_option("-n", "--rploginssort", help="number of events per relying party, sorted numerically",
                      action="store_true")
    parser.add_option("-m", "--msgprofiles", help="usage of SAML message profiles per relying party ",
                      action="store_true")
    parser.add_option("-q", "--quiet", help="suppress all descriptive or decorative output",
                      action="store_true" )

    # Parse options and do basic sanity checking
    (options, args) = parser.parse_args()
    if len(args) == 0:
        print "Missing filename(s). Specify '-' as filename to read from STDIN.\n"
        parser.print_help()
        sys.exit(-1)
    if options.rplogins and options.rploginssort:
        parser.error("Options -p and -n are mutually exclusive (just use one or the other).")

    # Make sure that at least one option is set, otherwise don't bother parsing any logfiles
    for value in options.__dict__.values():
        if value:
            db = parseFiles(args,options)
            break
    else:
        print "Missing option: At least one option needs to be supplied.\n"
        parser.print_help()
        sys.exit(-1)

    # map command line options to procedures
    if options.uniqrp: uniqueRps(db)
    if options.rpcount: uniqueRpCount(db,options)
    if options.uniqusers: uniqueUsers(db,options)
    if options.allusers: allUsers(db)
    if options.logins: loginCount(db,options)
    if options.rplogins or options.rploginssort:
        if not options.quiet:
            header = "logins\t | relyingPartyId"
            print "\n" + header + "\n" + '-'*(len(header)+1)
    if options.rplogins: loginsPerRp(db,options)
    if options.rploginssort: loginsPerRpSorted(db,options)
    if options.msgprofiles: rpPerMessageProfile(db,options)

if __name__ == "__main__":
    main()
