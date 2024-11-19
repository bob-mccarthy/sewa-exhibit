import subprocess
import json
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

def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)
def get_fps(video_path):
    command = [
        'ffprobe', 
        '-v', 'error', 
        '-select_streams', 'v:0',  # Select the first video stream
        '-show_entries', 'stream=r_frame_rate',  # Get number of frames
        '-of', 'json',  # Output in JSON format
        video_path
    ]
    try:
        # Run the ffprobe command and capture the output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # Parse the output as JSON
        info = json.loads(result.stdout)
        if info == {}:
            return 0
        # print(video_path, info)
        # Extract the number of frames
        fps = info['streams'][0].get('r_frame_rate')
        
        if fps is None:
            raise ValueError("Frame count not found in ffprobe output")
        
        return fps
    
    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding ffprobe output.")
        return None
   
def get_video_frame_count(video_path):
    # Run ffprobe command to get video stream information in JSON format
    command = [
        'ffprobe', 
        '-v', 'error', 
        '-select_streams', 'v:0',  # Select the first video stream
        '-show_entries', 'stream=nb_frames',  # Get number of frames
        '-of', 'json',  # Output in JSON format
        video_path
    ]
    
    try:
        # Run the ffprobe command and capture the output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # Parse the output as JSON
        info = json.loads(result.stdout)
        if info == {}:
            return 0
        # print(video_path, info)
        # Extract the number of frames
        frame_count = info['streams'][0].get('nb_frames')
        
        if frame_count is None:
            raise ValueError("Frame count not found in ffprobe output")
        
        return int(frame_count)
    
    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding ffprobe output.")
        return None

