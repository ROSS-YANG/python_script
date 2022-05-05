import Node_Test_Main
import pandas as pd 
df = pd.read_excel("list.xlsx")
ssh_list = df['hostname']
data = Node_Test_Main.get_temperature_alarm(ssh_list)
L1 = []
for i in data :
    if 'thres' in i['Common_Result_Data'] :
        print(i['Node'])


