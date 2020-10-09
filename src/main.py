'''
Created on 30 Sep. 2020

@author: tim
'''
'''
Created on 5 Sep 2019
Modified 17 12 2019a

@author: tim

'''
from tkinter.messagebox import showinfo
from threading import Thread
# from pylint.test import test_self

import time


#  https://www.youtube.com/watch?v=A0gaXfM1UN0&t=343s
# https://www.youtube.com/watch?v=D8-snVfekto
# How to Program a GUI Application (with Python Tkinter)!
# https://www.tutorialspoint.com/python3/python_gui_programming

HEIGHT = 1000
WIDTH = 1100

import tkinter as tk

from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog


# import os
from PIL import ImageTk,Image 

import src.functions as functions
import src.parameters as parameters


from datetime import datetime
import calendar

import threading
LARGE_FONT= ("Verdana", 12)


class Main_GUI(tk.Tk):
    # comment
    
    def __init__(self, *args, **kwargs):
        
        
        tk.Tk.__init__(self, *args, **kwargs)        
        tk.Tk.wm_title(self, "Cacophony Audio Tagger")
        # https://stackoverflow.com/questions/47829756/setting-frame-width-and-height?rq=1
        container = tk.Frame(self,width=WIDTH, height=HEIGHT)
        container.grid_propagate(False)        
        container.pack(side="top", fill="both", expand=True)        
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
       
        self.frames = {}
        
#         for F in (HomePage, RecordingsPage, TaggingPage, CreateWekaModelPage, ClassifyOnsetsUsingWekaModelPage, CreateOnsetsPage, CreateSpectrogramsPage, CreateTagsFromOnsetsPage, EvaluateWekaModelRunResultPage, CreateTagsOnCacophonyServerFromModelRunPage, ModelAccuracyAnalysisPage, ManuallyCreateTrainingAndTestDataPage):
        for F in (HomePage, RecordingsPage, ManuallyCreateTrainingAndTestDataPage, UpdateTrainingDataUsingAModelsPredictions):
          
            frame = F(container, self)
            self.frames[F] = frame            
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(HomePage)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        
def qf(param):
    print(param)
        
class HomePage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
       
        label = tk.Label(self, text="Home Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)       
        
        instuctions_text2 = "SQLite is used as the database, without any wrapper (such as GRDB) to allow for concurrent db write access.  This means if you run two versions of this application at once, you will get errors."
        instuctions_msg2 = tk.Message(self, text = instuctions_text2)
        instuctions_msg2.config(width=600)
        instuctions_msg2.pack(pady=10,padx=10)
        
        instuctions_text3 = "Keep an eye on the Console - you will need to enter your Cacophony server password, and view other messages"
        instuctions_msg3 = tk.Message(self, text = instuctions_text3)
        instuctions_msg3.config(width=600)
        instuctions_msg3.pack(pady=10,padx=10)
        
        recordings_button = ttk.Button(self, text="Download Recordings from Server (Do not always use)",
                            command=lambda: controller.show_frame(RecordingsPage))        
        recordings_button.pack()        
                    
        manuallyCreateTrainingAndTestDataPage_button = ttk.Button(self, text="Create Training/Validation or Test data ",
                            command=lambda: controller.show_frame(ManuallyCreateTrainingAndTestDataPage))        
        manuallyCreateTrainingAndTestDataPage_button.pack()
        
        updateTrainingDataUsingAModelsPredictionsPage_button = ttk.Button(self, text="Use model predictions to update training data",
                            command=lambda: controller.show_frame(UpdateTrainingDataUsingAModelsPredictions))        
        updateTrainingDataUsingAModelsPredictionsPage_button.pack() 
        

class RecordingsPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        title_label = ttk.Label(self, text="Recordings Page", font=LARGE_FONT)
        title_label.grid(column=0, columnspan=1, row=0)
        
        device_name_label = ttk.Label(self, text="Device name e.g hammond_park_v2")
        device_name_label.grid(column=0, columnspan=1, row=1)
             
        device_name = StringVar(value='hammond_park_v4')
        device_name_entry = tk.Entry(self,  textvariable=device_name, width=30)
        device_name_entry.grid(column=1, columnspan=1, row=1)
        
        device_super_name_label = ttk.Label(self, text="Device Super name (e.g. Hammond_Park)")
        device_super_name_label.grid(column=0, columnspan=1, row=2)
        
        device_super_name = StringVar(value='Hammond_Park')
        device_super_name_entry = tk.Entry(self,  textvariable=device_super_name, width=30)
        device_super_name_entry.grid(column=1, columnspan=1,row=2)               
        
        get_new_recordings_from_server_button = ttk.Button(self, text="Get New Recordings For specified Device from Server",
                            command=lambda: functions.get_recordings_from_server(device_name.get(), device_super_name.get()))
        get_new_recordings_from_server_button.grid(column=0, columnspan=1, row=5)
        
        get_new_recordings_from_server_instructions = "This will get the recordings for the device in the device name box. It will also assign a super name from the Super Name box. Code will wait for you to ENTER YOUR PASSWORD in CONSOLE"

        msg2 = tk.Message(self, text = get_new_recordings_from_server_instructions)
        msg2.config(width=600)
        msg2.grid(column=1, columnspan=2, row=5)   
        
        get_new_recordings_from_server_button = ttk.Button(self, text="Get Recordings For all devices already in local database from Server",
                            command=lambda: functions.get_recordings_from_server_for_all_devices())
        get_new_recordings_from_server_button.grid(column=0, columnspan=1, row=6)
        
        get_new_recordings_from_server_instructions = "This will see what devices have already been used and the recordings for all of them, and will used the device_super_name already in the local database (will not use the text in the boxes above)."


        msg3 = tk.Message(self, text = get_new_recordings_from_server_instructions)
        msg3.config(width=600)
        msg3.grid(column=1, columnspan=2, row=6) 
        
        retrive_any_missing_recordings_info_from_server_button = ttk.Button(self, text="Retrieve any missing recordings info from server",
                            command=lambda: functions.retrieve_missing_recording_information()())
        retrive_any_missing_recordings_info_from_server_button.grid(column=0, columnspan=1, row=10)
        
        retrive_any_missing_recordings_info_from_server_instructions = "You shouldn't have to use this, but if the previous process was interrupted, you may need to run this to get the missing recording information (there will be nulls in the recordingDateTime etc database field)."


        msg3 = tk.Message(self, text = retrive_any_missing_recordings_info_from_server_instructions)
        msg3.config(width=600)
        msg3.grid(column=1, columnspan=2, row=10)   
        
            
        
        back_to_home_button = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(HomePage))
        back_to_home_button.grid(column=0, columnspan=1, row=20)               


