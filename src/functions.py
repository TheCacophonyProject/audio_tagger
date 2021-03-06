

# import main.parameters as parameters
import src.parameters as parameters
from src.parameters import cacophony_user_name
import scipy
import sqlite3
from sqlite3 import Error
import requests
import json


import os.path

import numpy as np
from scipy.signal import butter, lfilter

import matplotlib.pyplot as plt
# import librosa.display
import matplotlib.colors as mcolors
import soundfile as sf
from subprocess import PIPE, run
from librosa import onset
import librosa.display
from PIL import ImageTk,Image 

import datetime
from pytz import timezone
import sys
from tkinter import filedialog

import warnings

from matplotlib.pyplot import specgram

from scipy import signal

from scipy.fft import fftshift


conn = None

def get_database_connection():
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """

    # https://stackoverflow.com/questions/8587610/unboundlocalerror-local-variable-conn-referenced-before-assignment
    global conn
    if conn is None:
        try:
            conn = sqlite3.connect(parameters.db_file)           
        except Error as e:
            print(e)
  
    return conn       
    

def get_tags_from_server(device_id):
    print('about to get tags from server for device ', device_id)
    

def get_recordings_from_server(device_name, device_super_name):
    if not device_name:
        print('Device name can NOT be null')
        return
    
    if not device_super_name:
        print('Device Super name can NOT be null')
        return    
        
    print('About to get recordings from server')
    retrieve_available_recordings_from_server(device_name, device_super_name)
    
def get_recordings_from_server_for_all_devices():
    sql = '''select distinct device_name, device_super_name from recordings'''
    cur = get_database_connection().cursor()  
    cur.execute(sql) 
    rows = cur.fetchall() 
    for row in rows:
        device_name = row[0]
        device_super_name = row[1]
        retrieve_available_recordings_from_server(device_name, device_super_name)
          
def retrieve_missing_recording_information():
    sql = ''' SELECT recording_id from recordings where recordingDateTime IS NULL '''
    cur = get_database_connection().cursor()  
   
    cur.execute(sql) 
    
    rows = cur.fetchall() 
    numberOfRows = len(rows)
    count = 0
    for row in rows:
        recording_id =  row[0]
        print("Processing ", count, " of ", numberOfRows)
        print("About to get recording information for ", recording_id)
        update_recording_information_for_single_recording(recording_id)
        count += 1
        
        
        
    
def get_latest_recording_id_from_local_db(device_name, device_super_name):
    # Need the last recording ID for this device, that we already have   

#     https://docs.python.org/2/library/sqlite3.html
    sql = ''' SELECT audio_file_id FROM audio_files WHERE device_super_name = ? ORDER BY audio_file_id DESC LIMIT 1'''
    cur = get_database_connection().cursor()  
   
    cur.execute(sql,(device_super_name,))   
 
    rows = cur.fetchall() 
    for row in rows:
        return row[0]
    
def retrieve_available_recordings_from_server(device_name, device_super_name):      

    recordings_folder = parameters.downloaded_recordings_folder     

    ids_of_recordings_to_download = get_recording_ids_for_device_name(device_name)
    
    # remove ids of recordings that we already have
    already_downloaded = []
    for file in os.listdir(recordings_folder):
        already_downloaded.append(os.path.splitext(file)[0])
       
    already_downloaded_set = set(already_downloaded)  
        
    ids_of_recordings_to_still_to_download = []
    
    for recording_id in ids_of_recordings_to_download:
        if not recording_id in already_downloaded_set:
            ids_of_recordings_to_still_to_download.append(recording_id)
        else:
            print('Already have recording ',recording_id, ' so will not download')
            # but still check to see if it is in database (some aren't if the database was locked)
            try: 
                cur = get_database_connection().cursor()
                cur.execute("SELECT ID FROM recordings WHERE recording_id = ?", (recording_id, ))
                records = cur.fetchone()             # https://stackoverflow.com/questions/2440147/how-to-check-the-existence-of-a-row-in-sqlite-with-python
                
                if records is None:
                    insert_recording_into_database(recording_id,recording_id + '.m4a' ,device_name,device_super_name)
                    # Also get recording information from server
                    update_recording_information_for_single_recording(recording_id)
                                
            except Exception as e:
                print(e, '\n')
            
       
    for recording_id in ids_of_recordings_to_still_to_download:
#         print('About to get token for downloading ',recording_id)
        token_for_retrieving_recording = get_token_for_retrieving_recording(recording_id)
        print('About to get recording ',recording_id)
        get_recording_from_server(token_for_retrieving_recording, recording_id, device_name, device_super_name)
        
        # Also get recording information from server
        update_recording_information_for_single_recording(recording_id)
     
    print('Finished retrieving recordings')  
 
        
def get_recording_from_server(token_for_retrieving_recording, recording_id, device_name, device_super_name):
    try:
      
        recording_local_filename = parameters.downloaded_recordings_folder + '/' + recording_id + '.m4a'
        
        recording_local_filename = parameters.downloaded_recordings_folder + '/' + recording_id + '.m4a'
            
        # Don't download it if we already have it.       
       
        if not os.path.exists(recording_local_filename):
            url = parameters.server_endpoint + parameters.get_a_recording
            querystring = {"jwt":token_for_retrieving_recording}     
           
            resp_for_getting_a_recording = requests.request("GET", url, params=querystring)
           
            if resp_for_getting_a_recording.status_code != 200:
                # This means something went wrong.
                print('Error from server is: ', resp_for_getting_a_recording.text)
                return               
             
            with open(recording_local_filename, 'wb') as f:  
                f.write(resp_for_getting_a_recording.content)
                
            # Update local database
            insert_recording_into_database(recording_id,recording_id + '.m4a' ,device_name,device_super_name)
            
        else:
            print('\t\tAlready have recording ', str(recording_id) , ' - so will not download again\n')
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to download recording ' + str(recording_id), '\n')
        
def get_token_for_retrieving_recording(recording_id):
    user_token = get_cacophony_user_token()

    get_a_token_for_recording_endpoint = parameters.server_endpoint + parameters.get_a_token_for_getting_a_recording_url + recording_id

    headers = {'Authorization': user_token}

    resp_for_getting_a_recordingToken = requests.request("GET", get_a_token_for_recording_endpoint, headers=headers)
    if resp_for_getting_a_recordingToken.status_code != 200:
        sys.exit('Could not get download token - exiting')
    recording_data = resp_for_getting_a_recordingToken.json()
    recording_download_token = recording_data['downloadFileJWT']
    
    return recording_download_token
    
def get_recording_ids_for_device_name(device_name): 
    
    # Get the highest recording id for this device that has already been downloaded
    cur = get_database_connection().cursor()   
    cur.execute("SELECT MAX(recording_id) FROM recordings WHERE device_name = ?", (device_name,))
    rows = cur.fetchall() 
    current_max_recording_id_for_this_device = rows[0][0]
    if current_max_recording_id_for_this_device is None:
        current_max_recording_id_for_this_device = 0
    current_max_recording_id_for_this_device = 0
        
    print('device_name ', device_name)
    print('max_recording_id ', current_max_recording_id_for_this_device)
    
    device_id = get_device_id_using_device_name(device_name)
    print('device_id is ', device_id)
    ids_recordings_for_device_name = []
    offset = 0
    while True:
        ids_of_recordings_to_download= get_ids_of_recordings_to_download_using_deviceId(device_id,offset, current_max_recording_id_for_this_device)
        print('ids_of_recordings_to_download ', ids_of_recordings_to_download)
        ids_recordings_for_device_name += ids_of_recordings_to_download
        
        # Check to see if the list from the server contains the previous max recording_id.  If it does, then don't get anymore ids
        
        if (len(ids_of_recordings_to_download) > 0):
            offset+=300
        else:
            break
    return ids_recordings_for_device_name

def get_ids_of_recordings_to_download_using_deviceId(deviceId, offset, current_max_recording_id):
    # This will get a list of the recording ids for every recording of length 59,60,61,62 from device_name
    user_token = get_cacophony_user_token()
   
    url = parameters.server_endpoint + parameters.query_available_recordings
    
    where_param = {}
    where_param['DeviceId'] = deviceId
    where_param['duration'] = 59,60,61,62
    
    grt_id_param = {}
    grt_id_param['$gt'] = current_max_recording_id
    where_param['id'] = grt_id_param
    
    json_where_param = json.dumps(where_param) 

    querystring = {"offset":offset, "where":json_where_param}    
    
    headers = {'Authorization': user_token}  

    resp = requests.request("GET", url, headers=headers, params=querystring)
   
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error from server is: ', resp.text)
        sys.exit('Could not download file - exiting')            
    
    data = resp.json() 
    
    recordings = data['rows'] 
    
    print('Number of recordings is ', len(recordings))

    ids_of_recordings_to_download = []    
    for recording in recordings:        
        recording_id = str(recording['id'])
        ids_of_recordings_to_download.append(recording_id)
        
    return ids_of_recordings_to_download    

def get_device_id_using_device_name(device_name):
    user_token = get_cacophony_user_token()
    url = parameters.server_endpoint + parameters.devices_endpoint
      
    headers = {'Authorization': user_token}  

    resp = requests.request("GET", url, headers=headers)
   
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error from server is: ', resp.text)
        sys.exit('Could not download file - exiting')
    
    data = resp.json()

    devices = data['devices'] 
    rows = devices['rows']
    for row in rows:
        devicename = row['devicename']        
        if devicename == device_name:
                device_id = row['id']
                return device_id     
            
def get_cacophony_user_token():
    parameters.cacophony_user_token
    parameters.cacophony_user_name
    parameters.cacophony_user_password 
    if parameters.cacophony_user_token:
        return parameters.cacophony_user_token
    
    print('About to get user_token from server')
    username = parameters.cacophony_user_name
    if parameters.cacophony_user_password == '':
        parameters.cacophony_user_password = input("Enter password for Cacophony user " + username + " (or change cacophony_user_name in parameters file): ")
           
    requestBody = {"nameOrEmail": username, "password": parameters.cacophony_user_password }
    login_endpoint = parameters.server_endpoint + parameters.login_user_url
    resp = requests.post(login_endpoint, data=requestBody)
    if resp.status_code != 200:
        # This means something went wrong.
        sys.exit('Could not connect to Cacophony Server - exiting')
    
    data = resp.json()
    parameters.cacophony_user_token = data['token']
    return parameters.cacophony_user_token
    
def load_recordings_from_local_folder(device_name, device_super_name):
    
    input_folder = filedialog.askdirectory()    
    
    for filename in os.listdir( input_folder):
        recording_id = filename.replace('-','.').split('.')[0]
        filename2 = recording_id +'.m4a'

        insert_recording_into_database(recording_id,filename2,device_name,device_super_name)
        
        # Now move file to recordings folder
        audio_in_path = input_folder + '/' + filename       
        audio_out_path = parameters.downloaded_recordings_folder + '/' + filename2
        
        print('Moving ', filename, ' to ', audio_out_path)
        os.rename(audio_in_path, audio_out_path)

        # Now need to get information about this recording from server
        update_recording_information_for_single_recording(recording_id)
        
def insert_recording_into_database(recording_id,filename,device_name,device_super_name):
    try:
        sql = ''' INSERT INTO recordings(recording_id,filename,device_name,device_super_name)
                  VALUES(?,?,?,?) '''
        cur = get_database_connection().cursor()
        cur.execute(sql, (recording_id,filename,device_name,device_super_name))
       
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert recording ' + str(recording_id), '\n')
        

def update_recordings_folder(recordings_folder):
    print("new_recording_folder ", recordings_folder)
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param recordings_folder:
    :return: project id
    """
    sql = ''' UPDATE settings
              SET downloaded_recordings_folder = ?               
              WHERE ID = 1'''
    cur = get_database_connection().cursor()
    cur.execute(sql, (recordings_folder,))
    get_database_connection().commit()      
        
    
def getRecordingsFolderWithOutHome():
    cur = get_database_connection().cursor()
    cur.execute("select * from settings")
 
    rows = cur.fetchall()   
 
    for row in rows:     
        return row[0]     
        
def update_recording_information_for_single_recording(recording_id):
    print('About to update recording information for recording ', recording_id)    
    recording_information = get_recording_information_for_a_single_recording(recording_id)
    print('recording_information ', recording_information)    
    if recording_information == None:        
        print('recording_information == None')     
        return
         
    recording = recording_information['recording']    
    recordingDateTime = recording['recordingDateTime']    
    recordingDateTimeNZ = convert_time_zones(recordingDateTime)
    relativeToDawn = recording['relativeToDawn']    
    relativeToDusk = recording['relativeToDusk']    
    duration = recording['duration'] 
       
    location = recording['location']        
    coordinates = location['coordinates']    
    locationLat = coordinates[0]    
    locationLong = coordinates[1]  
       
    version = recording['version']    
    batteryLevel = recording['batteryLevel']    
    
    additionalMetadata = recording['additionalMetadata']    
    phoneModel = additionalMetadata['Phone model']    
    androidApiLevel = additionalMetadata['Android API Level']  
    
    Device = recording['Device']    
    deviceId = Device['id']
    device_name = Device['devicename']
         
    nightRecording =  'false'
    
    if relativeToDusk is not None:
        if relativeToDusk > 0:
            nightRecording = 'true' 
    elif relativeToDawn is not None:
        if relativeToDawn < 0:
            nightRecording = 'true'   
                   
