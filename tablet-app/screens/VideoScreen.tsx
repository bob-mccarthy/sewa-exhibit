import { useState, useContext, useEffect } from "react";
import {Text, View, TouchableOpacity } from "react-native";
import Video, {VideoRef} from 'react-native-video';
import { GestureHandlerRootView, Gesture, GestureDetector } from 'react-native-gesture-handler';
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useFocusEffect } from '@react-navigation/native';
import ActionContext from '../Context';


export default function VideoScreen({navigation} : any)
{
    const action = useContext(ActionContext)
    const [debugMode, setDebugMode] = useState<boolean>(false)
    const [displayVid, setDisplayVid] = useState<string | null>(null)
    const [showHeader, setShowHeader] = useState<boolean>(false)
    const [paused, setPaused] = useState<boolean>(false)
    const [hideVideo, setHideVideo] = useState<boolean>(false) //hideVideo is true when the exhibit needs to be turned off

    useFocusEffect(() => {
        async function getDisplayVid()
        {
            let storedDisplayVid = await AsyncStorage.getItem('display-vid')
            //only unpause and set video if the exhibit is on
            if (storedDisplayVid !== null && !hideVideo)
            {
                setPaused(false)
                setDisplayVid(storedDisplayVid)
            }
        }
        getDisplayVid() 
    })

    useEffect(() => {
        if (action?.message === 'tabletStart')
        {
            setHideVideo(false)
            setPaused(false)
        }
        else if (action?.message === 'tabletStop')
        {
            setHideVideo(true)
            setPaused(true)
        }
        else if (action?.message === 'debug')
        {
            setDebugMode(true)
        }
        else if (action?.message === 'prod')
        {
            setDebugMode(false)
        }
    },[action])

    const tripleTap = Gesture.Tap()
    .maxDuration(250)
    .numberOfTaps(3)
    .onStart(() => {
      setShowHeader(!showHeader)
    });
    console.log(paused)
    return (
        <GestureHandlerRootView 
            style = {{
                flex: 1,
                backgroundColor: 'black',
                position: 'relative'
            }}>
            {hideVideo &&  <View 
                style = {{
                    width: '100%',
                    height: '100%',
                    backgroundColor: 'black',
                    position: 'absolute',
                    zIndex: 2
                }}>
            </View>}
            {debugMode && showHeader && <TouchableOpacity 
                style = {{
                    position: 'absolute',
                    width: '100%',
                    height: '10%',
                    backgroundColor: 'skyblue',
                    justifyContent: 'center',
                    alignItems: 'center',
                    zIndex: 1
                }}  
                onPress={() => {
                    setPaused(true)
                    navigation.navigate('Settings')
                }}>
                <Text style = {{
                    fontSize: 30
                }}>
                    Back
                </Text>
            </TouchableOpacity>}
            <GestureDetector gesture = {tripleTap}>
                <View style = {{
                            flex: 1
                        }}>
                    {displayVid && 
                    <Video 
                        style = {{
                            flex: 1
                        }}
                        source = {{uri:displayVid}}
                        repeat = {true}
                        paused = {paused}
                        >
                    </Video>
                    }
                </View>
            
            </GestureDetector>
        </GestureHandlerRootView>
    )
}