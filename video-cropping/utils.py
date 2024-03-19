
#given a list of intervals of the form [start,end] and an bigger interval which contains the entire list of intervals
#this function returns all the remaining intervals which are not covered by the input list 
def findFillerIntervals(intervals, totalInterval):
  fillerIntervals = []
  currInterval = totalInterval
  for start, end in intervals:
    # print(currInterval[0], start)
    if currInterval[0] < start:
      fillerIntervals.append([currInterval[0], start])
    currInterval[0] = end
  if currInterval[0] != currInterval[1]:
    fillerIntervals.append(currInterval)
  return fillerIntervals

#given two intervals ([start,end]) a and b it returns true if they are overlapping
def isOverlapping(a, b):
  startA, endA = a
  startB, endB = b
  return startA <= startB < endA or startB <= startA < endB

#given two intervals ([start, end]) a and b it returns tuple where 
#the first element is the intersection if there is one (null otherwise) 
#the second element is a intervals that are in interval b that where not in the intersection
def intersect(a,b):
  startA, endA = a
  startB, endB = b
  if isOverlapping(a,b): 
    intersection = [max(startA, startB), min(endA, endB)]
    nonIntersectedParts = []
    if intersection[0] > startB:
      nonIntersectedParts.append([startB, intersection[0]])
    if intersection[1] < endB:
      nonIntersectedParts.append([intersection[1], endB])
    return (intersection, nonIntersectedParts)
  return (None, [b])

def calculateBoundsForCenteredGivenScreen(screenWidth, screenHeight, videoWidth, videoHeight):
  scaleFacY = videoHeight/screenHeight #ratio of the height of our video to the height of our screen
  scaleFacX = videoWidth/screenWidth #ratio of the width of our video to the width of our screen 


  #we want to pick the scale factors which will give us dimensions that make our screen smaller than our video 
  #because we do not want our video to have black bars.
  #So we pick scaleFacX if scaleFacX * height of our screen is less than or equal the height of our video
  #But if is not then we know that scaleY * the width of our screen is less than or equal to width so we pick that one
  finalScaleFac = scaleFacX if scaleFacX * screenHeight <= videoHeight  else scaleFacY

  #get the dimension of the screen in pixels
  screenDimX = screenWidth * finalScaleFac 
  screenDimY = screenHeight * finalScaleFac

  screenCenterX = screenDimX / 2
  screenCenterY = screenDimY / 2

  videoCenterX = videoWidth / 2
  videoCenterY = videoHeight / 2
  #returns coordinate of the Top Left corner are on the original video, and the scale Factor to go from screen size to videoSize
  return [[int(videoCenterX - screenCenterX), int(videoCenterY - screenCenterY)], finalScaleFac]



#calculates bounds to center video given its dimensions(wxh) and the number of phones in the grid columns x rows (cxr)
# assuming that each phone as an aspect ratio of 9x16
def calculateBoundsForCentered(c,r,w,h):
  phoneAspectRatio = [9,16]
  totalAspectRatioX, totalAspectRatioY = 0,0
  totalAspectRatioX += phoneAspectRatio[0] * c
  totalAspectRatioY += phoneAspectRatio[1] * r
  # print(totalAspectRatioX, totalAspectRatioY)
  
  scaleFacY = h/totalAspectRatioY #ratio of the height of our video to the height of our screen
  scaleFacX = w/totalAspectRatioX #ratio of the width of our video to the width of our screen 

  #we want to pick the scale factors which will give us dimensions that make our screen smaller than our video 
  #because we do not want our video to have black bars.
  #So we pick scaleFacX if scaleFacX * height of our screen is less than or equal the height of our video
  #But if is not then we know that scaleY * the width of our screen is less than or equal to width so we pick that one
  finalScaleFac = scaleFacX if scaleFacX * totalAspectRatioY <= h  else scaleFacY

  #get the dimension of the screen in pixels
  screenDimX = totalAspectRatioX * finalScaleFac 
  screenDimY = totalAspectRatioY * finalScaleFac

  screenCenterX = screenDimX // 2
  screenCenterY = screenDimY // 2

  videoCenterX = w // 2
  videoCenterY = h // 2

  #returns coordinate of the Top Left corner of the Bottom Right Corner are on the original video
  return [[videoCenterX - screenCenterX, videoCenterY - screenCenterY],[videoCenterX + screenCenterX, videoCenterY + screenCenterY]]


# import ffmpeg
# import math

# def rotate_video(input_file, output_file, rotation_angle):
#     (
#         ffmpeg
#         .input(input_file)
#         .filter('rotate', angle=rotation_angle)
#         .output(output_file)
#         .run()
#     )

# # Example usage:
# input_file = './videos/input/drakex21.mp4'
# output_file = 'output_rotated.mp4'
# rotation_angle = math.pi/2  # Possible values: 'clock', 'cclock', 'cclock_flip', 'clock_flip'

# def rotate_video(input_file, output_file, rotation_angle):
#     (
#         ffmpeg
#         .input(input_file)
#         .filter('transpose', dir='clock')  # Rotate counterclockwise
#         # .filter('scale', w='iw*1.5', h='ih*1.5')  # Scale up to handle the aspect ratio change
#         # .filter('crop', w='iw*0.75', h='ih*0.75')  # Crop to maintain the aspect ratio
#         .output(output_file)
#         .run()
#     )

# # Example usage:
# input_file = './videos/input/drakex21.mp4'
# output_file = 'output_rotated.mp4'

# # rotate_video(input_file, output_file)
# # 
# rotate_video(input_file, output_file, rotation_angle)