#     update_recording_in_database(recordingDateTime, relativeToDawn, relativeToDusk, duration, locationLat, locationLong, version, batteryLevel, phoneModel, androidApiLevel, deviceId, nightRecording, device_name, recording_id, recordingDateTimeNZ)
    # determine original recording sample rate
    sample_rate = get_original_recording_sample_rate(recording_id)
    
    
    update_recording_in_database(recordingDateTime, relativeToDawn, relativeToDusk, duration, locationLat, locationLong, version, batteryLevel, phoneModel, androidApiLevel, deviceId, nightRecording, device_name, recording_id, recordingDateTimeNZ, sample_rate)
    print('Finished updating recording information for recording ', recording_id)
               
  
def update_recording_in_database(recordingDateTime, relativeToDawn, relativeToDusk, duration, locationLat, locationLong, version, batteryLevel, phoneModel,androidApiLevel, deviceId, nightRecording, device_name, recording_id, recordingDateTimeNZ, sample_rate):
    try:
#         conn = get_database_connection()
        # https://www.sqlitetutorial.net/sqlite-python/update/
        sql = ''' UPDATE recordings 
                  SET recordingDateTime = ?,
                      relativeToDawn = ?,
                      relativeToDusk = ?,
                      duration = ?,
                      locationLat = ?,
                      locationLong = ?,
                      version = ?,
                      batteryLevel = ?,
                      phoneModel = ?,
                      androidApiLevel = ?,
                      deviceId = ?,
                      nightRecording = ?,
                      device_name = ?,
                      recordingDateTimeNZ = ?,
                      sample_rate = sample_rate
                  WHERE recording_id = ? '''
        cur = get_database_connection().cursor()
        cur.execute(sql, (recordingDateTime, relativeToDawn, relativeToDusk, duration, locationLat, locationLong, version, batteryLevel, phoneModel, androidApiLevel, deviceId, nightRecording, device_name, recordingDateTimeNZ, recording_id, sample_rate))
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert recording ' + str(recording_id), '\n')
        
   
    
def get_recording_information_for_a_single_recording(recording_id):
    user_token = get_cacophony_user_token()

    get_a_token_for_recording_endpoint = parameters.server_endpoint + parameters.get_information_on_single_recording + recording_id

    headers = {'Authorization': user_token}

    resp_for_getting_a_recordingToken = requests.request("GET", get_a_token_for_recording_endpoint, headers=headers)
    if resp_for_getting_a_recordingToken.status_code != 200:
        print('Could not get download token')
        return None
    recording_data_for_single_recording = resp_for_getting_a_recordingToken.json()      
    
    return recording_data_for_single_recording     



def update_recording_information_for_all_local_database_recordings():
    cur = get_database_connection().cursor()
    cur.execute("SELECT recording_id, recordingDateTime FROM recordings")
 
    rows = cur.fetchall()
 
    for row in rows:
        # Don't update if we already have recordingDateTime
        recordingDateTime = row[1]
        if not recordingDateTime:
            print(recordingDateTime, ' is empty so will update record')
            recording_id = row[0]
            update_recording_information_for_single_recording(recording_id)
        print('Finished updating recording information')
    


def get_audio_recordings_with_tags_information_from_server(user_token, recording_type, deviceId):
    print('Retrieving recordings basic information from Cacophony Server\n')
    url = parameters.server_endpoint + parameters.query_available_recordings
    
    where_param = {}
    where_param['type'] = recording_type    
    where_param['DeviceId'] = deviceId
    json_where_param = json.dumps(where_param)
    querystring = {"tagMode":"tagged", "where":json_where_param}    
    headers = {'Authorization': user_token}  

    resp = requests.request("GET", url, headers=headers, params=querystring)
   
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error from server is: ', resp.text)
        sys.exit('Could not download file - exiting')    
        
    
    data = resp.json()
   
    recordings = data['rows']
    
    return recordings   



def get_and_store_tag_information_for_recording(recording_id, deviceId, device_name, device_super_name):
    single_recording_full_information = get_recording_information_for_a_single_recording(recording_id)
    recording = single_recording_full_information['recording']  
    tags = recording['Tags']   
    for tag in tags:
        server_Id = tag['id']
        what = tag['what']
        detail = tag['detail']
        confidence = tag['confidence']
        startTime = tag['startTime']
        duration = tag['duration']
        automatic = tag['automatic']
        version = tag['version']
        createdAt = tag['createdAt']
        tagger =tag['tagger']        
        tagger_username = tagger['username']
        what = tag['what']
        insert_tag_into_database(recording_id,server_Id, what, detail, confidence, startTime, duration, automatic, version, createdAt, tagger_username, deviceId, device_name, device_super_name)
    
    

    
def insert_tag_into_database(recording_id,server_Id, what, detail, confidence, startTime, duration, automatic, version, createdAt, tagger_username, deviceId, device_name, device_super_name ):
    # Use this for tags that have been downloaded from the server
    try:
        if check_if_tag_alredy_in_database(server_Id) == True:
            print('tag exists')
            return
        else:
            print('going to insert tag')

        sql = ''' INSERT INTO tags(recording_id,server_Id, what, detail, confidence, startTime, duration, automatic, version, createdAt, tagger_username, deviceId, device_name, device_super_name)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = get_database_connection().cursor()
        cur.execute(sql, (recording_id,server_Id, what, detail, confidence, startTime, duration, automatic, version, createdAt, tagger_username, deviceId, device_name, device_super_name))
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert tag ' + str(recording_id), '\n')   
        
def insert_locally_created_tag_into_database(recording_id,what, detail, confidence, startTime, duration, createdAt, tagger_username, deviceId, device_name, device_super_name ):
    # Use this is the tag was created in this application, rather than being downloaded from the server - becuase some fields are missing e.g. server_Id
    try:        

        sql = ''' INSERT INTO tags(recording_id, what, detail, confidence, startTime, duration, createdAt, tagger_username, deviceId, device_name, device_super_name)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
        cur = get_database_connection().cursor()
        cur.execute(sql, (recording_id, what, detail, confidence, startTime, duration, createdAt, tagger_username, deviceId, device_name, device_super_name))
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert tag ' + str(recording_id), '\n')   
       

def check_if_tag_alredy_in_database(server_Id):
    cur = get_database_connection().cursor()
    cur.execute("SELECT server_Id FROM tags WHERE server_Id = ?", (server_Id,))
    data=cur.fetchone()
    if data is None:
        return False
    else:
        return True


 
def get_all_tags_for_all_devices_in_local_database():
    user_token = get_cacophony_user_token()
    unique_devices = get_unique_devices_stored_locally()

    for unique_device in unique_devices:  
        deviceId = unique_device[0]
        device_name = unique_device[1]
        device_super_name = unique_device[2]        
      
        recording_type = 'audio'
        recordings_with_tags = get_audio_recordings_with_tags_information_from_server(user_token, recording_type, deviceId)

        for recording_with_tag in recordings_with_tags:
            print('device is', deviceId, '\n') 
            recording_id =recording_with_tag['id']
            print('recording_id ', recording_id, '\n')
            get_and_store_tag_information_for_recording(str(recording_id), deviceId, device_name, device_super_name)
    print('Finished getting tags from server')
    
     
def get_unique_devices_stored_locally():
    cur = get_database_connection().cursor()
    cur.execute("SELECT DISTINCT deviceId, device_name, device_super_name FROM recordings") 
    rows = cur.fetchall()
    return rows   

def get_unique_recording_ids_that_have_been_tagged_with_this_tag_stored_locally(tag):
    print('tag', tag)
    cur = get_database_connection().cursor()
    cur.execute("SELECT DISTINCT recording_id FROM tags WHERE what = ?", (tag,)) 
    rows = cur.fetchall()
    return rows 

        
def get_onsets_stored_locally(onset_version):
    global version
    if onset_version:
        version_to_use = onset_version
    else:
        version_to_use = version
        
    cur = get_database_connection().cursor()
    cur.execute("SELECT version, recording_id, start_time_seconds, duration_seconds FROM onsets WHERE version = ? ORDER BY recording_id", (version_to_use)) 
    rows = cur.fetchall()
    return rows 


def get_onsets_stored_locally_for_recording_id(version_to_use, recording_id):
#     global version
    cur = get_database_connection().cursor()
    if version_to_use:
#         version_to_use = onset_version
        cur.execute("SELECT version, recording_id, start_time_seconds, duration_seconds FROM onsets WHERE version = ? AND recording_id = ? ORDER BY recording_id", (version_to_use, recording_id)) 
    else: 
        cur.execute("SELECT version, recording_id, start_time_seconds, duration_seconds FROM onsets WHERE recording_id = ? ORDER BY recording_id", (recording_id,))
    rows = cur.fetchall()
    return rows

def get_model_run_results(modelRunName, actualConfirmedFilter, predictedFilter, predicted_probability_filter, predicted_probability_filter_value_str, location_filter, actual_confirmed_other, predicted_other, used_to_create_model_filter, recording_id_filter_value):   
       
    if location_filter =='Not Used':
        location_filter ='not_used'
         
    sqlBuilding = "SELECT ID FROM model_run_result WHERE modelRunName = '" + modelRunName + "'"
    
    if actualConfirmedFilter !='not_used':
        sqlBuilding += " AND "
        if actualConfirmedFilter == "IS NULL":
            if actual_confirmed_other == 'off':
                sqlBuilding += "actual_confirmed IS NULL"
            else: # Everything other is checked
                sqlBuilding += "actual_confirmed IS NOT NULL"
        else:
            if actual_confirmed_other == 'off':
                sqlBuilding +=  "actual_confirmed = '" + actualConfirmedFilter + "'"
            else: # Everything other is checked
                sqlBuilding +=  "actual_confirmed <> '" + actualConfirmedFilter + "'"
                
            
    if predictedFilter !='not_used':
        sqlBuilding += " AND "
        if predictedFilter == "IS NULL":
            if predicted_other == 'off':
                sqlBuilding += "predictedByModel IS NULL"
            else:
                sqlBuilding += "predictedByModel IS NOT NULL"
        else:
            if predicted_other == 'off':
                sqlBuilding +=  "predictedByModel = '" + predictedFilter + "'"
            else:
                sqlBuilding +=  "predictedByModel <> '" + predictedFilter + "'"
            
    if location_filter !='not_used':
        sqlBuilding += " AND "
        sqlBuilding +=  "device_super_name = '" + location_filter + "'"
        
    if (predicted_probability_filter_value_str == '') or (predicted_probability_filter == 'not_used'):
        predicted_probability_filter = 'not_used'
    else:    
        if predicted_probability_filter == 'greater_than':  
            probabilty_comparator = '>'
#             predicted_probability_filter_value = float(predicted_probability_filter_value_str)    
        elif predicted_probability_filter == 'less_than': 
            probabilty_comparator = '<'
#             predicted_probability_filter_value = float(predicted_probability_filter_value_str)    
        sqlBuilding += " AND "
#         sqlBuilding += " probability " + probabilty_comparator + " '" + predicted_probability_filter_value + "'"
        sqlBuilding += " probability " + probabilty_comparator + " '" + predicted_probability_filter_value_str + "'"
        
    if used_to_create_model_filter != 'not_used':
        sqlBuilding += " AND "
        if used_to_create_model_filter == 'yes':
            sqlBuilding +=  "used_to_create_model = 1"
        else:
#             sqlBuilding +=  "used_to_create_model = 0"
            sqlBuilding +=  "used_to_create_model IS NULL"
            
    if recording_id_filter_value:
        sqlBuilding += " AND "        
        sqlBuilding +=  "recording_id = '" + recording_id_filter_value + "'"
        
        
    sqlBuilding += " ORDER BY recording_id DESC, startTime ASC"
        
    print("The sql is: ", sqlBuilding)
    cur = get_database_connection().cursor()
    cur.execute(sqlBuilding)
#     cur.execute("SELECT ID FROM model_run_result WHERE modelRunName = '2019_12_11_1' ORDER BY recording_id DESC, startTime ASC")
    rows = cur.fetchall()
    return rows



def get_model_run_result(database_ID):        
    cur = get_database_connection().cursor()
    cur.execute("SELECT ID, recording_id, startTime, duration, predictedByModel, actual_confirmed, probability, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ FROM model_run_result WHERE ID = ?", (database_ID,)) 
    rows = cur.fetchall()
    return rows[0] 

