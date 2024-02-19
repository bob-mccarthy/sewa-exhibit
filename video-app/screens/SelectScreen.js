import { StyleSheet, Text, View, SafeAreaView, TouchableOpacity } from 'react-native';
import { useState, useEffect, useContext } from 'react';
import ActionContext from '../Context';
import * as FileSystem from 'expo-file-system'



const baseUrl = 'http://192.168.0.223'


export default function SelectScreen({navigation, route}) {
  const action = useContext(ActionContext)
  const [gridDim, setGridDim] = useState({r:0, c:0})
  const [buttonGrid, setButtonGrid] = useState(null)
  const [phonePos, setPhonePos] = useState(null)

  const download = async (row, col) => {
    const callback = downloadProgress => {
      const progress = downloadProgress.totalBytesWritten / downloadProgress.totalBytesExpectedToWrite;
      console.log(progress)
    };
    console.log({row, col})
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

  useEffect(() => {
    fetch(`${baseUrl}/dim`)
      .then(payload => payload.json())
      .then(gridDimension => setGridDim(gridDimension))
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
              <TouchableOpacity style = {[styles.gridBtn,(phonePos && phonePos[0]-1 == i && phonePos[1]-1 == j)? styles.selected: styles.unselected]} key={`${i+1},${j+1}`} onPress = {() => setPhonePos([i+1, j+1])}>
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
      <TouchableOpacity style = {styles.btn} onPress={() => {
        if(phonePos !== null){
          navigation.navigate("video", {phonePos})
        }
        }}>
        <Text style = {{textAlign:'center'}}>
          Go to Video Screen
        </Text>
      </TouchableOpacity>

      {phonePos && <TouchableOpacity style = {styles.btn} onPress={() => download(...phonePos)}>
        <Text style = {{textAlign:'center'}}>
          Download Video
        </Text>
      </TouchableOpacity>}
      
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
    width: '100%',
    backgroundColor: 'skyblue',
    borderRadius: 10,
    justifyContent:'center',
    alignContent: 'center',
  }
});