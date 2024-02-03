import { StyleSheet, Text, View, SafeAreaView, TouchableOpacity } from 'react-native';
import { useState, useEffect, useContext } from 'react';
import ActionContext from '../Context';

const outputTime = (action) => {
  if(action.message === "start"){
    let startTime = new Date(action.startTime)
    let currTime = new Date()
    return `start time: ${startTime}, currTime: ${currTime}, diff: ${startTime-currTime}`
  }
  return action.message
}

// const ActionContext = createContext(null);
export default function SelectScreen({navigation, route}) {
  const action = useContext(ActionContext)
  // const {action} = route.params
  // const [gridDim, setGridDim] = useState(JSON.parse(AsyncStorage.getItem('gridDim')))
  const [gridDim, setGridDim] = useState({r:0, c:0})
  // const [connected, setConnected] = useState("Not Connected")
  const [buttonGrid, setButtonGrid] = useState(null)
  const [phonePos, setPhonePos] = useState(null)
  useEffect(() => {
    fetch('http://192.168.0.222/dim')
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
              <TouchableOpacity style = {styles.gridBtn} key={`${i+1},${j+1}`} onPress = {() => setPhonePos([i+1, j+1])}>
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
  },[gridDim])

  return (
    <SafeAreaView style = {styles.view}>
      {/* <Text>
        Hello World
      </Text> */}
      <View style = {styles.gridContainer}>
        {buttonGrid}
      </View>
      <TouchableOpacity style = {styles.btn} onPress={() => {
        if(phonePos !== null){
          navigation.navigate("video", {phonePos})
        }
        }}>
        <Text>
          Go to Video Screen
        </Text>
      </TouchableOpacity>
      <Text>
        {action ? outputTime(action): "Nothing"}
      </Text>
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
  gridBtn: {
    flex: 1, 
    width: '100%', 
    height: '100%', 
    backgroundColor: 'lightblue',
    alignContent: 'center',
    justifyContent: 'center'
  },
  btn: {
    height:'10%',
    width: '100%',
    backgroundColor: 'skyblue'
  }
});