def get_single_training_data(database_ID):        
    cur = get_database_connection().cursor()
    cur.execute("SELECT ID, recording_id, start_time_seconds, duration_seconds, predicted_by_model, actual_confirmed, probability, device_super_name FROM training_data WHERE ID = ?", (database_ID,)) 
    rows = cur.fetchall()
    return rows[0] 
    
def scan_local_folder_for_recordings_not_in_local_db_and_update(device_name, device_super_name):
    
    for filename in os.listdir(parameters.downloaded_recordings_folder):
        recording_id = filename.replace('-','.').split('.')[0]
        print(recording_id)
        cur = get_database_connection().cursor()
        cur.execute("SELECT * FROM recordings WHERE recording_id = ?",(recording_id,))
        
        # https://stackoverflow.com/questions/16561362/python-how-to-check-if-a-result-set-is-empty
        row = cur.fetchone()
        if row == None:
            # Get the information for this recording from server and insert into local db   
            filename = recording_id + '.m4a'
            insert_recording_into_database(recording_id,filename, device_name,device_super_name) # The device name will be updated next when getting infor from server
            # Now update this recording with information from server
            update_recording_information_for_single_recording(recording_id)           


    
def update_local_tags_with_version():
    # This is probably only used the once to modify intial rows to indicate they are from my first morepork tagging of Hammond Park
    cur = get_database_connection().cursor()
    cur.execute("select ID from tags")
 
    rows = cur.fetchall()     
 
    for row in rows:              
        ID =  row[0] 
        print('ID ', ID) 
        sql = ''' UPDATE tags
                  SET version = ?               
                  WHERE ID = ?'''
        cur = get_database_connection().cursor()
        cur.execute(sql, ('morepork_base', ID))
    
    get_database_connection().commit()    
    
def update_model_run_result(ID, actual_confirmed):
    cur = get_database_connection().cursor()
    sql = ''' UPDATE model_run_result
              SET actual_confirmed = ?               
              WHERE ID = ?'''
    if (actual_confirmed == 'None') or (actual_confirmed == 'not_used'): # Must not put None into the db as the model breaks - instead convert to Null as descrived here - https://johnmludwig.blogspot.com/2018/01/null-vs-none-in-sqlite3-for-python.html
        cur.execute(sql, (None, ID))
    else:
        cur.execute(sql, (actual_confirmed, ID))
    
    get_database_connection().commit() 
    
    
def update_onset(recording_id, start_time_seconds, actual_confirmed):
    cur = get_database_connection().cursor()
    if (actual_confirmed == 'None') or (actual_confirmed == 'not_used'): # Must not put None into the db as the model breaks - instead convert to Null as descrived here - https://johnmludwig.blogspot.com/2018/01/null-vs-none-in-sqlite3-for-python.html
        cur.execute("UPDATE onsets SET actual_confirmed = ? WHERE recording_id = ? AND start_time_seconds = ?", (None, recording_id, start_time_seconds))   
    else:        
        cur.execute("UPDATE onsets SET actual_confirmed = ? WHERE recording_id = ? AND start_time_seconds = ?", (actual_confirmed, recording_id, start_time_seconds))  
        
    get_database_connection().commit()      

def update_training_data(model_run_name, recording_id, start_time_seconds, duration_seconds, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ, actual_confirmed):
        
    sql = ''' REPLACE INTO training_data (version, recording_id, start_time_seconds, duration_seconds, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ, actual_confirmed)
              VALUES(?,?,?,?,?,?,?,?,?) ''' 
    cur = get_database_connection().cursor()
    
    if (actual_confirmed == 'None') or (actual_confirmed == 'not_used'): # Must not put None into the db as the model breaks - instead convert to Null as descrived here - https://johnmludwig.blogspot.com/2018/01/null-vs-none-in-sqlite3-for-python.html
        cur.execute(sql, (model_run_name, recording_id, start_time_seconds, duration_seconds, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ, None)) 
    else:        
        cur.execute(sql, (model_run_name, recording_id, start_time_seconds, duration_seconds, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ, actual_confirmed))  
    
    get_database_connection().commit() 
    
      
def run_model(model_folder):
    # https://stackoverflow.com/questions/21406887/subprocess-changing-directory
    # https://stackoverflow.com/questions/1996518/retrieving-the-output-of-subprocess-call

    os.chdir(model_folder)  
    command = ['java', '--add-opens=java.base/java.lang=ALL-UNNAMED', '-jar', 'run.jar', 'shell=True']     
    
    result = run(command, stdout=PIPE, stderr=PIPE, text=True)   
    
    return result    

           
def get_recording_array(recording_id):
    recordings_folder_with_path = parameters.base_folder + '/' + parameters.downloaded_recordings_folder
    filename = str(recording_id) + ".m4a"
    audio_in_path = recordings_folder_with_path + "/" + filename
    y, sr = librosa.load(audio_in_path)    
    return y, sr

    
def insert_model_run_result_into_database(modelRunName, recording_id, startTime, duration, actual, predictedByModel, probability, actual_confirmed, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ):
       
    try:
        cur = get_database_connection().cursor()
        if actual_confirmed:
            sql = ''' INSERT INTO model_run_result(modelRunName, recording_id, startTime, duration, actual, predictedByModel, probability, actual_confirmed, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ)
                      VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
            cur.execute(sql, (modelRunName, recording_id, startTime, duration, actual, predictedByModel, probability, actual_confirmed, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ))
        else:
            sql = ''' INSERT INTO model_run_result(modelRunName, recording_id, startTime, duration, actual, predictedByModel, probability, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ)
                      VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
            cur.execute(sql, (modelRunName, recording_id, startTime, duration, actual, predictedByModel, probability, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ))
        
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert result' + str(recording_id) + ' ' + str(startTime), '\n')  
    
def play_clip(recording_id, start_time, duration, applyBandPassFilter, min_freq, max_freq):
       
    
    from pathlib import Path
    audio_in_path = parameters.downloaded_recordings_folder + '/' + recording_id + '.m4a'
    print('audio_in_path ', audio_in_path)
    print('start_time ', start_time)
    print('duration ', duration)
    audio_out_folder = parameters.base_folder + '/' + parameters.temp_folder
    Path(audio_out_folder).mkdir(parents=True, exist_ok=True)
#     audio_out_path = base_folder + '/' + temp_folder + '/' + 'temp.wav'
    audio_out_path = audio_out_folder + '/' + 'temp.wav'
    
    print('audio_out_path ', audio_out_path)
    
    y, sr = librosa.load(audio_in_path, sr=None) 
    if applyBandPassFilter:
#         y = apply_band_pass_filter(y, sr)
        y = butter_bandpass_filter(y, min_freq, max_freq, sr)    
    y_amplified = np.int16(y/np.max(np.abs(y)) * 32767)
    y_amplified_start = sr * start_time
    y_amplified_end = (sr * start_time) + (sr * duration)
    y_amplified_to_play = y_amplified[int(y_amplified_start):int(y_amplified_end)]

    sf.write(audio_out_path, y_amplified_to_play, sr)

    os.system("aplay " + audio_out_path + " &")
    
def stop_clip():
#     https://www.reddit.com/r/learnpython/comments/9rxxj0/python_how_do_i_stop_a_audio_file_from_playing/
    os.system("killall aplay")
 
    
def create_arff_file_headder(output_folder, arff_filename, comments, relation, attribute_labels, attribute_features): 
         
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  
        
    output_path_filename = output_folder + "/" + arff_filename
        
    f= open(output_path_filename,"w+")   
    f.write(comments)
    f.write("\n") 
    f.write(relation)
    f.write("\n") 
    f.write("\n") 
    for attribute_label in attribute_labels:
        f.write(attribute_label)
        f.write("\n")   
    for attribute_feature in attribute_features:
        f.write(attribute_feature)
        f.write("\n")   
        
    f.write("\n")    
    
    f.write("@data")  
    f.write("\n")  
    f.write("\n")  
        
    f.close()
  
        
def insert_onset_into_database(version, recording_id, start_time_seconds, duration_seconds):
    
    print('duration_seconds', duration_seconds)
    cur1 = get_database_connection().cursor()
    cur1.execute("SELECT device_super_name, device_name, recordingDateTime, recordingDateTimeNZ FROM recordings WHERE recording_id = ?", (recording_id,)) 
    rows = cur1.fetchall() 
    device_super_name = rows[0][0]  
    device_name = rows[0][1]
    recordingDateTime = rows[0][2]  
    recordingDateTimeNZ = rows[0][3] 
    
#     recordingDateTimeNZ = convert_time_zones(recordingDateTime)
    
    try:     
        sql = ''' INSERT INTO onsets(version, recording_id, start_time_seconds, duration_seconds, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ)
                  VALUES(?,?,?,?,?,?,?,?) '''
        cur2 = get_database_connection().cursor()
        cur2.execute(sql, (version, recording_id, start_time_seconds, duration_seconds, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ))
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert onest ' + str(recording_id), '\n')   
 
   
   
def create_onsets_in_local_db():
    
    cur = get_database_connection().cursor()  

    total_onset_pairs_including_more_than_40 = 0
    total_onset_pairs_including_not_including_more_40 = 0    
       
    # First need to find out what recordings have previously been used to create onsets - as we don't want to repeat
    cur.execute("SELECT recording_id, filename,  recordingDateTime FROM recordings WHERE processed_for_onsets IS NOT ? ORDER BY recording_id DESC", (parameters.onset_version,))
    recordings_with_no_onsets = cur.fetchall()
    print('There are ', len(recordings_with_no_onsets), ' recordings with no ', parameters.onset_version, ' onsets')     
    
    count = 0
    number_of_recordings_with_no_onsets = len(recordings_with_no_onsets)
    for recording_with_no_onsets in recordings_with_no_onsets: 
        try: 
            count += 1
            recording_id = recording_with_no_onsets[0]
            filename = recording_with_no_onsets[1]
           
            
            print('Processing ',count, ' of ', number_of_recordings_with_no_onsets)
            print('Recording id is ', recording_with_no_onsets) 
            count_of_onset_pairs_including_more_than_40, count_of_onset_pairs_including_not_including_more_40 = create_onsets_in_local_db_for_recording(filename)
            
            # Update recordings table to show that this recording has been processed for onsets
            cur.execute("UPDATE recordings SET processed_for_onsets = ? WHERE recording_id = ?", (parameters.onset_version, recording_id,))  
            get_database_connection().commit()
            
            total_onset_pairs_including_more_than_40 += count_of_onset_pairs_including_more_than_40
            total_onset_pairs_including_not_including_more_40 += count_of_onset_pairs_including_not_including_more_40
            print('total_onset_pairs_including_more_than_40:', total_onset_pairs_including_more_than_40)
            print('total_onset_pairs_including_not_including_more_40:', total_onset_pairs_including_not_including_more_40, '\n')
        except Exception as e:
#             print(e, '\n')
            print('Error processing file ', recording_id, '\n')
            cur.execute("UPDATE recordings SET processed_for_onsets = -1 WHERE recording_id = ?", (recording_id,))  
            get_database_connection().commit()    

     
def create_onsets_in_local_db_for_recording(filename): 
    try:

        recordings_folder_with_path = parameters.base_folder + '/' + parameters.downloaded_recordings_folder
        
        count_of_onset_pairs_including_more_than_40 = 0
        count_of_onset_pairs_including_not_including_more_40 = 0
        
        audio_in_path = recordings_folder_with_path + "/" + filename
        
        # Some recordings are not available
        if not os.path.isfile(audio_in_path):
            print("This recording is not available ", filename)
            # Update the db to say that it has been processed
   
        y, sr = librosa.load(audio_in_path)
        y_filtered = butter_bandpass_filter(y, 600, 1200, sr, order=6)    
        y_filtered_and_noise_reduced = noise_reduce(y_filtered, sr)
    
        onsets = find_squawk_location_secs_in_single_recording(y_filtered_and_noise_reduced,sr)          
    
        number_of_onsets = len(onsets)
        if not number_of_onsets == 0:
            if number_of_onsets > 40:
                count_of_onset_pairs_including_more_than_40 += number_of_onsets
            else:                
                
                count_of_onset_pairs_including_more_than_40 += number_of_onsets
                count_of_onset_pairs_including_not_including_more_40 += number_of_onsets                        
           
                recording_id = filename.split('.')[0]  
                insert_onset_list_into_db(recording_id, onsets)
                
        return count_of_onset_pairs_including_more_than_40, count_of_onset_pairs_including_not_including_more_40 

    except Exception:
        pass
                    
def insert_onset_list_into_db(recording_id, onsets):
    global squawk_duration_seconds
    prev_onset = -1
    for onset in onsets:
        if prev_onset == -1:
            print("onset " , onset)    
            insert_onset_into_database(parameters.onset_version, recording_id, onset, squawk_duration_seconds)
            prev_onset =  onset
        else:
            if (onset - prev_onset) < (squawk_duration_seconds + 0.1):
                print("Onset too close to previous, not inserting into database " , onset) 
            else:
                prev_onset = onset 
                insert_onset_into_database(parameters.onset_version, recording_id, onset, squawk_duration_seconds)
                print("Inserting onset into database " , onset)

