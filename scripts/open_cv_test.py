#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import collections
import pathlib
import numpy
import cv2
import struct
import matplotlib.pyplot
import mm.text_utilities
import mm.misc_utilities

#------------------------------------------------------------------------------    
VideoPropertiesOpenCV = collections.namedtuple('VideoPropertiesOpenCV', ['width', 'height', 'frame_rate', 'frame_count', 'codec_4cc', 'retrieve_format','convert_rgb'])

#------------------------------------------------------------------------------    
def get_video_properties(video_capture):    
    return VideoPropertiesOpenCV(
            height          = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT),
            width           = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH),
            frame_rate      = video_capture.get(cv2.CAP_PROP_FPS),
            frame_count     = video_capture.get(cv2.CAP_PROP_FRAME_COUNT),
            codec_4cc       = bytes(struct.pack("f", video_capture.get(cv2.CAP_PROP_FOURCC))),
            retrieve_format = str(video_capture.get(cv2.CAP_PROP_FORMAT)),
            convert_rgb     = bool(video_capture.get(cv2.CAP_PROP_CONVERT_RGB)))

#------------------------------------------------------------------------------    
def standardize_frame(frame_og):    
    standard_height = 720.0

    (og_width, og_height, _og_depth) = frame_og.shape
    resize_ratio = standard_height / og_height
    return cv2.resize(frame_og, (int(standard_height), int(og_width*resize_ratio)))
# # I/O Paths    
# #---------------------------------------------------------------------------------------------------    
# # test Image
# test_image_path = pathlib.Path(r'C:\Users\micha\Documents\python\scripts\test_image.png')  

# # Open and Display Image
# #---------------------------------------------------------------------------------------------------    
# img_og = cv2.imread(r'C:\Users\micha\Documents\python\scripts\test_image.png')

# img_bgr = cv2.cvtColor(img_og, cv2.COLOR_RGB2BGR)
# matplotlib.pyplot.imshow(img_og)
# matplotlib.pyplot.title('ORIGINAL')
# matplotlib.pyplot.show()

# matplotlib.pyplot.imshow(img_bgr)
# matplotlib.pyplot.title('BGR')
# matplotlib.pyplot.show()

# Open and Display Video
#---------------------------------------------------------------------------------------------------    
video_capture = cv2.VideoCapture(r'C:\Users\micha\Documents\python\scripts\test_video.mkv')

video_properties = get_video_properties(video_capture)

print(video_properties)

print("width={0:f}, height={1:f}, frame_rate={2:f}, frame_count={3}, codec_4cc={4}, retrieve_format={5}, convert_rgb={6}".format(*video_properties))

(ret, frame_og) = video_capture.read()
frame_std = standardize_frame(frame_og)



video_capture.release()

# height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
# width  = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH) 
# print ("Video Dimension: height:{} width:{}".format( height, width))

# framecount = video_capture.get(cv2.CAP_PROP_FRAME_COUNT ) 
# frames_per_sec = video_capture.get(cv2.CAP_PROP_FPS)
# print("Video frame count:{} frame rate:{}".format(framecount,frames_per_sec))

# while(video_capture.isOpened()):
    # (ret, frame_og) = video_capture.read()

    # cv2.imshow('frame',frame_og)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# video_capture.release()
# video_capture.destroyAllWindows()