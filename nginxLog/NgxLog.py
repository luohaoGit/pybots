# -*- coding: UTF-8 -*-
import os

from pyinotify import WatchManager, Notifier, ProcessEvent, IN_MODIFY


log_path = '/var/log/nginx/access.log'
file = None


class ProcessTransientFile(ProcessEvent):
    def process_IN_MODIFY(self, event):
        print("Modify file: %s " % os.path.join(event.path, event.name))
        global file
        line = file.readline()
        if line:
            print(line)


def monitor(file_name='.'):
    global file
    file = open(file_name, 'r')
    st_results = os.stat(file_name)
    st_size = st_results[6]
    file.seek(st_size)
    wm = WatchManager()
    notifier = Notifier(wm)
    wm.watch_transient_file(file_name, IN_MODIFY, ProcessTransientFile)
    print('now starting monitor %s' % file_name)
    notifier.loop()


if __name__ == "__main__":
    monitor(log_path)
