import os
import pandas as pd
import time
from threading import Thread
import csv
import NEW_PRB_REQUEST
import DINGDING
import platform
import pickle
import Node_Test_Main
# print(Time)
IP = '10.101.87.52'
# IP = '10.87.0.51'
# IP = '10.102.87.42'

Totle = 5180
# Node_Test_Main.GET_BJ_TIME()
List_Title =[{'Name':['worker','name']},{'PID':['worker','pid']},{'Status':['status']},
    {'Last Message':['lastMessage']}, {'Block Height':['paraHeaderSynchedTo']}, {'Public Key':['publicKey']}, 
    {'State':['minerInfoJson','raw','state']}, {'V':['minerInfoJson','v']}, {'Ve':['minerInfoJson','ve']}, 
    {'pInit':['minerInfoJson','benchmark','pInit']},
    {'pInstant':['minerInfoJson','benchmark','pInstant']},
    {'Minted':['minerInfoJson','stats','totalReward']}, {'Miner Account':['minerAccountId']}, 
    {'Stake Amount(BN)':['worker','stake']}, {'UUID':['worker','uuid']}, 
    {'parentHeaderSynchedTo':['parentHeaderSynchedTo']},
    {'paraHeaderSynchedTo':['paraHeaderSynchedTo']}, 
    {'Initialized':['initialized']},{'Endpoint':['worker','endpoint']}]
