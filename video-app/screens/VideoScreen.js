import { StyleSheet, Text, View, SafeAreaView, Button, TouchableOpacity } from 'react-native';
import { useState, useRef, useEffect, useContext } from 'react';
import Video from 'react-native-video';
import { GestureHandlerRootView, Gesture, GestureDetector } from 'react-native-gesture-handler';
import ActionContext from '../Context';







export default function VideoScreen({navigation, route}) {
  const action = useContext(ActionContext)
  const [isVisible, setIsVisible] = useState(false)
  const {phonePos} = route.params //determines which phone that we get
  const [showHeader, setShowHeader] = useState(false)
  const [paused, setPaused] = useState(true)
  const videoRef = useRef(null)
  const handleProgress = ({currentTime, playableDuration, seekableDuration}) =>{
    // console.log({currentTime, playableDuration, seekableDuration})
    // if(currentTime >= 20){
    //   setPaused(true)
    // }
  }
  const tap = Gesture.Tap()
    .onBegin(() => {
      console.log('tap')
      setShowHeader(!showHeader)
    });
  useEffect(() => {
    if(action?.message === 'start'){
      // let startTime = new Date(action.startTime)
      // let currTime = new Date()
      // setTimeout(() => {
      //   setPaused(false)
      //   console.log(`starting to play at: ${new Date()}`)
      // }, startTime - currTime)
      // setTimeout(() => {
      //   setIsVisible(true)
      // }, startTime-currTime+action.delay)
      // console.log(`current time: ${currTime} `)
      // console.log(`start time: ${startTime} `)
      // console.log(`time until unpaused: ${startTime-currTime}`)
      setTimeout(() => {
        setIsVisible(true)
      }, action.delay ? Math.random()*2000 : 0)
      setPaused(false)
    }
    else if (action?.message === 'stop'){
      setPaused(true)
    }
    else if (action?.message === 'restart'){
      videoRef.current?.seek(0)
    }
  }, [action])
  
  

  return (
    <SafeAreaView style = {{width: '100%', height: '100%'}}>
    <GestureHandlerRootView style = {styles.view}>
      {showHeader && 
        <SafeAreaView style = {styles.header}>
          <TouchableOpacity style = {styles.btn} onPress={() =>navigation.navigate('select')}>
            <Text>
              Back
            </Text>
          </TouchableOpacity>
        </SafeAreaView>
      }
      {/* <View style = {styles.videoContainer}>  */}
      <GestureDetector s gesture={tap}>
        <View style = {styles.videoCoverContainer}>
        <SafeAreaView style = {[styles.videoCover, {zIndex: isVisible ? 0: 1}]}>
        </SafeAreaView>
        <SafeAreaView style = {styles.videoContainer} >
          <Video 
            ref = {videoRef}
            style = {styles.video}
            source = {{uri: `http://192.168.0.222/video/${phonePos[0]}/${phonePos[1]}`}}
            controls = {false}
            fullscreen = {false}
            volume={0.5}
            muted = {false}
            paused ={paused}
            ignoreSilentSwitch={"ignore"}
            resizeMode='cover'
            rate={1}
            onProgress={handleProgress}
            >
          </Video>
        </SafeAreaView>
        </View>
      </GestureDetector>
      {/* </View> */}
    </GestureHandlerRootView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  view: {

    alignItems: 'center',
    flex: 1,
    // flexDirection: 'column',
    justifyContent: 'center',
    backgroundColor: 'white',
    
  },
  header:{
    flex:1,
    backgroundColor: 'black',
    width: '100%',
    maxHeight: 100,
    minHeight: 50,
    // maxHeight: 100,
    zIndex:1
  },
  btn:{
    width: '100%',
    height: '100%',
    backgroundColor: 'lightblue'
  },
  videoCoverContainer:{
    position: 'relative',
    width:'100%',
    height:'100%',
  },
  videoContainer:{
    position:'absolute',
    flex: 1,
    backgroundColor: 'black',
    width:'100%',
    height:'100%'
  },
  video:{
    width:'100%',
    height:'100%',
    // zIndex: 1
  },
  videoCover:{
    position:'absolute',
    width:'100%',
    height:'100%',
    backgroundColor: 'black',
  }

});