def find_squawk_location_secs_in_single_recording(y, sr):

    squawks = FindSquawks(y, sr)
    squawks_secs = []

    for squawk in squawks:
        squawk_start = squawk['start']
        squawk_start_sec = squawk_start / sr
        squawks_secs.append(round(squawk_start_sec, 1))
        
    return squawks_secs



def FindSquawks(source, sampleRate):
    result = []
    source = source / max(source)
    startIndex = None
    stopIndex = None
    smallTime = int(sampleRate*0.1)
    tolerance = 0.2
    
    for index in range(source.shape[0]):
        if not startIndex:
            if abs(source[index]) > tolerance:
                startIndex = index
                stopIndex = index
            continue
        if abs(source[index]) > tolerance:
            stopIndex = index
        elif index > stopIndex+smallTime:
            duration = (stopIndex-startIndex)/sampleRate
            if duration > 0.05:
                squawk = {'start': startIndex,
                          'stop': stopIndex, 'duration': duration}
                squawk['rms'] = rms(source[startIndex:stopIndex])
                result.append(squawk)
            startIndex = None
    return result


def rms(x):
    """Root-Mean-Square."""
    return np.sqrt(x.dot(x) / x.size)


            
            
def get_single_create_focused_mel_spectrogram(recording_id, start_time_seconds, duration_seconds, run_folder):

    temp_display_images_folder_path = parameters.base_folder + '/' + run_folder + '/' + parameters.temp_display_images_folder 
    if not os.path.exists(temp_display_images_folder_path):
        os.makedirs(temp_display_images_folder_path)         

    try:
        
        audio_filename = str(recording_id) + '.m4a'
        audio_in_path = parameters.downloaded_recordings_folder + '/' +  audio_filename 
        image_out_name = 'temp_spectrogram.jpg'
        print('image_out_name', image_out_name)           
       
        image_out_path = temp_display_images_folder_path + '/' + image_out_name
        
        y, sr = librosa.load(audio_in_path, sr=None)      
               
        start_time_seconds_float = float(start_time_seconds)            
        
        start_position_array = int(sr * start_time_seconds_float)              
                   
        end_position_array = start_position_array + int((sr * duration_seconds))                  
                    
        y_part = y[start_position_array:end_position_array]  
        mel_spectrogram = librosa.feature.melspectrogram(y=y_part, sr=sr, n_mels=32, fmin=700,fmax=1000)
        
        plt.axis('off') # no axis
        plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[]) # Remove the white edge
        librosa.display.specshow(mel_spectrogram, cmap='binary') #https://matplotlib.org/examples/color/colormaps_reference.html
        plt.savefig(image_out_path, bbox_inches=None, pad_inches=0)
        plt.close()
        
        return get_image(image_out_path)
        
    except Exception as e:
        print(e, '\n')
        print('Error processing onset ', onset)
        
def get_single_create_focused_mel_spectrogram_return_path(recording_id, start_time_seconds, duration_seconds, run_folder):

    temp_display_images_folder_path = parameters.base_folder + '/' + run_folder + '/' + parameters.temp_display_images_folder 
    if not os.path.exists(temp_display_images_folder_path):
        os.makedirs(temp_display_images_folder_path)         

    try:
        
        audio_filename = str(recording_id) + '.m4a'
        audio_in_path = parameters.base_folder + '/' + parameters.downloaded_recordings_folder + '/' +  audio_filename 
        image_out_name = 'temp_spectrogram.jpg'
        print('image_out_name', image_out_name)           
       
        image_out_path = temp_display_images_folder_path + '/' + image_out_name
        
        # Delete the image to make sure it isn't using an old one
        try: # might give error on first time around loop
            os.remove(image_out_path)
        except:
            print(image_out_path, " was not there.")
             
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            y, sr = librosa.load(audio_in_path, sr=None)      
               
        start_time_seconds_float = float(start_time_seconds)            
        
        start_position_array = int(sr * start_time_seconds_float)              
                   
        end_position_array = start_position_array + int((sr * duration_seconds))                  
                    
        y_part = y[start_position_array:end_position_array]  
#         mel_spectrogram = librosa.feature.melspectrogram(y=y_part, sr=sr, n_mels=32, fmin=700,fmax=1000)
        mel_spectrogram = librosa.feature.melspectrogram(y=y_part, sr=sr, n_mels=32, fmin=parameters.morepork_min_freq_for_model_spectrograms,fmax=parameters.morepork_max_freq_for_model_spectrograms)
                       
        
        plt.axis('off') # no axis
        plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[]) # Remove the white edge
#         librosa.display.specshow(mel_spectrogram, cmap='binary') #https://matplotlib.org/examples/color/colormaps_reference.html
        
        librosa.display.specshow(librosa.power_to_db(mel_spectrogram**2, ref=np.max), sr=sr, cmap='binary')
        
        plt.savefig(image_out_path, bbox_inches=None, pad_inches=0)
        plt.close()
        
        return image_out_path
        
    except Exception as e:
        print(e, '\n')
        print('Error processing onset ', onset)

def scale_minmax(X, min=0.0, max=1.0):
    X_std = (X - X.min()) / (X.max() - X.min())
    X_scaled = X_std * (max - min) + min
    return X_scaled        



# def get_spectrogram_for_creating_training_and_test_data(recording_id, min_freq, max_freq):
#      
#     print("min_freq ", min_freq)
#     print("max_freq ", max_freq)
#  
#     temp_display_images_folder_path = parameters.base_folder + '/' + parameters.run_folder + '/' + parameters.temp_display_images_folder 
#     if not os.path.exists(temp_display_images_folder_path):
#         os.makedirs(temp_display_images_folder_path)         
#  
#     try:
#          
#         audio_filename = str(recording_id) + '.m4a'
#         audio_in_path = parameters.downloaded_recordings_folder + '/' +  audio_filename 
#         image_out_name = 'temp_spectrogram.jpg'
#         print('image_out_name', image_out_name)           
#         
#         image_out_path = temp_display_images_folder_path + '/' + image_out_name
#          
#         y, sr = librosa.load(audio_in_path, sr=None)  
#                        
#         mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, fmin=min_freq,fmax=max_freq, n_mels=32)
#         print(mel_spectrogram.shape)
#         maxElement = np.amax(mel_spectrogram)
#         print(maxElement)
#          
#               
#         plt.figure()
#          
#         plt.axis('off') # no axis
#         plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[]) # Remove the white edge
#  
#         librosa.display.specshow(librosa.power_to_db(mel_spectrogram**2, ref=np.max), sr=sr, cmap='binary')
#         
#         plt.savefig(image_out_path, bbox_inches=None, pad_inches=0)
#         plt.close()
#          
#         return get_image_for_for_creating_test_data(image_out_path)
#          
#     except Exception as e:
#         print(e, '\n')
#         print('Error processing spectrogram ', onset)

# def get_spectrogram_for_creating_training_and_test_data2(recording_id, min_freq, max_freq):
#     
#     print("min_freq ", min_freq)
#     print("max_freq ", max_freq)
# 
#     temp_display_images_folder_path = parameters.base_folder + '/' + parameters.run_folder + '/' + parameters.temp_display_images_folder 
#     if not os.path.exists(temp_display_images_folder_path):
#         os.makedirs(temp_display_images_folder_path)         
# 
#     try:
#         
#         audio_filename = str(recording_id) + '.m4a'
#         audio_in_path = parameters.downloaded_recordings_folder + '/' +  audio_filename 
#         image_out_name = 'temp_spectrogram.jpg'
#         print('image_out_name', image_out_name)           
#        
#         image_out_path = temp_display_images_folder_path + '/' + image_out_name
#         
#         y, sr = librosa.load(audio_in_path, sr=None)  
#                       
# #         mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, fmin=min_freq,fmax=max_freq, n_mels=32)
# #         print(mel_spectrogram.shape)
# #         maxElement = np.amax(mel_spectrogram)
# #         print(maxElement)
#        
#         S = librosa.stft(y)  # STFT of y
#     
#         S_db = librosa.power_to_db(S**2)
#         
#         height = S_db.shape[0]
#     
#         height_step = sr/2 / height
#          
#         # to show a freq range
#         # min=600, max=1200
#         # 
#         array_min = int( min_freq / height_step)
#         array_max = int(max_freq / height_step)  
#         
#         S_db_part = S_db[array_min : array_max, :]    
#         S_db_part = np.flip(S_db_part, 0) # Needed as plot was upside down
#         
#              
#         plt.axis("off")
#         fig=plt.imshow(S_db_part, cmap='binary')
#         fig.axes.get_xaxis().set_visible(False)
#         fig.axes.get_yaxis().set_visible(False)
#         plt.savefig(image_out_path, bbox_inches='tight', pad_inches=0)
#     
#         plt.close()
#         
#         return get_image_for_for_creating_test_data(image_out_path)
#         
#     except Exception as e:
#         print(e, '\n')
#         print('Error processing spectrogram ', onset)
        
def get_spectrogram_for_creating_training_and_test_data3(recording_id, min_freq, max_freq):
    
    print("min_freq ", min_freq)
    print("max_freq ", max_freq)

    temp_display_images_folder_path = parameters.base_folder + '/' + parameters.run_folder + '/' + parameters.temp_display_images_folder 
    if not os.path.exists(temp_display_images_folder_path):
        os.makedirs(temp_display_images_folder_path)         

    try:
        
        audio_filename = str(recording_id) + '.m4a'
        audio_in_path = parameters.downloaded_recordings_folder + '/' +  audio_filename 
        image_out_name = 'temp_spectrogram.jpg'
        print('image_out_name', image_out_name)           
       
        image_out_path = temp_display_images_folder_path + '/' + image_out_name
        
        y, sr = librosa.load(audio_in_path, sr=None)                        
    
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, fmin=min_freq, fmax=max_freq, n_mels=32)
            
        plt.figure()                
        plt.axis('off') # no axis    
        
        S_dB = librosa.power_to_db(mel_spectrogram, ref=np.max)
        librosa.display.specshow(S_dB, sr=sr, cmap='binary')        
        
        plt.savefig(image_out_path, bbox_inches='tight', pad_inches=0)        
        plt.close()
            
        return get_image_for_for_creating_test_data(image_out_path)
            
    except Exception as e:
        print(e, '\n')
        print('Error processing spectrogram ', onset)
           
def get_single_waveform_image(recording_id, start_time_seconds, duration_seconds):

    temp_display_images_folder_path = parameters.base_folder + '/' + parameters.run_folder + '/' + parameters.temp_display_images_folder 
    if not os.path.exists(temp_display_images_folder_path):
        os.makedirs(temp_display_images_folder_path)         

    try:
        
        audio_filename = str(recording_id) + '.m4a'
        audio_in_path = parameters.downloaded_recordings_folder + '/' +  audio_filename 
        image_out_name = 'temp_waveform.jpg'
        print('image_out_name', image_out_name)           
       
        image_out_path = temp_display_images_folder_path + '/' + image_out_name
        
        y, sr = librosa.load(audio_in_path, sr=None) 
        
        start_time_seconds_float = float(start_time_seconds)            
        
        start_position_array = int(sr * start_time_seconds_float)              
                   
        end_position_array = start_position_array + int((sr * duration_seconds))                  
                    
        y_part = y[start_position_array:end_position_array]  
    
        plt.axis('off') # no axis
        plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[]) # Remove the white edge
        librosa.display.waveplot(y=y_part, sr=sr)
        plt.savefig(image_out_path, bbox_inches=None, pad_inches=0)
        plt.close()
        
        return get_image(image_out_path)
        
    except Exception as e:
        print(e, '\n')
        print('Error processing onset ', onset)
               
def get_image(image_name_path): 
        
    image = Image.open(image_name_path)
    [imageSizeWidth, imageSizeHeight] = image.size
    image = image.resize((int(imageSizeWidth/2),int(imageSizeHeight/2)), Image.ANTIALIAS)
    spectrogram_image = ImageTk.PhotoImage(image)
    return spectrogram_image

def get_image_for_for_creating_test_data(image_name_path): 
        
    image = Image.open(image_name_path)
    print("Image size is ", image.size)
    [imageSizeWidth, imageSizeHeight] = image.size
#     image = image.resize((int(imageSizeWidth*4),int(imageSizeHeight*2)), Image.ANTIALIAS)
#     image = image.resize((int(imageSizeWidth*4),int(imageSizeHeight*4)), Image.ANTIALIAS)
#     image = image.resize((int(imageSizeWidth*4),int(imageSizeHeight)), Image.ANTIALIAS)
#     image = image.resize((int(imageSizeWidth*3.9),int(imageSizeHeight)), Image.ANTIALIAS)
#     image = image.resize((int(imageSizeWidth*3.85),int(imageSizeHeight)), Image.ANTIALIAS)
#     image = image.resize((int(imageSizeWidth*3.84),int(imageSizeHeight)), Image.ANTIALIAS)
    image = image.resize((int(imageSizeWidth*3.84* 1.29),int(imageSizeHeight*1.30 )), Image.ANTIALIAS)

    print("Image size is ", image.size)
    spectrogram_image = ImageTk.PhotoImage(image)
    return spectrogram_image

