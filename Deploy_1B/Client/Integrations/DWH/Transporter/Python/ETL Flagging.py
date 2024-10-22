import pyodbc
import ParametersReader
import base64

DB = ParametersReader.get_params("DBParam")

paswrd = base64.b64decode(DB['PWD']).decode("utf-8")

ael_variables = []


def ael_main(params): 
    conn = 'DRIVER='+DB['DRIVER'] + ';SERVER='+DB['SERVER'] + ';DATABASE='+DB['DATABASE'] + ';UID='+DB['UID']  +';PWD='+ paswrd
    cnxn = pyodbc.connect(conn)
    cursor = cnxn.cursor()
    query = """SET NOCOUNT ON; EXEC SP_FLAGGINGETL """
    cursor.execute(query)
    cursor.commit()





