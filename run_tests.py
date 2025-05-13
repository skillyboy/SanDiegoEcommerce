#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'project.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # Get test modules from command line arguments or run all tests
    if len(sys.argv) > 1:
        test_modules = sys.argv[1:]
    else:
        test_modules = ['afriapp.tests', 'logistics.tests']

    failures = test_runner.run_tests(test_modules)
    sys.exit(bool(failures))
