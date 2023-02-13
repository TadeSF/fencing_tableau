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
            version_commit_short = version_commit[:3] + "." + version_commit[-3:]
        if line.startswith('date:'):
            version_date = line.split(':')[1].strip()


version_tuple = (version_stage, version_major, version_count, version_commit_short, version_date)

VERSION = version_stage + '-' + version_major + '.' + version_count + '-' + version_commit_short + '.' + version_date
