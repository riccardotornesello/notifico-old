import subprocess


def ping(options):
    command = ['ping', '-w', '1', options['host']]
    return subprocess.call(command) == 0
