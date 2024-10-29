#!/bin/bash
source venv/bin/activate

python -u -m pytest -s App/tests/api_key_service_test.py
python -u -m pytest -s App/tests/openai_service_test.py
python -u -m pytest -s App/tests/openai_routes_test.py

deactivate
