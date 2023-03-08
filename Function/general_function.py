import datetime
import csv

def writeLog(filename, content):
    try:
        with open(filename+'.txt', 'a', newline='', encoding='utf-8') as logfile:
                logfile.writelines(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))+ " " +content+"\n") 
    except Exception as e :
        print(e.with_traceback)

def write_csv(filename, content , type='') : # type預設空 ,給 ['user', 'action', 'start_time', 'end_time', 'status_code', 'diff', 'response']
    try:
        with open(filename+'.csv', 'a', newline='', encoding='utf-8') as csvfile:
            if type == '':
                fieldnames = ['user', 'action', 'start_time', 'end_time', 'status_code', 'diff', 'response']
            else: # 多增加欄位
                fieldnames = type


            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
        
            writer.writerow(content)
            csvfile.close()
    except:
        pass