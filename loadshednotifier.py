from datetime import datetime

import time

from win11toast import toast

import requests

import configparser

CONFIG_FILE_PATH = "C:\\Users\\colem\\lsconfig\\config.ini"

config = configparser.ConfigParser()

config.read(CONFIG_FILE_PATH)


KEY = config['API']['api_key']
AREA_ID = config['API']['area_id']
header = {"token": KEY}



def allowance_request():
    """requests allowance balance"""

    api_url = "https://developer.sepush.co.za/business/2.0/api_allowance"
    response = requests.get(api_url, headers=header, timeout=10)
    if response.status_code==200:
        return response
    else:
        return "failed"


def schedule_request():
    """requests schedule"""

    api_url = f"https://developer.sepush.co.za/business/2.0/area?id={AREA_ID}"
    response = requests.get(api_url, headers=header, timeout=10)
    if response.status_code==200:
        return response
    else:
        return "failed"

def allowance_reached():
    """Check if API limit reached (doesn't count towards limit)"""

    req = allowance_request()
    if req!="failed":
        limit = req.json()["allowance"]["count"]
    
        return limit>50
    else:
        return "failed" 


def get_schedule():
    """Gets current schedule (add &test=current at end when making changes doesn't add to api calls)"""
 
    req = schedule_request()
    if req!="failed":
        events = req.json()["events"]
        return events
    else:
        return "failed" 


def get_loadshedtime(sched):
    """Gets next load shed time"""
    return sched[0]["start"][11:16]



def loadshed_today(sched):
    """Check if loadshedding today"""


    loadshedyear = sched[0]["start"][0:4]
    current_year = str(datetime.now())[0:4]

    loadshedmonth = sched[0]["start"][5:7]
    current_month = str(datetime.now())[5:7]


    loadshedday = sched[0]["start"][8:10]
    current_day = str(datetime.now())[8:10]

    if (loadshedyear==current_year and loadshedmonth==current_month and loadshedday == current_day):
        return True


    return False



def time_difference_in_minutes(loadshedtime):
    """Check time difference between now and loadshed time"""


    current_time = str(datetime.now())[11:16]
    

    start = datetime.strptime(current_time, "%H:%M") 
    end = datetime.strptime(loadshedtime, "%H:%M") 
    
    difference = end - start


    seconds = difference.total_seconds() 
    
    minutes = seconds / 60
    return minutes





def send_notification(instruction):

    """sends toast notification to user"""

    if (instruction=="limit"):
        toast("daily limit reached. No more loadshed updates today")
    
    if (instruction=="55"):
        toast("Loadshed in 55 mins")
    
    if(instruction=="15"):
        toast("Loadshed in 15 mins") 
    



def main():
    """main method"""


    allowance = allowance_reached()
    schedule = get_schedule()

    if (allowance=="failed" or schedule=="failed"):
        return

    if(allowance):
        send_notification("limit")

    else:
        sched = schedule

        while(True):

            #Gets update on schedule at specified times
            current_time = str(datetime.now())[11:16]
            if(current_time=="00:00" or current_time=="05:00" or current_time=="12:00" or current_time=="16:00" or current_time=="20:00"):
                sched = get_schedule()

            #If theres loadshedding today, checks how long till loadshedding and lets user know via toast
            if(loadshed_today(sched)):
                ls_time = get_loadshedtime(sched)
                difference = time_difference_in_minutes(ls_time)
                if(difference==55):
                    send_notification("55")
                elif(difference==15):
                    send_notification("15")
            
            #Gives CPU a break
            time.sleep(60)




if __name__ == "__main__":
    main()



# # # Schedule the notification at a specific time (adjust the time as needed)
# schedule.every().hours.at(":05").do(main)
# schedule.every().hours.at(":45").do(main)


# # # loop in the background
# while True:
#     schedule.run_pending()
#     time.sleep(1)  