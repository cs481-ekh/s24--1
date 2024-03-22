import sys
import os
import pytest
import main
import inspect

#   CLI tests
class Test_CLI_No_Opts:
    def test_print_usage_no_error(self):
        main.print_usage()

    def test_print_details_no_error(self):
        main.print_details()

    def test_select_calc_no_opt(self):
        main.select_calc_option("")

    def test_select_out_no_opt(self):
        main.select_out_option("")

    def test_cli_init_no_opt(self):
        with pytest.raises(TypeError):
            main.cli_init()

class Test_CLI_Flag_Errors:
    def test_calc_flag_no_option(self):
        main.cli_init("")

