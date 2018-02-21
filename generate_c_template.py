#!/usr/bin/env python
"""Create an 'exercism'-ish test template for C."""

import sys
import json
import os
import errno
import re
import urllib2
from distutils.dir_util import copy_tree

# check input
if len(sys.argv) == 1:
    sys.exit('Usage: %s exercise' % sys.argv[0])

exercise = sys.argv[1]
exercise_ = exercise.replace('-', '_')

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

# create makefile
f = open(exercise + '/makefile', 'w')
print >> f, 'CFLAGS  = -std=c99'
print >> f, 'CFLAGS += -g'
print >> f, 'CFLAGS += -Wall'
print >> f, 'CFLAGS += -Wextra'
print >> f, 'CFLAGS += -pedantic'
print >> f, 'CFLAGS += -Werror'
print >> f
print >> f, 'VFLAGS  = --quiet'
print >> f, 'VFLAGS += --tool=memcheck'
print >> f, 'VFLAGS += --leak-check=full'
print >> f, 'VFLAGS += --error-exitcode=1'
print >> f
print >> f, 'test: tests.out'
print >> f, '\t@./tests.out'
print >> f
print >> f, 'memcheck: tests.out'
print >> f, '\t@valgrind $(VFLAGS) ./tests.out'
print >> f, '\t@echo "Memory check passed"'
print >> f
print >> f, 'clean:'
print >> f, '\trm -rf *.o *.out *.out.dSYM'
print >> f
print >> f, ('tests.out: test/'
             + 'test_' + exercise_ + '.c'
             ' src/' + exercise_ + '.c src/' + exercise_ + '.h')
print >> f, '\t@echo Compiling $@'
print >> f, ('\t@cc $(CFLAGS) src/' + exercise_ + '.c test/vendor/unity.c'
             ' test/test_' + exercise_ + '.c -o tests.out')

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

exnum = 0
if 'cases' in data['cases'][0]:
    top = data['cases'][0]['cases']
else:
    top = data['cases']
for item in top:
    exnum += 1
    desc = re.sub('[^0-9a-zA-Z]+', '_', item['description'])
    print >> f, 'void test_' + desc.lower() + '(void)'
    print >> f, '{'
    if exnum == 2:
        print >> f, ('        TEST_IGNORE();               '
                     '// delete this line to run test')
    elif exnum > 2:
        print >> f, '        TEST_IGNORE();'
    print >> f, '        /*'
    print >> f, '----Input----'
    print >> f, json.dumps(item['input'], indent=3)
    print >> f, '---Expected---'
    print >> f, json.dumps(item['expected'], indent=3)
    print >> f, '        */'
    print >> f
    print >> f
    print >> f, '}'
    print >> f

print >> f, 'int main(void)'
print >> f, '{'
print >> f, '        UnityBegin("test/test_' + exercise_ + '.c");'
print >> f

for item in top:
    desc = re.sub('[^0-9a-zA-Z]+', '_', item['description'])
    print >> f, '        RUN_TEST(test_' + desc.lower() + ');'

print >> f
print >> f, '        UnityEnd();'
print >> f, '        return 0;'
print >> f, '}'
