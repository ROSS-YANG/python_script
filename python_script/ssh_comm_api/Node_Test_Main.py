import datetime
import subprocess
from threading import Thread
import queue 
# import DINGDING
import re
import os
import time
import csv
# import PRB_DATA_CLASS
THREADS = 30
Q = queue.Queue()

def EXECUTIVE_COMMOND(Commond='',Timeout=None,Node='Node') :
    Comm_Result = subprocess.Popen(Commond,shell = True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0)
    try :
        Comm_Result_Data = Comm_Result.communicate(timeout=Timeout)[0].decode('utf-8')
        Q.put({"Node":Node,"Result_Type" : "Succed","Common_Result_Data" : Comm_Result_Data})
    except Exception as ERROR:
        Q.put({"Node":Node,"Result_Type" : "ERROR","Common_Result_Data" : str(ERROR) })
def GET_ERROR_NODE() :
    print("获取列表中.....")
    Result =  subprocess.Popen(f'/home/phala/dump_prb_workers.rb', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try :
        print(str(Result.communicate(timeout=60)))
        print("获取完成")
    except Exception as ERROR :
        print(ERROR)
def THREAD(List,Comm,Timeout=None) :
    Thread_Result = []
    start_num = 0
    end_num = 0
    while start_num < len(List) :
        start_num = end_num
        end_num += THREADS
        print(start_num,end_num) 
        Threads = []
        for i in List[start_num:end_num:] :
            i = i.strip()
            if i != "" :
                Args_Dict = {
                    'Commond' : Comm.replace('Args',i),
                    "Timeout" : Timeout,
                    "Node" : i
                }
                T = Thread(target=EXECUTIVE_COMMOND,name=i,kwargs=Args_Dict)
                T.start()
                Threads.append(T)
        for T in Threads :
            T.join()
            Thread_Result.append(Q.get()) 
        
    return Thread_Result
def SORT_LIST(LIST) :
    LIST.sort(key=lambda x :int(re.search(r".*?-(\d*).(\d*)",x).group(2)))
    LIST.sort(key=lambda x :int(re.search(r".*?-(\d*).(\d*)",x).group(1)))
    return LIST  
def NODE_SSH_COMMOND(Node_Comm_Dict,Node_List,Time_Out) :
    Result = {}
    for key in Node_Comm_Dict :
        Node_Comm = Node_Comm_Dict[key]
        Comm = f'echo Args `ssh -o StrictHostkeyChecking=no -o ConnectTimeout=2 -o ConnectionAttempts=2 ubuntu@Args "{Node_Comm}"`'
        Get_Node_Log_Infor_Data = THREAD(Node_List,Comm,Timeout=Time_Out)
        Result[key] = Get_Node_Log_Infor_Data
    return Result
def PING_NODE_DATA(Node_List) :
    Comm = f'ping -c 3 -W 2 Args'
    Ping_Node_Comm_Data = THREAD(Node_List,Comm,Timeout=10)
    return DEAL_PING_DATA(Ping_Node_Comm_Data)
def DEAL_PING_DATA(Ping_Node_Comm_Data):
    Can_Ping_List = []
    Ping_Timeout_List = []
    Canot_Ping_Other_List = []
    Ping_Node_Comm_Result = {}
    for Comm_Data in Ping_Node_Comm_Data :
        Ping_Node_Name = Comm_Data["Node"]
        Ping_Comm_Type = Comm_Data["Result_Type"]
        Ping_Comm_Result_Data = Comm_Data["Common_Result_Data"]
        Ping_Node_Comm_Result[Ping_Node_Name] = Ping_Comm_Result_Data
        if Ping_Comm_Type == 'ERROR':
            Canot_Ping_Other_List.append(Ping_Node_Name)
        if Ping_Comm_Type == 'Succed' :
                if " 0 received, 100% packet loss" in Ping_Comm_Result_Data :
                    Ping_Timeout_List.append(Ping_Node_Name)
                elif "min/avg/max/mdev" in Ping_Comm_Result_Data :
                    Can_Ping_List.append(Ping_Node_Name)
                else :
                    Canot_Ping_Other_List.append(Ping_Node_Name)
    return {
        "Ping_OK" : Can_Ping_List,
        "Ping_Timeout" : Ping_Timeout_List,
        "Ping_Filed" : Canot_Ping_Other_List,
        "Ping_Comm_Result" : Ping_Node_Comm_Result
    }
def SSH_TEST_DATA(Node_List) :
    SSH_Connect_Test = {"SSH_Connect_Test" : "echo ssh-ok"}
    SSH_Node_Comm_Data = NODE_SSH_COMMOND(SSH_Connect_Test,Node_List,Time_Out=10)
    return DEAL_SSH_DATA(SSH_Node_Comm_Data['SSH_Connect_Test']) 
def DEAL_SSH_DATA(SSH_Node_Comm_Data) :  
    SSH_Test_Comm_Result = {}
    SSH_Test_OK = []
    SSH_Test_ERROR = []
    for Comm_Data in SSH_Node_Comm_Data :
        SSH_Node_Name = Comm_Data["Node"]
        SSH_Comm_Type = Comm_Data["Result_Type"]
        SSH_Comm_Result_Data = Comm_Data["Common_Result_Data"]
        SSH_Test_Comm_Result[SSH_Node_Name] = SSH_Comm_Result_Data
        if SSH_Comm_Type == 'ERROR':
            SSH_Test_ERROR.append(SSH_Node_Name)
        if SSH_Comm_Type == 'Succed' :
                if "ssh-ok" in SSH_Comm_Result_Data :
                    SSH_Test_OK.append(SSH_Node_Name)
                else :
                    SSH_Test_ERROR.append(SSH_Node_Name)
    return {
        "SSH_Test_OK" : SSH_Test_OK,
        'SSH_Test_ERROR' : SSH_Test_ERROR,
        "SSH_Comm_Result" : SSH_Test_Comm_Result
    }
def SGX_TEST_DATA(Node_List) :
    SGX_Eable_Test_Comm = {"SGX_Eable_Test_Comm":"sudo /opt/phala/sgx_enable"}
    SGX_Node_Comm_Data = NODE_SSH_COMMOND(SGX_Eable_Test_Comm,Node_List,Time_Out=10)
    return DEAL_SGX_DATA(SGX_Node_Comm_Data["SGX_Eable_Test_Comm"]) 
def DEAL_SGX_DATA(SGX_Node_Comm_Data) :
    SGX_Test_Comm_Result = {}
    SGX_Test_Enable = []
    SGX_Test_Unable = []
    SGX_Test_No_Dir = []
    SGX_Test_Other_ERROR = []
    SGX_Test_Need_Reboot =  []
    for Comm_Data in SGX_Node_Comm_Data :
        SGX_Test_Node_Name = Comm_Data["Node"]
        SGX_Test_Comm_Type = Comm_Data["Result_Type"]
        SGX_Comm_Result_Data = Comm_Data["Common_Result_Data"]
        SGX_Test_Comm_Result[SGX_Test_Node_Name] = SGX_Comm_Result_Data
        if SGX_Test_Comm_Type == 'ERROR':
            SGX_Test_Other_ERROR.append(SGX_Test_Node_Name)
        if SGX_Test_Comm_Type == 'Succed' :
            if " No such file or directory" in SGX_Comm_Result_Data :
                SGX_Test_No_Dir.append(SGX_Test_Node_Name)
            elif " Intel SGX is already enabled on this system" in SGX_Comm_Result_Data :
                SGX_Test_Enable.append(SGX_Test_Node_Name)
            elif "explicit option to enable Intel SGX" in SGX_Comm_Result_Data :
                SGX_Test_Unable.append(SGX_Test_Node_Name)
            elif 'reboot' in SGX_Comm_Result_Data :
                SGX_Test_Need_Reboot.append(SGX_Test_Node_Name)
            else :
                SGX_Test_Other_ERROR.append(SGX_Test_Node_Name)
    return {
        "SGX_Test_Enable" : SGX_Test_Enable,
        'SGX_Test_Need_open' : SGX_Test_Unable,
        'SGX_Test_No_Dir' : SGX_Test_No_Dir,
        'SGX_Test_Other_ERROR' : SGX_Test_Other_ERROR,
        "SGX_Comm_Result" : SGX_Test_Comm_Result,
        'SGX_Test_Need_Reboot' : SGX_Test_Need_Reboot
    }
def CHECK_DOCKER_DATA(Node_List) :
    Check_Docker_Comm = {"Check_Docker_Comm" : "sudo docker ps --all"}
    Check_Docker_Comm_Data = NODE_SSH_COMMOND(Check_Docker_Comm,Node_List,Time_Out=10)
    return DEAL_CHECK_DOCKER_DATA(Check_Docker_Comm_Data["Check_Docker_Comm"])   
def DEAL_CHECK_DOCKER_DATA(Check_Docker_Comm_Data) :
    Check_Docker_Comm_Result = {}
    Check_Docker_Ok = []
    Check_Docker_Status_Exit = []
    Check_Docker_No_Docker = []
    Check_Docker_Status_Abnormal = []
    Check_Docker_No_Pruntime = []
    Check_Docker_Other_ERROR = []
    for Comm_Data in Check_Docker_Comm_Data :
        Check_Docker_Test_Node_Name = Comm_Data["Node"]
        Check_Docker_Test_Comm_Type = Comm_Data["Result_Type"]
        Check_Docker_Comm_Result_Data = Comm_Data["Common_Result_Data"]
        Check_Docker_Comm_Result[Check_Docker_Test_Node_Name] = Check_Docker_Comm_Result_Data
        if Check_Docker_Test_Comm_Type == 'ERROR':
            Check_Docker_Other_ERROR.append(Check_Docker_Test_Node_Name)
        if Check_Docker_Test_Comm_Type == 'Succed' :
            if "command not found" in Check_Docker_Comm_Result_Data :
                Check_Docker_No_Docker.append(Check_Docker_Test_Node_Name)
            elif "CONTAINER ID IMAGE" in Check_Docker_Comm_Result_Data :
                if "Up" in Check_Docker_Comm_Result_Data and "deploy_pruntime_1" in Check_Docker_Comm_Result_Data :
                    Check_Docker_Ok.append(Check_Docker_Test_Node_Name)
                elif "Exited (" in Check_Docker_Comm_Result_Data and "deploy_pruntime_1" in Check_Docker_Comm_Result_Data :
                    Check_Docker_Status_Exit.append(Check_Docker_Test_Node_Name)
                elif "deploy_pruntime_1" in Check_Docker_Comm_Result_Data and "Up" not in Check_Docker_Comm_Result_Data :
                    Check_Docker_Status_Abnormal.append(Check_Docker_Test_Node_Name)
                else :
                    Check_Docker_No_Pruntime.append(Check_Docker_Test_Node_Name)
            else :
                Check_Docker_Other_ERROR.append(Check_Docker_Test_Node_Name)
    return {
        "Check_Docker_Ok" : Check_Docker_Ok,
        "Check_Docker_Other_ERROR" : Check_Docker_Other_ERROR,
        "Check_Docker_No_Docker" : Check_Docker_No_Docker,
        "Check_Docker_Stauts_Exit" : Check_Docker_Status_Exit,
        "Check_Docker_Status_Abnormal" : Check_Docker_Status_Abnormal,
        "Check_Docker_No_Pruntime" : Check_Docker_No_Pruntime,
        "Check_Docker_Comm_Result" : Check_Docker_Comm_Result,
    }
def CURL_TEST_DATA(Node_List) :
    Comm = f'curl --connect-timeout 20 --max-time 20 -s http://Args:8000/get_info | jq -r .payload | jq -r .version&echo Args'
    Curl_Test_Comm_Data = THREAD(Node_List,Comm,Timeout=30)
    return DEAL_CURL_TEST_DATA(Curl_Test_Comm_Data)
def DEAL_CURL_TEST_DATA(Curl_Test_Comm_Data) :
    Curl_Test_OK = []
    Curl_Test_Return_None = []
    Curl_Test_Column_ERROR = []
    Curl_Test_Comm_Result = {}
    Curl_Test_Other_ERROR = []
    for Comm_Data in Curl_Test_Comm_Data :
        Curl_Test_Node_Name = Comm_Data["Node"]
        Curl_Test_Comm_Type = Comm_Data["Result_Type"]
        Curl_Test_Comm_Result_Data = Comm_Data["Common_Result_Data"]
        Curl_Test_Comm_Result[Curl_Test_Node_Name] = Curl_Test_Comm_Result_Data
        if Curl_Test_Comm_Type == 'ERROR':
            Curl_Test_Other_ERROR.append(Curl_Test_Comm_Result_Data)
        if Curl_Test_Comm_Type == 'Succed' :
            # print(Curl_Test_Comm_Result_Data)
            if "0.1.3" in Curl_Test_Comm_Result_Data :
                Curl_Test_OK.append(Curl_Test_Node_Name)
            elif "Invalid numeric literal at line 2, column 22" in Curl_Test_Comm_Result_Data :
                Curl_Test_Column_ERROR.append(Curl_Test_Node_Name)
            elif f"(b'{Curl_Test_Node_Name}\\n', None)" ==  Curl_Test_Comm_Result_Data :
                Curl_Test_Return_None.append(Curl_Test_Node_Name)
            else :
                Curl_Test_Other_ERROR.append(Curl_Test_Node_Name)
    return {
        "Curl_Test_OK" : Curl_Test_OK,
        'Curl_Test_Return_None_Need_Reboot' : Curl_Test_Return_None,
        'Curl_Test_Column_ERROR_Pruntime_Version_too_old' : Curl_Test_Column_ERROR,
        'Curl_Test_Other_ERROR' : Curl_Test_Other_ERROR,
        "Curl_Test_Comm_Result" : Curl_Test_Comm_Result
    } 
def GET_NODE_LOG_ERROR_AND_BUG_INFOR(Node_List) :
    Get_Node_Comm_Result = {}
    Node_Comm_Dict = {
    "View_SGX_Dirver" : "ls /dev | grep -i sgx",
    "SGX_Log" : "dmesg | grep -i sgx",
    "Start_BUG_Or_Error" : "dmesg | grep -iE 'bug|error'",
    "Sys_Log_BUG_Or_Error" :"cat /var/log/syslog | grep -iE 'error|bug'",
    # "Docker_Log_BUG_Or_Error" : "journalctl -u docker.service | grep -iE 'error|bug'"
    }
    Get_Node_Log_Infor_Data = NODE_SSH_COMMOND(Node_Comm_Dict,Node_List,Time_Out=20)
    for key in Get_Node_Log_Infor_Data :
        Tmp = {}
        for i in Get_Node_Log_Infor_Data[key] :
            Tmp[i["Node"]] = i["Common_Result_Data"]
        Get_Node_Comm_Result[key] = Tmp
    return Get_Node_Comm_Result
def REBOOT_NODE(Node_List) :
    # Node_List = list(Node_List)
    # print(Node_List)
    # exit()
    Reboot_Comm = {"Reboot_Comm":"sudo reboot"}
    Reboot_Comm_Data = NODE_SSH_COMMOND(Reboot_Comm,Node_List,Time_Out=10)
    Reboot_Comm_Data_Result =  Reboot_Comm_Data["Reboot_Comm"]
    Tmp = {}
    for i in Reboot_Comm_Data_Result :
        Tmp[i["Node"]] = i["Common_Result_Data"]
    Reboot_Comm_Data["Reboot_Comm"] = Tmp
    return Reboot_Comm_Data
def CREAT_LOCAL_CSV() :
    with open("Local_IT_OP_Histroy.csv",mode="w",newline="") as F :
        CSV_Wirte = csv.writer(F)
        CSV_Wirte.writerow(["DATE","NODE","OP","REASON"])
def GET_LOCAL_IT_OP() :
    if os.path.exists("Local_IT_OP_Histroy.csv") != True :
        CREAT_LOCAL_CSV()
    else :
        with open("Local_IT_OP_Histroy.csv",mode="r") as F :
            Data = list(csv.reader(F))
            if Data == [["DATE","NODE","OP","REASON","RESULT"]] :
                return 0
            else :
                CREAT_LOCAL_CSV()
                return Data[1::]
def GET_BJ_TIME() :
    from datetime import datetime
    from datetime import timedelta
    from datetime import timezone
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    beijing_now = utc_now.astimezone(SHA_TZ)
    BJ_Time = str(beijing_now).split(".")[0].replace(" ","_")
    return BJ_Time.replace(":","-")
def GET_BIOS_AND_CPU_INFOR(Node_List) :
    Get_Bios_And_CPU_Result_Comm_Dict = {'Get_Bios_And_CPU_Result': "sudo dmidecode type bios | grep -E 'Product Name:|CPU|Version:|Release'"}
    Get_Bios_And_CPU_Infor_Data = NODE_SSH_COMMOND(Get_Bios_And_CPU_Result_Comm_Dict,Node_List,Time_Out=10)
    # Get_Bios_And_CPU_Infor_Result = Get_Bios_And_CPU_Infor_Data
    # ['Get_Bios_And_CPU_Result']
    return Get_Bios_And_CPU_Infor_Data
# def GET_BIOS_AND_CPU_INFOR_TO_EXCEL(DATA) :
def POWEROFF(Node_List) :
    poweroff_Comm_Dict = {'poweroff': "sudo poweroff"}
    poweroff_Data = NODE_SSH_COMMOND(poweroff_Comm_Dict,Node_List,Time_Out=10)
    for i in poweroff_Data['poweroff'] :
        print(i)
    # ['Get_Bios_And_CPU_Result']
    return poweroff_Data
def RESTART_DOCKER(Node_List) :
    Restart_Docker_Comm_Dict = {'restart_docker': "sudo docker restart deploy_pruntime_1"}
    Restart_Docker_Data = NODE_SSH_COMMOND(Restart_Docker_Comm_Dict,Node_List,Time_Out=10)
    for i in Restart_Docker_Data['restart_docker'] :
        print(i)
    # ['Get_Bios_And_CPU_Result']
    return Restart_Docker_Data
def GET_ETH(Node_List) :
    Get_ETH_Speed_Dict = {"Get_Speed":"sudo ethtool enp2s0 | grep Speed"}
    Get_ETH_Data = NODE_SSH_COMMOND(Get_ETH_Speed_Dict,Node_List,Time_Out=10)
    return Get_ETH_Data
def GET_ETH1(Node_List) :
    Get_ETH_Speed_Dict = {"Get_Speed": "sudo ethtool eno1 | grep Speed"}
    Get_ETH_Data = NODE_SSH_COMMOND(Get_ETH_Speed_Dict,Node_List,Time_Out=10)
    return Get_ETH_Data
def get_temperature_alarm(Node_List) :
    get_temperature_data = {"get_tempreature_alarm": "cat /var/log/syslog | grep -i threshold | tail -n 1"}
    get_temperature_result = NODE_SSH_COMMOND(get_temperature_data,Node_List,Time_Out=10)
    return get_temperature_result["get_tempreature_alarm"]
def get_temperature(node_list) :
    get_temperature_dict = {"get_temperature": " sudo sensors | grep Package "}
    get_temperature_data = NODE_SSH_COMMOND(get_temperature_dict,node_list,Time_Out=10)
    return get_temperature_data['get_temperature']
def install_softwave(node_list,apt_commond) :
    install_dict = {"install": apt_commond}
    install_data = NODE_SSH_COMMOND(install_dict,node_list,Time_Out=10)
    return install_data['install']
if __name__ == "__main__" :
    pass
    # # exit()
    # # List = ['node-600-1']
    # # Data = GET_BIOS_AND_CPU_INFOR(List)
    # # print(Data)
    # # exit()
    # # print(os.path.exists("Node_Test_Log.csv"))
    # # exit()
    # # Get_ERROR_List/home/phala/tmp/
    # # GET_ERROR_NODE()
    # # with open('tmp/suspicious_broken',mode='r') as F :
    # # import PRB_DATA_NEW
    # # List = PRB_DATA_NEW.MAIN()
    # List = PRB_DATA_CLASS.MAIN()
    # if len(List) > 500 :
    #     DINGDING.SEND_MSG_TO_DINGDING('S_ERROR数量较多')
    #     # exit()
    # # exit()
    # # PRB_Data = PRB_DATA.MAIN()
    # print(SORT_LIST(List))
    # List = List
    # # exit()
    # # with open('2.txt',mode='r') as F :
    # #     List = F.readlines()
    # #     print(List)
    # print(f"有{len(List)}有问题节点")
    # print(f"有{len(set(List))}有问题节点")
    # print("开始执行预定命令，请确保目前权限为root,不是root请立即CTRL+C退出")
    # List = set(List)
    # List = list(List)
    # Title_List = [
    # "DATE","NODE_NAME","TEST_STAGE","ERROR_TYPE",
    # "TEST_COMM_RESULT","ls /dev | grep -i sgx",
    # "dmesg | grep -i sgx","dmesg | grep -iE 'bug|error'",
    # "cat /var/log/syslog | grep -iE 'error|bug'"
    # #  "journalctl -u docker.service | grep -iE 'error|bug'"
    #  ]
    # Node_Test_Log = []
    # Node_Test_Log.append(Title_List)

    # Date = GET_BJ_TIME()
    # Date1 = Date.split("_")[0] 
    # Ping_Data = PING_NODE_DATA(List)
    # Test_Stage = "Ping_Node"
    # Need_Manual_Reboot_List = []
    # Need_Manual_Reboot_Dict = []
    # for key in Ping_Data :
    #     if key not in ["Ping_OK","Ping_Comm_Result"] :
    #         for Node_Name in Ping_Data[key] :
    #             Need_Manual_Reboot_List.append(Node_Name)
    #             Node_Data = [Date,Node_Name,Test_Stage,key,Ping_Data["Ping_Comm_Result"][Node_Name]]
    #             # print(Node_Data)
    #             Node_Test_Log.append(Node_Data)
    # SSH_Test_List = Ping_Data["Ping_OK"]
    # print(len(SSH_Test_List))
    # Test_Stage = "SSH_Connect_Test"
    # SSH_Connect_Data = SSH_TEST_DATA(SSH_Test_List)
    # for key in SSH_Connect_Data :
    #     if key not in ["SSH_Test_OK","SSH_Comm_Result"] :
    #         for Node_Name in SSH_Connect_Data[key] :
    #             # print(key)
    #             Need_Manual_Reboot_List.append(Node_Name)
    #             Node_Data = [Date,Node_Name,Test_Stage,key,SSH_Connect_Data["SSH_Comm_Result"][Node_Name]]
    #             Node_Test_Log.append(Node_Data)
    #             # print(Node_Data)
    # Check_SGX_Enable_List = SSH_Connect_Data["SSH_Test_OK"]
    # print(len(Check_SGX_Enable_List))
    # Test_SGX_Enable_Data = SGX_TEST_DATA(Check_SGX_Enable_List)
    # Test_Stage = "Check_SGX_Enable"
    # for key in Test_SGX_Enable_Data :
    #     if key not in ["SGX_Test_Enable","SGX_Comm_Result"] :
    #         for Node_Name in Test_SGX_Enable_Data[key] :
    #             Node_Data = [Date,Node_Name,Test_Stage,key,Test_SGX_Enable_Data["SGX_Comm_Result"][Node_Name]]
    #             Node_Test_Log.append(Node_Data)

    # Check_Docker_List = Test_SGX_Enable_Data["SGX_Test_Enable"]
    # print(len(Check_Docker_List))
    # Check_Docker_Data = CHECK_DOCKER_DATA(Check_Docker_List)
    # Check_Docker_Need_Log_List = []
    # Test_Stage ="Check_Docker"
    # for key in Check_Docker_Data :
    #     if key in ["Check_Docker_Other_ERROR","Check_Docker_Stauts_Exit","Check_Docker_Status_Abnormal"] :
    #         Check_Docker_Need_Log_List += Check_Docker_Data[key]
    # # Check_Docker_Log_Data = GET_NODE_LOG_ERROR_AND_BUG_INFOR(Check_Docker_Need_Log_List)
    # for key in Check_Docker_Data :
    #     if key not in ["Check_Docker_Ok","Check_Docker_Comm_Result"] :
    #         for Node_Name in Check_Docker_Data[key] :
    #             Node_Data = [Date,Node_Name,Test_Stage,key,Check_Docker_Data["Check_Docker_Comm_Result"][Node_Name]]
    #             # for i in Check_Docker_Log_Data.keys() :
    #             #     Node_Data.append(Check_Docker_Log_Data[i][Node_Name])
    #             Node_Test_Log.append(Node_Data)
    #             # print(Node_Data)
    # Curl_Test_List = Check_Docker_Data["Check_Docker_Ok"]
    # print(len(Curl_Test_List))
    # Curl_Test_Data = CURL_TEST_DATA(Curl_Test_List)
    # Test_Stage = "Curl_Test"
    # Curl_Test_Need_Log_List = []
    # for key in Curl_Test_Data :
    #     if key not in ["Curl_Test_OK","Curl_Test_Comm_Result"] :
    #         Curl_Test_Need_Log_List += Curl_Test_Data[key]
    # # Curl_Test_Log_Data = GET_NODE_LOG_ERROR_AND_BUG_INFOR(Curl_Test_Need_Log_List)
    # for key in Curl_Test_Data :
    #     if key not in ["Curl_Test_Comm_Result"] :
    #     # if key not in ["Curl_Test_OK","Curl_Test_Comm_Result"] :
    #         for Node_Name in Curl_Test_Data[key] :
    #             Node_Data = [Date,Node_Name,Test_Stage,key,Curl_Test_Data["Curl_Test_Comm_Result"][Node_Name]]
    #             # for i in Curl_Test_Log_Data.keys() :
    #             #     Node_Data.append(Curl_Test_Log_Data[i][Node_Name])
    #             Node_Test_Log.append(Node_Data)

    #             # print(Node_Data)
    # Test_Stage = "Loacl_IT_OP"
    # Local_IT_OP_Data = GET_LOCAL_IT_OP()


    
    # Test_Stage = "Reboot_Node"
    # Check_Docker_Other_Error_Need_Reboot = []
    # for key in Check_Docker_Data["Check_Docker_Comm_Result"] :
    #     if "Cannot connect to the Docker daemon"  in Check_Docker_Data["Check_Docker_Comm_Result"][key] :
    #         Check_Docker_Other_Error_Need_Reboot.append(key)
    #     if "unexpected fault address"  in Check_Docker_Data["Check_Docker_Comm_Result"][key] :
    #         Check_Docker_Other_Error_Need_Reboot.append(key)
    # print(Check_Docker_Other_Error_Need_Reboot)

    # Need_Reboot_Node_Dict = {
    # "Curl_Test_Return_None_Need_Reboot":Curl_Test_Data["Curl_Test_Return_None_Need_Reboot"],
    # "Check_Docker_Stauts_Exit" : Check_Docker_Data["Check_Docker_Stauts_Exit"],
    # "Check_Docker_Other_Error_Need_Reboot" : Check_Docker_Other_Error_Need_Reboot
    # }
    # for j in Need_Reboot_Node_Dict.keys() :
    #     Reboot_Node_Data = REBOOT_NODE(Need_Reboot_Node_Dict[j])
    #     for key in Reboot_Node_Data :
    #         for i in Reboot_Node_Data[key].keys() :
    #             Node_Data = [Date,i,Test_Stage,j,Reboot_Node_Data[key][i]]
    #             Node_Test_Log.append(Node_Data)
    # print("执行命令结束")
    # print("开始写入LOG")
    # with open("Node_Test_Log.csv",mode="a",newline="") as F :
    #     CSV_Wirte = csv.writer(F)
    #     if os.path.exists("Node_Test_Log.csv") != True :
    #         print("不存在日志文件，创建并写入文件")
    #         CSV_Wirte.writerows(Node_Test_Log)
    #     else :
    #         CSV_Wirte.writerows(Node_Test_Log[1::])


    # # with open(f"{Date}_Node_Test_Log.csv",mode="w",newline="") as F :
    # #     CSV_Wirte = csv.writer(F)
    # #     CSV_Wirte.writerows(Node_Test_Log)
    # print("文件写入结束")
    # DINGDING_Str = ""
    # print(f"需要手动重启列表，详细重启原因请看{Date}_Node_Test_Log.csv")
    # DINGDING_Str = "需要手动重启列表\n"
    # try :
    #     SORT_LIST(Need_Manual_Reboot_List)
    #     for i in Need_Manual_Reboot_List :
    #         print(i)
    #         DINGDING_Str += f"{i}\n"
    # except :
    #     print("排序失败，节点名称不符合node-x-x命名")
    #     for i in Need_Manual_Reboot_List :
    #         print(i)
 
    # DINGDING.SEND_MSG_TO_DINGDING(DINGDING_Str)
    # SQL_Var = []
    # for i in Node_Test_Log[1::] :
    #     # print(i)
    #     Date = i[0].split("_")[0]
    #     Time = i[0].split("_")[1]
    #     i[0] = Date
    #     i.insert(1,Time)
    #     # print(i)
    #     # break
    #     SQL_Var.append(tuple(i))
    # import SJK
    # SJK.MAIN1(SQL_Var)
    


    


    #         print(f"{key}--{Comm_Data['Node']}--{Comm_Data['Common_Result_Data']}")      

        # pass
    # for SGX_Test_Node_Name in Ping_Data :
    #     if SGX_Test_Node_Name not in ["Ping_OK","Ping_Comm_Result"] :
    #         # print(Ping_SGX_Comm_Result_Data)
    #         print(SGX_Test_Node_Name,":")
    #         Data = SORT_LIST(Ping_SGX_Comm_Result_Data)
    #         print(Data)
    # SSH_Test_Data = SSH_TEST_DATA(List)
    # for SGX_Test_Node_Name in SSH_Test_Data :
    #     if SGX_Test_Node_Name == "SSH_Test_ERROR" :
    #         print(SGX_Test_Node_Name)
    #         # print(SORT_LIST(SSH_Test_SGX_Comm_Result_Data))
    # SGX_Test_Data = SGX_TEST_DATA(List)
    # for key in SGX_Test_Data :
    #     if key != "SGX_Comm_Result" :
    #         print(SORT_LIST(SGX_Test_Data[key]))
    # Check_Docker_Data = CHECK_DOCKER_DATA(List) 
    # for key in Check_Docker_Data :
    #     if key != "Check_Docker_Comm_Result" :
    #         print(key)
    #         print(SORT_LIST(Check_Docker_Data[key]))
    # Curl_Test_Data = CURL_TEST_DATA(List)
    # for key in Curl_Test_Data :
    #     # if key != "Curl_Test_Comm_Result" :
    #         print(key)
    #         print(Curl_Test_Data[key])
            # print(SORT_LIST(Curl_Test_Data[key]))
    # Get_Log_Infor = GET_NODE_LOG_ERROR_AND_BUG_INFOR(List)      
    # for key in Get_Log_Infor :
    #     for Comm_Data in Get_Log_Infor[key] :
    #         print(f"{key}--{Comm_Data['Node']}--{Comm_Data['Common_Result_Data']}")      