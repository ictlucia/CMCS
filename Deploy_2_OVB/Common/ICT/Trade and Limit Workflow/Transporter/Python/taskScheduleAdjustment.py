import acm

def getLastBusinessDay(today, countryLoc):
    jakarta = acm.FCalendar[countryLoc]
    lastDate = acm.Time().LastDayOfMonth(today)
    lastDateAdj = acm.Time.DateAdjustPeriod(acm.Time().DateAddDelta(lastDate, 0, 0, 1), '-1d', jakarta, 2)
    dayLast =  acm.Time().DateToYMD(lastDateAdj)[2]
    return dayLast
    
def scheduleAdjustment(groupName, dayUse):
    taskGroup = acm.FAelTaskGroup[groupName]

    for task in taskGroup.Tasks().Filter(lambda x : "BO" in str(x.Name())):
        for schedule in task.Schedules():
            if str(schedule.Period()) == "Month":
                schedule.MonthOptionDayNumber(dayUse)
                schedule.Commit()


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Task Schedule Adjustment'}
ael_variables=[
    ["countryLoc", "Country Location", "string", ["Jakarta", "Singapore", "Hong Kong", "New York", "Tokyo"], "Jakarta", 1, 0]
]

def ael_main(parameter):
    countryLoc = str(parameter["countryLoc"])
    
    todayDate = acm.Time().DateToday()
    lastDay = getLastBusinessDay(todayDate, countryLoc)
    
    groupNames = ["REPORTING_BO"]
    for groupName in groupNames :
        scheduleAdjustment(groupName, lastDay)