def get_unique_model_run_names():   
    cur = get_database_connection().cursor()
    cur.execute("SELECT DISTINCT model_run_name FROM model_run_result") 
    rows = cur.fetchall()  
    
    unique_model_run_names = []
    for row in rows:
        unique_model_run_names.append(row[0])
        
    return unique_model_run_names  


def get_unique_locations(table_name):   
    cur = get_database_connection().cursor()
    if table_name == 'recordings':
        cur.execute("SELECT DISTINCT device_super_name FROM recordings") 
    else:
        cur.execute("SELECT DISTINCT device_super_name FROM tags") 
    rows = cur.fetchall()  
    
    unique_locations = []
    unique_locations.append('Not Used')
    for row in rows:
        unique_locations.append(row[0])        
        
    return unique_locations  

    
       

def get_single_recording_info_from_local_db(recording_id):

    cur = get_database_connection().cursor()
    cur.execute("SELECT device_super_name, recordingDateTime FROM recordings WHERE recording_id = ?", (recording_id,))  
  
    recordings = cur.fetchall()
     
    single_recording =  recordings[0]   
    device_super_name = single_recording[0]
    recordingDateTime = single_recording[1]
    
    date_time_obj = datetime.datetime.strptime(recordingDateTime, "%Y-%m-%dT%H:%M:%S.000Z")    
    date_time_obj_Zulu = timezone('Zulu').localize(date_time_obj)

    fmt = "%Y-%m-%d %H:%M"
    
    date_time_obj_NZ = date_time_obj_Zulu.astimezone(timezone('Pacific/Auckland'))

    return device_super_name, date_time_obj_NZ.strftime(fmt)

def update_onsets_with_latest_model_run_actual_confirmed():
    cur = get_database_connection().cursor()
    previous_model_run = "2019_12_05_1"
    
    cur.execute("SELECT recording_id, startTime, actual_confirmed FROM model_run_result WHERE actual_confirmed IS NOT NULL AND modelRunName = ?", (previous_model_run,)) 
    
    confirmed_rows = cur.fetchall()
    
    for confirmed_row in confirmed_rows:
       
        recording_id = confirmed_row[0]
        startTime = confirmed_row[1]
        actual_confirmed = confirmed_row[2]
        
        print(recording_id, ' ', startTime, ' ', actual_confirmed)
        
        cur2 = get_database_connection().cursor()                
        cur2.execute("UPDATE onsets SET actual_confirmed = ? WHERE recording_id = ? AND start_time_seconds = ?", (actual_confirmed, recording_id, startTime))  
                
        get_database_connection().commit()
    

def update_onsets_device_super_name():
    # Used to back fill recording_id into onsets table
    cur = get_database_connection().cursor()
    cur.execute("SELECT ID, recording_id FROM onsets ") 
    onsets = cur.fetchall()
    count = 0
    total = len(onsets)
    for onset in onsets:
        count+=1
        print('Updating ', count, ' of ', total)
        ID = onset[0]
        recording_id = onset[1]
        
        cur1 = get_database_connection().cursor()
        cur1.execute("SELECT device_super_name FROM recordings WHERE recording_id = ?", (recording_id,)) 
        rows = cur1.fetchall() 
        device_super_name = rows[0][0]
        
        cur2 = get_database_connection().cursor()                
        cur2.execute("UPDATE onsets SET device_super_name = ? WHERE ID = ?", (device_super_name, ID))  
                
        get_database_connection().commit()
        
def update_model_run_result_device_super_name():
    # Used to back fill recording_id into onsets table
    cur = get_database_connection().cursor()
    cur.execute("SELECT ID, recording_id FROM model_run_result ") 
    model_run_results = cur.fetchall()
    count = 0
    total = len(model_run_results)
    for model_run_result in model_run_results:
        count+=1
        print('Updating ', count, ' of ', total)
        ID = model_run_result[0]
        recording_id = model_run_result[1]
        
        cur1 = get_database_connection().cursor()
        cur1.execute("SELECT device_super_name FROM recordings WHERE recording_id = ?", (recording_id,)) 
        rows = cur1.fetchall() 
        device_super_name = rows[0][0]
        
        cur2 = get_database_connection().cursor()                
        cur2.execute("UPDATE model_run_result SET device_super_name = ? WHERE ID = ?", (device_super_name, ID))  
                
        get_database_connection().commit()
        
        
def test_query():        
    cur = get_database_connection().cursor()
#     cur.execute("SELECT ID, device_super_name FROM model_run_result WHERE modelRunName = '2019_12_11_1' AND device_super_name = 'Hammond Park' ORDER BY recording_id DESC, startTime ASC")
    cur.execute("SELECT ID, device_super_name FROM model_run_result WHERE modelRunName = '2019_12_11_1' ORDER BY recording_id DESC, startTime ASC")  
    model_run_results = cur.fetchall() 
    count = 0
    total = len(model_run_results)
    for model_run_result in model_run_results:
        count+=1
        print('Processing ', count, ' of ', total)
        ID = model_run_result[0]
        device_super_name = model_run_result[1] 
        print('ID is ', ID, ' device_super_name is ', device_super_name) 
        if count > 20:
            break  
    


def add_tag_to_recording(user_token, recordingId, json_data):
    url = parameters.server_endpoint + parameters.tags_url
    

    payload = "recordingId=" + recordingId + \
        "&tag=" \
        + json_data        
        
    headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': user_token
            }

    response = requests.request("POST", url, data=payload, headers=headers)

    return response

def test_add_tag_to_recording():
    user_token = get_cacophony_user_token()
    version = '000003'
    tag = {}
    tag['animal'] = 'bigBirdzz'
    tag['startTime'] = 1
    tag['duration'] = 2
    tag['automatic'] = True
    tag['confidence'] = 0.9
    tag['confirmed'] = True
    tag['version'] = version
    json_tag = json.dumps(tag)
    resp = add_tag_to_recording(user_token, "158698", json_tag)
    print('resp is: ', resp.text)



def update_device_name_onsets_when_missing():
    cur = get_database_connection().cursor()
    cur.execute("SELECT ID, recording_id FROM onsets WHERE device_name IS NULL")  
    onsets_with_null_device_name = cur.fetchall()
    count = 0
    for onset_with_null_device_name in onsets_with_null_device_name:
        count+=1
        print('Updating ', count, ' of ', len(onsets_with_null_device_name))
        ID = onset_with_null_device_name[0]
        recording_id = onset_with_null_device_name[1]
        
        cur1 = get_database_connection().cursor()
        cur1.execute("SELECT device_name FROM recordings WHERE recording_id = ?", (recording_id,)) 
        rows = cur1.fetchall() 
        device_name = rows[0][0]
        
        cur2 = get_database_connection().cursor()                
        cur2.execute("UPDATE onsets SET device_name = ? WHERE ID = ?", (device_name, ID))  
                
        get_database_connection().commit()
        
def update_device_name_model_run_result_when_missing():
    cur = get_database_connection().cursor()
    cur.execute("SELECT ID, recording_id FROM model_run_result WHERE device_name IS NULL")  
    onsets_with_null_device_name = cur.fetchall()
    count = 0
    for onset_with_null_device_name in onsets_with_null_device_name:
        count+=1
        print('Updating ', count, ' of ', len(onsets_with_null_device_name))
        ID = onset_with_null_device_name[0]
        recording_id = onset_with_null_device_name[1]
        
        cur1 = get_database_connection().cursor()
        cur1.execute("SELECT device_name FROM recordings WHERE recording_id = ?", (recording_id,)) 
        rows = cur1.fetchall() 
        device_name = rows[0][0]
        
        cur2 = get_database_connection().cursor()                
        cur2.execute("UPDATE model_run_result SET device_name = ? WHERE ID = ?", (device_name, ID))  
                
        get_database_connection().commit()   
    print('Finished updating model_run_result device_names') 

def upload_tags_for_all_locations_to_cacophony_server():
    print("About to upload ALL tags to Cacophony Server")
    
    sql = '''select distinct device_super_name from tags'''
    cur = get_database_connection().cursor()  
    cur.execute(sql) 
    rows = cur.fetchall() 
    for row in rows:        
        device_super_name = row[0]
        upload_tags_to_cacophony_server(device_super_name)

def upload_tags_to_cacophony_server(location_filter):
    print("About to upload tags to Cacophony Server")
    user_token = get_cacophony_user_token()
    cur = get_database_connection().cursor()
    
    if location_filter !='not_used':
        cur.execute("SELECT ID, recording_id, startTime, duration, what, automatic, confidence, confirmed_by_human, modelRunName, version FROM tags WHERE modelRunName = ? AND (copied_to_server IS NULL OR copied_to_server = 0) AND device_super_name = ?", (parameters.model_run_name, location_filter))   
    else:            
        cur.execute("SELECT ID, recording_id, startTime, duration, what, automatic, confidence, confirmed_by_human, modelRunName, version FROM tags WHERE modelRunName = ? AND (copied_to_server IS NULL OR copied_to_server = 0)", (parameters.model_run_name,))   
    
    tags_to_send_to_server = cur.fetchall()
    count_of_tags_to_send_to_server = len(tags_to_send_to_server)
    
    if count_of_tags_to_send_to_server < 1:
        print('There are no tags to process :-(')
        return 
    
    count = 0
    for tag_to_send_to_server in tags_to_send_to_server:
        try:
            count+=1
            print('Processing ', count, ' of ', count_of_tags_to_send_to_server)
            ID = tag_to_send_to_server[0]
            recording_id = tag_to_send_to_server[1]
            recording_id_str = str(recording_id)
            startTime = tag_to_send_to_server[2]
            duration = tag_to_send_to_server[3]
            what = tag_to_send_to_server[4]
            automatic_str = tag_to_send_to_server[5]
            
            automatic_bool = (automatic_str == 'True')
            confidence = tag_to_send_to_server[6]
            confirmed_by_human_int = tag_to_send_to_server[7]
            confirmed_by_human_bool = bool(confirmed_by_human_int)
            

                
            tag = {}
            tag['what'] = what
            tag['startTime'] = str(startTime)
            tag['duration'] = str(duration)
            tag['automatic'] = automatic_bool
            tag['confidence'] = str(confidence)
            tag['confirmed'] = confirmed_by_human_bool
            tag['version'] = str(version)
            json_tag = json.dumps(tag)

            resp = add_tag_to_recording(user_token, recording_id_str, json_tag)
            resp_dict = json.loads(resp.text)
            
            cur2 = get_database_connection().cursor()  
            
            print('Going to update tags table for recording: ', recording_id_str, ' startTime: ', startTime, ' at ', location_filter, ' with a ', what)
                          
            if resp.ok:                
                success = resp_dict['success']
                print('success is: ', success)
                if success:
                    
                    cur2.execute("UPDATE tags SET copied_to_server = ? WHERE ID = ?", (1, ID)) 
                     
                else:
                    print('Error processing ', recording_id_str, ' ', resp.text)
                    cur2.execute("UPDATE tags SET copied_to_server = ? WHERE ID = ?", (-1, ID))
                
            else:
                error_message = resp_dict['message']
                print('Server returned the error: ', error_message)
                cur2.execute("UPDATE tags SET copied_to_server = ? WHERE ID = ?", (-1, ID))
                
            get_database_connection().commit() 
        
        except Exception as e:
            print(e, '\n')
            print('Error processing tag ', recording_id_str,  ' ', resp.text)


def update_model_run_results_with_onsets_used_to_create_model(model_run_name, csv_filename):
    print(model_run_name)   
    print("\n")   
    print(csv_filename)   
    
    # Extract onsets from csv file.
    with open(csv_filename) as fp:
        line = fp.readline()        
        while line:
          
            lineParts = line.split(',')
            recording_id = lineParts[1]
            start_time = lineParts[2]
            print('recording id is ', recording_id, '\n')
            print('start time is ', start_time, '\n\n')
            
            # now update model_run_result
            cur = get_database_connection().cursor()                
            cur.execute("UPDATE model_run_result SET used_to_create_model = 1 WHERE modelRunName = ? AND recording_id = ? AND startTime = ?", (model_run_name, recording_id, start_time))  
                                    
            get_database_connection().commit()  
                
            line = fp.readline()
            
    print("Finished updating model run result table") 








             
        


def convert_time_zones(day_time_from_database):
    # recording ID is  319810 - server says time is Thu Jun 13 2019, 06:42:00
#     day_time_from_database = '2019-06-12T18:42:00.000Z'
    day_time_from_database_00_format = datetime.datetime.fromisoformat(day_time_from_database.replace('Z', '+00:00'))
    print('day_time_from_database_00_format: ', day_time_from_database_00_format)
    nz = timezone('NZ')
    day_time_nz = day_time_from_database_00_format.astimezone(nz)
    print('day_time_nz: ', day_time_nz)
    return day_time_nz
    
