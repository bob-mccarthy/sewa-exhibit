import { StyleSheet, Text, View, TouchableOpacity } from 'react-native';
import { useEffect, useState } from 'react';
import WifiManager from "react-native-wifi-reborn";
import { PermissionsAndroid } from 'react-native';
import VideoScreen from './VideoScreen';
import SelectScreen from './SelectScreen';
import DimensionScreen from './DimensionScreen';
import AsyncStorage from '@react-native-async-storage/async-storage';
import ActionContext from '../Context';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import WebSocketManager from '../websocket';
import {WIFI_SSID, WIFI_PASSWORD} from '@env'

const Stack = createNativeStackNavigator();
export default function HomePage() {
  const [action, setAction] = useState({message: 'nothing'})
  const [notConnected, setNotConnected] = useState<boolean>(false)
  const [connectionStr, setConnectionStr] = useState<string>("Click the reconnect button below")
  const connectToWifi = () => {
    WifiManager.connectToProtectedWifiSSID({ssid:WIFI_SSID, password: WIFI_PASSWORD}).then(
      () => { 
        console.log("Connected successfully!");
        setNotConnected(false)
      },  
      (error) => {
        console.log(error);
        setConnectionStr("Could not reconnect to the internet call tech support")
        console.log("Connection failed!");
      }
    );
  }

  const connectToWebSocket = () =>{
    let ws = WebSocketManager.getInstance()
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
  useEffect(() => {
    
    console.log('starting up')
    connectToWebSocket()
    
   return () => {
   };
   },[])
  useEffect(() => {
    PermissionsAndroid.request(
      PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
      {
        title: 'Location permission is required for WiFi connections',
        message:
          'This app needs location permission as this is required  ' +
          'to scan for wifi networks.',
        buttonNegative: 'DENY',
        buttonPositive: 'ALLOW',
      },
    ).then((granted) => {
      if (granted === PermissionsAndroid.RESULTS.GRANTED) {
        // You can now use react-native-wifi-reborn
        WifiManager.getCurrentWifiSSID().then(
          ssid => {
            console.log("Your current connected wifi SSID is " + ssid);
            if (ssid !== "NETGEAR94" && ssid !== "NETGEAR94-5G"){
              setNotConnected(true)
            }
          },
          () => {
            console.log("Cannot get current SSID!");
            setNotConnected(true)
          }
        ); 
    } 
    }) 
    
  }, [])
  return (
    <ActionContext.Provider value = {action}>
    {/* <NavigationContainer> */}
    <View style = {{width: '100%', height: '100%'}}>
      
      {notConnected && <View style = { [styles.videoCover, {backgroundColor: 'red', justifyContent:'center', alignContent:'center'}]}>
        <Text style = {{textAlign: 'center', fontSize: 24, color:'white'}}>
          Not Connected to the Internet 
        </Text>
        <Text style = {{textAlign: 'center', fontSize: 16, color:'white'}}>
          {connectionStr}
        </Text>
        <View style={styles.btnContainer}>
        <TouchableOpacity style = {styles.btn} onPress={connectToWifi}>
          <Text style = {{textAlign: 'center', fontSize: 16, color:'white'}}>
            Reconnect
          </Text>
        </TouchableOpacity>
        </View>
      </View>}
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
    </View>
    {/* </NavigationContainer> */}
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
  videoCover:{
    flex:1,
    position:'absolute',
    width:'100%',
    height:'100%',
    zIndex: 99
  },
  btn: {
    padding: 10,
    backgroundColor: 'orange',
    borderRadius: 10,
    justifyContent:'center',
    alignContent: 'center',
  },
  btnContainer:{
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height:50,
    width: '100%',
  }
  // videoCoverContainer:{
  //   position: 'relative',
  //   width:'100%',
  //   height:'100%',
  // },
});
