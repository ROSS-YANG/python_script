import requests
import json

def Post_Request(IP,url,Post_Data) :
    url = url
    dic = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection" : "keep-alive",
        "Content-Type": "application/json",
        "Host": f"{IP}:3000",
        "Origin": f"http://{IP}:3000",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    }

    try :
        Resp = requests.post(url,data=Post_Data,headers=dic,timeout=6)
        Resp_data = Resp.json()
        Resp.close()
        return Resp_data
    except Exception as Post_ERROR :
        print(Post_ERROR)
def GET_DISCOVER_INFOR(IP) :
    url = f'http://{IP}:3000/ptp/discover'
    Data = Post_Request(IP,url,'')
    return Data
def GET_PRB_INFOR(IP) :
    Data = GET_DISCOVER_INFOR(IP)
    PRB_IP_Infor = {}
    for i in Data['lifecycleManagers'] :
        belong_to_IP = i['remoteAddr'].split('/')[2]
        PRB_IP_Infor[belong_to_IP] = i['peerId']
    return PRB_IP_Infor
def GET_WORKER_INFOR(IP) :
    print(IP)
    
    PRB_IP_Infor = GET_PRB_INFOR(IP)
    PRB_Worker_Data = {}
    for key in PRB_IP_Infor :
        try :
            # print(IP)
            url = f'http://{IP}:3000/ptp/proxy/{PRB_IP_Infor[key]}/GetWorkerStatus'
            print(f'api_collect("{url}");')
            Worker_Status_Infor = Post_Request(IP,url,'')["data"]["workerStates"]
            PRB_Worker_Data[key] = Worker_Status_Infor
        except Exception as ERR:
            print(ERR)
    return PRB_Worker_Data
def RESTART_WORKER(IP,UUID_And_Belong_To_IP_Data) :
    """
    UUID_And_Belong_To_IP_Data = {"127.0.0.1":[UUID1,UUID2]}
    """
    # print(UUID_And_Belong_To_IP_Data)
    import Node_Test_Main
    BJ_TIME = Node_Test_Main.GET_BJ_TIME()
    PRB_IP_Infor = GET_PRB_INFOR(IP)
    for key in UUID_And_Belong_To_IP_Data :
        try :
            url = f"http://{IP}:3000/ptp/proxy/{PRB_IP_Infor[key]}/RestartWorker"
            Post_Data = {"ids":UUID_And_Belong_To_IP_Data[key]}
            Data = Post_Request(IP,url,json.dumps(Post_Data))
            print(BJ_TIME,key,"成功restart",len(Data["data"]["workerStates"]),"条数据")
        except Exception as Restart_Worker_ERR:
            print(Restart_Worker_ERR)
            return Restart_Worker_ERR
def GET_POOL_LIST(IP) :
    PRB_IP_Infor = GET_PRB_INFOR(IP)
    Pool_List_Dic = {}
    Pool_List_Data = []
    for key in PRB_IP_Infor :
        try :
            url = f"http://{IP}:3000/ptp/proxy/{PRB_IP_Infor[key]}/ListPool"
            Data = Post_Request(IP,url,"")
            Pool_List_Dic[key] = Data["data"]["pools"]
            Pool_List_Data += Data["data"]["pools"]
        except Exception as Get_Pool_List_ERR :
            print("Get_Pool_List_ERR:",Get_Pool_List_ERR)
    return Pool_List_Data
if __name__ == '__main__' :
    IP = ''
    IP = '10.87.0.52'

    GET_WORKER_INFOR(IP)
    # Data = GET_PRB_INFOR("10.101.87.52")
    # print(Data)
    # Data = GET_POOL_LIST("10.101.87.52")
    # import pandas as pd 
    # df = pd.DataFrame(Data)
    # df.to_excel("pool_list.xlsx")
    # print(Data)