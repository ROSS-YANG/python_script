import time
import datetime
from turtle import st
class AboutTime :
    def __init__(self) -> None:
        pass
    def get_beijing_time(self) :
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
    def utc08float_to_beijing_time(self,utc = "2022-04-13T08:52:30.000Z") :
        """
        将这种utc = "2022-04-13T08:52:30.000Z"转换为BJ_TIME
        """
        import datetime
        UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
        utc_time = datetime.datetime.strptime(utc, UTC_FORMAT)
        local_time = utc_time + datetime.timedelta(hours=8)
        return local_time 
    def delta_date(self,start_date='',delta_date_rangs=0) :
        """
        example:
        start_date = "2022-01-01
        delta_date_rangs=1
        return : ["2022-01-02"]
        """
        date_list = []
        if start_date == '' :
            start_date = self.get_beijing_time().split("_")
            start_date = start_date[0]
        start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
        if delta_date_rangs > 0 :
            for i in range(1,delta_date_rangs+1) :
                time_infor = start_date + datetime.timedelta(i)
                date_list.append(str(time_infor).split(" ")[0])
        elif delta_date_rangs<0 :
            for i in range(-1,delta_date_rangs-1,-1) :
                time_infor = start_date + datetime.timedelta(i)
                date_list.append(str(time_infor).split(" ")[0])
        return date_list
if __name__ == '__main__' :

    AboutTime().delta_date('2022-01-01',-5)
        