class ManuallyCreateTrainingAndTestDataPage(tk.Frame):      
   
     
        
    def leftMousePressedcallback(self, event):
    
        self.x_scroll_bar_minimum = self.scroll_x.get()[0]   
        self.x_scroll_bar_maximum = self.scroll_x.get()[1]                     

        self.x_rectangle_start_position_percent = functions.spectrogram_clicked_at_x_percent(event.x, self.x_scroll_bar_minimum, self.x_scroll_bar_maximum, int(self.canvas.cget("width")))        
        self.y_rectangle_start_position_percent = functions.get_spectrogram_clicked_at_y_percent(event.y, self.spectrogram_image.height())  
            
        duration = self.recordings[self.current_recordings_index][3]
       
        self.x_rectangle_start_position_seconds = functions.get_recording_position_in_seconds(event.x, self.x_scroll_bar_minimum, self.x_scroll_bar_maximum, int(self.canvas.cget("width")), duration)        

        self.y_rectangle_start_position_hertz = functions.get_recording_position_in_hertz(event.y, self.spectrogram_image.height(), int(self.min_freq.get()), int(self.max_freq.get()))  
   

    def on_move_press(self, event):
        if self.temp_rectangle is not None:
            self.canvas.delete(self.temp_rectangle)
        
        self.x_rectangle_finish_position_percent = functions.spectrogram_clicked_at_x_percent(event.x, self.x_scroll_bar_minimum, self.x_scroll_bar_maximum, int(self.canvas.cget("width")))
        self.y_rectangle_finish_position_percent = functions.get_spectrogram_clicked_at_y_percent(event.y, self.spectrogram_image.height())     
        
        
        if not self.actual_confirmed.get():
            # The 'what' radio button hasn't been selected 
            return         

        rectangle_bbox_x1 = functions.convert_x_or_y_postion_percent_to_x_or_y_spectrogram_image_postion(self.spectrogram_image.width(), self.x_rectangle_start_position_percent)
        rectangle_bbox_y1 = functions.convert_x_or_y_postion_percent_to_x_or_y_spectrogram_image_postion(self.spectrogram_image.height(), self.y_rectangle_start_position_percent)
        
        rectangle_bbox_x2 = functions.convert_x_or_y_postion_percent_to_x_or_y_spectrogram_image_postion(self.spectrogram_image.width(), self.x_rectangle_finish_position_percent)
        rectangle_bbox_y2 = functions.convert_x_or_y_postion_percent_to_x_or_y_spectrogram_image_postion(self.spectrogram_image.height(), self.y_rectangle_finish_position_percent)

        self.temp_rectangle = self.canvas.create_rectangle(rectangle_bbox_x1, rectangle_bbox_y1, rectangle_bbox_x2, rectangle_bbox_y2 )
        
        
        
    def leftMouseReleasedcallback(self, event):
        duration = self.recordings[self.current_recordings_index][3]

        self.x_rectangle_finish_position_seconds = functions.get_recording_position_in_seconds(event.x, self.x_scroll_bar_minimum, self.x_scroll_bar_maximum, int(self.canvas.cget("width")), duration)
        self.y_rectangle_finish_position_hertz = functions.get_recording_position_in_hertz(event.y, self.spectrogram_image.height(), int(self.min_freq.get()), int(self.max_freq.get()))
                  
        if self.y_rectangle_start_position_hertz > self.y_rectangle_finish_position_hertz:
            upper_freq_hertz = self.y_rectangle_start_position_hertz
            lower_freq_hertz = self.y_rectangle_finish_position_hertz
        else:
            upper_freq_hertz = self.y_rectangle_finish_position_hertz
            lower_freq_hertz = self.y_rectangle_start_position_hertz
            
        if self.x_rectangle_start_position_seconds <  self.x_rectangle_finish_position_seconds:
            start_position_seconds = self.x_rectangle_start_position_seconds
            finish_position_seconds = self.x_rectangle_finish_position_seconds
        else:
            finish_position_seconds = self.x_rectangle_start_position_seconds
            start_position_seconds = self.x_rectangle_finish_position_seconds    
        
        if abs(finish_position_seconds - start_position_seconds) < 0.1:
            self.play_clip(start_position_seconds)
            return
        
        if not self.actual_confirmed.get():
            # The 'what' radio button hasn't been selected               
            messagebox.showinfo("Oops", "You haven't selected an Actual Confirmed radio button")
            return 
              
        # Create another rectangle and delete the temp_rectangle.  Had to do this to stop on_move_mouse deleting the previous finished rectangle
        if self.temp_rectangle is not None:           

            recording_id = self.recordings[self.current_recordings_index][0]           

            rectangle_bbox_x1 = functions.convert_x_or_y_postion_percent_to_x_or_y_spectrogram_image_postion(self.spectrogram_image.width(), self.x_rectangle_start_position_percent)
            rectangle_bbox_y1 = functions.convert_x_or_y_postion_percent_to_x_or_y_spectrogram_image_postion(self.spectrogram_image.height(), self.y_rectangle_start_position_percent)
            
            rectangle_bbox_x2 = functions.convert_x_or_y_postion_percent_to_x_or_y_spectrogram_image_postion(self.spectrogram_image.width(), self.x_rectangle_finish_position_percent)
            rectangle_bbox_y2 = functions.convert_x_or_y_postion_percent_to_x_or_y_spectrogram_image_postion(self.spectrogram_image.height(), self.y_rectangle_finish_position_percent)
            
            what = self.actual_confirmed.get()
            
            fill_colour = functions.get_spectrogram_rectangle_selection_colour(what)
            
            aRectangle_id = self.canvas.create_rectangle(rectangle_bbox_x1, rectangle_bbox_y1,rectangle_bbox_x2, rectangle_bbox_y2, fill=fill_colour, stipple="gray12" )
        
            self.canvas.delete(self.temp_rectangle) 
            self.canvas.itemconfig(aRectangle_id, tags=(str(recording_id), str(start_position_seconds), str(finish_position_seconds), str(lower_freq_hertz), str(upper_freq_hertz) , self.actual_confirmed.get()))
                                  
            result = functions.insert_data_into_database(recording_id, start_position_seconds, finish_position_seconds, lower_freq_hertz, upper_freq_hertz, self.actual_confirmed.get(), parameters.cacophony_user_name)
            if not result:                
                messagebox.showinfo("Oops", "Could not update database - is it locked?")   
                self.canvas.delete(aRectangle_id) 

    def rightMousePressedcallback(self, event):        
      
        selected_item_id = event.widget.find_withtag('current')[0]        

        item_type = self.canvas.type(CURRENT) # https://stackoverflow.com/questions/38982313/python-tkinter-identify-object-on-click
        if item_type != "image":
            # Deleted it from the database
                       
            tags_from_item = self.canvas.gettags(selected_item_id)
                
            recording_id = tags_from_item[0]
            start_time_seconds = tags_from_item[1]
            finish_time_seconds = tags_from_item[2]
            lower_freq_hertz = tags_from_item[3]
            upper_freq_hertz = tags_from_item[4]
            what = tags_from_item[5]                      

            functions.delete_test_data_row(recording_id, start_time_seconds, finish_time_seconds, lower_freq_hertz, upper_freq_hertz, what)
                            
            # Now delete it from the canvas
            self.canvas.delete(selected_item_id)       
        

    def retrieve_training_validation_test_data_from_database_and_add_rectangles_to_image(self):  
              
        recording_id = self.recordings[self.current_recordings_index][0]
        duration = self.recordings[self.current_recordings_index][3]
        test_data_rectangles = functions.retrieve_training_validation_test_data_from_database(recording_id)     
                          
        for test_data_rectangle in test_data_rectangles:
            recording_id = test_data_rectangle[0]
            start_time_seconds = test_data_rectangle[1]
            finish_time_seconds = test_data_rectangle[2]
            lower_freq_hertz = test_data_rectangle[3]
            upper_freq_hertz = test_data_rectangle[4]
            what = test_data_rectangle[5]            

            rectangle_bbox_x1 = functions.convert_time_in_seconds_to_x_value_for_canvas_create_method(start_time_seconds, duration, self.spectrogram_image.width())
            rectangle_bbox_y1 = functions.convert_frequency_to_y_value_for_canvas_create_method(int(self.min_freq.get()), int(self.max_freq.get()), lower_freq_hertz, self.spectrogram_image.height())  
            rectangle_bbox_x2 = functions.convert_time_in_seconds_to_x_value_for_canvas_create_method(finish_time_seconds, duration, self.spectrogram_image.width())
            rectangle_bbox_y2 = functions.convert_frequency_to_y_value_for_canvas_create_method(int(self.min_freq.get()), int(self.max_freq.get()), upper_freq_hertz, self.spectrogram_image.height())
            
            fill_colour = functions.get_spectrogram_rectangle_selection_colour(what)
           
            aRectangle_id = self.canvas.create_rectangle(rectangle_bbox_x1,rectangle_bbox_y1,rectangle_bbox_x2, rectangle_bbox_y2,fill=fill_colour, stipple="gray12")         
            
            # Attach details of test_data to the rectangles (so can 'look' at it one day - with mouse hover?)
            self.canvas.itemconfig(aRectangle_id, tags=(str(recording_id), str(start_time_seconds), str(finish_time_seconds), str(lower_freq_hertz), str(upper_freq_hertz) , what))
            
    def draw_horizontal_frequency_reference_line(self):
        ref_line_canvas_value = functions.convert_frequency_to_y_value_for_canvas_create_method(int(self.min_freq.get()), int(self.max_freq.get()), int(self.horizonal_ref_line_freq.get()), self.spectrogram_image.height())  
        ref_line_id = self.canvas.create_line(0,ref_line_canvas_value,self.spectrogram_image.width(),ref_line_canvas_value, fill='blue')       
        
    def load_all_training_recordings(self):
        self.config(bg="blue")
        self.recordings = functions.retrieve_recordings("not_march_2020", self.retrieve_recording_even_if_not_tagged_by_model_human.get(), self.retrieve_recordings_with_model_predictions.get(), self.retrieve_recordings_with_manual_analysis.get(), self.model_must_predict_what_combobox.get(), self.probability_combobox.get(), self.run_names_combo.get(), self.probability_greater_less_than.get())
        self.current_recordings_index = 0
        self.display_spectrogram()
             
    def load_feb_2020_training_recordings(self):
        self.config(bg="green")
        self.recordings = functions.retrieve_recordings("feb_2020", self.retrieve_recording_even_if_not_tagged_by_model_human.get(), self.retrieve_recordings_with_model_predictions.get(), self.retrieve_recordings_with_manual_analysis.get(), self.model_must_predict_what_combobox.get(), self.probability_combobox.get(), self.run_names_combo.get(), self.probability_greater_less_than.get())
        self.current_recordings_index = 0
        self.display_spectrogram()
        
    def load_march_2020_test_recordings(self):
        self.config(bg="yellow")
        self.recordings = functions.retrieve_recordings("march_2020", self.retrieve_recording_even_if_not_tagged_by_model_human.get(), self.retrieve_recordings_with_model_predictions.get(), self.retrieve_recordings_with_manual_analysis.get(), self.model_must_predict_what_combobox.get(), self.probability_combobox.get(), self.run_names_combo.get(), self.probability_greater_less_than.get())
        self.current_recordings_index = 0   
        self.display_spectrogram()           
                
    def display_spectrogram(self):
        try:
            self.stop_clip()
            recording_id = self.recordings[self.current_recordings_index][0]
            recording_date_time = self.recordings[self.current_recordings_index][1]
            recording_device_super_name = self.recordings[self.current_recordings_index][4]
    
            self.spectrogram_image = functions.get_spectrogram_for_creating_training_and_test_data(str(recording_id), int(self.min_freq.get()), int(self.max_freq.get()))
            
            self.image = self.canvas.create_image(0, 0, image=self.spectrogram_image, anchor=NW)   
            self.canvas.configure(height=self.spectrogram_image.height())             
           
            self.canvas.grid(row=520, rowspan = 50, columnspan=20, column=0)
            
            self.scroll_x = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scroll_x.grid(row=571, columnspan=20, column=0, sticky="ew")        
          
            self.canvas.configure(xscrollcommand=self.scroll_x.set)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                  
            self.canvas.bind("<Button-1>", self.leftMousePressedcallback)        
            self.canvas.bind("<ButtonRelease-1>", self.leftMouseReleasedcallback) 
            self.canvas.bind("<B1-Motion>", self.on_move_press)
            
            self.canvas.bind("<Button-3>", self.rightMousePressedcallback) 
            
            self.retrieve_training_validation_test_data_from_database_and_add_rectangles_to_image()    
            
            if self.show_model_predictions.get():
                self.display_model_predictions()                
            
            self.draw_horizontal_frequency_reference_line()   
            
            recording_date_time = self.recordings[self.current_recordings_index][1]
            recording_device_super_name = self.recordings[self.current_recordings_index][4]
            
            self.recording_id_and_result_place_value2.set("Recording Id: " + str(recording_id) + " at location " + recording_device_super_name) 
            self.recording_date_and_time_value.set("Date and Time: " + recording_date_time)                              
            
            self.recording_index_out_of_total_of_recordings_value.set("Result " + str(self.current_recordings_index) + " of "   + str(len(self.recordings)) + " recordings")
                        
            if self.auto_play.get():
                self.play_clip(0)                
                    
        except Exception as e:
            print(e)                        
            
    def change_spectrogram(self):
        self.stop_clip()
        if len(self.recordings) < 1:
            messagebox.showinfo("No Recordings", "Sorry, there are no recordings with the selected criteria")
            self.recording_id_and_result_place_value2.set("Recording Id: ")
            self.recording_index_out_of_total_of_recordings_value.set("Result ")            
            self.canvas.delete("all")
            
        else:
        
            recording_id = self.recordings[self.current_recordings_index][0]
            recording_date_time = self.recordings[self.current_recordings_index][1]
            recording_device_super_name = self.recordings[self.current_recordings_index][4]
    
            self.spectrogram_image = functions.get_spectrogram_for_creating_training_and_test_data(str(recording_id), int(self.min_freq.get()), int(self.max_freq.get()))  
            self.canvas.configure(height=self.spectrogram_image.height())  
            self.image = self.canvas.create_image(0, 0, image=self.spectrogram_image, anchor=NW)  
                                 
    
            self.retrieve_training_validation_test_data_from_database_and_add_rectangles_to_image()  
            
            if self.show_model_predictions.get():
                self.display_model_predictions()               
            
            self.draw_horizontal_frequency_reference_line()   
                        
            self.recording_id_and_result_place_value2.set("Recording Id: " + str(recording_id) + " at location " + recording_device_super_name) 
            self.recording_date_and_time_value.set("Date and Time: " + recording_date_time) 
            self.recording_index_out_of_total_of_recordings_value.set("Result " + str(self.current_recordings_index) + " of "   + str(len(self.recordings)) + " recordings")
            
            if self.auto_play.get():
                self.play_clip(0)     
    
    def previous_recording(self):
        if self.current_recordings_index > 0:
            self.current_recordings_index = self.current_recordings_index -1
            self.change_spectrogram()        
           
    def next_recording(self):
        if self.current_recordings_index < (len(self.recordings) - 1): # Did have -2, but not sure why now!
            self.current_recordings_index = self.current_recordings_index + 1
            self.change_spectrogram() 
            
    def next_recording_and_mark_as_analysed(self):
        recording_id = self.recordings[self.current_recordings_index][0]
        what = self.marked_as_what_combobox.get()
        result = functions.mark_recording_as_analysed(recording_id, what, parameters.cacophony_user_name)
        if result:
            self.next_recording()
            # Also reset the radio button to the same as what we are currently marking the recording as analaysed as (because that is the most likely rectangle to add)
            self.actual_confirmed.set(self.marked_as_what_combobox.get())
        else:
            messagebox.showinfo("Oops", "Could not update database - is it locked?")   
                
    def confirm_actual(self):  
       
        print('self.actual_confirmed.get() ', self.actual_confirmed.get()) 
        # Set the what box - used to enter row in test_data_recording_analysis table     
