import sys
import os
import pytest
import main

#   CLI tests
class Test_CLI:
    def test_print_usage_no_error():
        main.print_usage()