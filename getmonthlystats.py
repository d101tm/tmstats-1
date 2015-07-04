#!/usr/bin/env python
""" This program gets all available monthly statistics from Toastmasters 
    for the current Toastmasters year.  Use it to catch up when starting
    to track district statistics. """

import urllib, datetime, tmparms, os, sys
from tmutil import cleandate

        
class Dateinfo:
    """ Information relative to a Toastmasters date """
    lasts = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    def __init__(self, m, y):


        if (m == 2) and (0 == y % 4):
            eom = (2, 29, y)
        else:
            eom = (m, self.lasts[m-1], y)
            
        self.monthend = '%d/%d/%d' % eom
        if (m == 12):
            self.nextday = [1, 1, y+1]
        else:
            self.nextday = [m+1, 1, y]
        self.lastday = self.lasts[self.nextday[0]-1]
        if (m == 1) and (0 == y % 4):
            self.lastday = 29
        
    def next(self):
        while (self.nextday[1] <= self.lastday):
            yield '%d/%d/%d' % (self.nextday[0], self.nextday[1], self.nextday[2])
            self.nextday[1] += 1
   
            
    def __iter__(self):
        return self

def makeurl(report, district, tmyearpiece="", monthend="", asof=""):
    baseurl = "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=" + report + "~" + district
    if monthend == "":
        return baseurl + "~~~" + tmyearpiece
    else:
        return baseurl + "~" + monthend + "~" + asof + "~" + tmyearpiece
        

def opener(what, parms):
    if what.startswith('http'):
        return urllib.urlopen(what % parms)
    else:
        return open(what, 'rbU')
        
def getresponse(url):
    clubinfo = urllib.urlopen(url).readlines()
    if len(clubinfo) < 10:
        # We didn't get anything of value
        clubinfo = False
    return clubinfo
        
        


    
def findlastformonth(mm, yy, report, tmyearpiece, district):
    info = Dateinfo(mm, yy)
    url = makeurl(report, district, tmyearpiece, info.monthend, info.monthend)
    good = info.monthend
    clubinfo = getresponse(url)
    for asof in info.next():
        print "getting %s for %s" %(report, asof)
        url = makeurl(report, district, tmyearpiece, info.monthend, asof)
        newinfo = getresponse(url)
        if not newinfo:
            break
        clubinfo = newinfo
        good = asof
    print '%s kept for %s' % (report, good)
    return (clubinfo, good, info.monthend)
    
    
def doareport(report, filename, months, tmyearpiece, district):    
    for (mm, yy) in months:
        (clubinfo, asof) = findlastformonth(mm, yy, report, tmyearpiece, district)
        # At this point, clubinfo has the last valid information for the month we care about
        if clubinfo: 
            open('%s.%s.csv' % (filename, cleandate(asof)),'w').write(''.join(clubinfo).replace('\r','')) 
            
def doreports(months, tmyearpiece, district):
    reports = {'clubperformance':'clubperf', 'districtperformance':'distperf','areaperformance':'areaperf'}
    for (mm, yy) in months:
        lastdate = None
        for r in reports:
            if not lastdate:
                (info, lastdate, monthend) = findlastformonth(mm, yy, r, tmyearpiece, district)
            else:
                info = getresponse(makeurl(r, district, tmyearpiece, monthend, monthend))
            if info:
                outfilename = '%s.%s.csv' % (reports[r], cleandate(lastdate))
                print 'Writing', outfilename
                with open(outfilename,'w') as outfile:
                    outfile.write(''.join(info).replace('\r',''))
                
        
            
if __name__ == "__main__":
    
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        if not sys.argv[1:]:
            sys.argv[1:] = '--district 4'.split()
    
    reload(sys).setdefaultencoding('utf8')
            
    parms = tmparms.tmparms()
    parms.add_argument('--district', type=int)
    parms.add_argument('--enddate', default='today')
    parms.parse()

    district = "%0.2d" % parms.district
    today = datetime.datetime.strptime(cleandate(parms.enddate), '%Y-%m-%d')


    # Start by figuring out what months we need info for:


    tmmonths = (7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6)
    # If it's January-July, we care about the TM year which started the previous July 1; otherwise, it's this year.
    if (today.month <= 7):
        tmyear = today.year - 1 
    else:
        tmyear = today.year

    tmyearpiece = '%d-%d' % (tmyear, tmyear+1)  # For the URLs

    # Now, compute the months we're going to look for

    if (today.month == 7):
        months = tmmonths
    else:
        months = []
        for m in tmmonths:
            months.append(m)
            if m == today.month:
                break
    months = [(m, tmyear + (1 if m <= 6 else 0)) for m in months]



    # Now we get the performance reports for the months we need
    doreports(months, tmyearpiece, district)




