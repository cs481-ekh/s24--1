#!/bin/bash

# Install dependencies
pip install -r ./workflow/requirements.txt

# Important: test files must be formatted `test_*.py`

# Run tests using pytest
pytest