#         self.marked_as_what.set(self.actual_confirmed.get())
            
        
    def play_clip(self,start_position_seconds):
        
        # Stop any clip that is currently playing
        functions.stop_clip()        
               
        self.canvas.delete("audio_position_line") # otherwise can have multiple lines on the spectrogram
        
        duration = self.recordings[self.current_recordings_index][3]
 
        x_canvas_pos = functions.convert_pos_in_seconds_to_canvas_position(self.spectrogram_image.width(), start_position_seconds, duration)  
       
        self.aLine_id = self.canvas.create_line(x_canvas_pos, 0,x_canvas_pos, self.spectrogram_image.height(), fill='red', tags = "audio_position_line")
        # Now play the clip
       
        functions.play_clip(str(self.recordings[self.current_recordings_index][0]), start_position_seconds,duration, self.play_filtered.get(),int(self.min_freq.get()), int(self.max_freq.get()))
        
        # https://www.youtube.com/watch?v=f8sKAot-15w
        # Need to calculate the speed to move the line, how many pixels per second
        speed = self.spectrogram_image.width()/duration/20 #  # Will update every 0.1 seconds

        self.playing = True 
        while self.playing:
            self.canvas.move(self.aLine_id,speed,0)
            self.update()
#             time.sleep(0.05)
#             time.sleep(0.0499) # line was moving fractionally slow
#             time.sleep(0.049) # line was moving fractionally slow
#             time.sleep(0.0495) # line was moving fractionally slow
            time.sleep(0.049) # line was moving fractionally slow
        
    def stop_clip(self):
        self.playing = False 
        functions.stop_clip()    
        
    def load_specific_recording_from_creating_test_data(self):
        recording_to_load_id = int(self.specific_recording_id.get())
        print(recording_to_load_id)
        
        # find the index of the recording with this recording_id
        length = len(self.recordings)
        for i in range(length):
            recording_id = int(self.recordings[i][0])
            if recording_id == recording_to_load_id:
                self.current_recordings_index = i
                # Now load this recording
                self.change_spectrogram()
                return
            
        # If it gets here then it didn't find the recording so display a message
        messagebox.showinfo("Oops", f"Recording id {recording_to_load_id} is not one of the currently loaded recordings")
        
        
                
    def load_specific_recording_by_result_index(self):  
        self.current_recordings_index = int(self.specific_recording_index.get())
        self.change_spectrogram()
        # Now change 
     
    def display_model_predictions(self):
        recording_id = self.recordings[self.current_recordings_index][0]
        duration_of_recording = self.recordings[self.current_recordings_index][3]
        
        model_predictions = functions.get_model_predictions(recording_id, self.run_names_combo.get()) 
        for model_prediction in model_predictions:
            startTime = model_prediction[0]
#             duration_of_prediction =  model_prediction[1] 
            duration_of_prediction = 0.3
            predictedByModel = model_prediction[2]
            probability = model_prediction[3]
            actual_confirmed = model_prediction[4]
            
            predictionsToDisplay = self.model_must_predict_what_combobox.get()
            
            if predictedByModel == predictionsToDisplay:
                
                twenty_percent_of_spectrogram_height = self.spectrogram_image.height() * 0.10
            
                rectangle_bbox_x1 = functions.convert_time_in_seconds_to_x_value_for_canvas_create_method(startTime, duration_of_recording, self.spectrogram_image.width())
                rectangle_bbox_y1 = functions.convert_frequency_to_y_value_for_canvas_create_method(int(self.min_freq.get()), int(self.max_freq.get()), int(self.min_freq.get()) + twenty_percent_of_spectrogram_height, self.spectrogram_image.height())  
                rectangle_bbox_x2 = functions.convert_time_in_seconds_to_x_value_for_canvas_create_method(startTime + duration_of_prediction, duration_of_recording, self.spectrogram_image.width())
                rectangle_bbox_y2 = functions.convert_frequency_to_y_value_for_canvas_create_method(int(self.min_freq.get()), int(self.max_freq.get()), int(self.max_freq.get()) - twenty_percent_of_spectrogram_height, self.spectrogram_image.height())
                
                fill_colour = functions.get_spectrogram_rectangle_selection_colour(predictedByModel)
               
                aRectangle_id = self.canvas.create_rectangle(rectangle_bbox_x1,rectangle_bbox_y1,rectangle_bbox_x2, rectangle_bbox_y2,fill=fill_colour, stipple="gray12")  
                
            if actual_confirmed:
                # Going to draw a slightly shorter/wider rectangle
                thirty_percent_of_spectrogram_height = self.spectrogram_image.height() * 0.30
                duration_of_prediction = 0.6
                
                rectangle2_bbox_x1 = functions.convert_time_in_seconds_to_x_value_for_canvas_create_method(startTime, duration_of_recording, self.spectrogram_image.width())
                rectangle2_bbox_y1 = functions.convert_frequency_to_y_value_for_canvas_create_method(int(self.min_freq.get()), int(self.max_freq.get()), int(self.min_freq.get()) + thirty_percent_of_spectrogram_height, self.spectrogram_image.height())  
                rectangle2_bbox_x2 = functions.convert_time_in_seconds_to_x_value_for_canvas_create_method(startTime + duration_of_prediction, duration_of_recording, self.spectrogram_image.width())
                rectangle2_bbox_y2 = functions.convert_frequency_to_y_value_for_canvas_create_method(int(self.min_freq.get()), int(self.max_freq.get()), int(self.max_freq.get()) - thirty_percent_of_spectrogram_height, self.spectrogram_image.height())
                
                fill_colour2 = functions.get_spectrogram_rectangle_selection_colour(predictedByModel)
                   
                aRectangle2_id = self.canvas.create_rectangle(rectangle2_bbox_x1,rectangle2_bbox_y1,rectangle2_bbox_x2, rectangle2_bbox_y2,fill=fill_colour2, stipple="gray12")  
                                       
                
    def retrieve_all_test_recordings_checkbox_pressed(self): 
            self.retrieve_recordings_with_model_predictions.set(False)             
            self.retrieve_recordings_with_manual_analysis.set(False)        
            
#     def probability_greater_than_checkbox_pressed(self):
#         self.probability_greater_than.set(True)
#         self.probability_less_than.set(False)
#         
#     def probability_less_than_checkbox_pressed(self):
#         self.probability_greater_than.set(False)
#         self.probability_less_than.set(True)
        
     
    def retrieve_model_or_manual_analysis_recordings_checkbox_pressed(self): 
        self.retrieve_recording_even_if_not_tagged_by_model_human.set(False)                
           
    
    def __init__(self, parent, controller):
        # https://stackoverflow.com/questions/7727804/tkinter-using-scrollbars-on-a-canvas
        # https://stackoverflow.com/questions/43731784/tkinter-canvas-scrollbar-with-grid
        # https://riptutorial.com/tkinter/example/27784/scrolling-a-canvas-widget-horizontally-and-vertically
                              
        tk.Frame.__init__(self, parent)    
        
        self.playing = False
        
        self.unique_model_run_names = functions.get_unique_model_run_names()
            
        self.temp_rectangle = None
        self.current_recordings_index = 0
        
        title_label = ttk.Label(self, text="Create Training OR Test Data", font=LARGE_FONT)
        title_label.grid(column=0, columnspan=1, row=0) 
                
        instruction_1 = ttk.Label(self, text="1) Decide what frequency range you want to focus on.", font=LARGE_FONT)
        instruction_1.grid(column=0, columnspan=2, row=1)  
        
        min_freq_label = ttk.Label(self, text="Enter the minimum frequency (Hz)")
        min_freq_label.grid(column=0, columnspan=1, row=50)             

        self.min_freq = StringVar(value=str(parameters.morepork_min_freq_display))
        min_freq_entry = tk.Entry(self,  textvariable=self.min_freq, width=30)
        min_freq_entry.grid(column=0, columnspan=1, row=51)        
        
        max_freq_label = ttk.Label(self, text="Enter the maximum frequency (Hz)")
        max_freq_label.grid(column=1, columnspan=1, row=50)             

        self.max_freq = StringVar(value=str(parameters.morepork_max_freq_display))
        max_freq_entry = tk.Entry(self,  textvariable=self.max_freq, width=30)
        max_freq_entry.grid(column=1, columnspan=1, row=51)
        
        horizonal_ref_line_freq_label = ttk.Label(self, text="Enter the frequency (Hz) of the horizontal reference line")
        horizonal_ref_line_freq_label.grid(column=2, columnspan=1, row=50)
        
        select_probability_label_1 = ttk.Label(self, text="Select Predicted probability condition")
        select_probability_label_1.grid(column=3, columnspan=1, row=50)
        
        
        self.horizonal_ref_line_freq = StringVar(value=str(parameters.morepork_expected_freq_display))      
        horizonal_ref_line_freq_entry = tk.Entry(self,  textvariable=self.horizonal_ref_line_freq, width=30)
        horizonal_ref_line_freq_entry.grid(column=2, columnspan=1, row=51)  
        
        self.canvas = tk.Canvas(self, width=10, height=10)

        self.canvas.config(height=parameters.test_data_canvas_height)
        self.canvas.config(width=parameters.test_data_canvas_width)         
        
        instruction_2 = ttk.Label(self, text="2) Use controls below to filter the recordings to use and then - Press one of the 3 'Load .... recordings' buttons", font=LARGE_FONT)
        instruction_2.grid(column=0, columnspan=3, row=60)   
        
        run_names_label = ttk.Label(self, text="Model Run Names")
        run_names_label.grid(column=2, columnspan=1, row=61)      
        
#         run_names_label = ttk.Label(self, text="Model Run Names2")
#         run_names_label.grid(column=2, columnspan=1, row=62)      
                                    
        self.run_name = StringVar()
        self.run_names_combo = ttk.Combobox(self, textvariable=self.run_name, values=self.unique_model_run_names, width=50)
        
        self.run_names_combo.grid(column=2, columnspan=1,row=62) 
       
        
        if len(self.unique_model_run_names) > 0:
            self.run_names_combo.current(0)           
