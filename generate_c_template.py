#!/usr/bin/env python
"""Create an 'exercism'-ish test template for C."""

import sys
import json
import os
import errno
import urllib2
from distutils.dir_util import copy_tree

# check input
if len(sys.argv) == 1:
    sys.exit('Usage: %s exercise' % sys.argv[0])

exercise = sys.argv[1]

# fetch readme
try:
    readme = urllib2.urlopen('https://raw.githubusercontent.com/exercism/'
                             'problem-specifications/master/exercises/'
                             + exercise +
                             '/description.md')
except urllib2.URLError, e:
    print e
    sys.exit('readme URL error')

# create main dir
try:
    os.makedirs(exercise)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# save readme
f = open(exercise + '/README.md', 'w')
print >> f, readme.read()

# create 'test' subdir
try:
    os.makedirs(exercise + "/test")
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# copy 'vemdor'
copy_tree('vendor', exercise + '/test/vendor')

# fetch json
try:
    canonical = urllib2.urlopen('https://raw.githubusercontent.com/exercism/'
                                'problem-specifications/master/exercises/'
                                + exercise +
                                '/canonical-data.json')
except urllib2.URLError, e:
    print e
    sys.exit('json URL error')

data = json.load(canonical)

exercise_ = exercise.replace('-', '_')

# create 'src' subdir
try:
    os.makedirs(exercise + "/src")
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# header file
f = open(exercise + '/src/' + exercise_ + '.h', 'w')
print >> f, '#ifndef ' + exercise_.upper() + '_H'
print >> f, '#define ' + exercise_.upper() + '_H'
print >> f
print >> f
print >> f
print >> f, '#endif'

# c exercise file
f = open(exercise + '/src/' + exercise_ + '.c', 'w')
print >> f, '#include "' + exercise_ + '.h"'
print >> f

# build the test file
f = open(exercise + '/test/test_' + exercise_ + '.c', 'w')

print >> f, '#include "vendor/unity.h"'
print >> f, '#include "../src/' + exercise_ + '.h"'
print >> f
print >> f, 'void setUp(void)'
print >> f, '{'
print >> f, '}'
print >> f
print >> f, 'void tearDown(void)'
print >> f, '{'
print >> f, '}'
print >> f
print >> f, '//Tests start here'

exnum = 0
for item in data['cases']:
    exnum += 1
    desc = item['description'].replace(' ', '_')  # switch
    print >> f, 'void test_' + desc + '(void)'
    print >> f, '{'
    if exnum == 2:
        print >> f, ('   TEST_IGNORE();               '
                     '// delete this line to run test')
    elif exnum > 2:
        print >> f, '   TEST_IGNORE();'
    print >> f, '/*'
    print >> f, '----Input----'
    print >> f, json.dumps(item['input'], indent=3)
    print >> f, '---Expected---'
    print >> f, json.dumps(item['expected'], indent=3)
    print >> f, '*/'
    print >> f
    print >> f
    print >> f, '}'
    print >> f

print >> f, 'int main(void)'
print >> f, '{'
print >> f, '   UnityBegin("test/test_' + exercise_ + '.c");'
print >> f

for item in data['cases']:
    print >> f, '   RUN_TEST(test_' + desc + ');'
    desc = item['description'].replace(' ', '_')  # switch

print >> f
print >> f, '   UnityEnd();'
print >> f, '   return 0;'
print >> f, '}'
