import ffmpeg
from Video import Video
from utils import calculateBoundsForCenteredGivenScreen, intersect
import ffmpeg
import os
mmToPixels = 1 / (25.4/160)

class Timeline:
  #phoneDim: 2D array where element i,j is the dimensions of the window size of phone in pixels, and
  #xSpacing and ySpacing are the spacing between the centers of the phones in their respective dimensions
  def __init__(self, phoneDim, xSpacing,ySpacing):
    #are pixel measurements are scaled such that there are 160 pixels per inch 
    
    height = len(phoneDim)
    width = len(phoneDim[0])
    
    self.phoneGrid = [[[] for _ in range(width)] for _ in range(height)]
    self.width = width
    self.height = height
    self.length = 0 #length of timeline in seconds
    self.phoneDim = phoneDim #array where phone dimension element i,j is the dimension of phone i,j (wxh, in pixels)
    self.ySpacing = ySpacing * mmToPixels
    self.xSpacing = xSpacing * mmToPixels
    # self.ySpacing = ySpacing 
    # self.xSpacing = xSpacing
    
    
  #gets the dimensions of the screen, offset , given the top left corner and the size of the grid 
  def getScreenDimInfo(self,tl, gridSize):
    #the offset is the amount we need to add to the x coordinate
    #such that the left side of the largest phone is equal to 0
    offset = 0
    #finds the offset which is equal to the phone in the first column with the biggest width divided by 2 
    for i in range(tl[0], tl[0] + gridSize[0]):
      if self.phoneDim[i][0]:
        offset = max(self.phoneDim[i][0][0] / 2, offset)

    screenHeight = 0
    #finds the screen height
    #screen height is equal to y position of the bottom of the longest phone in the last row
    for i in range(tl[1], tl[1] + gridSize[1]):
      lastRowInGrid = tl[0] + gridSize[0] - 1
      if self.phoneDim[lastRowInGrid][i]:
        screenHeight = max(self.phoneDim[lastRowInGrid][i][1] + self.ySpacing*(gridSize[0] - 1), screenHeight)

    screenWidth = 0
    #finds the screen width
    #screen width is equal to the x position of the right side of the largest phone in the last column
    for i in range(tl[0], tl[0] + gridSize[0]):
      lastColInGrid = tl[1] + gridSize[1] -1
      if self.phoneDim[i][lastColInGrid]:
        screenWidth = max(self.xSpacing * (gridSize[1] - 1) + self.phoneDim[i][lastColInGrid][0]/2 + offset, screenWidth)
    
  
    return int(screenWidth), int(screenHeight), int(offset)



    

  #given the position of the top left phone in the grid (row, col), the size of the phone grid  (num rows, num cols), the filename of the video, aspect ratio of the video (wxh), 
  # the time it should start on the timeline, if that time should be absolutely positioned, the zIndex of the video, and the video start and end if you want to trim the video 
  def addVideo(self, tlPos, gridSize, filename, ar, timelineStart, isAbs = True, zIndex = 0, vidStart = 0, vidEnd = None):
    if tlPos[1] + gridSize[1] > self.width or tlPos[0] + gridSize[0] > self.height or tlPos[0] < 0 or tlPos[1]< 0:
      print('invalid phone position and grid size')
      return 
    rows, cols = gridSize

    #if the positioning of clip on the timeline is not absolute (it is relative)
    #then we loop through the last video in all of the grid slots this video will take up
    #find the video out of all of those slots that ends last and then our video will start
    #timelineStart seconds after the end of the last video
    if not isAbs:
      endOfLastClip = 0
      #loop through every grid slot this video inhabits
      for i in range(tlPos[1], tlPos[1]+cols):
        for j in range(tlPos[0], tlPos[0]+rows):
          #for every slot that has at least one video check if this video ends later than any other video we have seen
          if self.phoneGrid[j][i]:
            currStart, currEnd, currTimelineStart = self.phoneGrid[j][i][-1].getStart(), self.phoneGrid[j][i][-1].getEnd(), self.phoneGrid[j][i][-1].getTimelineStart()
            endOfLastClip = max(currTimelineStart + (currEnd-currStart), endOfLastClip)

      timelineStart += endOfLastClip 


    screenWidth, screenHeight, offset = self.getScreenDimInfo(tlPos, gridSize)
    

    tl, scaleFac = calculateBoundsForCenteredGivenScreen(screenWidth, screenHeight, ar[0], ar[1]) # get the tl of the cropped video and scaleFactor which is (size of video/size of screen)
    # print(tl, scaleFac)
    w = int(tl[0] + screenWidth * scaleFac)
    h = int(tl[1] + screenHeight * scaleFac)
    for i in range(tlPos[0], tlPos[0]+rows):
      for j in range(tlPos[1], tlPos[1]+cols):
        #some video slots are empty and we don't put a video there
        if self.phoneDim[i][j] == None:
          continue
        #top left x position of the phone is the x value of where the video starts + the spacing of all of the phones to its left - half of the phones width + the offset we calculated 
        #before * the factor to scale from screen size to video size 
        phoneTopLeftX = int(tl[0] + (((self.xSpacing * j) - self.phoneDim[i][j][0] / 2 + offset ) * scaleFac))
        #top left y position of the phone is the y value of where the video starts + y spacing of times the number of phones above it * the factor to scale from screen to video size 
        phoneTopLeftY = int(tl[1] + (((self.ySpacing * i)) * scaleFac))
        self.phoneGrid[i][j].append(
          Video(
            filename, 
            ar, 
            timelineStart, 
            cropPos = [phoneTopLeftX, phoneTopLeftY], 
            
            cropDim=[int(int(self.phoneDim[i][j][0]) * scaleFac),int(int(self.phoneDim[i][j][1]) * scaleFac) ], 
            zIndex = zIndex, start=vidStart, 
            end=vidEnd
            )
          )

    self.length = max((self.phoneGrid[tlPos[0]][tlPos[1]][-1].getEnd() - self.phoneGrid[tlPos[0]][tlPos[1]][-1].getStart()) + timelineStart, self.length) #change the length if this video extends past current timeline length
  
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
      
  def processVideos(self):
    phoneResHeight = 1280 #maximum height of video is 640 and we scale width accordingly
    for i in range(self.height):
      for j in range(self.width):
        if self.phoneDim[i][j] is not None:
          processedVideoList = self.__preprocessVideoList(self.phoneGrid[i][j])
          videos = []
          for video in processedVideoList:
            filename, start, end,fps, [x,y], cropDim = video.getVideoProcessingInfo()

            phoneWidth, phoneHeight = self.phoneDim[i][j]
            #scale the width to keep it at the same aspect ratio given that the video height is phoneResHeight
            phoneResWidth = (phoneWidth / phoneHeight) * phoneResHeight 
            # print(f'before: {phoneResWidth}')
            #all video dimensions need to be divisible by 2, so we round down to the nearest multiple of two
            phoneResWidth = (int(phoneResWidth) // 2) * 2
            # print(f'after: {phoneResWidth}')
            if cropDim is None:
              videos.append(
                ffmpeg
                .input(filename)
                .trim(start_frame = int(fps*start), end_frame = int(fps*end))
                .filter('fps', fps=30, round='up')
                .setpts ('PTS-STARTPTS')
                .filter('scale', phoneResWidth, phoneResHeight)
                .filter('setsar', 1)
              )
            else:
              width, height = cropDim
              cropInstructions = [width, height, x, y]
              videos.append(
                ffmpeg
                .input(filename)
                .trim(start_frame = int(fps*start), end_frame = int(fps*end))
                .filter('fps', fps=30, round='up')
                .setpts ('PTS-STARTPTS')
                .filter('crop', *cropInstructions)
                .filter('scale', phoneResWidth, phoneResHeight)
                .filter('setsar', 1)
                
              )
          ffmpeg.concat(*videos).output(f'videos/{i+1}-{j+1}.mp4').overwrite_output().run()
        
            

  def test(self):
    for row in self.phoneGrid:
      for phoneList in row:
        for video in self.__preprocessVideoList(phoneList):
          print(video.getVideoProcessingInfo())
          # print(video.getTimelineStart())


  def printGrid(self):
    for row in self.phoneGrid:
      print('[', end = '')
      for col in row:
        print(f'[{(len(col) * "x") + ((5-len(col)) * " ")}], ', end = "")
        
      print(']')

    # print(self.phoneGrid)
phoneDim = [[[68,128],[71,128],[62,116],[68,128],[62,110],[62,106],None],[[68,127],[62,116],[62,98],[62,111],[62,98],[68,116],[71,128]],[None,[68,127],[63,118],[68,116],[62,116],[62,106],None]]
for i in range(len(phoneDim)):
  for j in range(len(phoneDim[i])):
    if phoneDim[i][j]:
      phoneDim[i][j][0] *= mmToPixels
      phoneDim[i][j][1] *= mmToPixels
# phoneDim = [[[62 * mmToPixels, 115 * mmToPixels], [62*mmToPixels, 110*mmToPixels], [68*mmToPixels, 127*mmToPixels]],
#             [[68*mmToPixels, 127*mmToPixels], [68*mmToPixels, 128*mmToPixels], [63*mmToPixels, 118*mmToPixels]]]

# print(phoneDim[0])
testT = Timeline(phoneDim, 113, 200)
# print(testT.getScreenDimInfo([0,0], [2,4]))

testT.addVideo([0,0], [1,1], './videos/input/zoom1.mp4', [1080, 1920], 0, zIndex=1)
testT.addVideo([0,1], [1,1], './videos/input/zoom2.mp4', [1080, 1920], 2, zIndex=1)
testT.addVideo([0,2], [1,1], './videos/input/zoom4.mp4', [1080, 1920], 6, zIndex=1)
testT.addVideo([1,0], [1,1], './videos/input/zoom5.mp4', [1080, 1920], 8, zIndex=1)
testT.addVideo([1,1], [1,1], './videos/input/zoom3.mp4', [1080, 1920], 7, zIndex=1)
testT.addVideo([1,2], [1,1], './videos/input/zoom6.mp4', [1080, 1920], 10, zIndex=1)



testT.addVideo([0,0], [3,7], './videos/input/rough-cut.mp4', [854,480], 12,zIndex=2, vidStart=120, vidEnd=180)

testT.processVideos()
# testT.test()
# testT.printGrid()