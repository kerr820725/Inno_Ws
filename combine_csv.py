from email import header
from msilib.schema import Error
import socket , glob ,datetime , configparser, os, time, csv
import pandas as pd

class Csv:
    def __init__(self):      
        config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        config.read('config.ini', encoding="utf-8") 
        self.csv_filename_path = config['config']['csv_filename_path']      
        self.csv_filename = config['config']['csv_filename_path'] + '*.csv'
        self.csv_list = glob.glob(self.csv_filename )
        self.merge_filename = '%s%s.csv'%(config['config']['csv_filename_path'] ,'merge_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        self.jmeter_path = config['config']['jmeter_path']
        
    def combine_all_csv(self):
        '''
        功能1 : 
        路徑下整合所有的csv(不包含merge開頭的csv), 並存成一merge_{currentTime}.csv檔案
        '''
        # 儲存不包含merge開頭的檔案
        csv_list = []
        for csv_file in self.csv_list:
                csv_file = os.path.normpath(csv_file)
                # 將merge開頭的檔案除外
                if not csv_file.split(os.sep)[-1].startswith('merge'):
                    csv_list.append(csv_file)

        if len(csv_list) == 0:
            return '目錄下無要合併的csv檔'
        else:
            all_data = []
            for csv_file in csv_list:
                csv_file = os.path.normpath(csv_file)            
                datas = []
                with open(csv_file, encoding='utf-8') as f:
                    reader = csv.reader(f)
                    datas = list(reader)
                    for data in datas[1:]:
                        all_data.append(data)
                column = datas[0]

                df = pd.DataFrame(all_data, columns=column)
                df.to_csv(self.merge_filename, index=False)
            
            return 'merge success'

    def writeToHtml(self):    
        '''
        功能2 : 
        將merge.csv產出Jmeter報告
        '''
        
        output = self.csv_filename_path + 'report_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') 
        os.mkdir(output)  
        if not os.path.exists(self.merge_filename):
            print(f'{self.merge_filename} 檔不存在')
        elif not os.access(output, os.R_OK) or not os.access(output, os.W_OK) or not os.access(output, os.X_OK):
            print(f'無權限讀取 or 寫入 or 執行{output} 檔')
        else:
            command = f'{self.jmeter_path}jmeter -J jmeter.reportgenerator.exporter.html.series_filter="api" -g {self.merge_filename} -o {output}'      
            # os.popen(command, 'w')
            print('Start generating Jmeter report')
            print(command)
            os.system(command)
            print(f'Done! '+output)


              
if __name__ == "__main__":
    csvob = Csv()
    msg = csvob.combine_all_csv()
    print(msg)
    csvob.writeToHtml()
