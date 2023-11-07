import os
import sys
import psutil

DIR = sys.argv[0]
PID = os.getpid()

def disconnect():
    procs = []
    print("Clearing unkilled Odoo Instances.")
    home = os.path.expanduser('~')
    if os.path.exists(home):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pid_file_path = os.path.join(current_dir, '.odoo_pid')
        if not os.path.exists(pid_file_path):
            for process in psutil.process_iter():
                if len(process.cmdline()) > 1:
                    if os.path.join(current_dir, 'odoo.py') in process.cmdline():
                        if any(['python' in cmd for cmd in process.cmdline()]):
                            procs.append(process)
            for p in procs:
                if p.pid != PID:
                    p.kill()
                    print('Killed Process (PID: %s)' % PID)
        else:
            last_pid = False
            p = False
            with open(pid_file_path, 'r') as fr:
                read_data = fr.read()
            if read_data:
                try:
                    last_pid = int(read_data)
                except:
                    print('Pid File is Corrupted !')
            if last_pid:
                try:
                    p = psutil.Process(last_pid)
                except:
                    print('Odoo PidFile Expired. No Such Process!')
                if p:
                    try:
                        p.kill()
                        print('Killed Last Process (PID: %s)' % p.pid)
                    except:
                        print('Sorry, Cannot kill the already running Odoo Instance')
                        return False
        with open(pid_file_path, 'w') as fw:
            fw.write(str(PID))
    return True


