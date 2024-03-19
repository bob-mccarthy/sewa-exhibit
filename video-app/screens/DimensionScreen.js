import Checkbox from 'expo-checkbox';
import React, { useEffect, useState } from 'react';
import {View, StyleSheet, Text, useWindowDimensions,TextInput, TouchableOpacity} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function DimensionScreen({navigation}) {
  const {height, width} = useWindowDimensions();
  const [screenHeightPX, setScreenHeightPX] = useState(height)
  const [screenHeightMM, setScreenHeightMM] = useState((height/160)*25.4)
  const [screenWidthPX, setScreenWidthPX] = useState(width)
  const [screenWidthMM, setScreenWidthMM] = useState((width/160)*25.4)
  const [screenOffsetY, setScreenOffsetY] = useState(0)
  const [isTablet, setIsTablet] = useState(false);

  const storeInfo = async (key, val) => {
    try {
      let item = await AsyncStorage.setItem(key, val);
    } catch (e) {
      console.log(e)
    }
  }

  const getInfo = async () => {
    let width = await AsyncStorage.getItem('width')
    let height = await AsyncStorage.getItem('height')
    let offsetY = await AsyncStorage.getItem('offsetY')
    let prevIsTablet = await AsyncStorage.getItem('isTablet')
    if (width){
      setScreenWidthMM(width)
      setScreenHeightPX(Math.floor((width / 25.4) * 160))
    }
    if(height){
      setScreenHeightMM(height)
      setScreenHeightPX(Math.floor((height / 25.4) * 160))
    }
    if(prevIsTablet !== null){
      setIsTablet(JSON.parse(prevIsTablet))
    }
    if(offsetY){
      setScreenOffsetY(offsetY)
    }
  }
  useEffect(() => {
    getInfo()

  }, [])
  const handleChangeHeight = (newText) => {
    // console.log(typeof(parseFloat(newText)))
    if(isNaN(parseFloat(newText))){
      console.log('invalid number')
      return
    }
    setScreenHeightMM(parseFloat(newText))
    setScreenHeightPX(Math.floor(parseFloat(newText) / 25.4 * 160))
    storeInfo('height', String(parseFloat(newText)))
  }
  const handleChangeWidth = (newText) => {
    if(isNaN(parseFloat(newText))){
      console.log('invalid number')
      return
    }
    setScreenWidthMM(parseFloat(newText))
    setScreenWidthPX(Math.floor(parseFloat(newText) / 25.4 * 160))
    storeInfo('width', String(parseFloat(newText)))
  }

  const handleChangeIsTablet = (currIsTablet) => { 
    setIsTablet(currIsTablet)
    storeInfo("isTablet", String(currIsTablet))
  }

  const handleChangeOffset = (offsetY) => { 
    setScreenOffsetY(offsetY)
    storeInfo("offsetY", String(offsetY))
  }

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Window Dimension Data</Text>
      <View style = {styles.textInputContainer}>
        <Text>Is this a Tablet?:</Text>
        <Checkbox value={isTablet} onValueChange={handleChangeIsTablet} />
      </View>

      <View style = {styles.textInputContainer}>
        <Text>Offset Y (mm):</Text>
        <TextInput style = {styles.input} keyboardType={"number-pad"} onChangeText={handleChangeOffset}>{screenOffsetY}</TextInput>
      </View>

      <Text>Height (px): {screenHeightPX}</Text>
      <View style = {styles.textInputContainer}>
        <Text>Height (mm):</Text>
        <TextInput style = {styles.input} keyboardType={"number-pad"} onChangeText={handleChangeHeight}>{screenHeightMM}</TextInput>
      </View>
      
      <Text>Width (px): {screenWidthPX}</Text>
      <View style = {styles.textInputContainer}>
        <Text>Width (mm):</Text>
        <TextInput style = {styles.input} keyboardType={"number-pad"} onChangeText={handleChangeWidth}>{screenWidthMM}</TextInput>
      </View>

      <TouchableOpacity style = {styles.btn} onPress={() => navigation.navigate("select")}>
        <Text style = {{textAlign:'center'}}>
          Back to Select Screen
        </Text>
      </TouchableOpacity>
    </View>
  );
};
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    rowGap:10
  },
  header: {
    fontSize: 20,
    marginBottom: 12,
  },
  input : {
    height: 50,
    width:100,
    borderWidth:2,
    padding: 5
  },
  textInputContainer :{
    flexDirection: 'row',
    gap: 10,
    alignItems: 'center'
  },
  btn: {
    height:50,
    width: '50%',
    backgroundColor: 'skyblue',
    borderRadius: 10,
    justifyContent:'center',
    alignContent: 'center',
  }
});

