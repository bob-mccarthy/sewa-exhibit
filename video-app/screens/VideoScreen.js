import { StyleSheet, Text, View, SafeAreaView, Button, TouchableOpacity } from 'react-native';
import { useState, useRef, useEffect, useContext } from 'react';
import Video from 'react-native-video';
import { GestureHandlerRootView, Gesture, GestureDetector } from 'react-native-gesture-handler';
import ActionContext from '../Context';
import ntpClient from 'react-native-ntp-client';
import * as FileSystem from 'expo-file-system'
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Updates from 'expo-updates';



const baseUrl = 'http://192.168.0.223'


export default function VideoScreen({navigation, route}) {
  const action = useContext(ActionContext)
  const [showHeader, setShowHeader] = useState(false)
  const [paused, setPaused] = useState(true)
  const videoRef = useRef(null)
  const refreshPage = async() =>{
    try {
      // Reload the app
      await Updates.reloadAsync();
    } catch (error) {
      console.error('Failed to reload the app:', error);
    }
  }
  const download = async (row, col) => {
    const callback = downloadProgress => {
      const progress = downloadProgress.totalBytesWritten / downloadProgress.totalBytesExpectedToWrite;
    };
    console.log(`http://192.168.0.223/video/${row}/${col}`)
    const downloadResumable = FileSystem.createDownloadResumable(
      `http://192.168.0.223/video/${row}/${col}`,
      FileSystem.documentDirectory + 'display-vid.mp4',
      {},
      callback
    );
  
    try {
      console.log('starting to download')
      const { uri } = await downloadResumable.downloadAsync();
      console.log('Finished downloading to ', uri);
      refreshPage()
    } catch (e) {
      console.error(e);
    } 
  }

  // const handleProgress = ({currentTime, playableDuration, seekableDuration}) =>{
  //   console.log({currentTime, playableDuration, seekableDuration})
  //   if(currentTime >= 20){
  //     setPaused(true)
  //   }
  // }

  //when the video ends the paused value should be set to 0
  const handleEnd = () => {
    setPaused(true)
  }
  const tap = Gesture.Tap()
    .onBegin(() => {
      setShowHeader(!showHeader)
    });
  useEffect(() => {
    if(action?.message === 'start'){
      setPaused(true)
      videoRef.current?.seek(0)
      ntpClient.getNetworkTime("192.168.0.223", 123, (error, date) => {
          if (error) {
              console.error(error);
              return;
          }
          let startTime = new Date(action.startTime)
          let currTime = date
          setTimeout(() => {
            setPaused(false)
            console.log(`starting to play at: ${new Date()}`)
            fetch(`${baseUrl}/logStart`)
          }, startTime - currTime)
          // setTimeout(() => {
          //   setIsVisible(true)
          // }, startTime-currTime+(action.delay ? Math.random()*2000 : 0))
          console.log(`current time: ${currTime} `)
          console.log(`start time: ${startTime} `)
          console.log(`time until unpaused: ${startTime-currTime}`)
      
          // console.log(`fetching current time: ${date}`); 
      });
    }
    else if (action?.message === 'stop'){
      setPaused(true)
    }
    else if (action?.message === 'restart'){
      videoRef.current?.seek(0)
    }
    else if (action?.message === 'download'){
      AsyncStorage.getItem('phonePos').then((phonePos) => {
        if (phonePos !== null){
          // console.log(JSON.parse(phonePos))
          download(...JSON.parse(phonePos))
          
        }
      })
      // download()
    }
    else if (action?.message === 'refresh'){
      refreshPage()
    }
  }, [action])
  
  

  return (
    <SafeAreaView style = {{width: '100%', height: '100vh'}}>
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
      <GestureDetector s gesture={tap}>
        <SafeAreaView style = {styles.videoCoverContainer}>
        <SafeAreaView style = {[styles.videoCover, {zIndex: paused ? 1: 0}]}>
        </SafeAreaView>
        <SafeAreaView style = {styles.videoContainer} >
          <Video 
            ref = {videoRef}
            style = {styles.video}
            source = {{uri: FileSystem.documentDirectory + 'display-vid.mp4'}}
            controls = {false}
            fullscreen = {false}
            volume={0.5}
            muted = {false}
            paused ={paused}
            ignoreSilentSwitch={"ignore"}
            resizeMode='cover'
            rate={1}
            // repeat = {true}
            // onProgress={handleProgress}
            onEnd={handleEnd}
            >
          </Video>
        </SafeAreaView>
        </SafeAreaView>
      </GestureDetector>
    </GestureHandlerRootView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  view: {
    alignItems: 'center',
    flex: 0,
    // flexDirection: 'column',
    justifyContent: 'center',
    backgroundColor: 'white',
    
  },
  header:{
    flex:0,
    backgroundColor: 'black',
    width: '100%',
    height: 50,
    // maxHeight: 100,
    zIndex:1
  },
  btn:{
    flex: 1,
    flexDirection: 'column-reverse',
    width: '100%',
    height: '100%',
    backgroundColor: 'lightblue',
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
