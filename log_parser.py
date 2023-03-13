import re
from typing import List

def parse_tournament_log() -> dict:

    with open('logs/tournament.log', 'r') as f:
        lines = f.readlines()

    loglines: List(dict) = []
    traceback_flag = False

    # If the log is empty, raise an error
    if len(lines) == 0:
        raise Exception('The log file is empty')
    
    # If the log is too long (> 300 lines), cut it down to the last 300 lines
    if len(lines) > 300:
        lines = lines[-300:]

    # Iterate over all lines
    for line in lines:
        # remove the newline character
        line = line.replace('\n', '')

        # If it is a traceback-Block, add it to the previous logline
        if line.startswith('Traceback'):
            traceback_flag = True
            loglines[-1]['traceback'] = []

        if traceback_flag:
            if len(re.findall(r'\d{4}', line[0:4])) > 0:
                traceback_flag = False
            else:
                # Add the traceback to the previous logline
                loglines[-1]['traceback'].append(line)
                continue

        # Otherwise, it must be a new logline. Parse it and add it to the list
        raw_line = line.split(' - ')

        try:
            logline = {
                'datetime': raw_line[0],
                'module': raw_line[1],
                'level': raw_line[2],
                'message': raw_line[3],
                'traceback': None
            }
            loglines.append(logline)
        except IndexError:
            logline = {
                'datetime': "0000-00-00 00:00:00,000",
                'module': "parser",
                'level': "ERROR",
                'message': "Line skipped, could not be parsed. Raw:\n" + line,
                'traceback': None
            }
            loglines.append(logline)

    return loglines