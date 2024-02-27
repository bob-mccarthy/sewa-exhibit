import ffmpeg

class Video:
  def __init__(self, filename, totDim,timelineStart,cropPos = [0,0],  cropDim = None, zIndex =0,start = 0, end = None):
    self.filename = filename
    self.zIndex = zIndex
    self.start = start #where in the video should it start from its beginning (in seconds)
    metadata = ffmpeg.probe(filename)
    fpsNum, fpsDiv = metadata['streams'][0]['avg_frame_rate'].split('/')
    self.fps = int(fpsNum) / int(fpsDiv)
    self.end = end if end else float(metadata['streams'][0]['duration']) #where the video should end if no option is provided it defaults to the end of the video
    self.totDim = totDim #dimensions of the original video [width, height]
    self.cropDim = cropDim #dimensions of the crop on the video [width, height]
    # self.cropDim = [min(cropDim[0], totDim[0] )]
    self.cropPos = cropPos #position of the top left corner of the part of the video to be cropped [x,y]
    self.timelineStart = timelineStart #where on the timeline the video starts playing

  def copy(self):
    return Video(self.filename, self.totDim, self.timelineStart, cropPos = self.cropPos, cropDim = self.cropDim, zIndex=self.zIndex, start = self.start, end = self.end)
  
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
  
  def getVideoProcessingInfo(self):
    return [self.filename, self.start, self.end,self.fps, self.cropPos, self.cropDim]
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

# filename ="black_video.mp4"

# metadata = ffmpeg.probe(filename)
# # video_stream = next((stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None)

# fps = metadata['streams'][0]['avg_frame_rate'].split('/')[0]
# duration = metadata['streams'][0]['duration']

# # width = int(video_stream['width'])
# # height = int(video_stream['height'])

# print(f' FPS: {fps}, Duration: {duration}')