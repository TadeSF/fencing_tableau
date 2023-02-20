import os

if not os.path.exists('Versionhistory.txt'):
    with open('Versionhistory.txt', 'w') as f:
        f.write('')

# Get version from VERSION.txt
try:
    with open('VERSION.txt') as f:
        for line in f:
            if line.startswith('stage:'):
                version_stage = line.split(':')[1].strip()
            if line.startswith('major:'):
                version_major = line.split(':')[1].strip()
            if line.startswith('count:'):
                version_count = line.split(':')[1].strip()
            if line.startswith('commit:'):
                version_commit = line.split(':')[1].strip()
                version_commit_short = version_commit[:6]
            if line.startswith('date:'):
                version_date = line.split(':')[1].strip()
except Exception as e:
    print('Error reading VERSION.txt: ' + str(e))
    version_stage = 'dev'
    version_major = '0'
    version_count = '0'
    version_commit = '0000000'
    version_commit_short = version_commit[:6]
    version_date = '000000'


version_tuple = (version_stage, version_major, version_count, version_commit_short, version_date)

VERSION = version_stage + '-' + version_major + '.' + version_count + '-' + version_commit_short + '.' + version_date


# Append new version to Versionhistory.txt if not already there
with open('Versionhistory.txt') as f:
    for line in f:
        if line.startswith(VERSION):
            break
    else:
        with open('Versionhistory.txt', 'a') as f:
            f.write(VERSION + '\n')