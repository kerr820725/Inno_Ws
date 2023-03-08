import pandas as pd
from collections import defaultdict
import glob , configparser , datetime
from openpyxl import load_workbook

class Kibana_convert:
    def __init__(self):
        
        config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        config.read('config.ini', encoding="utf-8")
        self.csv_path = config['config']['csv_filename_path'] 
        self.csv_filename = self.csv_path +  '/*.csv'
        self.csv_list = glob.glob(self.csv_filename )# 找尋所有 相關 檔案名 , 回傳list
        self.api_count_dict = defaultdict(list)
        

    def convert_csv_data(self , csv_path):

        csv_data = pd.read_csv(f'{csv_path}').to_dict('records')
        
        for dict_ in csv_data:
            try:
                api_name = dict_['Top values of path.keyword']
                api_count =  str(dict_['Count of records']) # 會有 字串 也有 int

                self.api_count_dict[api_name].append(  int(api_count.replace(',', '') )  )# 遇到千分未

            except Exception as e:
                print('convert_csv_data error :  %s'%e)
        
        return True

    def sum_csv_data(self): # 將 self.api_count_dict  的 value list 總合起來
        api_sum_dict = {'Api': [] , '總數量': [] }
        print('self.api_count_dict : %s'%self.api_count_dict)
        for api_name , api_list  in self.api_count_dict.items():
            api_sum_dict['Api'].append(api_name)
            api_sum_dict['總數量'].append(sum(api_list) )
        return api_sum_dict


    def data_to_xlsx(self):
        api_sum_dict = self.sum_csv_data()# 將 value list 算總和
        print('api_sum_dict: %s'%api_sum_dict)
        try:
            self.excel_path = f"{self.csv_path}/kibana_data_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            secondMockDF = pd.DataFrame(api_sum_dict )
            sort_value = secondMockDF.sort_values('總數量' , ascending=False)
            
            def color_code_by_text(val):
                if type(val) is int:
                    if val > 10000:
                        color='color: %s' % 'red'
                    elif val > 1000 :
                        color='color: %s' % 'green'
                    else:
                        color='color: %s' % 'blue'

                    return color

            #styled = (secondMockDF.style.applymap(color_code_by_text))# 將fail資訊 return 紅色
            writer = pd.ExcelWriter(self.excel_path, engine = 'openpyxl')
            sort_value.to_excel(writer, sheet_name = 'api_sum' , index = False )

            writer.close()

            print ('轉excel Ok')

            self.excel_book = load_workbook(self.excel_path)
        except Exception as e:
            print('轉 excel 錯誤 : %s'%e)
            return False


kibana_convert = Kibana_convert()

if len(kibana_convert.csv_list) == 0:
    print('找不到相關csv 檔案 ,　請確認config csv_filename_path 路徑')
else:
    for filter_csv in kibana_convert.csv_list:
        print('filter_csv: %s'%filter_csv)
        kibana_convert.convert_csv_data( csv_path =  filter_csv)

    
    kibana_convert.data_to_xlsx()