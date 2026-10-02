import React,{createContext,useContext,useRef,useState,useEffect,useCallback} from 'react';
import {useRealm} from './RealmContext';
const WorldContext=createContext(null);
export const useWorld=()=>useContext(WorldContext);
export const WorldProvider=({children})=>{
 const {api}=useRealm(),city=useRef(null);
 const [world,setWorld]=useState(null),[loading,setLoading]=useState(true),[error,setError]=useState(false);
 const [camera,setCamera]=useState({x:0,z:0,zoom:1}),[district,setDistrict]=useState('all'),[layers,setLayers]=useState({labels:true,territories:true}),[top,setTop]=useState(false);
 const reload=useCallback(async()=>{try{const {data}=await api.get('/world');setWorld(data);setError(false);}catch{setError(true);}finally{setLoading(false);}},[api]);
 useEffect(()=>{setWorld(null);setLoading(true);setDistrict('all');reload();const timer=setInterval(reload,60000);return()=>clearInterval(timer);},[reload]);
 const focus=useCallback(d=>{setDistrict(d.id);city.current?.focus(d.x,d.z);},[]);
 const reset=useCallback(()=>{setDistrict('all');setTop(false);city.current?.reset();},[]);
 return <WorldContext.Provider value={{world,loading,error,reload,city,camera,setCamera,district,layers,setLayers,top,setTop,focus,reset}}>{children}</WorldContext.Provider>;
};