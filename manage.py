#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault(str("DJANGO_SETTINGS_MODULE"), str("parlalize.settings"))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
