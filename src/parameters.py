'''
Created on 30 Sep. 2020

@author: tim
'''
import sys

model_run_name='2020_05_04_1'
onset_version = '7'

march_2020_test_data_start_date = '2020-03-01'
march_2020_test_data_end_date = '2020-04-01' # Note, this will be interpreted as the first second of the day, so won't include results for this day.

feb_2020_training_data_start_date = '2020-02-01'
feb_2020_training_data_end_date = '2020-03-01' # Note, this will be interpreted as the first second of the day, so won't include results for this day.



#### Cacophony Server Configuration
server_endpoint = 'https://api.cacophony.org.nz' # Production


cacophony_user_name = 'timhot' # change as needed
cacophony_user_password = '' # code will prompt for this, so don't store here.
cacophony_user_token = ''

login_user_url = '/authenticate_user'
query_available_recordings = '/api/v1/recordings/'
get_information_on_single_recording = '/api/v1/recordings/'
get_a_token_for_getting_a_recording_url = '/api/v1/recordings/' # should change the name of this
get_a_recording = '/api/v1/signedUrl'
tags_url = '/api/v1/tags'
groups = '/api/v1/groups'
devices_endpoint = '/api/v1/devices'

#### End of Cacophony Server Configuration

#### Local File Structure Configuration



base_folder = '/media/tim/HDD1/Work/Cacophony/audio_analysis'
downloaded_recordings_folder = base_folder + '/downloaded_recordings/all_recordings'
# db_file = base_folder + '/audio_analysis_db3.db'
db_file = base_folder + '/audio_analysis_db3_new_tags.db'
run_folder = 'Audio_Analysis/audio_classifier_runs' + '/' + model_run_name
temp_folder = 'Temp'
temp_display_images_folder = 'temp_display_images'


morepork_more_pork_call_duration = 0.9
morepork_min_freq_for_model_spectrograms = 600
morepork_min_freq_for_model_spectrograms = 1100

morepork_min_freq_display = 600
morepork_max_freq_display = 1200
morepork_expected_freq_display = 900


test_data_canvas_height = 1000
test_data_canvas_width = 2455

class_names = 'morepork_more-pork,unknown,siren,dog,duck,dove,human,bird,car,rumble,white_noise,cow,buzzy_insect,plane,hammering,frog,morepork_more-pork_part,chainsaw,crackle,car_horn,water,fire_work,maybe_morepork_more-pork,music,hand_saw'


