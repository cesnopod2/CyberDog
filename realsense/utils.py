import pyrealsense2 as rs
import numpy as np 
import queue
import traitlets
import threading

class RealsenseData(traitlets.HasTraits):
    
    rgb_data_value = traitlets.Any()

class Realsense:
    def __init__(self, enable_single_frameset):

        self.rgb_data_queue = queue.Queue()
        self.depth_data_queue = queue.Queue()
        self.data = RealsenseData()
        self.config = rs.config()
        self.pipeline = rs.pipeline()
        self.pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        self.pipeline_profile = self.config.resolve(self.pipeline_wrapper)
        self.device = self.pipeline_profile.get_device()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.data.rgb_data_value = np.empty((640,480,3), dtype=np.int8)
        self.cam_thread = None
        self.enable_single_frameset = enable_single_frameset

    def get_info_device(self):
        print(str(self.device.get_info(rs.camera_info.product_line)))    

    

    def stream_camera(self):
        self.pipeline.start(self.config)
        try:
            while True:
                frames = self.pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                if not depth_frame or not color_frame:
                    continue

                # Convert images to numpy arrays
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                # self.data_value.value = color_image
                self.data.rgb_data_value = color_image
                self.rgb_data_queue.put(color_image)
        finally:
            self.pipeline.stop()

    def start(self):
        self.cam_thread = threading.Thread(target=self.stream_camera)
        self.cam_thread.start()
        

    def stop(self):
        if hasattr(self, 'cam_thread'):
            self.cam_thread.join()

    @property
    def enable_single_frameset(self):
        return self._enable_single_frameset
    
    @enable_single_frameset.setter
    def enable_single_frameset(self,value):
        self._enable_single_frameset = value
        if value == True: 
            self.filt = rs.save_single_frameset()
        else : 
            self.filt = None
        