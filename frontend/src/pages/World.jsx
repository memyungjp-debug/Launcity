import React from 'react';
import {Plus,Minus,Focus,Map,Box,RefreshCw,ArrowUpRight} from 'lucide-react';
import {Link} from 'react-router-dom';
import {useWorld} from '../context/WorldContext';

export default function World(){
 const {world,loading,error,reload,city,reset,top,setTop}=useWorld();
 return <main className="live-world" data-testid="world-page" aria-label="Interactive NEXUS token world">
  {loading&&<div className="world-message" data-testid="world-loading"><RefreshCw size={21} className="spin"/>Opening the world…</div>}
  {error&&<div className="world-message" role="alert" data-testid="world-error"><span>World data is temporarily unavailable.</span><button data-testid="retry-world" onClick={reload}>Try again <RefreshCw size={15}/></button></div>}
  {!loading&&!error&&!world?.tokens.length&&<div className="world-message" data-testid="world-empty"><span>The first building starts with you.</span><Link to="/launch" data-testid="genesis-launch">Launch a token<ArrowUpRight size={15}/></Link></div>}
  <div className="world-bottom"><span className="world-summary" data-testid="world-status"><span className="status-dot"/><span data-testid="world-token-count">{world?.tokens.length??'—'} tokens</span></span>
   <div className="simple-map-controls" aria-label="Map controls">{[[Plus,'Zoom in','zoom-in',()=>city.current?.zoom(1)],[Minus,'Zoom out','zoom-out',()=>city.current?.zoom(-1)],[Focus,'Reset view','reset-view',reset],[top?Box:Map,top?'3D view':'Top view','toggle-view',()=>{setTop(!top);city.current?.view(!top);}]].map(([Icon,label,id,action])=><button key={id} data-testid={id} title={label} aria-label={label} onClick={action}><Icon size={17}/></button>)}</div>
  </div>
 </main>;
}