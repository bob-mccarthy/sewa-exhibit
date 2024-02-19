
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
  print(finalScaleFac)

  #get the dimension of the screen in pixels
  screenDimX = totalAspectRatioX * finalScaleFac 
  screenDimY = totalAspectRatioY * finalScaleFac
  print(657 + totalAspectRatioX * finalScaleFac )

  screenCenterX = screenDimX // 2
  screenCenterY = screenDimY // 2

  videoCenterX = w // 2
  videoCenterY = h // 2

  #returns coordinate of the Top Left corner of the Bottom Right Corner are on the original video
  return [[videoCenterX - screenCenterX, videoCenterY - screenCenterY],[videoCenterX + screenCenterX, videoCenterY + screenCenterY]]



# def concatenate_videos(inputVideos, output_path):
    
#     # Create a list of input video files
#     inputArgs = []
#     for video in inputVideos:
#       inputArgs.append(ffmpeg.input(video))

#     # Concatenate the input videos
#     ffmpeg.concat(*inputArgs).output(output_path).run()

# # Example usage
# # video_list = ["test-scale.mp4","drakex21.mp4"]
# video_list = ["test-scale.mp4"]
# output_video = "test123.mp4"
# ffmpeg.input("drakex21.mp4").trim(start_frame  = 100).setpts('PTS-STARTPTS').output('test-trim.mp4').run()

# ffmpeg.input("test_video.mp4").output('test-scale.mp4', vf = 'scale=1280:720').run()

# concatenate_videos(video_list, output_video)

print(calculateBoundsForCentered(1000,1000, 1920, 1080))