def update_table_with_NZ_time():
    table_name = 'recordings'
    
    cur = get_database_connection().cursor()
    cur.execute("select ID, recordingDateTime from " + table_name + " where recordingDateTimeNZ IS NULL")      
    records = cur.fetchall()
    numOfRecords = len(records)
    count = 0
    
    for record in records:
        try:        
        
            ID = record[0]
            recordingDateTime = record[1]
            
            print('Processing ID ' + str(ID) + " which is " + str(count) + ' of ' + str(numOfRecords))
            
            recordingDateTimeNZ = convert_time_zones(recordingDateTime)
            
            sql = ''' UPDATE ''' + table_name + ''' 
                    SET recordingDateTimeNZ = ?               
                    WHERE ID = ?'''
            
            cur.execute(sql, (recordingDateTimeNZ, ID))
            count+=1
            get_database_connection().commit() 
            
        except Exception as e:
            print(str(e))
            print("Error processing ID " + str(ID))
        
def test_not_between_dates(firstDateStr, lastDateStr):
    table_name = 'onsets'
    
    firstDateStr = firstDateStr + ':00:00:00'
    lastDateStr = lastDateStr + ':23:59:59'
    
    cur = get_database_connection().cursor()
    # https://stackoverflow.com/questions/8187288/sql-select-between-dates
    cur.execute("select ID, recordingDateTime from " + table_name + " where strftime('%Y-%m-%d:%H-%M-%S', recordingDateTimeNZ) NOT BETWEEN '" + firstDateStr + "' AND '" + lastDateStr + "' order by recordingDateTimeNZ")      
         
    records = cur.fetchall()
    numOfRecords = len(records)
    count = 0
    
    for record in records:          
        
        ID = record[0]
        recordingDateTime = record[1]
        
        print('Processing ID ' + str(ID) + " which is " + str(count) + ' of ' + str(numOfRecords) + ' ' + recordingDateTime)
       
def get_recording_position_in_seconds(x_mouse_pos, x_scroll_bar_minimum, x_scroll_bar_maximum, canvas_width, recording_length):
    recording_pos_seconds = (((x_mouse_pos/canvas_width) * (x_scroll_bar_maximum - x_scroll_bar_minimum)) + x_scroll_bar_minimum) * recording_length
    print("x clicked at ", recording_pos_seconds, ' seconds')
    return round(recording_pos_seconds,1)

def get_recording_position_in_hertz(y_mouse_pos, canvas_height, recording_minimum_freq, recording_maximum_freq):
    recording_pos_hertz = recording_maximum_freq - ((y_mouse_pos/canvas_height) * (recording_maximum_freq - recording_minimum_freq))
    return int(recording_pos_hertz)    

def get_spectrogram_clicked_at_y_percent(y_mouse_pos,canvas_height):
    return y_mouse_pos/canvas_height

def spectrogram_clicked_at_x_percent(x_mouse_pos, x_scroll_bar_minimum, x_scroll_bar_maximum, canvas_width):
    x_position_percent = (((x_mouse_pos/canvas_width) * (x_scroll_bar_maximum - x_scroll_bar_minimum)) + x_scroll_bar_minimum)
#     print("x_position_percent ", x_position_percent)
    return x_position_percent

def convert_event_x_pos_to_canvas_x_pos(event_x):
    return event_x

def convert_pos_in_secs_to_canvas_pos2(recording_pos_seconds, recording_length, x_scroll_bar_minimum, x_scroll_bar_maximum, canvas_width):
    print("recording_pos_seconds ", recording_pos_seconds)
    print("x_scroll_bar_minimum ", x_scroll_bar_minimum)
    print("x_scroll_bar_maximum ", x_scroll_bar_maximum)
    print("canvas_width ", canvas_width)
    
    recording_pos_seconds_div_recording_length = recording_pos_seconds/recording_length
    print("recording_pos_seconds_div_recording_length ", recording_pos_seconds_div_recording_length)
    recording_pos_seconds_div_recording_length_minus_x_scroll_bar_minimum = recording_pos_seconds_div_recording_length - x_scroll_bar_minimum
    print("recording_pos_seconds_div_recording_length_minus_x_scroll_bar_minimum ", recording_pos_seconds_div_recording_length_minus_x_scroll_bar_minimum) 
    x_scroll_bar_maximum_minus_x_scroll_bar_minimum = x_scroll_bar_maximum-x_scroll_bar_minimum
    print("x_scroll_bar_maximum_minus_x_scroll_bar_minimum ", x_scroll_bar_maximum_minus_x_scroll_bar_minimum) 
    result = ((recording_pos_seconds_div_recording_length_minus_x_scroll_bar_minimum)*x_scroll_bar_maximum_minus_x_scroll_bar_minimum)* canvas_width
    print("result ", result)
    
    x_mouse_pos = (((recording_pos_seconds/recording_length)-x_scroll_bar_minimum)*(x_scroll_bar_maximum-x_scroll_bar_minimum))*canvas_width
    return x_mouse_pos

def convert_time_in_seconds_to_x_value_for_canvas_create_method(start_time_seconds, duration, spectrogram_image_width):
    return  ((start_time_seconds/duration) * spectrogram_image_width)  

def convert_frequency_to_y_value_for_canvas_create_method(spectrogram_image_min_freq, spectrogram_image_max_freq, freq_to_convert, spectrogram_image_height):    
    frequency_range = spectrogram_image_max_freq - spectrogram_image_min_freq
    how_far_from_top_of_freq_range = spectrogram_image_max_freq - freq_to_convert   
    result =  (how_far_from_top_of_freq_range/frequency_range)*spectrogram_image_height    
    return  result    

def convert_pos_in_percent_to_position_in_seconds(pos_in_percent, duration):
    return duration * pos_in_percent
    
def convert_pos_in_seconds_to_position_in_percent(pos_in_seconds, duration):
    return pos_in_seconds / duration
    
def convert_pos_in_seconds_to_canvas_position(spectrogram_image_width, pos_in_seconds, duration):
    pos_in_percent = convert_pos_in_seconds_to_position_in_percent(pos_in_seconds, duration)
    return spectrogram_image_width * pos_in_percent

def convert_frequency_to_vertical_position_on_spectrogram(spectrogram_image_height, frequency, spectrogram_start_frequency, spectrogram_finish_frequency):
    return spectrogram_image_height - (spectrogram_image_height*frequency/(spectrogram_finish_frequency - spectrogram_start_frequency))
        
def convert_x_or_y_postion_percent_to_x_or_y_spectrogram_image_postion(spectrogram_image_width_or_height, x_or_y_postion_percent):
    return spectrogram_image_width_or_height * x_or_y_postion_percent
    
def save_spectrogram_selection(selection_to_save):
    print("selection_to_save ", selection_to_save)
    
