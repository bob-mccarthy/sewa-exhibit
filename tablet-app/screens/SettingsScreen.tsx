import { useState, useEffect } from 'react';
import { Button, Text, SafeAreaView, ScrollView, StyleSheet, Image, View, Platform, TouchableOpacity } from 'react-native';
import * as MediaLibrary from 'expo-media-library';
import Video from 'react-native-video';
import AsyncStorage from '@react-native-async-storage/async-storage';



export default function SettingScreen({navigation}: any)
{
    
    const [assets, setAssets] = useState<MediaLibrary.Asset[] | null>(null);
    const [selectedVid, setSelectedVid] = useState<number | null>(null);
    
    const [permissionResponse, requestPermission] = MediaLibrary.usePermissions();

    useEffect(() => {
        async function getAssets() 
        {
            if (permissionResponse && permissionResponse.status !== 'granted') 
            {
            await requestPermission();
            }
            const fetchedAlbums = await MediaLibrary.getAlbumsAsync({
            includeSmartAlbums: true,
            });
            let currAssets: MediaLibrary.Asset[] = []
            for (const album of fetchedAlbums)
            {
                const albumAssets = await MediaLibrary.getAssetsAsync({ album, mediaType: 'video'});
                currAssets = currAssets.concat(albumAssets.assets) 
            }
            setAssets(currAssets)
        }
        getAssets()
    }, [])

    return (
        <View style = {{
                position: 'relative',
                height: '100%'
        }}>
            <View style = {{
                flex: 1,
                flexDirection: 'row',
                flexWrap: 'wrap',
                position: 'absolute',
                width: '100%',
                height: '100%',
                overflow: 'scroll',
                
            }}>
                {assets && assets.map((asset, i) => {
                    return( 
                        
                        <TouchableOpacity 
                            style = {{
                                flexBasis: '33%',
                                height: 200, 
                            }}
                            key = {i} 
                            onPressIn={() => setSelectedVid(i)}>
                            {/* <Text
                                style = {{
                                    flexBasis: '33%',
                                    borderWidth: selectedVid === i ? 10 : 0,
                                    borderColor: 'skyblue',
                                    // width: 200,
                                    // height: '50%'
                                    margin: 5,
                                    flex: 1
                                }}>
                                {asset.uri}
                                
                            </Text> */}
                            <Video 
                                style = {{
                                    flexBasis: '33%',
                                    borderWidth: selectedVid === i ? 10 : 0,
                                    borderColor: 'skyblue',
                                    // width: 200,
                                    // height: '50%'
                                    margin: 5,
                                    flex: 1
                                }}
                                paused = {i !== selectedVid} 
                                // repeat = {true}
                                source = {{uri: asset.uri}} />
                        </TouchableOpacity>
                    )
                })}
            </View>
            <View style = {{
                position: 'absolute',
                height: '15%',
                width: '100%',
                top: '85%',
                flex: 1,
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'center',


            }}>
                <TouchableOpacity style = {{
                    flex: 1,
                    height: '10%',
                    backgroundColor: 'skyblue',
                    minHeight: '90%',
                    maxWidth: '50%',
                    padding: -10,
                    borderRadius: 20,
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: 10
                    

                }} 
                    onPressIn={() => navigation.navigate('Video')}>
                    <Text style = {{
                        fontSize: 40,
                        color: 'white'
                    }}>
                        Go To Video Screen
                    </Text>
                </TouchableOpacity>

                <TouchableOpacity style = {{
                    flex: 1,
                    height: '10%',
                    backgroundColor: 'skyblue',
                    minHeight: '90%',
                    maxWidth: '50%',
                    padding: -10,
                    borderRadius: 20,
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: 10

                }} 
                    onPressIn={() => 
                    {
                        if (assets && selectedVid)
                        {
                            AsyncStorage.setItem('display-vid', assets[selectedVid].uri)
                        }
                        
                    }}>
                    <Text style = {{
                        fontSize: 40,
                        color: 'white'
                    }}>
                        Select Main Video
                    </Text>
                </TouchableOpacity>
            </View>
            
        </View>
    )
}
