from tkinter import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import cv2
import imutils
from utils import Realsense
from tkinter import messagebox
import os
import time
from datetime import datetime


class App(Frame):
    def __init__(self, master, window_title,  dataset_root):
        super().__init__(master)
        self.master = master
        self.master.title(window_title)
        self.pack(side=RIGHT)
        
        self.image_canva = Frame(master)
        self.image_canva.pack()

        self.canva_left = Frame(master)
        self.canva_left.pack()

        self.camera = Realsense(enable_single_frameset=False)
        self.camera.start()
        
        self.current_frame = None
        self.delay = 15
        self.update_cam_view()
        self.create_dataset_directory(root=dataset_root)
        
        #
        self.is_recording = False
        self.blinking = False
        self.blink_state = False
        self.recorder = None
        self.record_name = None
        self.elapsed_time = 0
        self.tags = []
        #
        self.create_widgets_tag()
        self.create_widgets_camera()
        self.master.mainloop()
    


    def create_dataset_directory(self, root):
        self.tag_directory = os.path.join(root, "dataset/tag_data")
        self.video_directory = os.path.join(root, "dataset/video_data")
        os.makedirs(self.tag_directory, exist_ok=True)
        os.makedirs(self.video_directory, exist_ok=True)


    def create_widgets_tag(self):
        self.tag_input = Entry(self, width=30)
        self.tag_input.grid(row=0, column=0, padx=10, pady=10)

        # Button to add tag
        self.add_button = Button(self, text="Add Tag", command=self.add_tag)
        self.add_button.grid(row=0, column=1, padx=10, pady=10)

        # Listbox to show tags
        self.tags_listbox = Listbox(self, width=30, height=10, selectmode=SINGLE)
        self.tags_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Button to remove selected tag
        self.remove_button = Button(self, text="Remove Selected Tag", command=self.remove_tag)
        self.remove_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Button to clear all tags
        self.clear_button = Button(self, text="Clear All Tags", command=self.clear_tags)
        self.clear_button.grid(row=3, column=0, columnspan=2, pady=10)


    def create_widgets_camera(self):
        self.image_canvas = Canvas(self.image_canva, width = 640, height = 480)
        self.image_canvas.pack()

        self.play_button = Button(self.canva_left, text="▶ Play", command=self.play_action,
                                     font=("Arial", 14, "bold"), fg="white", bg="#4CAF50", relief="raised",
                                     width=10, height=2)
        self.play_button.grid(row=1, column=0, padx=20, pady=20)

        # Stop Button
        self.stop_button = Button(self.canva_left, text="■ Stop", command=self.stop_action,
                                     font=("Arial", 14, "bold"), fg="white", bg="#F44336", relief="raised",
                                     width=10, height=2)
        self.stop_button.grid(row=1, column=1, padx=20, pady=20)

        # Save Button
        self.save_button = Button(self.canva_left, text="💾 Save", command=self.save_action,
                                     font=("Arial", 14, "bold"), fg="white", bg="#2196F3", relief="raised",
                                     width=10, height=2)
        self.save_button.grid(row=1, column=2, padx=20, pady=20)

        # Spanshot Button
        self.save_button = Button(self.canva_left, text="📸 Shot", command=self.save_action,
                                     font=("Arial", 14, "bold"), fg="white", bg="#2196F3", relief="raised",
                                     width=10, height=2)
        self.save_button.grid(row=1, column=3, padx=20, pady=20)

        # REC Indicator Label
        self.rec_label = Label(self.canva_left, text="REC", font=("Arial", 24, "bold"), fg="white",
                                  width=10, height=2)
        self.rec_label.grid(row=2, column=0, columnspan=3, padx=20, pady=20)
        self.rec_label.grid_forget()  # Hide REC label initially


        self.timer_label = Label(self.canva_left, text="00:00", font=("Arial", 18), fg="red", width=10, height=2)
        self.timer_label.grid(row=2, column=2, padx=20, pady=20)
        self.timer_label.grid_forget() # Hide timer label initially


    def update_cam_view(self):
        if not self.camera.rgb_data_queue.empty():
            item  = self.camera.rgb_data_queue.get()
            self.current_frame = item
            item = cv2.cvtColor(item, cv2.COLOR_RGB2BGR)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(item))
            self.image_canvas.create_image(0, 0, image = self.photo, anchor = NW)
            if self.recorder is not None and self.is_recording is True:
                self.recorder.write(item)
        self.master.after(self.delay, self.update_cam_view)

    def play_action(self):
        if self.recorder is None : 
            self.record_name = self.create_name()
            self.recorder = self.initialize_recording(path=os.path.join(self.video_directory, self.record_name+".mp4"))

        self.is_recording = True
        self.blinking = True
        self.blink_state = False  # Start blinking
        self.rec_label.grid()  # Show the REC label
        self.timer_label.grid()
        self.blink_rec()  # Start the blinking effect
        self.update_timer()  # Start the timer update
        

    def stop_action(self):
        self.is_recording = False
        self.blinking = False
        self.rec_label.grid_forget()  # Hide the REC label when stopped
        self.timer_label.grid_forget() # Hide the timer label when stopped

    def save_action(self):
        messagebox.showinfo("Save", "Save action triggered!")
        
        self.elapsed_time = 0 
        self.is_recording = False
        self.blinking = False
        self.recorder.release()
        self.recorder = None
        if self.record_name is not None :
            # txt_file_path = osself.record_name  
            with open(os.path.join(self.tag_directory, self.record_name+".txt"), "w") as f:
                for tag in self.tags:
                    f.write(tag+"\n")
                
        self.clear_tags()
        # fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        # out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640,480))
     
        self.rec_label.grid_forget() 
        self.timer_label.grid_forget() 

    def blink_rec(self):
        """Method to make the REC indicator blink."""
        if self.blinking:
            if self.blink_state:
                self.rec_label.config(fg="white")  # Hide the REC text (simulating blinking off)
            else:
                self.rec_label.config(fg="red")  # Show REC text in red (simulating blinking on)
            self.blink_state = not self.blink_state  # Toggle the blink state
            self.rec_label.after(500, self.blink_rec)  # Call this method again after 500ms for blinking effect


    def update_timer(self):
        """Update the timer every second."""
        if self.is_recording:
            self.elapsed_time += 1  # Increase elapsed time by 1 second
            self.timer_label.config(text=self.format_time(self.elapsed_time))  # Update the timer label
            self.after(1000, self.update_timer)  # Call this method again after 1000ms (1 second)

    def format_time(self, seconds):
        """Format the time in MM:SS format."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def add_tag(self):
        tag = self.tag_input.get().strip()
        if tag:
            if tag not in self.tags:
                self.tags.append(tag)
                self.update_tags_listbox()
                self.tag_input.delete(0, END)
            else:
                messagebox.showinfo("Tag Exists", "This tag is already added.")
        else:
            messagebox.showwarning("Empty Input", "Please enter a valid tag.")

    def remove_tag(self):
        try:
            selected_index = self.tags_listbox.curselection()[0]
            tag = self.tags_listbox.get(selected_index)
            self.tags.remove(tag)
            self.update_tags_listbox()
        except IndexError:
            messagebox.showwarning("No Selection", "Please select a tag to remove.")

    def clear_tags(self):
        self.tags.clear()
        self.update_tags_listbox()

    def update_tags_listbox(self):
        self.tags_listbox.delete(0, END)
        for tag in self.tags:
            self.tags_listbox.insert(END, tag)

    def initialize_recording(self, path):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # hardcoded now 
        out = cv2.VideoWriter(path, fourcc, 30.0, (640,480))
        return out

    @staticmethod
    def create_name():
        name = datetime.now().strftime('%Y_%m_%d_%H-%M-%S')
        name = "video_" + name
        return name 


if __name__ == '__main__':
    dataset_dir = "/home/filip/cyberdog_git/realsense"
    widnow =Tk()
    App(master=widnow, window_title="CyberDog", dataset_root=dataset_dir)
    # cam = Realsense(enable_single_frameset=False)
    # print(cam.config))