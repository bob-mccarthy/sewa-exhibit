
import { StatusBar } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import SettingScreen from './screens/SettingsScreen';
import VideoScreen from './screens/VideoScreen';
import * as NavigationBar from 'expo-navigation-bar';
import { useEffect, useState } from 'react';
import WebSocketManager from './websocket';
import ActionContext from './Context';

const Stack = createNativeStackNavigator();

export default function App() {
  const [action, setAction] = useState<any>({message: 'nothing'})
  const visibility = NavigationBar.useVisibility()
  useEffect(() => {
    setInterval(() => {
      NavigationBar.setVisibilityAsync('hidden')
    }, 5000)
  },[])
  useEffect(()=> {
    NavigationBar.setVisibilityAsync('hidden')
    NavigationBar.setPositionAsync("absolute");
    NavigationBar.setBackgroundColorAsync("transparent");
  },[visibility])

  const connectToWebSocket = () =>{
    let ws = WebSocketManager.getInstance()
    ws.onopen = () => {
    // connection opened
    ws.send('open'); // send a message
    console.log('opening');
    setInterval(() => {
      ws.send(`ping: side tablet`)
      
    }, 30 * 1000)
   }
     
     
   ws.onmessage = e => {
     // console.log(`message: ${e}`)
     console.log(`message: ${JSON.stringify(e)}`)
     setAction(JSON.parse(e.data))
   };
   
   ws.onerror = e => {
     // an error occurred
     console.log(e);
   };
   
   ws.onclose = e => {
     console.log('closing')
     // connection closed
     console.log(e.code, e.reason);
     WebSocketManager.resetInstance();
     setTimeout(() => connectToWebSocket(), 3000)
    //  connectToWebSocket()
   };
  }

  // useEffect(() => {
    
  //   console.log('starting up')
  //   connectToWebSocket()
    
  //  return () => {
  //  };
  //  },[])
  return (
    <>
    <ActionContext.Provider value = {action}>
      <NavigationContainer >
        <Stack.Navigator screenOptions={{headerShown: false}} initialRouteName='Settings'>
          <Stack.Screen name="Settings" component={SettingScreen} />
          <Stack.Screen name="Video" component={VideoScreen} />
        </Stack.Navigator>
      </NavigationContainer>
      <StatusBar hidden translucent backgroundColor="transparent" />
    </ActionContext.Provider>
    </>
      
  )
}


