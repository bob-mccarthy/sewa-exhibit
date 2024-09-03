import { useState, useRef, useEffect } from "react";
import { StyleSheet, Text, SafeAreaView, TouchableOpacity } from "react-native";
import Video, {VideoRef} from 'react-native-video';
import { GestureHandlerRootView, Gesture, GestureDetector } from 'react-native-gesture-handler';
import * as FileSystem from 'expo-file-system';
import ActionContext from '../Context';
import ntpClient from 'react-native-ntp-client';
import { useContext } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Updates from 'expo-updates';
import WebSocketManager from "../websocket";


export default function VideoScreen({navigation}: any) {
    const action = useContext(ActionContext)
    const [debugMode, setDebugMode] = useState<boolean>(true);
    const [paused, setPaused] = useState<boolean>(true);
    const [isDoneDownloading, setIsDoneDownloading] = useState<boolean>(false);
    const [showHeader, setShowHeader] = useState<boolean>(false);

    const videoRef = useRef<VideoRef>(null);

    const handleProgress = ({currentTime, playableDuration, seekableDuration}:any) =>{
        // console.log({currentTime, playableDuration, seekableDuration})
        console.log(`ct: ${currentTime} pd: ${playableDuration} sd: ${seekableDuration} paused: ${paused}`)
      }

    const refreshPage = async() =>{
        try {
          // Reload the app
          await Updates.reloadAsync();
        } catch (error) {
          console.error('Failed to reload the app:', error);
        }
      }

    const download = async (row:number, col:number) => {
        const callback = (downloadProgress : FileSystem.DownloadProgressData) => {
          const progress : number = downloadProgress.totalBytesWritten / downloadProgress.totalBytesExpectedToWrite;
        };
        const downloadResumable = FileSystem.createDownloadResumable(
          `http://192.168.0.223/video/${row}/${col}`,
          FileSystem.documentDirectory + 'display-vid.mp4',
          {},
          callback
        );
      
        try {
          console.log('starting to download')
          const result = await downloadResumable.downloadAsync();
          console.log('Finished downloading to ', result?.uri);
        } catch (e) {
          console.error(e);
        } 
      }
    //if video is not paused at the end of the video, it will not immediately play on restart 
    const handleEnd = () => {
        console.log('calling end function')
        setPaused(true)
    }

    useEffect(() => {
      console.log(`current value of paused ${paused}`)
    },[paused])

    useEffect(() => {
        let ws = WebSocketManager.getInstance();
        if(action?.message === 'start'){
          setPaused(true)
          videoRef.current?.seek(0)
          videoRef.current?.pause()
          ntpClient.getNetworkTime('192.168.0.223', 123, (error: any, date: Date) => {
              if (error) {
                  console.error(error);
                  return;
              }
              if (action.startTime === undefined){
                console.log("start time was not defined")
                return;
              }
              console.log('action startTime')
              console.log(action.startTime)
              let startTime = new Date(action.startTime)
              let currTime = date
              //if it gets the message after start time then do not play the video
              if (currTime.getTime() > startTime.getTime()){
                console.log(currTime.getTime(), startTime.getTime())
                console.log('received after it was supposed to play')
                return;
              }
              setTimeout(() => {
                setPaused(false)
                console.log(`starting to play at: ${new Date()}`)
                ws.send('started')
                
              }, startTime.getTime() - currTime.getTime())
              // setTimeout(() => {
              //   setIsVisible(true)
              // }, startTime-currTime+(action.delay ? Math.random()*2000 : 0))
              console.log(`current time: ${currTime}`)
              console.log(`time until unpaused: ${startTime.getTime()-currTime.getTime()}`)
          
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
              let parsedPhonePos: [number, number] =  JSON.parse(phonePos)
              download(...parsedPhonePos)
              
            }
          })
          // download()
        }
        else if (action?.message === 'refresh'){
          refreshPage()
        }
        else if (action?.message === 'debug'){
          setDebugMode(true)
        } 
        else if (action?.message === 'prod'){
          setDebugMode(false)
        }
      }, [action])

    const longPress = Gesture.Tap().onEnd((e,success) => {
        if (success){
          setShowHeader(!showHeader)
        }
      })
    return (
        <SafeAreaView style = {{width: '100%', height: '100%'}}>
            <GestureHandlerRootView style = {styles.view}>
            {showHeader && debugMode && 
                <SafeAreaView style = {styles.header}>
                <TouchableOpacity style = {styles.btn} onPress={() =>navigation.navigate('select')}>
                    <Text>
                        Back
                    </Text>
                </TouchableOpacity>
                </SafeAreaView>
            }
            <GestureDetector gesture={longPress}>
                <SafeAreaView style = {styles.videoCoverContainer}>
                    <SafeAreaView style = {[styles.videoCover, {zIndex: paused ? 1: 0}, {backgroundColor: isDoneDownloading ? 'green': 'black'}]}>
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
                    onEnd={handleEnd}
                    onProgress={handleProgress}
                    >
                </Video>
                </SafeAreaView>
                </SafeAreaView>
            </GestureDetector>
            </GestureHandlerRootView>
        </SafeAreaView>
    )
}

const styles = StyleSheet.create({
    view: {
      alignItems: 'center',
      flex: 0,
      justifyContent: 'center',
      backgroundColor: 'white',
      
    },
    header:{
      flex:0,
      backgroundColor: 'black',
      width: '100%',
      height: 50,
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
      width:'100%',
      height:'100%'
    },
    video:{
      width:'100%',
      height:'100%',
    },
    videoCover:{
      position:'absolute',
      width:'100%',
      height:'100%',
    }
  
  });
  