import acm

def getLastBusinessDay(today):
    jakarta = acm.FCalendar['Jakarta']
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
ael_variables=[]

def ael_main(parameter):
    todayDate = acm.Time().DateToday()
    lastDay = getLastBusinessDay(todayDate)
    
    groupNames = ["BO_REPORTING", "BO_PYTHON_REPORTING"]
    for groupName in groupNames :
        scheduleAdjustment(groupName, lastDay)