class DEAL_PRB_DATA :
    def __init__(self,IP,List_Title) :
        self.IP = IP
        self.List_Title = List_Title
        self.Dict_Host_Data = {}
        self.Threads = []
        self.List_Host_Data = []
        self.S_ERROR_List_Infor = {}
        self.Status_List = []
        self.PHA_Count = 0
        self.S_ERROR_List = []
        self.Status_Data_Dict = {}
        self.Status_Type = []
        self.Need_Write_Data = []
        self.State_List = []
        self.State_Dict_Data = {}
        self.DATE = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.Mysql_Need_Data = []
        self.BJ_DATE = ""
        self.BJ_TIME = ""
        self.Need_Restart_In_PRB_List = {}
        self.Mismatch_Node_Infor_Dict = {}
        self.Mismatch_Node_Infor_List = []
        self.Resp_Data = ''
        self.Update_Bios_Filad_List = []
        self.Gte_Mismatch_List = []
        self.Need_GL_Node = []
        self.Need_Restart_Worker_And_IP = {}
        self.Block_Abnormal = []
        self.GL_node()
    def GET_PRB_DATA(self) :
        # import Node_Test_Main
        DATE = Node_Test_Main.GET_BJ_TIME()
        self.BJ_DATE = DATE.split("_")[0]
        self.BJ_TIME = DATE.split("_")[1]
        self.Resp_Data = NEW_PRB_REQUEST.GET_WORKER_INFOR(self.IP)
    def GET_DICT_HOST_DATA(self,Data1) :
        for j in self.List_Title :
            # print(j)
            for key in j :
                self.Dict_Host_Data['DATE'] = self.BJ_DATE
                self.Dict_Host_Data['TIME'] = self.BJ_TIME
                self.Dict_Host_Data['PRB_IP'] = self.IP
                self.Dict_Host_Data['PRB_Host_Name'] = self.Node_Name
                Data = Data1.copy()
                for n in  j[key] :
                    try :
                        Data = Data[n]
                    except :
                        Data = "-"
                    # print(Data)
                self.Dict_Host_Data[key] = Data
        Values = tuple(self.Dict_Host_Data.values())

        self.Mysql_Need_Data.append(Values)
                    # print(self.Dict_Host_Data)
        return self.Dict_Host_Data
    def GET_LIST_HOST_DATA(self,Data) :
        self.List_Host_Data.append(Data)
    @staticmethod
    def CREAT_PRB_DATA_DIR() :
        if os.path.exists("PRB_DATA_DIR") != True :
            os.mkdir("PRB_DATA_DIR")
    def WRITE_DATA_TO_EXCEL(self) :
        self.CREAT_PRB_DATA_DIR()
        df = pd.DataFrame(self.List_Host_Data)
        if platform.system() == 'Windows' :
            df.to_excel(f'PRB_DATA_DIR\{self.DATE}-PRB_DATA--{self.PHA_Count}.xlsx')
        else :
            df.to_excel(f'PRB_DATA_DIR/{self.DATE}-PRB_DATA--{self.PHA_Count}.xlsx')
        return len(self.List_Host_Data)
    def GET_MINTED(self) :
        if self.Dict_Host_Data['Minted'] not in ["-"] :
            Minted = int(self.Dict_Host_Data['Minted'].replace(",",""))/1000000000000
            self.PHA_Count += Minted
        self.PHA_Count = round(self.PHA_Count,2)
    def GET_ERROR_LIST(self) :
        if self.Dict_Host_Data['Name'] not in self.Need_GL_Node and self.Dict_Host_Data['Status'] == 'S_ERROR' and self.Dict_Host_Data["PID"] not in ["525","527","530"]  :
            self.S_ERROR_List.append(self.Dict_Host_Data["Name"])
            self.S_ERROR_List_Infor[self.Dict_Host_Data["Name"]] = self.Dict_Host_Data
            if self.Dict_Host_Data["PRB_IP"] not in self.Need_Restart_Worker_And_IP :
                self.Need_Restart_Worker_And_IP[self.Dict_Host_Data["PRB_IP"]] = []
                self.Need_Restart_Worker_And_IP[self.Dict_Host_Data["PRB_IP"]].append(self.Dict_Host_Data["UUID"])
            else :
                self.Need_Restart_Worker_And_IP[self.Dict_Host_Data["PRB_IP"]].append(self.Dict_Host_Data["UUID"])
    def GET_UPDATE_BIOS_FILED_LIST(self) :
        if 'code 500' in self.Dict_Host_Data['Last Message'] :
            self.Update_Bios_Filad_List.append(self.Dict_Host_Data["Name"])
    def GET_NEED_RESTART_WORKER(self) :
        if self.Dict_Host_Data['Block Height'] == -1 :
            if self.Dict_Host_Data["PRB_IP"] not in self.Need_Restart_Worker_And_IP :
                self.Need_Restart_Worker_And_IP[self.Dict_Host_Data["PRB_IP"]] = []
                self.Need_Restart_Worker_And_IP[self.Dict_Host_Data["PRB_IP"]].append(self.Dict_Host_Data["UUID"])
            else :
                self.Need_Restart_Worker_And_IP[self.Dict_Host_Data["PRB_IP"]].append(self.Dict_Host_Data["UUID"])
            self.Block_Abnormal.append(self.Dict_Host_Data['Name'])
    def GET_MISMATCH_LIST(self) :
        if 'BlockNumberMismatch' in self.Dict_Host_Data['Last Message'] :
            self.Gte_Mismatch_List.append(self.Dict_Host_Data["Name"])
    def NEED_GL_NODE(self) :
        if self.Dict_Host_Data['State'] == "Ready" :
            self.Need_GL_Node.append(self.Dict_Host_Data["Name"])
    def WRITE_MINTED_HISTORY(self) :
        Title = ["DATE","Minted"]
        Data = {"DATE":self.DATE,"Minted":self.PHA_Count}
        Need_Data = [Data["DATE"],str(Data["Minted"])]
        self.Need_Write_Data.append(Title)
        self.Need_Write_Data.append(Need_Data)
        with open("PRB_Data_Histroy.csv",mode="w",newline="") as F:
            CSV_Writer = csv.writer(F)
            CSV_Writer.writerows(self.Need_Write_Data)
        with open("PRB_Data_Histroy_All.csv",mode="a",newline="") as F:
            CSV_Writer = csv.writer(F)
            if os.path.exists("PRB_Data_Histroy_All.csv") == True :
                CSV_Writer.writerows(self.Need_Write_Data[1])
            else :
                CSV_Writer.writerows(self.Need_Write_Data)
    def COMPERE_MINTED(self):
        if os.path.exists("PRB_Data_Histroy.csv") != True :
            Str_Data = f"目前机器总数:{len(self.List_Host_Data)}\n机器状态统计：\n"
            Str_Data += "PRB_Status：\n"
            for key in self.Status_Data_Dict :
                Str_Data +=f"{key} : {self.Status_Data_Dict[key]}\n"
            Str_Data += "Chain_Status：\n"
            for key in self.State_Dict_Data :
                Str_Data +=f"{key} : {self.State_Dict_Data[key]}\n"
            # Str_Data += f"目前总产值（PHA）: {self.PHA_Count}\n"
            print(Str_Data)
            return Str_Data
        else :
            with open("PRB_Data_Histroy.csv",mode="r") as F :
                CSV_Data = F.readlines()
                Last_DATE = CSV_Data[1].split(",")[0]
                Last_Minted = float(CSV_Data[1].split(",")[1].strip("\n"))
                Str_Data_1 = f"目前机器总数:{len(self.List_Host_Data)}\n机器状态统计：\n"
                Str_Data_1 += "PRB_Status：\n"
                for key in self.Status_Data_Dict :
                    Str_Data_1 += f"{key} : {self.Status_Data_Dict[key]}\n"
                Str_Data_1 += "\nChain_Status：\n"
                for key in self.State_Dict_Data :
                    Str_Data_1 +=f"{key} : {self.State_Dict_Data[key]}\n"
                Str_Data_1 += f"\n块高度异常计数：{len(self.Block_Abnormal)}\n"
                # Str_Data_1 +=f"目前总产值（PHA）: {self.PHA_Count}\n较上一次日期: {Last_DATE}\nPHA产量增加: {round(self.PHA_Count-Last_Minted,2)}\n"
                print(Str_Data_1)
                return Str_Data_1
    def GET_DATA_MAIN(self) :
        self.GET_PRB_DATA()
        for key in self.Resp_Data :
            self.IP = key
            self.Node_Name = 'PRB'+self.IP[-1]
            for i in self.Resp_Data[key] :
                i['minerInfoJson'] = dict(eval(i['minerInfoJson']))
                self.GET_DICT_HOST_DATA(i)
                self.GET_MINTED()
                self.GET_ERROR_LIST()
                # self.GET_UPDATE_BIOS_FILED_LIST()
                # self.GET_MISMATCH_LIST()
                self.NEED_GL_NODE()
                self.GET_NEED_RESTART_WORKER()
                self.Status_List.append(self.Dict_Host_Data["Status"])
                self.State_List.append(self.Dict_Host_Data["State"])
                self.GET_LIST_HOST_DATA(self.Dict_Host_Data.copy())
    def GET_WOREKER_STATUS_COUNT(self) :
        self.Status_Type = list(set(self.Status_List.copy()))
        for Type in self.Status_Type :
            self.Status_Data_Dict[Type] = self.Status_List.count(Type)
    def GET_WORKER_STATE_COUNT(self) :
        self.State_Type = list(set(self.State_List.copy()))
        for Type in self.State_Type :
            self.State_Dict_Data[Type] = self.State_List.count(Type)
    def GL_node(self) :
        df = pd.read_excel("Need_Poweroff_TJ.xlsx")
        GL_List = list(df["hostname"])
        # print(GL_List)
        self.Need_GL_Node += GL_List
    def THREAD_MAIN(self) :
        self.GET_DATA_MAIN()
        self.GET_WOREKER_STATUS_COUNT()
        self.GET_WORKER_STATE_COUNT()
        self.WRITE_DATA_TO_EXCEL()
        self.COMPERE_MINTED()
        self.WRITE_MINTED_HISTORY() 
        self.GL_node()
        print(len(self.S_ERROR_List))

    