#             self.run_names_combo.current(len(self.unique_model_run_names) - 1)    
      
        
        self.model_must_predict_what_combobox = ttk.Combobox(self,  values=parameters.class_names.split(","), width=30)                   
        self.model_must_predict_what_combobox.grid(column=2, columnspan=1, row=64)  
        self.model_must_predict_what_combobox.current(0)
        
        self.retrieve_recording_even_if_not_tagged_by_model_human = BooleanVar()
        retrieve_all_test_validation_recordings_Checkbuttton = Checkbutton(self, text="Retrieve all recordings (even if not tagged by model/human)", variable=self.retrieve_recording_even_if_not_tagged_by_model_human, command=lambda: self.retrieve_all_test_recordings_checkbox_pressed())
        retrieve_all_test_validation_recordings_Checkbuttton.grid(column=0, columnspan=2, row=65)
        self.retrieve_recording_even_if_not_tagged_by_model_human.set(True)
        
        self.retrieve_recordings_with_model_predictions = BooleanVar()
        retrieve_recordings_with_model_predictions_Checkbuttton = Checkbutton(self, text="Recordings must have a model prediction of these values", variable=self.retrieve_recordings_with_model_predictions, command=lambda: self.retrieve_model_or_manual_analysis_recordings_checkbox_pressed())
        retrieve_recordings_with_model_predictions_Checkbuttton.grid(column=2, columnspan=2, row=65)
        self.retrieve_recordings_with_model_predictions.set(False)
        
        self.show_model_predictions = BooleanVar()
        show_model_predictions_Checkbuttton = Checkbutton(self, text="Show (these) model predictions", variable=self.show_model_predictions)
        show_model_predictions_Checkbuttton.grid(column=2, columnspan=1, row=66)
        self.show_model_predictions.set(True)
        
        select_probability_label_2 = ttk.Label(self, text="Binary model range is 0 (certain) to 0.5 (uncertain)")
        select_probability_label_2.grid(column=3, columnspan=1, row=51)
        
        self.probability_greater_less_than = StringVar()
        self.probability_greater_less_than.set("greater")        
      
        probability_greater_than_Radiobutton = Radiobutton(self, text="Greater than >=", variable=self.probability_greater_less_than, value="greater")
        probability_greater_than_Radiobutton.grid(column=3, columnspan=1, row=60)       
        
        probability_less_than_Radiobutton = Radiobutton(self, text="Less than <=", variable=self.probability_greater_less_than, value="less")
        probability_less_than_Radiobutton.grid(column=3, columnspan=1, row=61)

        
        self.probability_combobox = ttk.Combobox(self,  values=["not_used", "0","0.1", "0.2","0.3","0.4","0.5","0.6","0.7","0.8","0.9"], width=30)                   
        self.probability_combobox.grid(column=3, columnspan=1, row=62)  
        self.probability_combobox.current(0)
        
        self.retrieve_recordings_with_manual_analysis = BooleanVar()
        retrieve_recordings_with_manual_analysis_Checkbuttton = Checkbutton(self, text="Recording must have manual analysis", variable=self.retrieve_recordings_with_manual_analysis, command=lambda: self.retrieve_model_or_manual_analysis_recordings_checkbox_pressed())
        retrieve_recordings_with_manual_analysis_Checkbuttton.grid(column=4, columnspan=1, row=65)
        self.retrieve_recordings_with_manual_analysis.set(False) 
               
        load_all_recordings_except_march_2020_button = ttk.Button(self, text="Load all training/validation recordings (All recordings except March 2020 Test recordings) - Blue background", command=lambda: self.load_all_training_recordings()) # https://effbot.org/tkinterbook/canvas.htm))
        load_all_recordings_except_march_2020_button.grid(column=0, columnspan=2, row=70) 
        
        load_feb_2020_training_recordings_button = ttk.Button(self, text="Load Feb 2020 training/validation recordings - Green background", command=lambda: self.load_feb_2020_training_recordings()) # https://effbot.org/tkinterbook/canvas.htm))
        load_feb_2020_training_recordings_button.grid(column=0, columnspan=2, row=75) 
        
        load_march_2020_test_recordings_button = ttk.Button(self, text="Load March 2020 Test recordings - Yellow background", command=lambda: self.load_march_2020_test_recordings()) # https://effbot.org/tkinterbook/canvas.htm))
        load_march_2020_test_recordings_button.grid(column=0, columnspan=2, row=80) 
       