def insert_data_into_database(recording_id, start_time_seconds, finish_time_seconds, lower_freq_hertz, upper_freq_hertz, what, username):    
    
    cur1 = get_database_connection().cursor()
    cur1.execute("SELECT device_super_name, device_name, recordingDateTime, recordingDateTimeNZ, sample_rate FROM recordings WHERE recording_id = ?", (recording_id,)) 
    rows = cur1.fetchall() 
    device_super_name = rows[0][0]  
    device_name = rows[0][1]
    recordingDateTime = rows[0][2]  
    recordingDateTimeNZ = rows[0][3] 
    sample_rate = rows[0][4] 
    
    date_created = datetime.datetime.now()
    
    try:     
        sql = ''' INSERT INTO training_validation_test_data(recording_id, start_time_seconds, finish_time_seconds, lower_freq_hertz, upper_freq_hertz, what, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ, username, sample_rate, date_created)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur2 = get_database_connection().cursor()
        cur2.execute(sql, (recording_id, start_time_seconds, finish_time_seconds, lower_freq_hertz, upper_freq_hertz, what, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ, username, sample_rate, date_created ))
        get_database_connection().commit()
        return True
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert training_validation_test_data ' + str(recording_id), '\n')   
        return False   
    
 
def delete_test_data_row(recording_id, start_time_seconds, finish_time_seconds, lower_freq_hertz, upper_freq_hertz, what): 
    
    cur3 = get_database_connection().cursor()
    sql = 'DELETE FROM training_validation_test_data WHERE recording_id=? and start_time_seconds=? and finish_time_seconds=? and lower_freq_hertz=? and upper_freq_hertz=? and what=?'
    cur3.execute(sql, (recording_id, start_time_seconds, finish_time_seconds, lower_freq_hertz, upper_freq_hertz, what))
    get_database_connection().commit()
    
def retrieve_training_validation_test_data_from_database(recording_id):
    
    cur = get_database_connection().cursor()
    cur.execute("SELECT recording_id, start_time_seconds, finish_time_seconds, lower_freq_hertz, upper_freq_hertz, what from training_validation_test_data WHERE recording_id = ?", (recording_id,)) 
    training_validation_test_data_rows = cur.fetchall() 
    return training_validation_test_data_rows
    
def retrieve_recordings(date_range, include_all_test_validation_recordings, include_recordings_with_model_predictions, include_recordings_that_have_been_manually_analysed, model_must_predict_what, probability_cutoff, model_run_name, probability_greater_or_less, exclude_recordings_that_have_been_manually_analysed, recordings_must_include_this_tag):
#     print("model_run_name ", model_run_name)
    
    table_name = 'recordings'
    
    if date_range == "march_2020":   
        firstDate = parameters.march_2020_test_data_start_date 
        lastDate = parameters.march_2020_test_data_end_date 
        sqlBuilding = "select recording_id, datetime(recordingDateTime,'localtime') as recordingDateTimeNZ, device_name, duration, device_super_name from " + table_name + " where recordingDateTimeNZ BETWEEN '" + firstDate + "' AND '" + lastDate + "'"
   
    elif date_range == "feb_2020":
        firstDate = parameters.feb_2020_training_data_start_date 
        lastDate = parameters.feb_2020_training_data_end_date 
        sqlBuilding = "select recording_id, datetime(recordingDateTime,'localtime') as recordingDateTimeNZ, device_name, duration, device_super_name from " + table_name + " where recordingDateTimeNZ BETWEEN '" + firstDate + "' AND '" + lastDate + "'"
   
    elif date_range == "not_march_2020":
        firstDate = parameters.march_2020_test_data_start_date 
        lastDate = parameters.march_2020_test_data_end_date 
        sqlBuilding = "select recording_id, datetime(recordingDateTime,'localtime') as recordingDateTimeNZ, device_name, duration, device_super_name from " + table_name + " where recordingDateTimeNZ < '" + firstDate + "' OR  recordingDateTimeNZ > '" + lastDate + "'"
   
    
#     probability_cutoff_float = float(probability_cutoff)
    

        
    if not include_all_test_validation_recordings:        
    
        if include_recordings_with_model_predictions:
            
            if probability_cutoff == "not_used":
#             if probability_cutoff_float == 0:
                
                sqlBuilding += " AND recording_id IN (SELECT recording_id FROM model_run_result WHERE model_run_name = '" + model_run_name + "' AND predicted_by_model = '" + model_must_predict_what + "')"
            else:
                
                if probability_greater_or_less == "greater":
                    comparison_symbol = ">="
                else:
                    comparison_symbol = "<="
                
#                 sqlBuilding += " AND recording_id IN (SELECT recording_id FROM model_run_result WHERE model_run_name = '" + model_run_name + "' AND predicted_by_model = '" + model_must_predict_what + "' AND probability > " + probability_cutoff + ")"
                sqlBuilding += " AND recording_id IN (SELECT recording_id FROM model_run_result WHERE model_run_name = '" + model_run_name + "' AND predicted_by_model = '" + model_must_predict_what + "' AND probability " + comparison_symbol + " " + probability_cutoff + ")"
           
                
    if include_recordings_that_have_been_manually_analysed:
        sqlBuilding += " AND recording_id IN (SELECT recording_id FROM training_validation_test_data)"     
        
    if exclude_recordings_that_have_been_manually_analysed:
        sqlBuilding += " AND recording_id NOT IN (SELECT recording_id FROM these_recordings_have_been_analysed_for)"         
     
    if recordings_must_include_this_tag != None:
        sqlBuilding += " AND recording_id IN (SELECT recording_id FROM training_validation_test_data WHERE what = '" + recordings_must_include_this_tag + "')"     
              

    sqlBuilding += " ORDER BY recording_id ASC"    
       
    print("The sql is: ", sqlBuilding)
    cur = get_database_connection().cursor()
    cur.execute(sqlBuilding)

    rows = cur.fetchall()
    return rows
    
def get_model_run_results_to_create_feb_2020_training_data(modelRunName, actualConfirmedFilter, predictedFilter, predicted_probability_filter, predicted_probability_filter_value_str, location_filter, actual_confirmed_other, predicted_other, recording_id_filter_value):   
       
    if location_filter =='Not Used':
        location_filter ='not_used'        
            
    sqlBuilding = "SELECT ID FROM model_run_result WHERE modelRunName = '" + modelRunName + "'"
    
    sqlBuilding += " AND recordingDateTimeNZ BETWEEN '" + parameters.feb_2020_training_data_start_date + "' AND '" + parameters.feb_2020_training_data_end_date + "'"
    
    if actualConfirmedFilter !='not_used':
        sqlBuilding += " AND "
        if actualConfirmedFilter == "IS NULL":
            if actual_confirmed_other == 'off':
                sqlBuilding += "actual_confirmed IS NULL"
            else: # Everything other is checked
                sqlBuilding += "actual_confirmed IS NOT NULL"
        else:
            if actual_confirmed_other == 'off':
                sqlBuilding +=  "actual_confirmed = '" + actualConfirmedFilter + "'"
            else: # Everything other is checked
                sqlBuilding +=  "actual_confirmed <> '" + actualConfirmedFilter + "'"
                
            
    if predictedFilter !='not_used':
        sqlBuilding += " AND "
        if predictedFilter == "IS NULL":
            if predicted_other == 'off':
                sqlBuilding += "predictedByModel IS NULL"
            else:
                sqlBuilding += "predictedByModel IS NOT NULL"
        else:
            if predicted_other == 'off':
                sqlBuilding +=  "predictedByModel = '" + predictedFilter + "'"
            else:
                sqlBuilding +=  "predictedByModel <> '" + predictedFilter + "'"
            
    if location_filter !='not_used':
        sqlBuilding += " AND "
        sqlBuilding +=  "device_super_name = '" + location_filter + "'"
        
    if (predicted_probability_filter_value_str == '') or (predicted_probability_filter == 'not_used'):
        predicted_probability_filter = 'not_used'
    else:    
        if predicted_probability_filter == 'greater_than':  
            probabilty_comparator = '>'
#             predicted_probability_filter_value = float(predicted_probability_filter_value_str)    
        elif predicted_probability_filter == 'less_than': 
            probabilty_comparator = '<'
#             predicted_probability_filter_value = float(predicted_probability_filter_value_str)    
        sqlBuilding += " AND "
#         sqlBuilding += " probability " + probabilty_comparator + " '" + predicted_probability_filter_value + "'"
        sqlBuilding += " probability " + probabilty_comparator + " '" + predicted_probability_filter_value_str + "'"        
            
    if recording_id_filter_value:
        sqlBuilding += " AND "        
        sqlBuilding +=  "recording_id = '" + recording_id_filter_value + "'"
        
        
    sqlBuilding += " ORDER BY recording_id DESC, startTime ASC"
        
    print("The sql is: ", sqlBuilding)
    cur = get_database_connection().cursor()
    cur.execute(sqlBuilding)
#     cur.execute("SELECT ID FROM model_run_result WHERE modelRunName = '2019_12_11_1' ORDER BY recording_id DESC, startTime ASC")
    rows = cur.fetchall()
    return rows
    
    
def mark_recording_as_analysed(recording_id, what, cacophony_user_name):
    try: 
        
        if has_this_recording_been_analysed_for_this(recording_id, what):
            # No need to try to insert data as it is already in database (and there is a unique constraint)
            return True 
        
        date_created = datetime.datetime.now()
                
        cur = get_database_connection().cursor()
        sql = ''' INSERT INTO these_recordings_have_been_analysed_for(recording_id, what, username, date_created)
                      VALUES(?,?,?,?) '''
        cur.execute(sql, (recording_id, what, cacophony_user_name, date_created))
        get_database_connection().commit()   
        return True
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert these_recordings_have_been_analysed_for ' + str(recording_id), '\n')  
        return False   
    
def has_this_recording_been_analysed_for_this(recording_id, what_to_filter_on):
    try: 
        cur = get_database_connection().cursor()
        cur.execute("SELECT ID FROM these_recordings_have_been_analysed_for WHERE recording_id = ? and what = ?", (recording_id, what_to_filter_on))
        record = cur.fetchone()             # https://stackoverflow.com/questions/2440147/how-to-check-the-existence-of-a-row-in-sqlite-with-python
        
        if record is None:
            return False
        else:
            return True
        
    except Exception as e:
        print(e, '\n')

def get_spectrogram_rectangle_selection_colour(what):
    # http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter
    switcher = {
        "bird": "blue",
        "buzzy_insect":"OliveDrab1",
        "car":"gold2",
        "car_horn": "linen",
        "chainsaw":"lavender blush",
        "cow":"light slate gray",
        "cow_sheep":"light slate gray",        
        "crackle": "dodger blue",    
        "dog": "light blue",        
        "dove":"pink1",
        "duck":"cyan",
        "fire_work": "red2",
        "frog":"light yellow",
        "hammering":"indian red",
        "hand_saw": "dark salmon",    
        "human": "purple1",
        "maybe_morepork_more-pork": "yellow2",
        "morepork_croaking":"pale green",
        "morepork_more-pork":"green4",        
        "morepork_more-pork_part": "green2",       
        "music":"maroon1",
        "plane": "MistyRose4",    
        "rumble": "SlateBlue4",   
        "siren":"magenta2",
        "unknown":"PaleTurquoise3",
        "water": "CadetBlue4",    
        "white_noise": "snow"  
    }
    return switcher.get(what, "red")
    
def get_model_predictions(recording_id, model_run_name):
    table_name = 'model_run_result'        
    
    cur = get_database_connection().cursor()    

    cur.execute("select startTime, duration, predicted_by_model, probability, actual_confirmed from " + table_name + " where recording_id = ? and model_run_name = ?", (recording_id, model_run_name) )
   
    records = cur.fetchall()
                  
    return records


def create_features_for_onsets():
    cur = get_database_connection().cursor()    

    # First do the onsets that have been confirmed
    cur.execute("select ID, recording_id, start_time_seconds, actual_confirmed, device_super_name, device_name, duration_seconds, recordingDateTime FROM ONSETs WHERE version = ? AND actual_confirmed IS NOT NULL AND NOT EXISTS (SELECT onset_id FROM features WHERE onsets.recording_id = features.recording_id AND onsets.start_time_seconds = features.start_time_seconds) ORDER BY recording_id DESC", (str(parameters.onset_version)) )
        
    records = cur.fetchall()
    process_onset_features(records, True)
        
    # Now to the rest of the onsets
    cur.execute("select ID, recording_id, start_time_seconds, actual_confirmed, device_super_name, device_name, duration_seconds, recordingDateTime FROM ONSETs WHERE version = ? AND actual_confirmed IS NULL AND NOT EXISTS (SELECT onset_id FROM features WHERE onsets.recording_id = features.recording_id AND onsets.start_time_seconds = features.start_time_seconds) ORDER BY recording_id DESC", (str(parameters.onset_version)))
    
    records = cur.fetchall()
    process_onset_features(records, False)

        
def process_onset_features(records, confirmed):
    number_of_records = len(records)
    
    count = 0
    
    previous_recording_id = -1 # Only going to read recording from file once - ie if it has changed since last row result
    y_filtered = None
    sr = None
    for record in records:
        count+=1
        if confirmed:
            print(count, " of (confirmed) ", number_of_records)
        else:
            print(count, " of (not confirmed) ", number_of_records)
            
        recording_id = record[1]
        if recording_id != previous_recording_id:
            print("recording_id to process changed from ", previous_recording_id, " to ", recording_id)
            y_filtered, sr  = get_filtered_recording(recording_id)            
            
        create_features_for_single_onset_version_2(record[0], recording_id, record[2], record[3], record[4], record[5], record[6], record[7], y_filtered, sr)
        previous_recording_id = recording_id
    

def get_filtered_recording(recording_id):
    recordings_folder_with_path = parameters.base_folder + '/' + parameters.downloaded_recordings_folder
    filename = str(recording_id) + ".m4a"
    audio_in_path = recordings_folder_with_path + "/" + filename
    y, sr = librosa.load(audio_in_path)
#     y_filtered = apply_band_pass_filter(y, sr)
    
    y = butter_bandpass_filter(y, parameters.morepork_min_freq_for_model_spectrograms, parameters.morepork_max_freq_for_model_spectrograms, sr)    
    y = noise_reduce(y, sr) 


    return y, sr
             
def create_features_for_single_onset_version_2(onset_id, recording_id, start_time_seconds, actual_confirmed, device_super_name, device_name, duration_seconds, recordingDateTime, y_filtered, sr):
    
    start_time_seconds_float = float(start_time_seconds)   
         
    try:
        
        start_position_array = int(sr * start_time_seconds_float)              
                   
        end_position_array = start_position_array + int((sr * 1.0))                  
                    
        y_part = y_filtered[start_position_array:end_position_array]  
                
        rms = librosa.feature.rms(y=y_part)
        
        spectral_centroid = librosa.feature.spectral_centroid(y=y_part, sr=sr)
        
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y_part, sr=sr)
        
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y_part, sr=sr)
        
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y_part)  
        
        number_of_frames = rms.shape[1]
        

        print("number_of_frames ", number_of_frames)

        sqlBuilding = "INSERT INTO features (onset_id, recording_id, start_time_seconds, actual_confirmed, device_super_name, device_name, duration_seconds, recordingDateTime"
        for i in range(number_of_frames):
            sqlBuilding += ", rms" + str(i) 
            
        for i in range(number_of_frames):
            sqlBuilding += ", spectral_centroid" + str(i)
            
        for i in range(number_of_frames):
            sqlBuilding += ", spectral_bandwidth" + str(i)
            
        for i in range(number_of_frames):
            sqlBuilding += ", spectral_rolloff" + str(i)
            
        for i in range(number_of_frames):
            sqlBuilding += ", zero_crossing_rate" + str(i)
        
        
        sqlBuilding += ")"
        sqlBuilding += " VALUES("
        
        sqlBuilding += str(onset_id) + ","
        sqlBuilding += str(recording_id) + ","
        sqlBuilding += str(start_time_seconds) + ","
        sqlBuilding += "'" + str(actual_confirmed) + "'" + ","
        
        sqlBuilding += "'" + str(device_super_name) + "'" + ","
        sqlBuilding += "'" + str(device_name) + "'" + ","
        sqlBuilding += str(duration_seconds) + ","
        sqlBuilding += "'" + str(recordingDateTime) + "'"
        
        for i in range(number_of_frames):
            sqlBuilding += "," + "'" + str(rms[0][i]) + "'"
         
        for i in range(number_of_frames):
            sqlBuilding += "," + "'" + str(spectral_centroid[0][i]) + "'"
            
        for i in range(number_of_frames):
            sqlBuilding += "," + "'" + str(spectral_bandwidth[0][i]) + "'"
            
        for i in range(number_of_frames):
            sqlBuilding += "," + "'" + str(spectral_rolloff[0][i]) + "'"
            
        for i in range(number_of_frames):
            sqlBuilding += "," + "'" + str(zero_crossing_rate[0][i]) + "'"
            
        sqlBuilding += ")"        

        
        cur = get_database_connection().cursor()
        cur.execute(sqlBuilding)
        get_database_connection().commit()        

    except Exception as e:
        print(e)      

    

def butter_bandpass(lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs):
    b, a = butter_bandpass(lowcut, highcut, fs, order=4)
    y = lfilter(b, a, data)
    return y




def paired_item(source):
    source_iter = iter(source)
    while True:
        try:
            yield next(source_iter).item(), next(source_iter).item()
        except StopIteration:
            return

def merge_paired_short_time(udarray, small_time):
    paired_iter = paired_item(udarray)
    r = None
    for s in paired_iter:
        if not r:
            r = s
        elif s[0] < r[1] + small_time:
            r = r[0], s[1]
        else:
            yield r
            r = s
    if r:
        yield r



class window_helper:
    cache = {}
  
#     def construct_window(self, width, family, scale):
    def construct_window(self,width, family, scale):
        if family == 'bartlett':
            return np.bartlett(width) * scale
  
        if family == 'blackman':
            return np.blackman(width) * scale
  
        if family == 'hamming':
            return np.hamming(width) * scale
  
        if family == 'hann':
            import scipy.signal
            return scipy.signal.hann(width) * scale
  
        if family == 'hanning':
            return np.hanning(width) * scale
  
        if family == 'kaiser':
            beta = 14
            return np.kaiser(width, beta) * scale
  
        if family == 'tukey':
            import scipy.signal
            return scipy.signal.tukey(width) * scale
  
        print('window family %s not supported' % family)
  

    def get_window(self, key):      
        if not key in self.cache:
                self.cache[key] = self.construct_window(*key)                
        return window_helper.cache[key]
    
def check_python_version():
    if sys.version_info[0] < 3:
        print('python version 2 not supported, try activate virtualenv or run setup.')
        sys.exit()

def get_window_const(width, family, scale=1.0):
    check_python_version()
    a_window_helper = window_helper()    
    return a_window_helper.get_window((width, family, scale))
    

class spectrogram_helper:
    def __init__(self, source_pad, spectrogram, stride, sample_rate):
        self.spectrogram = spectrogram
        (self.block_count, dct_width) = spectrogram.shape
        self.stride = stride
 
        window_c = get_window_const(dct_width, 'tukey')
 
        for index in range(self.block_count):
            block_index = index * stride
            block = source_pad[block_index:block_index + dct_width] * window_c
            dct = scipy.fft.dct(block)
            spectrogram[index] = dct
 
        self.buckets = []
        msw = 50 * sample_rate // stride
        max_spec_width = min(msw, self.block_count)
        division_count = max(int((self.block_count * 1.7) / max_spec_width), 1)
        for i in range(division_count):
            t0 = 0
            if i:
                t0 = (self.block_count - max_spec_width) * \
                    i // (division_count - 1)
            t1 = min(t0 + max_spec_width, self.block_count)
            self.buckets.append((t0, t1))
 
        self.currentBucket = -2
 
    def get_tolerance(self, index):
        qb = (index, index, index)
        q = min(self.buckets, key=lambda x: abs(x[0] + x[1] - 2 * index))
        if self.currentBucket != q:
            self.currentBucket = q
            (t0, t1) = q
            bin_medians = np.median(abs(self.spectrogram[t0:t1, ]), axis=0)
            self.tolerance = 4 * \
                np.convolve(bin_medians, np.ones(8) / 8)[4:-3]
 
        return self.tolerance

def noise_reduce_dct(source, sample_rate):
    original_sample_count = source.shape[0]
    dct_width = 2048

    trim_width = int(dct_width / 8)
    stride = dct_width - trim_width * 3

    block_count = (original_sample_count + stride - 1) // stride
    source_pad = np.pad(source, (stride, stride * 2), 'reflect')

    #print('Building spectrogram')
    spectrogram = np.empty((block_count, dct_width))

    sph = spectrogram_helper(source_pad, spectrogram, stride, sample_rate)

    # anything below bass_cut_off_freq requires specialised techniques
    bass_cut_off_freq = 100
    bass_cut_off_band = bass_cut_off_freq * 2 * dct_width // sample_rate

    spectrogram_trimmed = np.empty((block_count, dct_width))
    rms_tab = np.empty(block_count)

    for index in range(block_count):
        dct = spectrogram[index]

        mask = np.ones_like(dct)
        mask[:bass_cut_off_band] *= 0

        rms_tab[index] = rms(dct * mask)

        tolerance = sph.get_tolerance(index)
        for band in range(dct_width):
            if abs(dct[band]) < tolerance[band]:
                mask[band] *= 0.0

        maskCon = 10 * np.convolve(mask, np.ones(8) / 8)[4:-3]

        maskBin = np.where(maskCon > 0.1, 0, 1)
        spectrogram_trimmed[index] = maskBin

    rms_cutoff = np.median(rms_tab)

    result_pad = np.zeros_like(source_pad)
    for index in range(1, block_count - 1):
        dct = spectrogram[index]

        trim3 = spectrogram_trimmed[index - 1] * \
            spectrogram_trimmed[index] * spectrogram_trimmed[index + 1]
        dct *= (1 - trim3)

        if rms(dct) < rms_cutoff:
            continue  # too soft

#         rt = scipy.fftpack.idct(dct) / (dct_width * 2)
        rt = scipy.fft.idct(dct) / (dct_width * 2)

        block_index = index * stride
        result_pad[block_index + trim_width * 1:block_index + trim_width *
                   2] += rt[trim_width * 1:trim_width * 2] * np.linspace(0, 1, trim_width)
        result_pad[block_index +
                   trim_width *
                   2:block_index +
                   trim_width *
                   6] = rt[trim_width *
                           2:trim_width *
                           6]  # *numpy.linspace(1,1,stride8*4)
        result_pad[block_index + trim_width * 6:block_index + trim_width *
                   7] = rt[trim_width * 6:trim_width * 7] * np.linspace(1, 0, trim_width)

    result = result_pad[stride:stride + original_sample_count]
    return result

def noise_reduce(source, sample_rate):
    return noise_reduce_dct(source, sample_rate)


        
        
def do_rectangle_times_overlap(rectangle_1_start, rectangle_1_finish, rectangle_2_start, rectangle_2_finish):
    rectangle_1_width = rectangle_1_finish - rectangle_1_start
    rectangle_2_width = rectangle_2_finish - rectangle_2_start
    
    if rectangle_1_width >= rectangle_2_width:
        # Determine in rectangle 2 start OR finish within rectangle 1 start AND finish
        if (rectangle_2_start >= rectangle_1_start) and (rectangle_2_start <= rectangle_1_finish):
            return True
        if (rectangle_2_finish >= rectangle_1_start) and (rectangle_2_finish <= rectangle_1_finish):
            return True
    else:
        # rectangle_2_width > rectangle_1_width
        if (rectangle_1_start >= rectangle_2_start) and (rectangle_1_start <= rectangle_2_finish):
            return True
        if (rectangle_1_finish >= rectangle_2_start) and (rectangle_1_finish <= rectangle_2_finish):
            return True
        
    return False
    
    
        

 
def update_model_run_result_actual_confirmed_from_training_data(modelRunName):
    # Use this to update each row in the model_run_table with the actual sound (if there exists one) from the training data

    cur = get_database_connection().cursor()
    cur.execute("SELECT ID, recording_id, startTime from model_run_result WHERE modelRunName = ? AND actual_confirmed IS NULL ORDER BY recording_id ASC", (modelRunName,))

    model_run_results = cur.fetchall()
    number_of_model_run_results = len(model_run_results)
    print("There are ", number_of_model_run_results, " without actual_confirmed values for ", modelRunName)
    
    count = 0    
    
    for model_run_result in model_run_results:
        count+=1
        print(count, " of ", number_of_model_run_results)        
        
        model_run_result_ID = model_run_result[0]
        recording_id = model_run_result[1]
        prediction_startTime = model_run_result[2]       
               
        search_start_time = prediction_startTime - 0.1
        search_end_time = prediction_startTime + 0.1                
    
        # Find if there is a training_data value for this prediction
        cur.execute("SELECT actual_confirmed from training_data WHERE recording_id = ? AND start_time_seconds BETWEEN ? AND ?", (recording_id, search_start_time, search_end_time))
        
        a_training_data_result = cur.fetchone()   # https://stackoverflow.com/questions/2440147/how-to-check-the-existence-of-a-row-in-sqlite-with-python
                
        if a_training_data_result is None:
            continue
        else:
            actual_confirmed = a_training_data_result[0]
            
            # update model_run_result with this actual_confirmed
            sql = ''' UPDATE model_run_result
                        SET actual_confirmed = ?
                        WHERE id = ?'''
            cur.execute(sql, (actual_confirmed, model_run_result_ID))        
            get_database_connection().commit()             
       
   
            



def copy_confirmed_onests_into_training_validation_test_data_table():
    cur = get_database_connection().cursor()
    cur.execute("SELECT recording_id, start_time_seconds, duration_seconds, actual_confirmed, device_super_name, device_name, recordingDateTime, recordingDateTimeNZ from onsets WHERE actual_confirmed IS NOT NULL")
    onset_rows = cur.fetchall() 
    num_of_rows = len(onset_rows)
    print("num_of_rows ", num_of_rows)
    
    count=0
    for onset_row in onset_rows:
        count+=1
        print(f"Processing {count} of {num_of_rows}")
        recording_id = onset_row[0]
        start_time_seconds = onset_row[1]
        duration_seconds = onset_row[2]
        actual_confirmed = onset_row[3]
        device_super_name = onset_row[4]
        device_name = onset_row[5]
        recordingDateTime = onset_row[6]
        recordingDateTimeNZ = onset_row[7]
        
        finish_time_seconds = start_time_seconds + duration_seconds        
        date_created = datetime.datetime.now()
        
        cur.execute("SELECT sample_rate FROM recordings WHERE recording_id = '" + str(recording_id) + "'")
        rows = cur.fetchall()        
        
        sample_rate = rows[0][0]
        
        try:
            sql = ''' INSERT INTO training_validation_test_data(recording_id, start_time_seconds, finish_time_seconds, device_name, device_super_name, what, recordingDateTime, recordingDateTimeNZ, sample_rate, username, date_created)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
            cur = get_database_connection().cursor()
            cur.execute(sql, (recording_id, start_time_seconds, finish_time_seconds, device_name, device_super_name, actual_confirmed, recordingDateTime, recordingDateTimeNZ, sample_rate, parameters.cacophony_user_name, date_created))
           
            get_database_connection().commit()
        except Exception as e:
            print(e, '\n')
            print('\t\tUnable to insert recording ' + str(recording_id), '\n')
        
        
        
        
        
