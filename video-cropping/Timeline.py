import ffmpeg
from Video import Video
from utils import calculateBoundsForCenteredGivenScreen, intersect
import ffmpeg
import os, glob
import json
import csv
mmToPixels = 1 / (25.4/160)

class Timeline:
  #deviceDim: 2D array where element i,j is the dimensions of the window size of phone in pixels, and
  #xSpacing and ySpacing are the spacing between the centers of the phones in their respective dimensions
  def __init__(self, deviceDim, isTablet, xSpacing,ySpacing):
    #are pixel measurements are scaled such that there are 160 pixels per inch 
    
    height = len(deviceDim)
    width = len(deviceDim[0])
    
    self.phoneGrid = [[[] for _ in range(width)] for _ in range(height)]
    self.width = width
    self.height = height
    self.length = 0 #length of timeline in seconds
    self.deviceDim = deviceDim #array where phone dimension element i,j is the dimension of phone i,j (wxh, in pixels)
    self.ySpacing = ySpacing * mmToPixels
    self.xSpacing = xSpacing * mmToPixels
    self.isTablet = isTablet
    self.vidStartTimes={} #dictionary of videos ids with their timeline starts as the values
    
    
    
  #gets the dimensions of the screen, offset , given the top left corner and the size of the grid 
  def getScreenDimInfo(self,tl, gridSize):
    #the offset is the amount we need to add to the x coordinate
    #such that the left side of the largest phone is equal to 0
    offset = 0
    #finds the offset which is equal to the phone in the first column with the biggest width divided by 2 
    for i in range(tl[0], tl[0] + gridSize[0]):
      if self.deviceDim[i][tl[1]]:
        offset = max(self.deviceDim[i][tl[1]][0] / 2, offset)


    screenHeight = 0
    #finds the screen height
    #screen height is equal to y position of the bottom of the longest phone in the last row 
    #(which is the length screen ,self.deviceDim[lastRowInGrid][i][1], + offset of where the screen starts ,self.deviceDim[lastRowInGrid][i][2], )
    for i in range(tl[1], tl[1] + gridSize[1]):
      lastRowInGrid = tl[0] + gridSize[0] - 1
      if self.deviceDim[lastRowInGrid][i]:
        screenHeight = max(self.deviceDim[lastRowInGrid][i][2] + self.deviceDim[lastRowInGrid][i][1] + self.ySpacing*(gridSize[0] - 1), screenHeight)

 

    screenWidth = 0
    #finds the screen width
    #screen width is equal to the x position of the right side of the largest phone in the last column
    for i in range(tl[0], tl[0] + gridSize[0]):
      
      lastColInGrid = tl[1] + gridSize[1] - 1
      if self.deviceDim[i][lastColInGrid]:
        screenWidth = max(self.xSpacing * (gridSize[1] - 1) + self.deviceDim[i][lastColInGrid][0]/2 + offset, screenWidth)
    
  
    return int(screenWidth), int(screenHeight), int(offset)



    

  #given the position of the top left phone in the grid (row, col), the size of the phone grid  (num rows, num cols), the filename of the video, aspect ratio of the video (wxh), 
  # the time it should start on the timeline, if that time should be absolutely positioned, the zIndex of the video, the video start and end if you want to trim the video, 
  #and the offset of the video from center
  def addVideo(self, tlPos, gridSize, filename, ar, timelineStart,id, isAbs = True,relativeTo = None, zIndex = 0, vidStart = 0, vidEnd = None, vidOffset = [0,0]):
    if tlPos[1] + gridSize[1] > self.width or tlPos[0] + gridSize[0] > self.height or tlPos[0] < 0 or tlPos[1]< 0:
      print(f'invalid phone position and grid size: {filename}: tlPos: {tlPos}, gridSize: {gridSize}')
      return 
    rows, cols = gridSize

    #if the positioning of clip on the timeline is not absolute (it is relative)
    #then we loop through the last video in all of the grid slots this video will take up
    #find the video out of all of those slots that ends last and then our video will start
    #timelineStart seconds after the end of the last video
    if not isAbs:
      if relativeTo is None:
        endOfLastClip = 0
        #loop through every grid slot this video inhabits
        for i in range(tlPos[1], tlPos[1]+cols):
          for j in range(tlPos[0], tlPos[0]+rows):
            #for every slot that has at least one video check if this video ends later than any other video we have seen
            if self.phoneGrid[j][i]:
              currStart, currEnd, currTimelineStart = self.phoneGrid[j][i][-1].getStart(), self.phoneGrid[j][i][-1].getEnd(), self.phoneGrid[j][i][-1].getTimelineStart()
              endOfLastClip = max(currTimelineStart + (currEnd-currStart), endOfLastClip)

        timelineStart += endOfLastClip
      else:
        timelineStart += self.vidStartTimes[relativeTo] 
      self.vidStartTimes[id] = timelineStart


    screenWidth, screenHeight, offset = self.getScreenDimInfo(tlPos, gridSize)
    
    tl, scaleFac = calculateBoundsForCenteredGivenScreen(screenWidth, screenHeight, ar[0], ar[1]) # get the tl of the cropped video and scaleFactor which is (size of video/size of screen)
    # print(offset)
    tl[0] += vidOffset[0]
    tl[1] += vidOffset[1]

    duration = None
    for i in range(tlPos[0], tlPos[0]+rows):
      for j in range(tlPos[1], tlPos[1]+cols):
        #some video slots are empty and we don't put a video there
        if self.deviceDim[i][j] == None:
          continue
        
        #top left y position of the device is the y value of where the video starts + (y spacing of times the number of phones above it + offset of where the screen starts) * the factor to scale from screen to video size 
        deviceTopLeftY = int(tl[1] + (((self.ySpacing * (i - tlPos[0]) + self.deviceDim[i][j][2] )) * scaleFac))
        #top left x position of the devices is the x value of where the video starts + the spacing of all of the devices to its left - half of the devices width + the offset we calculated 
        #before * the factor to scale from screen size to video size 
        deviceTopLeftX = int(tl[0] + (((self.xSpacing * (j -tlPos[1])) - self.deviceDim[i][j][0] / 2 + offset ) * scaleFac))

        self.phoneGrid[i][j].append(
          Video(
            filename, 
            ar, 
            timelineStart, 
            cropPos = [deviceTopLeftX, deviceTopLeftY], 
            
            cropDim=[int(int(self.deviceDim[i][j][0]) * scaleFac),int(int(self.deviceDim[i][j][1]) * scaleFac) ], 
            zIndex = zIndex, start=vidStart, 
            end=vidEnd
            )
          )
        if not duration:
          duration = self.phoneGrid[i][j][-1].getEnd() - self.phoneGrid[i][j][-1].getStart()
    
    self.length = max(duration + timelineStart, self.length) #change the length if this video extends past current timeline length
  
  #takes a list of overlapping video and processes them so it is no longer a list of overlappibg videos such that video of the highest zIndex is playing at each slot in time
  def __preprocessVideoList(self, videoList):
    videoList.sort(key = lambda x: x.getZIndex(), reverse = True) # sort videos so highest Z index is first
    processedVideoList = []
    freeIntervals = [[0, self.length]]
    for video in videoList:
      newIntervals = []
      #loop through all of the intervals which has not already been filled by other videos
      for interval in freeIntervals:
        start, end, timelineStart = video.getStart(), video.getEnd(), video.getTimelineStart()
        timelineEnd = timelineStart + (end - start)
        intersection, unintersected = intersect([timelineStart, timelineEnd], interval) #check if interval representing this video intersection with this current free interval
        #if there is an intersection between this video and a free interval 
        #then we trim this video to fit within that intersection (if necessary)
        if intersection: 
          newTimelineStart, newTimelineEnd = intersection
          newVideo = video.copy()
          newVideo.modifyToNewInterval(newTimelineStart, newTimelineEnd)
          processedVideoList.append(newVideo)

        for interval in unintersected:
          newIntervals.append(interval)
      freeIntervals = newIntervals
    #for all of the remaining intervals which do not have a video in them
    #they fill it with black videos
    for interval in freeIntervals:
      blackVideoFilename = f'./videos/black-videos/black-video-{float(interval[1] - interval[0])}.mp4'
      if not os.path.exists(blackVideoFilename):
        self.__generateBlackVideo(blackVideoFilename, interval[1] - interval[0], 720, 1280)
      processedVideoList.append(Video(blackVideoFilename, [720, 1280], interval[0], end = interval[1] - interval[0]))
    processedVideoList.sort(key = lambda x: x.getTimelineStart())
    return processedVideoList
  
  def __generateBlackVideo(self, output_file, duration, width, height):
    framerate = 30
    # Generate black video directly with specified duration
    ffmpeg.input('color=black:s={}x{}:duration={}'.format(width, height, duration), f='lavfi').output(output_file, t=duration, r=framerate).run()
      
  def processVideos(self, renderIndices = None):
    phoneResHeight = 1280 #maximum height of video is 1280 and we scale width accordingly
    tabletResHeight = 720 #maximum height of video on tablet (considering tablets will be landscape)
    vidInfo = {'vidLen': self.length}
    jsonObject = json.dumps(vidInfo)
    with open('videos/output/vidInfo.json','w') as outfile:
      outfile.write(jsonObject)

    for i in range(self.height):
      for j in range(self.width):
        # print((i,j))
        if renderIndices and (i,j) not in renderIndices:
          continue
        
        if self.deviceDim[i][j] is not None:
          processedVideoList = self.__preprocessVideoList(self.phoneGrid[i][j])
          videos = []
          for video in processedVideoList:
            filename, start, end,fps, [x,y], cropDim = video.getVideoProcessingInfo()
            deviceWidth, deviceHeight, _ = self.deviceDim[i][j]
            
            deviceResHeight = tabletResHeight if self.isTablet[i][j] else phoneResHeight
            #scale the width to keep it at the same aspect ratio given that the video height is phoneResHeight
            deviceResWidth = (deviceWidth / deviceHeight) * (deviceResHeight) 

            #all video dimensions need to be divisible by 2, so we round down to the nearest multiple of two
            deviceResWidth = (int(deviceResWidth) // 2) * 2
            # print(ffmpeg.probe(filename)['streams'][0])
            ffmpegVideo = (ffmpeg.input(filename)
                            .trim(start_frame = int(fps*start), end_frame = int(fps*end))
                            .filter('fps', fps=30, round='up')
                            .setpts ('PTS-STARTPTS'))
            if cropDim:
              width, height = cropDim
              cropInstructions = [width, height, x, y]
              ffmpegVideo = ffmpegVideo.filter('crop', *cropInstructions)

            

            ffmpegVideo = (ffmpegVideo.filter('scale', deviceResWidth, deviceResHeight)
                            .filter('setsar', 1))
            #if the video is a tablet we must rotate by 90 degrees CW
            if self.isTablet[i][j]:
              ffmpegVideo = ffmpegVideo.filter('transpose', dir='clock')
            
            videos.append(ffmpegVideo)
          for k in range(len(videos)):
            videos[k].output(f'videos/temp/{k}.mp4').overwrite_output().run()
          filenames = os.listdir('./videos/temp')
          filenames.sort(key = lambda x: int(x[:x.index('.')]))
          ffmpeg.concat(*[ffmpeg.input(f'./videos/temp/{x}') for x in filenames[:len(videos)]]).output(f'videos/output/{i+1}-{j+1}.mp4').overwrite_output().run()
          # ffmpeg.concat(*videos).output(f'videos/output/{i+1}-{j+1}.mp4').overwrite_output().run()
        
            

  def getDevicePosInScreen(self, devicePos, tlPos, gridSize, ar):
    screenWidth, screenHeight, offset = self.getScreenDimInfo(tlPos, gridSize)
    i, j = devicePos
    tl, scaleFac = calculateBoundsForCenteredGivenScreen(screenWidth, screenHeight, ar[0], ar[1]) # get the tl of the cropped video and scaleFactor which is (size of video/size of screen)
    #top left y position of the device is the y value of where the video starts + (y spacing of times the number of phones above it + offset of where the screen starts) * the factor to scale from screen to video size 
    deviceTopLeftY = int(tl[1] + (((self.ySpacing * (devicePos[0] - tlPos[0]) + self.deviceDim[i][j][2] )) * scaleFac))
    #top left x position of the devices is the x value of where the video starts + the spacing of all of the devices to its left - half of the devices width + the offset we calculated 
    #before * the factor to scale from screen size to video size 
    deviceTopLeftX = int(tl[0] + (((self.xSpacing * (devicePos[1] -tlPos[1])) - self.deviceDim[i][j][0] / 2 + offset ) * scaleFac))
    
    #returns x,y and width and height of the video
    return deviceTopLeftX, deviceTopLeftY, self.deviceDim[i][j][0] * scaleFac, self.deviceDim[i][j][1] * scaleFac
  

  def readCSV(self, csvPath):
    with open(csvPath, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
          if row['id'] == '':
            continue
          tlPos = [int(x) for x in row['tlPos'][1:-1].split(',')]
          gridSize = [int(x) for x in row['gridSize'][1:-1].split(',')]
          filename = row['filename']
          ar = [int(x) for x in row['ar'][1:-1].split(',')]
          timelineStart = int(row['timelineStart'])
          id = int(row['id'])
          isAbs = True if row['isAbs'] == '' or row['isAbs'] == 'TRUE' else False
          if isAbs:
            self.vidStartTimes[id] = timelineStart
          relativeTo = None if row['relativeTo'] == '' else int(row['relativeTo']) 
          zIndex = 0 if row['zIndex'] == '' else int(row['zIndex'])
          vidStart = 0 if row['vidStart'] == '' else int(row['vidStart'])
          vidEnd = None if row['vidEnd'] == '' else int(row['vidEnd'])
          vidOffset = [0,0] if row['vidOffset'] == '' else [int(x) for x in row['vidOffset'][1:-1].split(',')]
          self.addVideo(tlPos, gridSize, filename, ar, timelineStart, id, isAbs=isAbs, relativeTo = relativeTo, zIndex = zIndex, vidStart=vidStart, vidEnd = vidEnd, vidOffset=vidOffset)

  def printGrid(self):
    for row in self.phoneGrid:
      print('[', end = '')
      for col in row:
        print(f'[{(len(col) * "x") + ((5-len(col)) * " ")}], ', end = "")
        
      print(']')
f = open('phoneDim.json')
dct = json.load(f)

deviceDim = dct['deviceDim']
isTablet = dct['isTabletGrid']
for i in range(len(deviceDim)):
  for j in range(len(deviceDim[i])):
    if deviceDim[i][j]:
      deviceDim[i][j][0] = int(deviceDim[i][j][0] * mmToPixels)
      deviceDim[i][j][1] = int(deviceDim[i][j][1] * mmToPixels)
      deviceDim[i][j][2] = int(deviceDim[i][j][2] * mmToPixels)


testT = Timeline(deviceDim,isTablet, 103, 190)


testT.readCSV('./csvs/exhibit-vids.csv')
testT.processVideos()
