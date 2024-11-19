import ffmpeg
import subprocess
import os

class Video:
  def __init__(self, filename, totDim,timelineStart,fps,cropPos = [0,0],  cropDim = None, zIndex =0,start = 0, end = None, cacheFolder = "/"):
    # print(filename)
    self.cachedFolder = cacheFolder
    self.filename = filename
    if cacheFolder == None:
      #if we are not caching this file then just use the normal filename as the cache name
      self.cacheFilename = filename
      self.cachedFps = fps
    else:
      #we make a cached version of the file which we encode encode in the mjpeg avi format so we can seek to every frame cut it
      self.cacheFilename = cacheFolder +'/' + filename.replace("/", "-").replace(".mp4", ".avi")
      self.cachedFps = 30
      if not os.path.exists(self.cacheFilename):
        command = [
        'ffmpeg',             
        '-i', filename,      # Input video file
        '-r', '30',             # Set the frame rate to 30 fps
        '-c:v', 'mjpeg',        # Set video codec to MJPEG
        '-q:v', '5',            # Set MJPEG quality (1 = best, 31 = worst)
        '-c:a', 'pcm_s16le',    # Set audio codec to PCM (16-bit little-endian)
        self.cacheFilename            # Output file name
        ]

        # reencode the file mjpeg avi format so we can cleanly seek to any frame we want
        subprocess.run(command)
    self.zIndex = zIndex
    self.start = start #where in the video should it start from its beginning (in seconds)
    self.fps = fps 
    self.end = end #where the video should end if no option is provided it defaults to the end of the video
    self.totDim = totDim #dimensions of the original video [width, height]
    self.cropDim = cropDim #dimensions of the crop on the video [width, height]
    # self.cropDim = [min(cropDim[0], totDim[0] )]
    self.cropPos = cropPos #position of the top left corner of the part of the video to be cropped [x,y]
    self.timelineStart = timelineStart #where on the timeline the video starts playing

  def copy(self):
    return Video(self.filename, self.totDim, self.timelineStart,self.fps, cropPos = self.cropPos, cropDim = self.cropDim, zIndex=self.zIndex, start = self.start, end = self.end, cacheFolder=self.cachedFolder)
  
  def getFps(self):
    return self.fps
  
  def setBounds(self, start, end):
    self.start = start 
    self.end = end
     
  def getStart(self):
    return self.start
  
  def getEnd(self):
    return self.end
  
  def getZIndex(self):
    return self.zIndex
  
  #this gets all the info needed for rendering the video to the proper length
  #We used the cacheFilename because we reencode the video in avi mjpeg format so that the video is seekable to the frame
  #so we can cut the videos exactly to the frame
  def getVideoProcessingInfo(self):
    return [self.cacheFilename, self.start, self.end,self.cachedFps, self.cropPos, self.cropDim]
    # return {'filename': self.filename,'start': self.start, 'end': self.end, 'cropPos' : self.cropPos, 'cropDim': self.cropDim}

  def setTimelineStart(self, timelineStart):
    self.timelineStart = timelineStart
  
  def getTimelineStart(self):
    return self.timelineStart
  
  def getTotDim(self):
    return self.totDim
  
  
  def setCrop(self,x,y, width, height):
    self.cropPos = [x,y]
    self.cropDim = [width, height]
  
  #given a new interval of where the video should start and end (which is inside the current interval this video spans)
  #modify the start, end and timelineStart to fit in this newtimeline
  def modifyToNewInterval(self, newTimelineStart, newTimelineEnd):
    #modify the end of the video by the same amount the timeline end was moved by (which is equal to (self.timelineStart + (self.end + self.start)) )
    self.end += newTimelineEnd - (self.timelineStart + (self.end - self.start)) 

    #the start should be moved the same amount the timelinestart was moved by
    self.start += newTimelineStart - self.timelineStart
    self.timelineStart = newTimelineStart


# import ffmpeg



# try:
#   metadata = ffmpeg.probe('/Volumes/LaCie/Sewa Exhibit/assets/Homework/Crafts/3.mp4')
#   print(metadata['streams'][0]['width'], metadata['streams'][0]['height'])
# except ffmpeg.Error as e:
#   # print('stdout:', e.stdout.decode('utf8'))
#   print('stderr:', e.stderr.decode('utf8'))
#   raise e

# fpsNum, fpsDiv = metadata['streams'][0]['avg_frame_rate'].split('/')
# int(fpsNum) / int(fpsDiv)

# filename ="black_video.mp4"

# metadata = ffmpeg.probe(filename)
# # video_stream = next((stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None)

# fps = metadata['streams'][0]['avg_frame_rate'].split('/')[0]
# duration = metadata['streams'][0]['duration']

# # width = int(video_stream['width'])
# # height = int(video_stream['height'])

# print(f' FPS: {fps}, Duration: {duration}')