"""-------------------------------------------------------------------
MODULE
    FDLCreateComponent - DataPrep script

DESCRIPTION
    Data preparation script to create required setup for DataLoader

--------------------------------------------------------------------"""

import acm

def CreateComponent(compName):
    try:
        component = acm.FComponent.Select01(f'compName={compName}', None)
        if not component:
            component = acm.FComponent()
            component.CompName(compName)
            component.RecordType('Component')
            component.Type('Application')
            component.Commit()
    except Exception as e:
        print("Error while creating component DataLoader : ", str(e))

def AddComponentToProfile(compName, profileName):
    component = acm.FComponent.Select01(f'compName={compName}', None)
    userprofile = acm.FUserProfile[profileName]
    
    if component and userprofile:
        try:
            prfcomponent = acm.FProfileComponent.Select01(f'userProfile={userprofile.Oid()} and component={component.Oid()}', None)
            if not prfcomponent:
                prfcomponent = acm.FProfileComponent()
                prfcomponent.Component(component)
                prfcomponent.UserProfile(userprofile)
                prfcomponent.Commit()
        except Exception as e:
            print("Error while adding component DataLoader in user profile : ", str(e))
			
CreateComponent('DataLoader')
AddComponentToProfile('DataLoader', 'ALL_COMPONENTS')
