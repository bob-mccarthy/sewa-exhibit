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
  const [action, setAction] = useState({message: 'nothing'})
  useEffect(() => {
    const es = new EventSource(`${baseUrl}/events`);

    es.addEventListener("open", (event) => {
      console.log("Open SSE connection.");
    });

    es.addEventListener("message", (event) => {
      setAction(JSON.parse(event.data))
      console.log({newMessage: JSON.parse(event.data)})
      console.log("New message event:", event.data);
    });

    es.addEventListener("error", (event) => {
      if (event.type === "error") {
        console.error("Connection error:", event.message);
      } else if (event.type === "exception") {
        console.error("Error:", event.message, event.error);
      }
    });

    es.addEventListener("close", (event) => {
      console.log("Close SSE connection.");
    });
    return () => {
      es.removeAllEventListeners();
      es.close();
    };
  },[])

  useEffect(() => {
    readDir()
    
  },[])
  
  return (
    <ActionContext.Provider value = {action}>
    <NavigationContainer>
      <Stack.Navigator initialRouteName='select' screenOptions={{headerShown: false}}>
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