def GL_NODE() :
    with open('300mac.txt',mode='r') as F :
        Data = F.readlines()
        # print(Data)
        Data1 = []
        for j in Data :
            Data1.append(j.replace('\n',''))
    df = pd.read_excel('need_gl_hostname.xlsx')
    Data1 = Data1+list(df['hostname'])
    return Data1
def WRTIE_OR_READ_APPEND_FILE(File_Name,Mode,Data="") :
    """
    Mode = r,rb,w,wb,a....
    """
    with open(File_Name,Mode) as F:
        if Mode in ['w','wb',"a"] :
            F.write(Data)
        else :
            File_Data = F.readlines()
            return File_Data

def MAIN() :
    OBJ = DEAL_PRB_DATA(IP,List_Title)
    OBJ.THREAD_MAIN()
    DINGDING.SEND_MSG_TO_DINGDING(OBJ.COMPERE_MINTED())
    OBJ.WRITE_DATA_TO_EXCEL()
    S_ERROR_List = OBJ.S_ERROR_List
    ERROR_List = set(S_ERROR_List) - set(OBJ.Need_GL_Node)
    if len(OBJ.List_Host_Data) != Totle :
        DINGDING.SEND_MSG_TO_DINGDING("PRB加载部分数据失败！！及时查看！！")
        DINGDING.SEND_MSG_TO_DINGDING("PRB加载部分数据失败！！及时查看！！")
        DINGDING.SEND_MSG_TO_DINGDING("PRB加载部分数据失败！！及时查看！！")
    if len(ERROR_List) > 120 :
        DINGDING.SEND_MSG_TO_DINGDING("ERROR_List:"+"数量较多请检查")
        DINGDING.SEND_MSG_TO_DINGDING("ERROR_List:"+"数量较多请检查")
        DINGDING.SEND_MSG_TO_DINGDING("ERROR_List:"+"数量较多请检查")
        exit()
    else :
        return list(ERROR_List)