#         first_not_yet_analysed_recording_button = ttk.Button(self, text="First Recording - not yet analysed", command=lambda: self.reload_recordings_for_creating_test_data(self.marked_as_what_combobox.get())) # https://effbot.org/tkinterbook/canvas.htm))
#         first_not_yet_analysed_recording_button.grid(column=0, columnspan=1, row=100) 
#         
#         first_recording_button = ttk.Button(self, text="First Recording (includes already analysed)", command=lambda: self.reload_recordings_for_creating_test_data(None)) # https://effbot.org/tkinterbook/canvas.htm))
#         first_recording_button.grid(column=0, columnspan=1, row=110) 
                       
        previous_recording_button = ttk.Button(self, text="Previous Recording", command=lambda: self.previous_recording()) # https://effbot.org/tkinterbook/canvas.htm))
        previous_recording_button.grid(column=1, columnspan=1, row=100) 
        
        play_button = ttk.Button(self, text="Play Recording", command=lambda: self.play_clip(0))
        play_button.grid(column=2, columnspan=1, row=100)        
        
        # https://effbot.org/tkinterbook/checkbutton.htm
        self.play_filtered = BooleanVar()
        play_filtered_Checkbuttton = Checkbutton(self, text="Apply Filter to Playback", variable=self.play_filtered)
        play_filtered_Checkbuttton.grid(column=2, columnspan=1, row=110)
        
        play_button = ttk.Button(self, text="Stop Playing", command=lambda: self.stop_clip())
        play_button.grid(column=3, columnspan=1, row=100)
        
        self.recording_index_out_of_total_of_recordings_value = tk.StringVar()
        recording_index_label = ttk.Label(self, textvariable=self.recording_index_out_of_total_of_recordings_value) 
        recording_index_label.grid(column=3, columnspan=1, row=110) 
        self.recording_index_out_of_total_of_recordings_value.set("Result ") 
                 
        next_recording_button = ttk.Button(self, text="Next Recording (Do NOT mark as Analysed)", command=lambda: self.next_recording()) # https://effbot.org/tkinterbook/canvas.htm))
        next_recording_button.grid(column=4, columnspan=1, row=100)       
        
        mark_as_what_message_text = "Pressing the green 'Next Recording (Mark as Analysed) will record in the database that this recording has been analysed for the sound currently selected in the combobox below"
        mark_as_what_message_msg = tk.Message(self, text = mark_as_what_message_text)
        mark_as_what_message_msg.config(width=300)   
        mark_as_what_message_msg.grid(column=5, row=85)  
        
        self.marked_as_what_combobox = ttk.Combobox(self,  values=parameters.class_names.split(","), width=30)                   
        self.marked_as_what_combobox.grid(column=5, columnspan=1, row=100)  
        self.marked_as_what_combobox.current(0) 
        
        # Note I used a different button type for this button so I could change the background colour
        next_recording_button = tk.Button(self, text="Next Recording (Mark as Analysed)", bg='green', command=lambda: self.next_recording_and_mark_as_analysed()) # https://effbot.org/tkinterbook/canvas.htm))
        next_recording_button.grid(column=5, columnspan=1, row=110)  
        
        self.auto_play = BooleanVar()
        auto_play_Checkbuttton = Checkbutton(self, text="Automatically play", variable=self.auto_play)
        auto_play_Checkbuttton.grid(column=6, columnspan=1, row=100) 
        
        self.specific_recording_id = StringVar(value='544235')   
        specific_recording_id_entry = tk.Entry(self,  textvariable=self.specific_recording_id, width=30)
        specific_recording_id_entry.grid(column=4, columnspan=1, row=150)        
        
        retrieve_specific_recording_id_button = ttk.Button(self, text="Retrieve this recording (has to be in loaded data)", command=lambda: self.load_specific_recording_from_creating_test_data())
        retrieve_specific_recording_id_button.grid(column=4, columnspan=1, row=151)          

        self.specific_recording_index = StringVar(value='0')      
        specific_recording_index_entry = tk.Entry(self,  textvariable=self.specific_recording_index, width=30)
        specific_recording_index_entry.grid(column=5, columnspan=1, row=150)        
        
        retrieve_specific_recording_index_button = ttk.Button(self, text="Retrieve this recording (result index)", command=lambda: self.load_specific_recording_by_result_index())
        retrieve_specific_recording_index_button.grid(column=5, columnspan=1, row=151, rowspan=1)   
        
        self.recording_id_and_result_place_value2 = tk.StringVar()
        recording_id_label = ttk.Label(self, textvariable=self.recording_id_and_result_place_value2) 
        recording_id_label.grid(column=6, columnspan=1, row=150) 
        self.recording_id_and_result_place_value2.set("Recording Id") 
        
        self.recording_date_and_time_value = tk.StringVar()
        recording_date_and_time_label = ttk.Label(self, textvariable=self.recording_date_and_time_value) 
        recording_date_and_time_label.grid(column=6, columnspan=1, row=151) 
        self.recording_date_and_time_value.set("Date and Time: ")        

        
        
        actual_label_confirmed = ttk.Label(self, text="3) Use the radio buttons below to select the noise/call and then use left mouse button to click and drag on spectrogram.", font=LARGE_FONT)
        actual_label_confirmed.grid(column=0, columnspan=3, row=180)
        
        actual_label_confirmed = ttk.Label(self, text="3b) When you release the left mouse button, the noise/call will be saved to the database")
        actual_label_confirmed.grid(column=0, columnspan=3, row=181)
        
        actual_label_confirmed = ttk.Label(self, text="3c) Click with the right mouse button to delete the noise/call from the database")
        actual_label_confirmed.grid(column=0, columnspan=3, row=182)
              
        self.actual_confirmed = tk.StringVar()

        actual_confirmed_radio_button_morepork_classic = ttk.Radiobutton(self,text='Morepork more-pork (green box)', variable=self.actual_confirmed, value='morepork_more-pork',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_morepork_classic.grid(column=0, columnspan=1, row=202)               
        
        actual_confirmed_radio_button_unknown = ttk.Radiobutton(self,text='Unknown', variable=self.actual_confirmed, value='unknown',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_unknown.grid(column=1, columnspan=1, row=202)
        actual_confirmed_radio_button_dove = ttk.Radiobutton(self,text='Dove', variable=self.actual_confirmed, value='dove',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_dove.grid(column=2, columnspan=1, row=202)   
        actual_confirmed_radio_button_duck = ttk.Radiobutton(self,text='Duck', variable=self.actual_confirmed, value='duck',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_duck.grid(column=3, columnspan=1, row=202) 
        actual_confirmed_radio_button_dog = ttk.Radiobutton(self,text='Dog', variable=self.actual_confirmed, value='dog',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_dog.grid(column=4, columnspan=1, row=202) 
        actual_confirmed_radio_button_human = ttk.Radiobutton(self,text='Human', variable=self.actual_confirmed, value='human',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_human.grid(column=5, columnspan=1, row=202)   
        actual_confirmed_radio_button_siren = ttk.Radiobutton(self,text='Siren', variable=self.actual_confirmed, value='siren',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_siren.grid(column=6, columnspan=1, row=202)
        
        actual_confirmed_radio_button_bird = ttk.Radiobutton(self,text='Bird', variable=self.actual_confirmed, value='bird',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_bird.grid(column=0, columnspan=1, row=203) 
        actual_confirmed_radio_button_car = ttk.Radiobutton(self,text='Car', variable=self.actual_confirmed, value='car',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_car.grid(column=1, columnspan=1, row=203)
        actual_confirmed_radio_button_rumble = ttk.Radiobutton(self,text='Rumble', variable=self.actual_confirmed, value='rumble',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_rumble.grid(column=2, columnspan=1, row=203)
        actual_confirmed_radio_button_water = ttk.Radiobutton(self,text='Water', variable=self.actual_confirmed, value='water',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_water.grid(column=3, columnspan=1, row=203)
        actual_confirmed_radio_button_hand_saw = ttk.Radiobutton(self,text='Hand saw', variable=self.actual_confirmed, value='hand_saw',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_hand_saw.grid(column=4, columnspan=1, row=203) 
        actual_confirmed_radio_button_white_noise = ttk.Radiobutton(self,text='White noise', variable=self.actual_confirmed, value='white_noise',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_white_noise.grid(column=5, columnspan=1, row=203)
        actual_confirmed_radio_button_plane = ttk.Radiobutton(self,text='Plane', variable=self.actual_confirmed, value='plane',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_plane.grid(column=6, columnspan=1, row=203)
        
        actual_confirmed_radio_button_cow = ttk.Radiobutton(self,text='Cow or Sheep', variable=self.actual_confirmed, value='cow_sheep',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_cow.grid(column=0, columnspan=1, row=204) 
        actual_confirmed_radio_button_buzzy_insect = ttk.Radiobutton(self,text='Buzzy insect', variable=self.actual_confirmed, value='buzzy_insect',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_buzzy_insect.grid(column=1, columnspan=1, row=204) 
        actual_confirmed_radio_morepork_more_pork_part = ttk.Radiobutton(self,text='Morepork more-pork Part (blue box)', variable=self.actual_confirmed, value='morepork_more-pork_part',command=lambda: self.confirm_actual())
        actual_confirmed_radio_morepork_more_pork_part.grid(column=2, columnspan=1, row=204) 
        actual_confirmed_radio_button_hammering = ttk.Radiobutton(self,text='Hammering', variable=self.actual_confirmed, value='hammering',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_hammering.grid(column=3, columnspan=1, row=204)  
        actual_confirmed_radio_button_frog = ttk.Radiobutton(self,text='Frog', variable=self.actual_confirmed, value='frog',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_frog.grid(column=4, columnspan=1, row=204)
        actual_confirmed_radio_button_chainsaw = ttk.Radiobutton(self,text='Chainsaw', variable=self.actual_confirmed, value='chainsaw',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_chainsaw.grid(column=5, columnspan=1, row=204) 
        actual_confirmed_radio_button_crackle = ttk.Radiobutton(self,text='Crackle', variable=self.actual_confirmed, value='crackle',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_crackle.grid(column=6, columnspan=1, row=204)  
        
        actual_confirmed_radio_button_car_horn = ttk.Radiobutton(self,text='Car horn', variable=self.actual_confirmed, value='car_horn',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_car_horn.grid(column=0, columnspan=1, row=205)
        actual_confirmed_radio_button_fire_work = ttk.Radiobutton(self,text='Fire work', variable=self.actual_confirmed, value='fire_work',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_fire_work.grid(column=1, columnspan=1, row=205)
        actual_confirmed_radio_button_maybe_morepork_more_pork = ttk.Radiobutton(self,text='Maybe Morepork more-pork (yellow box)', variable=self.actual_confirmed, value='maybe_morepork_more-pork',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_maybe_morepork_more_pork.grid(column=2, columnspan=1, row=205)
        actual_confirmed_radio_button_music = ttk.Radiobutton(self,text='Music', variable=self.actual_confirmed, value='music',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_music.grid(column=3, columnspan=1, row=205) 
        actual_confirmed_radio_button_music = ttk.Radiobutton(self,text='Morepork croaking (cyan2 box)', variable=self.actual_confirmed, value='morepork_croaking',command=lambda: self.confirm_actual())
        actual_confirmed_radio_button_music.grid(column=4, columnspan=1, row=205)  
        
        test_validation_data_analysis_label = ttk.Label(self, text="Test validation data analysis", font=LARGE_FONT)
        test_validation_data_analysis_label.grid(column=0, columnspan=1, row=300)        
             
        back_to_home_button = ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame(HomePage))
        back_to_home_button.grid(column=0, columnspan=1, row=1000) 
        
class UpdateTrainingDataUsingAModelsPredictions(tk.Frame):    
    
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        self.current_training_data_array_pos = 0
        self.current_model_run_result_ID = 0        
        
        self.unique_model_run_names = functions.get_unique_model_run_names() 
        self.unique_locations = functions.get_unique_locations('recordings')            
                    
        title_label = ttk.Label(self, text="Update Feb 2020 training data from model predictions", font=LARGE_FONT)
        title_label.grid(column=0, columnspan=1, row=0)           
                
        refresh_model_run_names_button = ttk.Button(self, text="Update actual_predicted for select Model Run",command=lambda: update_predicted_from_training_data())
        refresh_model_run_names_button.grid(column=0, columnspan=1, row=3) 
        
        run_names_label = ttk.Label(self, text="Model Run Names")
        run_names_label.grid(column=1, columnspan=1, row=2)      
                                    
        self.run_name = StringVar()
        self.run_names_combo = ttk.Combobox(self, textvariable=self.run_name, values=self.unique_model_run_names)
        
        if len(self.unique_model_run_names) > 0:
            self.run_names_combo.current(0)
            self.run_names_combo.grid(column=1, columnspan=1,row=3) 
            self.run_names_combo.current(len(self.unique_model_run_names) - 1)       
            
        location_filter_label = ttk.Label(self, text="Location Filter")
        location_filter_label.grid(column=2, columnspan=1, row=2)      
                                    
        self.location_filter = StringVar()
        self.location_filter_combo = ttk.Combobox(self, textvariable=self.location_filter, values=self.unique_locations)        
                                    
        self.recording_id_filter = StringVar()
        
        if len(self.unique_locations) > 0:
            self.location_filter_combo.current(0)
            self.location_filter_combo.grid(column=2, columnspan=1,row=3) 
            
        recording_id_filter_label = ttk.Label(self, text="Recording ID Filter (leave blank if not used)")
        recording_id_filter_label.grid(column=3, columnspan=1, row=2)   
        
        self.recording_id_filter_value = StringVar(value='')
        self.recording_id_filter_entry = tk.Entry(self,  textvariable=self.recording_id_filter_value, width=10).grid(column=3, columnspan=1,row=3)   
   
        actual_confirmed_filter_label = ttk.Label(self, text="Filter - Current Actual Confirmed", font=LARGE_FONT)
        actual_confirmed_filter_label.grid(column=0, columnspan=1, row=4)   
        
        # http://effbot.org/tkinterbook/checkbutton.htm
        self.actual_confirmed_other = StringVar() 
        actual_confirmed_other_than_checkbox = ttk.Checkbutton(self,text='Everything OTHER than selected', variable=self.actual_confirmed_other, onvalue="on", offvalue="off")
        actual_confirmed_other_than_checkbox.grid(column=1, columnspan=1, row=4)
        self.actual_confirmed_other.set('off')
             
        self.actual_confirmed_filter = tk.StringVar()
        actual_confirmed_filter_radio_button_none = ttk.Radiobutton(self,text='Not Used', variable=self.actual_confirmed_filter, value='not_used')
        actual_confirmed_filter_radio_button_none.grid(column=0, columnspan=1, row=13)        
        actual_confirmed_filter_radio_button_null = ttk.Radiobutton(self,text='Null Filter (ie nothing in DB table)', variable=self.actual_confirmed_filter, value='IS NULL')
        actual_confirmed_filter_radio_button_null.grid(column=0, columnspan=1, row=14)        
        actual_confirmed_filter_radio_button_morepork_classic = ttk.Radiobutton(self,text='Morepork more-pork', variable=self.actual_confirmed_filter, value='morepork_more-pork')
        actual_confirmed_filter_radio_button_morepork_classic.grid(column=0, columnspan=1, row=15)
        actual_confirmed_filter_radio_button_unknown = ttk.Radiobutton(self,text='Unknown', variable=self.actual_confirmed_filter, value='unknown')
        actual_confirmed_filter_radio_button_unknown.grid(column=0, columnspan=1, row=16) 
        actual_confirmed_filter_radio_button_dove = ttk.Radiobutton(self,text='Dove', variable=self.actual_confirmed_filter, value='dove')
        actual_confirmed_filter_radio_button_dove.grid(column=0, columnspan=1, row=17) 
        actual_confirmed_filter_radio_button_duck = ttk.Radiobutton(self,text='Duck', variable=self.actual_confirmed_filter, value='duck')
        actual_confirmed_filter_radio_button_duck.grid(column=0, columnspan=1, row=18) 
        actual_confirmed_filter_radio_button_dog = ttk.Radiobutton(self,text='Dog', variable=self.actual_confirmed_filter, value='dog')
        actual_confirmed_filter_radio_button_dog.grid(column=0, columnspan=1, row=19) 
        actual_confirmed_filter_radio_button_human = ttk.Radiobutton(self,text='Human', variable=self.actual_confirmed_filter, value='human')
        actual_confirmed_filter_radio_button_human.grid(column=0, columnspan=1, row=20) 
        actual_confirmed_filter_radio_button_siren = ttk.Radiobutton(self,text='Siren', variable=self.actual_confirmed_filter, value='siren')
        actual_confirmed_filter_radio_button_siren.grid(column=0, columnspan=1, row=21) 
        actual_confirmed_filter_radio_button_bird = ttk.Radiobutton(self,text='Bird', variable=self.actual_confirmed_filter, value='bird')
        actual_confirmed_filter_radio_button_bird.grid(column=0, columnspan=1, row=22) 
        actual_confirmed_filter_radio_button_car = ttk.Radiobutton(self,text='Car', variable=self.actual_confirmed_filter, value='car')
        actual_confirmed_filter_radio_button_car.grid(column=0, columnspan=1, row=23) 
        actual_confirmed_filter_radio_button_rumble = ttk.Radiobutton(self,text='Rumble', variable=self.actual_confirmed_filter, value='rumble')
        actual_confirmed_filter_radio_button_rumble.grid(column=0, columnspan=1, row=24)
        actual_confirmed_filter_radio_button_water = ttk.Radiobutton(self,text='Water', variable=self.actual_confirmed_filter, value='water')
        actual_confirmed_filter_radio_button_water.grid(column=0, columnspan=1, row=25)
        actual_confirmed_filter_radio_button_hand_saw = ttk.Radiobutton(self,text='Hand saw', variable=self.actual_confirmed_filter, value='hand_saw')
        actual_confirmed_filter_radio_button_hand_saw.grid(column=0, columnspan=1, row=26)
        actual_confirmed_filter_radio_button_wind = ttk.Radiobutton(self,text='Wind', variable=self.actual_confirmed_filter, value='wind')
        actual_confirmed_filter_radio_button_wind.grid(column=0, columnspan=1, row=27)        
        
        actual_confirmed_filter_radio_button_white_noise = ttk.Radiobutton(self,text='White noise', variable=self.actual_confirmed_filter, value='white_noise')
        actual_confirmed_filter_radio_button_white_noise.grid(column=1, columnspan=1, row=13)
        actual_confirmed_filter_radio_button_plane = ttk.Radiobutton(self,text='Plane', variable=self.actual_confirmed_filter, value='plane')
        actual_confirmed_filter_radio_button_plane.grid(column=1, columnspan=1, row=14)
        actual_confirmed_filter_radio_button_cow = ttk.Radiobutton(self,text='Cow or Sheep', variable=self.actual_confirmed_filter, value='cow_sheep')
        actual_confirmed_filter_radio_button_cow.grid(column=1, columnspan=1, row=15)
        actual_confirmed_filter_radio_button_buzzy_insect = ttk.Radiobutton(self,text='Buzzy_insect', variable=self.actual_confirmed_filter, value='buzzy_insect')
        actual_confirmed_filter_radio_button_buzzy_insect.grid(column=1, columnspan=1, row=16)
        actual_confirmed_filter_radio_button_morepork_more_pork_part = ttk.Radiobutton(self,text='Morepork more-pork Part', variable=self.actual_confirmed_filter, value='morepork_more-pork_part')
        actual_confirmed_filter_radio_button_morepork_more_pork_part.grid(column=1, columnspan=1, row=17)
        actual_confirmed_filter_radio_button_hammering = ttk.Radiobutton(self,text='Hammering', variable=self.actual_confirmed_filter, value='hammering')
        actual_confirmed_filter_radio_button_hammering.grid(column=1, columnspan=1, row=18)
        actual_confirmed_filter_radio_button_frog = ttk.Radiobutton(self,text='Frog', variable=self.actual_confirmed_filter, value='frog')
        actual_confirmed_filter_radio_button_frog.grid(column=1, columnspan=1, row=19)
        actual_confirmed_filter_radio_button_chainsaw = ttk.Radiobutton(self,text='Chainsaw', variable=self.actual_confirmed_filter, value='chainsaw')
        actual_confirmed_filter_radio_button_chainsaw.grid(column=1, columnspan=1, row=20)
        actual_confirmed_filter_radio_button_crackle = ttk.Radiobutton(self,text='Crackle', variable=self.actual_confirmed_filter, value='crackle')
        actual_confirmed_filter_radio_button_crackle.grid(column=1, columnspan=1, row=21)
        actual_confirmed_filter_radio_button_car_horn = ttk.Radiobutton(self,text='Car horn', variable=self.actual_confirmed_filter, value='car_horn')
        actual_confirmed_filter_radio_button_car_horn.grid(column=1, columnspan=1, row=22)
        actual_confirmed_filter_radio_button_fire_work = ttk.Radiobutton(self,text='Fire work', variable=self.actual_confirmed_filter, value='fire_work')
        actual_confirmed_filter_radio_button_fire_work.grid(column=1, columnspan=1, row=23)
        actual_confirmed_filter_radio_button_maybe_morepork_more_pork = ttk.Radiobutton(self,text='Maybe Morepork more-pork', variable=self.actual_confirmed_filter, value='maybe_morepork_more-pork')
        actual_confirmed_filter_radio_button_maybe_morepork_more_pork.grid(column=1, columnspan=1, row=24)
        actual_confirmed_filter_radio_button_music = ttk.Radiobutton(self,text='Music', variable=self.actual_confirmed_filter, value='music')
        actual_confirmed_filter_radio_button_music.grid(column=1, columnspan=1, row=25)
        actual_confirmed_filter_radio_button_morepork_croaking = ttk.Radiobutton(self,text='Morepork croaking', variable=self.actual_confirmed_filter, value='morepork_croaking')
        actual_confirmed_filter_radio_button_morepork_croaking.grid(column=1, columnspan=1, row=26)
        
        self.actual_confirmed_filter.set('not_used')
        
        predicted_filter_label = ttk.Label(self, text="Filter - Predicted", font=LARGE_FONT)
        predicted_filter_label.grid(column=2, columnspan=1, row=4)  
        
        self.predicted_other = StringVar()
        predicted_other_than_checkbox = ttk.Checkbutton(self,text='Everything OTHER than selected', variable=self.predicted_other, onvalue="on", offvalue="off")
        predicted_other_than_checkbox.grid(column=3, columnspan=1, row=4)
        self.predicted_other.set('off')
             
        self.predicted_filter = tk.StringVar()        
        predicted_filter_radio_button_none = ttk.Radiobutton(self,text='Not Used', variable=self.predicted_filter, value='not_used')
        predicted_filter_radio_button_none.grid(column=2, columnspan=1, row=13)
        predicted_filter_radio_button_morepork_classic = ttk.Radiobutton(self,text='Morepork more-pork', variable=self.predicted_filter, value='morepork_more-pork')
        predicted_filter_radio_button_morepork_classic.grid(column=2, columnspan=1, row=14)
        predicted_filter_radio_button_unknown = ttk.Radiobutton(self,text='Unknown', variable=self.predicted_filter, value='unknown')
        predicted_filter_radio_button_unknown.grid(column=2, columnspan=1, row=15) 
        predicted_filter_radio_button_dove = ttk.Radiobutton(self,text='Dove', variable=self.predicted_filter, value='dove')
        predicted_filter_radio_button_dove.grid(column=2, columnspan=1, row=16) 
        predicted_filter_radio_button_duck = ttk.Radiobutton(self,text='Duck', variable=self.predicted_filter, value='duck')
        predicted_filter_radio_button_duck.grid(column=2, columnspan=1, row=17) 
        predicted_filter_radio_button_dog = ttk.Radiobutton(self,text='Dog', variable=self.predicted_filter, value='dog')
        predicted_filter_radio_button_dog.grid(column=2, columnspan=1, row=18) 
        predicted_filter_radio_button_human = ttk.Radiobutton(self,text='Human', variable=self.predicted_filter, value='human')
        predicted_filter_radio_button_human.grid(column=2, columnspan=1, row=19) 
        predicted_filter_radio_button_siren = ttk.Radiobutton(self,text='Siren', variable=self.predicted_filter, value='siren')
        predicted_filter_radio_button_siren.grid(column=2, columnspan=1, row=20) 
        predicted_filter_radio_button_bird = ttk.Radiobutton(self,text='Bird', variable=self.predicted_filter, value='bird')
        predicted_filter_radio_button_bird.grid(column=2, columnspan=1, row=21) 
        predicted_filter_radio_button_car = ttk.Radiobutton(self,text='Car', variable=self.predicted_filter, value='car')
        predicted_filter_radio_button_car.grid(column=2, columnspan=1, row=22)
        predicted_filter_radio_button_rumble = ttk.Radiobutton(self,text='Rumble', variable=self.predicted_filter, value='rumble')
        predicted_filter_radio_button_rumble.grid(column=2, columnspan=1, row=23)
        predicted_filter_radio_button_water = ttk.Radiobutton(self,text='Water', variable=self.predicted_filter, value='water')
        predicted_filter_radio_button_water.grid(column=2, columnspan=1, row=24)
        predicted_filter_radio_button_hand_saw = ttk.Radiobutton(self,text='Hand saw', variable=self.predicted_filter, value='hand_saw')
        predicted_filter_radio_button_hand_saw.grid(column=2, columnspan=1, row=25) 
        predicted_filter_radio_button_wind = ttk.Radiobutton(self,text='Wind', variable=self.predicted_filter, value='wind')
        predicted_filter_radio_button_wind.grid(column=2, columnspan=1, row=26) 
        
        
        predicted_filter_radio_button_white_noise = ttk.Radiobutton(self,text='White noise', variable=self.predicted_filter, value='white_noise')
        predicted_filter_radio_button_white_noise.grid(column=3, columnspan=1, row=13)  
        predicted_filter_radio_button_plane = ttk.Radiobutton(self,text='Plane', variable=self.predicted_filter, value='plane')
        predicted_filter_radio_button_plane.grid(column=3, columnspan=1, row=14)
        predicted_filter_radio_button_cow = ttk.Radiobutton(self,text='Cow or Sheep', variable=self.predicted_filter, value='cow_sheep')
        predicted_filter_radio_button_cow.grid(column=3, columnspan=1, row=15)  
        predicted_filter_radio_button_buzzy_insect = ttk.Radiobutton(self,text='Buzzy insect', variable=self.predicted_filter, value='buzzy_insect')
        predicted_filter_radio_button_buzzy_insect.grid(column=3, columnspan=1, row=16)
        predicted_filter_radio_button_morepork_more_pork_part = ttk.Radiobutton(self,text='Morepork more-pork Part', variable=self.predicted_filter, value='morepork_more-pork_part')
        predicted_filter_radio_button_morepork_more_pork_part.grid(column=3, columnspan=1, row=17) 
        predicted_filter_radio_button_hammering = ttk.Radiobutton(self,text='Hammering', variable=self.predicted_filter, value='hammering')
        predicted_filter_radio_button_hammering.grid(column=3, columnspan=1, row=18)
        predicted_filter_radio_button_frog = ttk.Radiobutton(self,text='Frog', variable=self.predicted_filter, value='frog')
        predicted_filter_radio_button_frog.grid(column=3, columnspan=1, row=19)  
        predicted_filter_radio_button_chainsaw = ttk.Radiobutton(self,text='Chainsaw', variable=self.predicted_filter, value='chainsaw')
        predicted_filter_radio_button_chainsaw.grid(column=3, columnspan=1, row=20) 
        predicted_filter_radio_button_crackle = ttk.Radiobutton(self,text='Crackle', variable=self.predicted_filter, value='crackle')
        predicted_filter_radio_button_crackle.grid(column=3, columnspan=1, row=21)  
        predicted_filter_radio_button_car_horn = ttk.Radiobutton(self,text='Car horn', variable=self.predicted_filter, value='car_horn')
        predicted_filter_radio_button_car_horn.grid(column=3, columnspan=1, row=22)
        predicted_filter_radio_button_fire_work = ttk.Radiobutton(self,text='Fire work', variable=self.predicted_filter, value='fire_work')
        predicted_filter_radio_button_fire_work.grid(column=3, columnspan=1, row=23) 
        predicted_filter_radio_button_maybe_morepork_more_pork = ttk.Radiobutton(self,text='Maybe Morepork more-pork', variable=self.predicted_filter, value='maybe_morepork_more-pork')
        predicted_filter_radio_button_maybe_morepork_more_pork.grid(column=3, columnspan=1, row=24)  
        predicted_filter_radio_button_music = ttk.Radiobutton(self,text='Music', variable=self.predicted_filter, value='music')
        predicted_filter_radio_button_music.grid(column=3, columnspan=1, row=25) 
        predicted_filter_radio_button_morepork_croaking = ttk.Radiobutton(self,text='Morepork croaking', variable=self.predicted_filter, value='morepork-croaking')
        predicted_filter_radio_button_morepork_croaking.grid(column=3, columnspan=1, row=26) 
        
        self.predicted_filter.set('not_used')
        
        run_probability_label = ttk.Label(self, text="Probability")
        run_probability_label.grid(column=2, columnspan=1, row=125)  
        
        self.predicted_probability_filter = tk.StringVar()
        predicted_probability_filter_radio_button_greater_than = ttk.Radiobutton(self,text='Greater than', variable=self.predicted_probability_filter, value='greater_than')
        predicted_probability_filter_radio_button_greater_than.grid(column=2, columnspan=1, row=126)
        predicted_probability_filter_radio_button_less_than = ttk.Radiobutton(self,text='Less than', variable=self.predicted_probability_filter, value='less_than')
        predicted_probability_filter_radio_button_less_than.grid(column=3, columnspan=1, row=126)
        self.predicted_probability_filter_value = StringVar(value='')
        self.predicted_probability_filter_entry = tk.Entry(self,  textvariable=self.predicted_probability_filter_value, width=10).grid(column=2, columnspan=1,row=127)    
        predicted_probability_filter_radio_button_not_used = ttk.Radiobutton(self,text='Not used', variable=self.predicted_probability_filter, value='not_used',command=lambda: self.predicted_probability_filter_value.set(''))
        predicted_probability_filter_radio_button_not_used.grid(column=3, columnspan=1, row=127)
       
        self.predicted_probability_filter.set('not_used')        
        
        load_run_results_button = ttk.Button(self, text="Load Run Results using Filters",command=lambda: get_model_run_result_data())
        load_run_results_button.grid(column=0, columnspan=1, row=133) 
        
        self.number_of_results_label_value = tk.StringVar()
        number_of_results_label_for_value = ttk.Label(self, textvariable=self.number_of_results_label_value)
        number_of_results_label_for_value.grid(column=0, columnspan=1, row=134)   
        
        self.recording_id_and_result_place_value = tk.StringVar()
        recording_id_label = ttk.Label(self, textvariable=self.recording_id_and_result_place_value) 
        recording_id_label.grid(column=0, columnspan=1, row=135) 
        self.recording_id_and_result_place_value.set("Recording Id")
                   
        start_time_label = ttk.Label(self, text="Start Time")
        start_time_label.grid(column=1, columnspan=1, row=134)        
        self.start_time = StringVar(value='0.0')
        self.start_time_entry = tk.Entry(self,  textvariable=self.start_time, width=30).grid(column=1, columnspan=1,row=135)
        
        self.location_recorded_value = tk.StringVar()
        location_recorded_label = ttk.Label(self, textvariable=self.location_recorded_value) 
        location_recorded_label.grid(column=2, columnspan=1, row=134) 
        self.location_recorded_value.set("Location: ")   
        
        self.when_recorded_value = tk.StringVar()
        when_recorded_label = ttk.Label(self, textvariable=self.when_recorded_value) 
        when_recorded_label.grid(column=2, columnspan=1, row=135) 
        self.when_recorded_value.set("When: ")     
        
        self.spectrogram_label = ttk.Label(self, image=None)
        self.spectrogram_label.grid(column=0, columnspan=1, row=136)
        
        self.waveform_label = ttk.Label(self, image=None)
        self.waveform_label.grid(column=1, columnspan=1, row=136)
        
        self.apply_bandpass_filter = StringVar() 
        apply_bandpass_filter_checkbox = ttk.Checkbutton(self,text='Apply bandpass filter', variable=self.apply_bandpass_filter, onvalue="on", offvalue="off")
        apply_bandpass_filter_checkbox.grid(column=2, columnspan=1, row=136)
        self.apply_bandpass_filter.set('off')
        
       
        actual_label_confirmed = ttk.Label(self, text="SET New Actual Confirmed", font=LARGE_FONT)
        actual_label_confirmed.grid(column=0, columnspan=2, row=240)
              
        self.actual_confirmed = tk.StringVar()

        actual_confirmed_radio_button_morepork_classic = ttk.Radiobutton(self,text='Morepork more-pork', variable=self.actual_confirmed, value='morepork_more-pork',command=lambda: confirm_actual())
        actual_confirmed_radio_button_morepork_classic.grid(column=0, columnspan=1, row=242) 
        actual_confirmed_radio_button_unknown = ttk.Radiobutton(self,text='Unknown', variable=self.actual_confirmed, value='unknown',command=lambda: confirm_actual())
        actual_confirmed_radio_button_unknown.grid(column=0, columnspan=1, row=243)
        actual_confirmed_radio_button_dove = ttk.Radiobutton(self,text='Dove', variable=self.actual_confirmed, value='dove',command=lambda: confirm_actual())
        actual_confirmed_radio_button_dove.grid(column=0, columnspan=1, row=244)   
        actual_confirmed_radio_button_duck = ttk.Radiobutton(self,text='Duck', variable=self.actual_confirmed, value='duck',command=lambda: confirm_actual())
        actual_confirmed_radio_button_duck.grid(column=0, columnspan=1, row=245) 
        actual_confirmed_radio_button_dog = ttk.Radiobutton(self,text='Dog', variable=self.actual_confirmed, value='dog',command=lambda: confirm_actual())
        actual_confirmed_radio_button_dog.grid(column=0, columnspan=1, row=246) 
        actual_confirmed_radio_button_human = ttk.Radiobutton(self,text='Human', variable=self.actual_confirmed, value='human',command=lambda: confirm_actual())
        actual_confirmed_radio_button_human.grid(column=0, columnspan=1, row=247)   
        actual_confirmed_radio_button_siren = ttk.Radiobutton(self,text='Siren', variable=self.actual_confirmed, value='siren',command=lambda: confirm_actual())
        actual_confirmed_radio_button_siren.grid(column=0, columnspan=1, row=248)
        actual_confirmed_radio_button_bird = ttk.Radiobutton(self,text='Bird', variable=self.actual_confirmed, value='bird',command=lambda: confirm_actual())
        actual_confirmed_radio_button_bird.grid(column=0, columnspan=1, row=249) 
        actual_confirmed_radio_button_car = ttk.Radiobutton(self,text='Car', variable=self.actual_confirmed, value='car',command=lambda: confirm_actual())
        actual_confirmed_radio_button_car.grid(column=0, columnspan=1, row=250)
        actual_confirmed_radio_button_rumble = ttk.Radiobutton(self,text='Rumble', variable=self.actual_confirmed, value='rumble',command=lambda: confirm_actual())
        actual_confirmed_radio_button_rumble.grid(column=0, columnspan=1, row=251)
        actual_confirmed_radio_button_water = ttk.Radiobutton(self,text='Water', variable=self.actual_confirmed, value='water',command=lambda: confirm_actual())
        actual_confirmed_radio_button_water.grid(column=0, columnspan=1, row=252)
        actual_confirmed_radio_button_hand_saw = ttk.Radiobutton(self,text='Hand saw', variable=self.actual_confirmed, value='hand_saw',command=lambda: confirm_actual())
        actual_confirmed_radio_button_hand_saw.grid(column=0, columnspan=1, row=253)
        actual_confirmed_radio_button_wind = ttk.Radiobutton(self,text='Wind', variable=self.actual_confirmed, value='wind',command=lambda: confirm_actual())
        actual_confirmed_radio_button_wind.grid(column=0, columnspan=1, row=254)
        
        actual_confirmed_radio_button_white_noise = ttk.Radiobutton(self,text='White noise', variable=self.actual_confirmed, value='white_noise',command=lambda: confirm_actual())
        actual_confirmed_radio_button_white_noise.grid(column=1, columnspan=1, row=242)
        actual_confirmed_radio_button_plane = ttk.Radiobutton(self,text='Plane', variable=self.actual_confirmed, value='plane',command=lambda: confirm_actual())
        actual_confirmed_radio_button_plane.grid(column=1, columnspan=1, row=243)
        actual_confirmed_radio_button_cow = ttk.Radiobutton(self,text='Cow or Sheep', variable=self.actual_confirmed, value='cow_sheep',command=lambda: confirm_actual())
        actual_confirmed_radio_button_cow.grid(column=1, columnspan=1, row=244) 
        actual_confirmed_radio_button_buzzy_insect = ttk.Radiobutton(self,text='Buzzy insect', variable=self.actual_confirmed, value='buzzy_insect',command=lambda: confirm_actual())
        actual_confirmed_radio_button_buzzy_insect.grid(column=1, columnspan=1, row=245) 
        actual_confirmed_radio_morepork_more_pork_part = ttk.Radiobutton(self,text='Morepork more-pork Part', variable=self.actual_confirmed, value='morepork_more-pork_part',command=lambda: confirm_actual())
        actual_confirmed_radio_morepork_more_pork_part.grid(column=1, columnspan=1, row=246) 
        actual_confirmed_radio_button_hammering = ttk.Radiobutton(self,text='Hammering', variable=self.actual_confirmed, value='hammering',command=lambda: confirm_actual())
        actual_confirmed_radio_button_hammering.grid(column=1, columnspan=1, row=247)  
        actual_confirmed_radio_button_frog = ttk.Radiobutton(self,text='Frog', variable=self.actual_confirmed, value='frog',command=lambda: confirm_actual())
        actual_confirmed_radio_button_frog.grid(column=1, columnspan=1, row=248)
        actual_confirmed_radio_button_chainsaw = ttk.Radiobutton(self,text='Chainsaw', variable=self.actual_confirmed, value='chainsaw',command=lambda: confirm_actual())
        actual_confirmed_radio_button_chainsaw.grid(column=1, columnspan=1, row=249) 
        actual_confirmed_radio_button_crackle = ttk.Radiobutton(self,text='Crackle', variable=self.actual_confirmed, value='crackle',command=lambda: confirm_actual())
        actual_confirmed_radio_button_crackle.grid(column=1, columnspan=1, row=250)  
        actual_confirmed_radio_button_car_horn = ttk.Radiobutton(self,text='Car horn', variable=self.actual_confirmed, value='car_horn',command=lambda: confirm_actual())
        actual_confirmed_radio_button_car_horn.grid(column=1, columnspan=1, row=251)
        actual_confirmed_radio_button_fire_work = ttk.Radiobutton(self,text='Fire work', variable=self.actual_confirmed, value='fire_work',command=lambda: confirm_actual())
        actual_confirmed_radio_button_fire_work.grid(column=1, columnspan=1, row=252)
        actual_confirmed_radio_button_maybe_morepork_more_pork = ttk.Radiobutton(self,text='Maybe Morepork more-pork', variable=self.actual_confirmed, value='maybe_morepork_more-pork',command=lambda: confirm_actual())
        actual_confirmed_radio_button_maybe_morepork_more_pork.grid(column=1, columnspan=1, row=253)
        actual_confirmed_radio_button_music = ttk.Radiobutton(self,text='Music', variable=self.actual_confirmed, value='music',command=lambda: confirm_actual())
        actual_confirmed_radio_button_music.grid(column=1, columnspan=1, row=254)
        
        actual_confirmed_radio_button_morepork_croaking = ttk.Radiobutton(self,text='Morepork croaking', variable=self.actual_confirmed, value='morepork_croaking',command=lambda: confirm_actual())
        actual_confirmed_radio_button_morepork_croaking.grid(column=2, columnspan=1, row=243)       
       
        predicted_label = ttk.Label(self, text="Predicted by model", font=LARGE_FONT)
        predicted_label.grid(column=2, columnspan=1, row=240)       
        
        self.predicted_label_value = tk.StringVar()
        predicted_label_value_for_value = ttk.Label(self, textvariable=self.predicted_label_value)
        predicted_label_value_for_value.grid(column=2, columnspan=1, row=241) 
        
        previous_button = ttk.Button(self, text="Previous", command=lambda: previous_model_run_result())
        previous_button.grid(column=2, columnspan=1, row=250)
                            
        play_again_button = ttk.Button(self, text="Play Again", command=lambda: play_clip())
        play_again_button.grid(column=2, columnspan=1, row=252)        
                          
        confirm_next_button = ttk.Button(self, text="Next", command=lambda: next_model_run_result())
        confirm_next_button.grid(column=3, columnspan=1, row=250)
        
        unselect_button = ttk.Button(self, text="Unselect", command=lambda: unselect_actual_confirmed())
        unselect_button.grid(column=3, columnspan=1, row=254)
        
        back_to_home_button = ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame(HomePage))
        back_to_home_button.grid(column=2, columnspan=1, row=254) 
                      
        def confirm_actual():
            print('self.actual_confirmed.get() ', self.actual_confirmed.get())
            functions.update_model_run_result(self.current_model_run_result_ID, self.actual_confirmed.get()) 
            functions.update_training_data(self.run_names_combo.get(), self.current_training_data_recording_id, self.current_training_data_start_time, self.current_training_data_duration, self.device_super_name, self.device_name, self.recordingDateTime, self.recordingDateTimeNZ, self.actual_confirmed.get())
        
        def unselect_actual_confirmed():
            self.actual_confirmed.set('not_used')
            confirm_actual()
        
            
        def update_predicted_from_training_data():            
            selected_model_run = self.run_names_combo.get()            
            functions.update_model_run_result_actual_confirmed_from_training_data(selected_model_run)            
                
        def get_model_run_result_data(): 
             
            # Need to check that the user didn't enter a probability without selecting the greater or lessor filter
            if (self.predicted_probability_filter.get() == 'not_used'):
                print('self.predicted_probability_filter_value.get() ', self.predicted_probability_filter_value.get())
                if self.predicted_probability_filter_value.get():
                    showinfo("Select Probability Sign", "Either clear the probability value, or select a probability radio button")
                    return
    
            print('self.actual_confirmed_other ', self.actual_confirmed_other.get())
            print('self.predicted_other ', self.predicted_other.get())            
            
            self.model_run_result_data = functions.get_model_run_results_to_create_feb_2020_training_data(self.run_names_combo.get(), self.actual_confirmed_filter.get(), self.predicted_filter.get(), self.predicted_probability_filter.get(), self.predicted_probability_filter_value.get(), self.location_filter_combo.get(), self.actual_confirmed_other.get(), self.predicted_other.get(), self.recording_id_filter_value.get())
                                                                 
            number_of_results_returned = len(self.model_run_result_data)
            print('number_of_results_returned ', number_of_results_returned)
            self.number_of_results_label_value.set("Number of results: " + str(number_of_results_returned))
            if number_of_results_returned > 0:
                first_result = self.model_run_result_data[0]
                self.current_model_run_result_ID = first_result[0]
                print('self.current_model_run_result_ID ', self.current_model_run_result_ID) 
                self.current_training_data_array_pos = 0                    
                load_current_model_run_result()       

        def next_model_run_result():
          
            if self.current_training_data_array_pos < (len(self.model_run_result_data)) -1:
                self.current_training_data_array_pos +=1
                print('current_training_data_array_pos ', self.current_training_data_array_pos)
                self.current_model_run_result_ID = self.model_run_result_data[self.current_training_data_array_pos][0]
                load_current_model_run_result()
             
        def previous_model_run_result():
            if self.current_training_data_array_pos > 0:
                self.current_training_data_array_pos -=1
                print('current_training_data_array_pos ', self.current_training_data_array_pos)
                self.current_model_run_result_ID = self.model_run_result_data[self.current_training_data_array_pos][0]
                load_current_model_run_result()
                
        def play_clip():

            if self.apply_bandpass_filter.get() == "on":
                applyBandPass = True
            else:
                applyBandPass = False        
        
            functions.play_clip(str(self.current_training_data_recording_id), float(self.current_training_data_start_time),self.current_training_data_duration, applyBandPass, parameters.morepork_min_freq, parameters.morepork_max_freq)
            
                     
        def display_images():
            run_folder = parameters.run_folder
            self.spectrogram_image = functions.get_single_create_focused_mel_spectrogram(self.current_training_data_recording_id, self.current_training_data_start_time, self.current_training_data_duration, run_folder)
            self.waveform_image = functions.get_single_waveform_image(self.current_training_data_recording_id, self.current_training_data_start_time, self.current_training_data_duration)            
            
            self.spectrogram_label.config(image=self.spectrogram_image)
            self.waveform_label.config(image=self.waveform_image)
            
        def load_current_model_run_result():  

            self.single_training_data = functions.get_model_run_result(int(self.current_model_run_result_ID))

            self.current_training_data_recording_id = self.single_training_data[1]    
            
            self.recording_id_and_result_place_value.set("Recording Id: " + str(self.current_training_data_recording_id) + " Result: " + str(self.current_training_data_array_pos))              

            device_super_name, recordingDateTime = functions.get_single_recording_info_from_local_db(self.current_training_data_recording_id)
            
            self.location_recorded_value.set(str(device_super_name))
            self.when_recorded_value.set(str(recordingDateTime))
            
            self.current_training_data_start_time = self.single_training_data[2]
            self.start_time.set(self.current_training_data_start_time)
            
            self.current_training_data_duration = self.single_training_data[3]
#             self.current_model_run_name_duration = 0.7 # The original length of 1.5 is too long for a morepork  
        
            self.current_training_data_predicted = self.single_training_data[4]             
            self.current_training_data_actual_confirmed = self.single_training_data[5]  

            if self.single_training_data[6]:
                self.current_training_data_probability = "{0:.2f}".format(self.single_training_data[6])
            else:
                self.current_training_data_probability = '?'
                 
   
            self.device_super_name = self.single_training_data[7]  
            self.device_name = self.single_training_data[8]  
            self.recordingDateTime = self.single_training_data[9]  
            self.recordingDateTimeNZ = self.single_training_data[10]              
            
            # Set the radio button
            print('current_training_data_actual_confirmed', self.current_training_data_actual_confirmed)
            if self.current_training_data_actual_confirmed == 'morepork_more-pork':
                self.actual_confirmed.set('morepork_more-pork')
            elif self.current_training_data_actual_confirmed == 'unknown':
                self.actual_confirmed.set('unknown')
            elif self.current_training_data_actual_confirmed == 'dove':
                self.actual_confirmed.set('dove')
            elif self.current_training_data_actual_confirmed == 'duck':
                self.actual_confirmed.set('duck')
            elif self.current_training_data_actual_confirmed == 'dog':
                self.actual_confirmed.set('dog')
            elif self.current_training_data_actual_confirmed == 'human':
                self.actual_confirmed.set('human')
            elif self.current_training_data_actual_confirmed == 'siren':
                self.actual_confirmed.set('siren')
            elif self.current_training_data_actual_confirmed == 'bird':
                self.actual_confirmed.set('bird')
            elif self.current_training_data_actual_confirmed == 'car':
                self.actual_confirmed.set('car')
            elif self.current_training_data_actual_confirmed == 'rumble':
                self.actual_confirmed.set('rumble')
            elif self.current_training_data_actual_confirmed == 'water':
                self.actual_confirmed.set('water')
                
            elif self.current_training_data_actual_confirmed == 'white_noise':
                self.actual_confirmed.set('white_noise')
            elif self.current_training_data_actual_confirmed == 'plane':
                self.actual_confirmed.set('plane')
#             elif self.current_training_data_actual_confirmed == 'cow':
#                 self.actual_confirmed.set('cow') 
            elif self.current_training_data_actual_confirmed == 'cow_sheep':
                self.actual_confirmed.set('cow_sheep') 
            elif self.current_training_data_actual_confirmed == 'buzzy_insect':
                self.actual_confirmed.set('buzzy_insect')
            elif self.current_training_data_actual_confirmed == 'morepork_more-pork_part':
                self.actual_confirmed.set('morepork_more-pork_part')
            elif self.current_training_data_actual_confirmed == 'hammering':
                self.actual_confirmed.set('hammering')
            elif self.current_training_data_actual_confirmed == 'frog':
                self.actual_confirmed.set('frog') 
            elif self.current_training_data_actual_confirmed == 'chainsaw':
                self.actual_confirmed.set('chainsaw') 
            elif self.current_training_data_actual_confirmed == 'crackle':
                self.actual_confirmed.set('crackle')
            elif self.current_training_data_actual_confirmed == 'car_horn':
                self.actual_confirmed.set('car_horn')
            elif self.current_training_data_actual_confirmed == 'fire_work':
                self.actual_confirmed.set('fire_work')
            elif self.current_training_data_actual_confirmed == 'maybe_morepork_more-pork':
                self.actual_confirmed.set('maybe_morepork_more-pork')
            elif self.current_training_data_actual_confirmed == 'music':
                self.actual_confirmed.set('music')
            elif self.current_training_data_actual_confirmed == 'morepork_croaking':
                self.actual_confirmed.set('morepork_croaking')
            elif self.current_training_data_actual_confirmed == 'wind':
                self.actual_confirmed.set('wind')
            else:
                self.actual_confirmed.set('not_set')   
                
            self.predicted_label_value.set(self.current_training_data_predicted + ' with ' + self.current_training_data_probability + ' probability')
            
            threading.Thread(target=play_clip(), args=(1,)).start()
            threading.Thread(target=display_images(), args=(1,)).start()
        
app = Main_GUI()
app.mainloop() 