import ffmpeg
from Video import Video
from utils import calculateBoundsForCentered, intersect
import ffmpeg
import os

class Timeline:
  def __init__(self, width, height, emptySlots = []):
    self.phoneGrid = [[[] for _ in range(width)] for _ in range(height)]
    self.width = width
    self.height = height
    self.length = 0 #length of timeline in seconds
    self.emptySlots = set(emptySlots)
    

  #given the position of the top left phone in the grid (col, row), the size of the phone grid  (num cols, num rols), the filename of the video, aspect ratio of the video (wxh), 
  # the time it should start on the timeline, and if that time should be absolutely positioned 
  def addVideo(self, tlPos, gridSize, filename, ar, timelineStart, isAbs = True, zIndex = 0, vidStart = 0, vidEnd = None):
    if tlPos[0] + gridSize[0] > self.width or tlPos[1] + gridSize[1] > self.height or tlPos[0] < 0 or tlPos[1]< 0:
      print('invalid phone position and grid size')
      return 
    
    cols, rows = gridSize
    print(filename, timelineStart)
    #if the positioning of clip on the timeline is not absolute (it is relative)
    #then we loop through the last video in all of the grid slots this video will take up
    #find the video out of all of those slots that ends last and then our video will start
    #timelineStart seconds after the end of the last video
    if not isAbs:

      endOfLastClip = 0
      #loop through every grid slot this video inhabits
      for i in range(tlPos[0], tlPos[0]+cols):
        for j in range(tlPos[1], tlPos[1]+rows):
          #for every slot that has at least one video check if this video ends later than any other video we have seen
          if self.phoneGrid[j][i]:
            currStart, currEnd, currTimelineStart = self.phoneGrid[j][i][-1].getStart(), self.phoneGrid[j][i][-1].getEnd(), self.phoneGrid[j][i][-1].getTimelineStart()
            endOfLastClip = max(currTimelineStart + (currEnd-currStart), endOfLastClip)

      timelineStart += endOfLastClip 
      # print(filename, timelineStart, endOfLastClip)

    
    tl, br = calculateBoundsForCentered(cols, rows, ar[0], ar[1]) # get the tl and br of the cropped video
    w = br[0] - tl[0]
    h = br[1] - tl[1]
    cropW = w / cols
    cropH = h / rows
    for i in range(tlPos[0], tlPos[0]+cols):
      for j in range(tlPos[1], tlPos[1]+rows):
        # cropDimensions = [cropW, cropH, ,  ]
        self.phoneGrid[j][i].append(Video(filename, ar, timelineStart, cropPos = [tl[0] + (cropW * i), tl[1] + (cropH * j)], cropDim=[cropW, cropH], zIndex = zIndex, start=vidStart, end=vidEnd))

    self.length = max(self.phoneGrid[tlPos[1]][tlPos[0]][-1].getEnd() + timelineStart, self.length) #change the length if this video extends past current timeline length
  
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

    # Generate black video frames
    num_frames = duration * framerate
    print(num_frames)
    # Generate black video directly with specified duration
    ffmpeg.input('color=black:s={}x{}:duration={}'.format(width, height, duration), f='lavfi').output(output_file, t=duration, r=framerate).run()
      
  def processVideos(self):
    maxPhoneRes = [640, 360]
    for i in range(self.height):
      for j in range(self.width):
        # print(i,j)
        if (i,j) not in self.emptySlots:
          processedVideoList = self.__preprocessVideoList(self.phoneGrid[i][j])
          videos = []
          for index, video in enumerate(processedVideoList):
            
            filename, start, end,fps, [x,y], cropDim = video.getVideoProcessingInfo()
            if cropDim is None:

              videos.append(
                ffmpeg
                .input(filename)
                .trim(start_frame = int(fps*start), end_frame = int(fps*end))
                .filter('fps', fps=30, round='up')
                .setpts ('PTS-STARTPTS')
                .filter('scale', maxPhoneRes[1], maxPhoneRes[0])
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
                .filter('scale', maxPhoneRes[1], maxPhoneRes[0])
                .filter('setsar', 1)
                
              )
        ffmpeg.concat(*videos).output(f'videos/{i+1}-{j+1}.mp4').overwrite_output().run()
        
            

  def test(self):
    for video in self.__preprocessVideoList(self.phoneGrid[0][0]):
      print(video.getVideoProcessingInfo())
      print(video.getTimelineStart())


  def printGrid(self):
    for row in self.phoneGrid:
      print('[', end = '')
      for col in row:
        print(f'[{(len(col) * "x") + ((5-len(col)) * " ")}], ', end = "")
        
      print(']')

    # print(self.phoneGrid)

testT = Timeline(6,2)

# testT.addVideo([1,2], [3,3], 'black_video.mp4', [1920, 1080], 4, zIndex=1)
# testT.addVideo([0,0], [3,4], 'test_video.mp4', [1920, 1080], 0, isAbs =False)
# testT.addVideo([4,4], [2,2], 'test_video.mp4', [1920, 1080], 6)
#position is number of column and the number of row
# print(os.path.exists('./videos/input/zoom1.mp4'))
testT.addVideo([0,0], [1,1], './videos/input/zoom1.mp4', [1080, 1920], 0, zIndex=1)
testT.addVideo([1,0], [1,1], './videos/input/zoom5.mp4', [1080, 1920], 3, zIndex=1)
testT.addVideo([2,0], [1,1], './videos/input/zoom6.mp4', [1080, 1920], 3.5, zIndex=1)
testT.addVideo([3,0], [1,1], './videos/input/zoom3.mp4', [1080, 1920], 2, zIndex=1)
testT.addVideo([4,0], [1,1], './videos/input/zoom8.mp4', [1080, 1920], 3.5, zIndex=1)
testT.addVideo([5,0], [1,1], './videos/input/zoom8.mp4', [1080, 1920], 3.5, zIndex=1)
testT.addVideo([0,1], [1,1], './videos/input/zoom9.mp4', [1080, 1920], 4, zIndex=1)
testT.addVideo([1,1], [1,1], './videos/input/zoom2.mp4', [1080, 1920], 1, zIndex=1)
testT.addVideo([2,1], [1,1], './videos/input/zoom10.mp4', [1080, 1920], 4, zIndex=1)
testT.addVideo([3,1], [1,1], './videos/input/zoom11.mp4', [1080, 1920], 4, zIndex=1)
testT.addVideo([4,1], [1,1], './videos/input/zoom12.mp4', [1080, 1920], 4, zIndex=1)
testT.addVideo([5,1], [1,1], './videos/input/zoom4.mp4', [1080, 1920], 2.5, zIndex=1)
testT.addVideo([0,0], [6,2], './videos/input/big-zoom.mp4', [1920, 1080], 12, zIndex=2)
# testT.addVideo([4,0], [2,2], 'quad-formal.mp4', [1920, 1080], 4, zIndex=1, vidEnd= 5)
# testT.addVideo([0,0], [6,2], 'drakex21.mp4', [1280, 720], 4)
testT.processVideos()
# testT.test()
# testT.printGrid()