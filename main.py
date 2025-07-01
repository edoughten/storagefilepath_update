import pyodbc
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def get_sql_connection():
    driver = os.getenv('DRIVER')
    csdigital_server = os.getenv('CSDIGITAL_SERVER')
    csdigital_database = os.getenv('CSDIGITAL_DATABASE')
    csdigital_uid = os.getenv('CSDIGITAL_UID')
    csdigital_pwd = os.getenv('CSDIGITAL_PWD')
    connection_string = f"Driver={driver};Server={csdigital_server};Database={csdigital_database};UID={csdigital_uid};PWD={csdigital_pwd};"
    return pyodbc.connect(connection_string)



def get_dataframe_from_sql(batch_size):
    connection = get_sql_connection()
    query = """

select top {batch_size} lower(CountyName) as CountyName, lower(StateAbbreviation) as StateAbbreviation, _CreatedDateTime, 
    r.sourceFilePath, r.storageFilePath, r.imageFileExists, r.recordID,
    '\\smb.dc2isilon.na.drillinginfo.com\county_scans_beta\cs_digital\' as base_path, left(r.recordID,4) as sub_directory
    from tblrecord r
    	left join tbllookupCounties c on c.countyID = r.countyID
    	left join tbllookupStates s on s.StateID = r.stateID
        left join dbo.temp_storagefilepath_null_updates n on r.recordID = n.recordID
    where sourceFilePath <> 'diml' and  isnull(r.storageFilePath,'') = '' and n.recordID is null"""
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def update_dataframe_with_storage_path(df):
    local_path = '/mnt/county_scans_beta/cs_digital/'

    df['storageFilePath'] = df.apply(
        lambda row: '\\' +row['base_path'] + '\\' +  row['StateAbbreviation'] + '\\' + row['CountyName'] + '\\' + row[
            'sub_directory'] + '\\' + row['recordID'] + '.pdf'
        if os.path.exists(os.path.join(local_path, row['StateAbbreviation'], row['CountyName'], row['sub_directory'],
                                       row['recordID'] + '.pdf'))
        else None,
        axis=1
    )
    df['imageFileExists'] = df['storageFilePath'].apply(lambda x: pd.notnull(x))
    return df

def save_dataframe_to_sql(df):
    connection = get_sql_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            IF OBJECT_ID('tempdb..#temp_storagefilepath') IS NOT NULL DROP TABLE #temp_storagefilepath;
    CREATE TABLE #temp_storagefilepath (
        recordID NVARCHAR(255),
        storageFilePath NVARCHAR(1024),
        imageFileExists BIT);
        """)
        # Bulk insert DataFrame rows
        rows = df[df['storageFilePath'].notnull()][['recordID', 'storageFilePath', 'imageFileExists']].values.tolist()
        no_update_rows = df[df['storageFilePath'].isnull()][['recordID', 'storageFilePath', 'imageFileExists']].values.tolist()
        cursor.fast_executemany = True
        cursor.executemany("""INSERT INTO #temp_storagefilepath (recordID, storageFilePath, imageFileExists)
                              VALUES (?, ?, ?)  """, rows)
        cursor.executemany("""INSERT INTO temp_storagefilepath_null_updates (recordID, storageFilePath, imageFileExists)
                              VALUES (?, ?, ?)  """, no_update_rows)
        # Run batch update
        cursor.execute("""
            UPDATE r
            SET r.storageFilePath = t.storageFilePath,
                r.imageFileExists = t.imageFileExists
            FROM tblrecord r
            INNER JOIN #temp_storagefilepath t ON r.recordID = t.recordID """)
        connection.commit()
    except:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

def process_records(batch_size):
    df = get_dataframe_from_sql(batch_size)
    df = update_dataframe_with_storage_path(df)
    save_dataframe_to_sql(df)


if __name__ == "__main__":
    batch_size = 1000000
    start_time = pd.Timestamp.now()
    print(f"Process started at {start_time}, processing batch size: {batch_size}")

    process_records(batch_size)
    end_time = pd.Timestamp.now()
    print(f"Process completed at {end_time}, duration: {end_time - start_time}")