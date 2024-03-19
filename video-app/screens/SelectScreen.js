import { StyleSheet, Text, View, SafeAreaView, TouchableOpacity, useWindowDimensions } from 'react-native';
import { useState, useEffect, useContext } from 'react';
import ActionContext from '../Context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system'




const baseUrl = 'http://192.168.0.223'


export default function SelectScreen({navigation}) {
  const action = useContext(ActionContext)
  const [gridDim, setGridDim] = useState({r:0, c:0})
  const [buttonGrid, setButtonGrid] = useState(null)
  const [phonePos, setPhonePos] = useState(null) //position of the phones in the grid [row, col], 1-indexed
  const [downloadProgress, setDownloadProgress] = useState(null)

  const download = async (row, col) => {
    const callback = downloadProgress => {
      const progress = downloadProgress.totalBytesWritten / downloadProgress.totalBytesExpectedToWrite;
      setDownloadProgress(progress)
    };
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
    } catch (e) {
      console.error(e);
    } 
  }

  const storeInfo = async (key, val) => {
    try {
      let item = await AsyncStorage.setItem(key, val);
    } catch (e) {
      console.log(e)
    }
  }

  const selectPhonePos = async (i, j) => {
    setPhonePos([i+1, j+1])
    
    storeInfo('phonePos', JSON.stringify([i+1, j+1]))
    let width = await AsyncStorage.getItem('width')
    let height = await AsyncStorage.getItem('height')
    let isTablet = await AsyncStorage.getItem('isTablet')
    let offsetY = await AsyncStorage.getItem('offsetY')
    // if this is a tablet it is then in landscape mode and we need to swap its width and height 
    if(isTablet){
      [width, height] = [height,width]
    }
    //send phone pos, and dimensions to servers (dimensions will be null if they have not been set)
    fetch('http://192.168.0.223/dim', {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        index: [i,j],
        dimension: [parseFloat(width), parseFloat(height), parseFloat(offsetY)],
        isTablet: isTablet === null ? false : isTablet,
      }),
    });
  } 

  useEffect(() => {
    fetch(`${baseUrl}/dim`)
      .then(payload => payload.json())
      .then(gridDimension => setGridDim(gridDimension))

      AsyncStorage.getItem('phonePos').then((oldPhonePos) => {
        if (oldPhonePos !== null){
          setPhonePos(JSON.parse(oldPhonePos))
        }
      })
  }, [])

  useEffect(() => {
    let newButtonGrid = []
    if(gridDim.r === 0){
      setButtonGrid(<Text>row was 0</Text>)
      return
    }
    for(let i = 0; i < gridDim.r; i++){
      let currButtonRow = []
      for(let j = 0; j < gridDim.c; j++){

          currButtonRow.push(
              <TouchableOpacity style = {[styles.gridBtn,(phonePos && phonePos[0]-1 == i && phonePos[1]-1 == j)? styles.selected: styles.unselected]} key={`${i+1},${j+1}`} onPress = {() => selectPhonePos(i, j)}>
                <Text style = {{textAlign: 'center'}}>
                {`r:${i+1},c:${j+1}`}
                </Text>
              </TouchableOpacity>   
          )        
      }
      newButtonGrid.push(
          <View style = {[styles.btnRow, {maxHeight:`${Math.round(100/gridDim.r)}%`}]} key = {i}>
            {currButtonRow}
          </View>
      )
    }
    setButtonGrid(newButtonGrid)
  },[gridDim, phonePos])

  return (
    <SafeAreaView style = {styles.view}>
      <View style = {styles.gridContainer}>
        {buttonGrid}
      </View>
      <Text>
        Server Message: {action?.message}
      </Text>
      <View style = {styles.btnsContainer}>
        <TouchableOpacity style = {styles.btn} onPress={() => {
          if(phonePos !== null){
            navigation.navigate("video", {phonePos})
          }
          }}>
          <Text style = {{textAlign:'center'}}>
            Go to Video Screen
          </Text>
        </TouchableOpacity>
        <TouchableOpacity style = {styles.btn} onPress={() => navigation.navigate("dim")}>
          <Text style = {{textAlign:'center'}}>
            Go to Dimension Screen
          </Text>
        </TouchableOpacity>
      </View>
      {phonePos && <TouchableOpacity style = {styles.btn} onPress={() => download(...phonePos)}>
        <Text style = {{textAlign:'center'}}>
          Download Video
        </Text>
      </TouchableOpacity>}
      {downloadProgress && 
        <Text>
          Download Progress: {downloadProgress === 1 ? 'Done' : `${Math.round(downloadProgress * 100)}%`}
        </Text>}
      
    </SafeAreaView>
  )

}

const styles = StyleSheet.create({
  view: {
    alignItems: 'center',
    justifyContent: 'center',
    margin: 5,
    gap: 5
  },
  gridContainer:{
    maxHeight: '95%',
    overflow: 'hidden',
    flexDirection: 'column',
    gap: 5,
  },
  btnRow:{
    // flex: 1,
    flexDirection: 'row',
    width: '100%',
    // maxHeight: 10,
    gap: 5
  },
  selected:{
    backgroundColor: 'lightblue'
  },
  unselected:{
    backgroundColor: 'grey'
  },
  gridBtn: {
    flex: 1, 
    width: '100%', 
    height: '100%', 
    alignContent: 'center',
    justifyContent: 'center',
    borderRadius: 10
  },
  btn: {
    height:50,
    width: '50%',
    backgroundColor: 'skyblue',
    borderRadius: 10,
    justifyContent:'center',
    alignContent: 'center',
  },
  btnsContainer: {
    flexDirection: 'row',
    width: '100%',
    gap: 5
  }
});