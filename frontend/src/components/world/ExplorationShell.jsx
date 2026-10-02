import React,{useEffect} from 'react';
import {useLocation,useNavigate} from 'react-router-dom';
import {CityCanvas} from '../../world/CityCanvas';
import {useWorld} from '../../context/WorldContext';
import {Header} from '../Header';
import {PrimaryNavigation} from '../PrimaryNavigation';

export const ExplorationShell=({children})=>{
 const {pathname}=useLocation(),navigate=useNavigate();
 const {world,city,district,layers,setCamera,reset}=useWorld();
 const inWorld=pathname==='/world';
 useEffect(()=>{if(!inWorld)window.scrollTo(0,0);},[pathname,inWorld]);
 useEffect(()=>{if(inWorld)reset();},[inWorld,reset]);
 return <div className={`exploration-shell ${inWorld?'in-world':'inside-place'}`} data-testid="exploration-shell">
  <Header tokens={world?.tokens||[]}/>
  {inWorld&&<div className="persistent-world" data-testid="world-scene"><CityCanvas ref={city} tokens={world?.tokens||[]} onSelect={id=>navigate(`/token/${id}`)} district={district} layers={layers} onCamera={setCamera}/></div>}
  <div className="realm-content">{children}</div>
  <PrimaryNavigation mobile/>
 </div>;
};