def RESTART_WORKER() :
    BJ_DATE = Node_Test_Main.GET_BJ_TIME()
    print(BJ_DATE)
    import ast
    if not os.path.exists("Last_Block_Abnormal") :
        Last_Block_Abnormal_List = []
    else :
        Last_Block_Abnormal_List = ast.literal_eval(WRTIE_OR_READ_APPEND_FILE("Last_Block_Abnormal",'r')[0])
    print(BJ_DATE,Last_Block_Abnormal_List)
    OBJ = DEAL_PRB_DATA(IP,List_Title)
    OBJ.THREAD_MAIN()
    New_Block_Abnormal = OBJ.Block_Abnormal
    Need_Restart_Pruntime = set(Last_Block_Abnormal_List) & set(New_Block_Abnormal)
    # if Need_Restart_Pruntime :
    #     Node_Test_Main.RESTART_DOCKER(Need_Restart_Pruntime)
    #     time.sleep(60)
    print(BJ_DATE,"Need_Restart_Pruntime:",Need_Restart_Pruntime)
    NEW_PRB_REQUEST.RESTART_WORKER(IP,OBJ.Need_Restart_Worker_And_IP)
    WRTIE_OR_READ_APPEND_FILE("Last_Block_Abnormal",'w',str(New_Block_Abnormal))
def ADD_DATA_TO_MYSQL() :
    OBJ = DEAL_PRB_DATA(IP,List_Title)
    OBJ.THREAD_MAIN()
    Need_Add_Data = OBJ.Mysql_Need_Data 
    import SJK
    SJK.ADD_PRB_DATA(Need_Add_Data)

if __name__ == "__main__" :
    # while True :
    
    RESTART_WORKER()

    # MAIN()
    # data2 = MAIN()ssh
    # print(data2)
    # ADD_DATA_TO_MYSQL()
    # import Node_Test_Main
    # print(Node_Test_Main.GET_BJ_TIME())









        
        



 