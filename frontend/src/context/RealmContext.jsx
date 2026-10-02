import React,{createContext,useCallback,useContext} from 'react';
import {Link,useNavigate} from 'react-router-dom';
import {api} from '../lib/api';

const path=to=>to;
const live={api,path};
const RealmContext=createContext(live);
export const useRealm=()=>useContext(RealmContext);
export const RealmProvider=({children})=><RealmContext.Provider value={live}>{children}</RealmContext.Provider>;
export const RealmLink=({to,...props})=><Link to={typeof to==='string'?path(to):to} {...props}/>;
export const useRealmNavigate=()=>{
 const navigate=useNavigate();
 return useCallback((to,options)=>navigate(typeof to==='string'?path(to):to,options),[navigate]);
};