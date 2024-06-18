import { StyleSheet} from 'react-native';
import EventSource from "react-native-sse";
import { useEffect, useState, createContext } from 'react';
import VideoScreen from './screens/VideoScreen'; 
import SelectScreen from './screens/SelectScreen';
import DimensionScreen from './screens/DimensionScreen';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import ActionContext from './Context';
import * as FileSystem from 'expo-file-system'
import * as Updates from 'expo-updates';
import ws from './Socket';
import AsyncStorage from '@react-native-async-storage/async-storage';



const readDir = async () => {
  let documents = await FileSystem.readDirectoryAsync(FileSystem.documentDirectory)
  let info = await FileSystem.getInfoAsync(FileSystem.documentDirectory + 'display-vid.mp4')
  console.log(documents)
  console.log({info})
  let modTime = new Date(0)
  modTime.setUTCSeconds(info.modificationTime)
  console.log(modTime.toLocaleDateString() + ' ' + modTime.toLocaleTimeString())
}


const Stack = createNativeStackNavigator();
// const ActionContext = createContext(null);
const baseUrl = 'http://192.168.0.223'

export default function App() {
  const reload = async () => {
    try {
      console.log('reloading');
      // Reload the app
      await Updates.reloadAsync();
    } catch (error) {
        console.error('Failed to reload the app:', error);
    }
  }
  const [reloadID, setReloadID] = useState(null)
  const [action, setAction] = useState({message: 'nothing'})
  useEffect(() => {
   setReloadID(setTimeout(() => reload(),30000))

   ws.onopen = () => {
    // connection opened
    ws.send('open'); // send a message
    console.log('opening');
    setInterval(() => {
      AsyncStorage.getItem('phonePos').then((phonePos)=>{
        console.log(`sending ping: ${phonePos}`)
        ws.send(`ping: ${phonePos}`)
      })
      
    }, 30 * 1000)
    setReloadID(prevReloadID => {
      console.log(prevReloadID)
      clearTimeout(prevReloadID)
      return setTimeout(() => reload(),45 * 1000)
    })
  }
    
    
  ws.onmessage = e => {
    // console.log(`message: ${e}`)
    console.log(`message: ${JSON.stringify(e)}`)
    setAction(JSON.parse(e.data))
    setReloadID(prevReloadID => {
      console.log(prevReloadID)
      clearTimeout(prevReloadID)
      return setTimeout(() => reload(),45 * 1000)
    })
  };
  
  ws.onerror = e => {
    // an error occurred
    console.log(e.message);
  };
  
  ws.onclose = e => {
    console.log('closing')
    reload();
    // connection closed
    console.log(e.code, e.reason);
  };
  return () => {
  };
  },[])

  useEffect(() => {
    readDir()
    
  },[])
  
  return (
    <ActionContext.Provider value = {action}>
    <NavigationContainer>
      <Stack.Navigator initialRouteName='video' screenOptions={{headerShown: false}}>
        <Stack.Screen
          name="video"
          component={VideoScreen}
        />
        <Stack.Screen
          name="select"
          component={SelectScreen}
        />
        <Stack.Screen
          name="dim"
          component={DimensionScreen}
        />
      </Stack.Navigator>
    </NavigationContainer>
    </ActionContext.Provider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
