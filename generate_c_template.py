#!/usr/bin/env python
"""Create an 'exercism'-ish test template for C."""

import sys
import json
import os
import errno
import re
import urllib2
from distutils.dir_util import copy_tree

exnum = 0
callers = ""
def print_functions(top):
    """ helper for the function names """
    global exnum
    global callers
    for item in top:
        if 'cases' in item:
            print_functions(item['cases'])
            continue
        exnum += 1
        desc = re.sub('[^0-9a-zA-Z]+', '_', item['description'])
        print >> F, ('void test_' + item['property'] + '_' +
                     desc.lower() + '(void)')
        print >> F, '{'
        if exnum == 2:
            print >> F, ('        TEST_IGNORE();               '
                         '// delete this line to run test')
        elif exnum > 2:
            print >> F, '        TEST_IGNORE();'
        print >> F, '        /*'
        print >> F, '----Input----'
        print >> F, json.dumps(item['input'], indent=3)
        print >> F, '---Expected---'
        print >> F, json.dumps(item['expected'], indent=3)
        print >> F, '        */'
        print >> F, '}'
        print >> F
        callers += ('        RUN_TEST(test_' + item['property'] + '_' +
                desc.lower() + ');')
        callers += '\n'
    return

# check input
if len(sys.argv) == 1:
    sys.exit('Usage: %s exercise' % sys.argv[0])

EXERCISE = sys.argv[1]
EXERCISE_ = EXERCISE.replace('-', '_')

# fetch README
try:
    README = urllib2.urlopen('https://raw.githubusercontent.com/exercism/'
                             'problem-specifications/master/exercises/'
                             + EXERCISE +
                             '/description.md')
except urllib2.URLError, url_error:
    print url_error
    sys.exit('README URL error')

# create main dir
try:
    os.makedirs(EXERCISE)
except OSError as dir_error:
    if dir_error.errno != errno.EEXIST:
        raise

# save README
F = open(EXERCISE + '/README.md', 'w')
print >> F, README.read()

# create makefile
F = open(EXERCISE + '/makefile', 'w')
print >> F, 'CFLAGS  = -std=c99'
print >> F, 'CFLAGS += -g'
print >> F, 'CFLAGS += -Wall'
print >> F, 'CFLAGS += -Wextra'
print >> F, 'CFLAGS += -pedantic'
print >> F, 'CFLAGS += -Werror'
print >> F
print >> F, 'VFLAGS  = --quiet'
print >> F, 'VFLAGS += --tool=memcheck'
print >> F, 'VFLAGS += --leak-check=full'
print >> F, 'VFLAGS += --error-exitcode=1'
print >> F
print >> F, 'test: tests.out'
print >> F, '\t@./tests.out'
print >> F
print >> F, 'memcheck: tests.out'
print >> F, '\t@valgrind $(VFLAGS) ./tests.out'
print >> F, '\t@echo "Memory check passed"'
print >> F
print >> F, 'clean:'
print >> F, '\trm -rf *.o *.out *.out.dSYM'
print >> F
print >> F, ('tests.out: test/'
             + 'test_' + EXERCISE_ + '.c'
             ' src/' + EXERCISE_ + '.c src/' + EXERCISE_ + '.h')
print >> F, '\t@echo Compiling $@'
print >> F, ('\t@cc $(CFLAGS) src/' + EXERCISE_ + '.c test/vendor/unity.c'
             ' test/test_' + EXERCISE_ + '.c -o tests.out')

# create 'test' subdir
try:
    os.makedirs(EXERCISE + "/test")
except OSError as dir_error:
    if dir_error.errno != errno.EEXIST:
        raise

# copy 'vemdor'
copy_tree('vendor', EXERCISE + '/test/vendor')

# fetch json
try:
    CANONICAL = urllib2.urlopen('https://raw.githubusercontent.com/exercism/'
                                'problem-specifications/master/exercises/'
                                + EXERCISE +
                                '/canonical-data.json')
except urllib2.URLError, url_error:
    print url_error
    sys.exit('json URL error')

DATA = json.load(CANONICAL)

# create 'src' subdir
try:
    os.makedirs(EXERCISE + "/src")
except OSError as dir_error:
    if dir_error.errno != errno.EEXIST:
        raise

# header file
F = open(EXERCISE + '/src/' + EXERCISE_ + '.h', 'w')
print >> F, '#ifndef ' + EXERCISE_.upper() + '_H'
print >> F, '#define ' + EXERCISE_.upper() + '_H'
print >> F
print >> F
print >> F
print >> F, '#endif'

# c EXERCISE file
F = open(EXERCISE + '/src/' + EXERCISE_ + '.c', 'w')
print >> F, '#include "' + EXERCISE_ + '.h"'
print >> F

# build the test file
F = open(EXERCISE + '/test/test_' + EXERCISE_ + '.c', 'w')

print >> F, '#include "vendor/unity.h"'
print >> F, '#include "../src/' + EXERCISE_ + '.h"'
print >> F
print >> F, 'void setUp(void)'
print >> F, '{'
print >> F, '}'
print >> F
print >> F, 'void tearDown(void)'
print >> F, '{'
print >> F, '}'
print >> F

print_functions(DATA['cases'])

print >> F, 'int main(void)'
print >> F, '{'
print >> F, '        UnityBegin("test/test_' + EXERCISE_ + '.c");'
print >> F

print >> F, callers

print >> F, '        UnityEnd();'
print >> F, '        return 0;'
print >> F, '}'