def get_original_recording_sample_rate(recording_id):   
    try:
        recordings_folder_with_path = parameters.downloaded_recordings_folder
        filename = str(recording_id) + ".m4a"
        audio_in_path = recordings_folder_with_path + "/" + filename
    
    
        y, sr = librosa.load(audio_in_path, sr=None, mono=True, duration=1) 
        
    except Exception as e:
        y = sr = -1
    
    return sr
        
        
def update_database_recordings_with_original_sample_rate():
    cur = get_database_connection().cursor()
    cur.execute("SELECT recording_id from recordings WHERE sample_rate IS NULL")
    recordings = cur.fetchall()  
    row_count = len(recordings)
    count = 0
    for row in recordings:
        count+=1
        print(count, " of ", row_count)
        
        recording_id = row[0]
        try:
            sample_rate = get_original_recording_sample_rate(recording_id)
        except:
            print("Problem with recording " + str(recording_id))
            continue
        print("sample_rate is ", sample_rate)
        
        try:
         
            sql = ''' UPDATE recordings 
                      SET sample_rate = ?                      
                      WHERE recording_id = ? '''

            cur.execute(sql, (sample_rate, recording_id))
            get_database_connection().commit()
            

            
            
        except Exception as e:
            print(e, '\n')
            print('\t\tUnable to update recording ' + str(recording_id), '\n')
        
        
        
def update_training_validation_test_data_with_username_date():       
    sql = ''' UPDATE training_validation_test_data 
                  SET username = ?,
                      date_created = ?                      
                  WHERE username IS NULL '''
    cur = get_database_connection().cursor()
    cur.execute(sql, ('timhot', '2020-10-03 15:42:37.398694'))
    get_database_connection().commit()
    
def update_these_recordings_have_been_analysed_for_with_username_date():       
    sql = ''' UPDATE these_recordings_have_been_analysed_for 
                  SET username = ?,
                      date_created = ?                      
                  WHERE username IS NULL '''
    cur = get_database_connection().cursor()
    cur.execute(sql, ('timhot', '2020-10-03 15:42:37.398694'))
    get_database_connection().commit()
        
        
        
        
        
def test_spectrogram():
    
    audio_filename = '547872.m4a'
    audio_in_path = parameters.downloaded_recordings_folder + '/' +  audio_filename 
    image_out_name = 'temp_spectrogram.jpg'
    print('image_out_name', image_out_name)    
    
    temp_display_images_folder_path = parameters.base_folder + '/' + parameters.run_folder + '/' + parameters.temp_display_images_folder        
   
    image_out_path = temp_display_images_folder_path + '/' + image_out_name
    
    y, sr = librosa.load(audio_in_path, sr=None) 
#     S = np.abs(librosa.stft(y))
    mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, fmin=0,fmax=2000)
    
    plt.figure()
    plt.axis('off') # no axis
    plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[]) # Remove the white edge
    
#     librosa.display.specshow(librosa.power_to_db(S**2, ref=np.max), sr=sr)
    librosa.display.specshow(librosa.power_to_db(mel_spectrogram**2, ref=np.max), sr=sr, cmap='binary')
    
    plt.savefig(image_out_path, bbox_inches=None, pad_inches=0)
    plt.close()
    
#     
#     
#     maxElement = np.amax(y)
#     print(maxElement)
#     minElement = np.amin(y)
#     print(minElement)
#     y=y*10
#     mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, fmin=0,fmax=2000)
#     
#     plt.figure()
#         
#     plt.axis('off') # no axis
#     plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[]) # Remove the white edge
#     librosa.display.specshow(mel_spectrogram, cmap='binary')
# #         plt.imshow(Sxx)
# #         librosa.display.specshow(Xdb, cmap='binary')
#        
#     plt.savefig(image_out_path, bbox_inches=None, pad_inches=0)
#     plt.close()
    
def update_training_validation_test_data_with_frequencies():       
    sql = ''' UPDATE training_validation_test_data 
                  SET lower_freq_hertz = ?,
                      upper_freq_hertz = ?                      
                  WHERE lower_freq_hertz IS NULL '''
    cur = get_database_connection().cursor()
    cur.execute(sql, ('700', '1100'))
    get_database_connection().commit()
   
        
        
        
        
