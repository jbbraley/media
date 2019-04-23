from __future__ import print_function

#GoPro_timestamp.py
#Created by Chris Rillahan
#Last Updated: 6/22/2015
#Written with Python 2.7.2, OpenCV 2.4.8, PILLOW 3.3.0

#This script uses ffprobe to interogate a MP4 file and extract the creation time.
#This information is then used to initiate a counter/clock which is used to put
#the timestamp on each frame of the video.  The videos are samed as *.avi files
#using DIVX compression due to the availability in OpenCV.  The audio is stripped
#out in this script.


import cv2, sys, time, os
import datetime as dt
import subprocess as sp
from PIL import Image


#Name of the file
#filename = 'GP050969.MP4'
#fdir = 'C:/users/john/videos'

#This function initiates a call to ffprobe which returns a summary report about
#the file of interest.  The returned information is then parsed to extract only
#the creation time of the file.

def creation_time(filename):
    cmnd = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', filename]
    p = sp.Popen(cmnd, stdout=sp.PIPE, stderr=sp.PIPE)
    print(filename)
    out, err =  p.communicate()
    print("==========output==========")
    print(out)
    if err:
        print("========= error ========")
        print(err)
    t = out.splitlines()
    time = str(t[14][18:37])
    return time

def stamp_file(filename, time_offset='0:0:0.0'):
    #Opens the video import and sets parameters
    video = cv2.VideoCapture(filename)

    #Checks to see if a the video was properly imported
    status = video.isOpened()
    print(status)

    if status == True:
        FPS = video.get(cv2.CAP_PROP_FPS)
        width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        size = (int(width), int(height))
        total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_lapse = (1/FPS)*1000

        #Initializes time origin of the video
        t = creation_time(filename)
        initial = dt.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        if time_offset[0]=='-':
            factor = -1
            string_ind = 1
        else:
            factor = 1
            string_ind = 0

        offset = dt.datetime.strptime(time_offset[0+string_ind:], "%H:%M:%S.%f")-dt.datetime.strptime('0:0:0', "%H:%M:%S")
        initial = initial + factor*offset
        timestamp = initial

        #Initializes the frame counter
        current_frame = 0
        start = time.time()

        # name of the new video file with timestamp
        Output_name = filename[:-4] + '_ts' + filename[-4:]

        #Command to send via the command prompt which specifies the pipe parameters
        command = ['ffmpeg.exe',
               '-y', # (optional) overwrite output file if it exists
               '-f', 'rawvideo', #Input is raw video
               '-vcodec', 'rawvideo',
               '-pix_fmt', 'bgr24', #Raw video format
               '-s', str(int(width)) + 'x' + str(int(height)), # size of one frame
               '-r', str(FPS), # frames per second
               '-i', '-', # The input comes from a pipe
               '-an', # Tells FFMPEG not to expect any audio
               '-vcodec', 'mpeg4',
               '-b:v', '10M', #Sets a maximum bit rate
               Output_name]

        #Open the pipe
        hole = open(os.devnull, 'w')
        pipe = sp.Popen(command, stdin=sp.PIPE, stdout=hole, stderr=sp.STDOUT)

        print('Processing....')
        print(' ')

        #Reads through each frame, calculates the timestamp, places it on the frame and
        #exports the frame to the output video.
        while current_frame < total_frames:
            success, image = video.read()
            elapsed_time = video.get(cv2.CAP_PROP_POS_MSEC)
            current_frame = video.get(cv2.CAP_PROP_POS_FRAMES)
            timestamp = initial + dt.timedelta(microseconds = elapsed_time*1000)
            cv2.putText(image, 'Date: ' + str(timestamp)[0:10], (50,int(height-150)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
            cv2.putText(image, 'Time: ' + str(timestamp)[11:-4], (50,int(height-100)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
            pipe.stdin.write(image.tostring())
            #print('frame {:4.0f} out of {:4.0f}      '.format(current_frame, total_frames)),

        video.release()
        pipe.stdin.close()
        #pipe.stderr.close()

        #Calculate how long the timestampping took
        duration = (time.time()-float(start))/60

        print("Video has been timestamped")
        print('This video took:' + str(duration) + ' minutes')

    else:
        print('Error: Could not load video')

def stamp_spec(filename, start_time, position):
    #Opens the video import and sets parameters
    video = cv2.VideoCapture(filename)

    #Checks to see if a the video was properly imported
    status = video.isOpened()
    print(status)

    if status == True:
        FPS = video.get(cv2.CAP_PROP_FPS)
        width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        size = (int(width), int(height))
        total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_lapse = (1/FPS)*1000

        #Initializes time origin of the video
        t = creation_time(filename)
        initial = dt.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
        timestamp = initial

        #Initializes the frame counter
        current_frame = 0
        start = time.time()

        # name of the new video file with timestamp
        Output_name = filename[:-4] + '_ts' + filename[-4:]

        #Command to send via the command prompt which specifies the pipe parameters
        command = ['ffmpeg.exe',
               '-y', # (optional) overwrite output file if it exists
               '-f', 'rawvideo', #Input is raw video
               '-vcodec', 'rawvideo',
               '-pix_fmt', 'bgr24', #Raw video format
               '-s', str(int(width)) + 'x' + str(int(height)), # size of one frame
               '-r', str(FPS), # frames per second
               '-i', '-', # The input comes from a pipe
               '-an', # Tells FFMPEG not to expect any audio
               '-vcodec', 'mpeg4',
               '-b:v', '10M', #Sets a maximum bit rate
               Output_name]

        #Open the pipe
        hole = open(os.devnull, 'w')
        pipe = sp.Popen(command, stdin=sp.PIPE, stdout=hole, stderr=sp.STDOUT)

        print('Processing....')
        print(' ')

        # specify text position
        if position=='top-left':
            xx = 50
            yy = 100
        elif position=='bottom-left':
            xx = 50
            yy = int(height-150)
        elif position=='top-right':
            xx = int(width-500)
            yy = 100
        else:
            xx = int(width-500)
            yy = int(height-150)

        #Reads through each frame, calculates the timestamp, places it on the frame and
        #exports the frame to the output video.
        while current_frame < total_frames:
            success, image = video.read()
            elapsed_time = video.get(cv2.CAP_PROP_POS_MSEC)
            current_frame = video.get(cv2.CAP_PROP_POS_FRAMES)
            timestamp = initial + dt.timedelta(microseconds = elapsed_time*1000)
            cv2.putText(image, 'Date: ' + str(timestamp)[0:10], (xx,yy), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
            cv2.putText(image, 'Time: ' + str(timestamp)[11:-4], (xx,int(yy+50)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
            pipe.stdin.write(image.tostring())
            #print('frame {:4.0f} out of {:4.0f}      '.format(current_frame, total_frames)),

        video.release()
        pipe.stdin.close()
        #pipe.stderr.close()

        #Calculate how long the timestampping took
        duration = (time.time()-float(start))/60

        print("Video has been timestamped")
        print('This video took:' + str(duration) + ' minutes')

    else:
        print('Error: Could not load video')

def stamp_folder(foldername, time_offset='0:0:0.0'):
    for root, dirs, filenames in os.walk(foldername):
        for f in filenames:
            if f[-4:] == '.MP4':

                print('working on: ' + str(f))

                video_filename = foldername + '/' + f
                stamp_file(video_filename,time_offset)
        break
