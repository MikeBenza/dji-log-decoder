This directory is intentionally empty.

To generate the files that go here, execute the following commands from the parent directory:

1. virtualenv venv
2. source venv/bin/activate
3. pip install git+git://github.com/MikeBenza/dji-log-data.git#egg=dji_log_data
4. generate_code -l python -f dji_log_data/frames.py -k dji_log_data/keys.py

That will generate the most up-to-date data files for DJI Flight Records.