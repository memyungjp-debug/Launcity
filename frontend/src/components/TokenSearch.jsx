import React,{useEffect,useRef,useState} from 'react';
import {useNavigate,useLocation} from 'react-router-dom';
import {Search,X,ArrowUpRight} from 'lucide-react';
import {money} from '../lib/api';
import {TokenAvatar} from './Shared';

export const TokenSearch=({tokens=[]})=>{
 const [query,setQuery]=useState(''),[focused,setFocused]=useState(false);
 const navigate=useNavigate(),{pathname}=useLocation(),input=useRef(null),wrap=useRef(null);
 const matches=tokens.filter(t=>`${t.name} ${t.symbol} ${t.mint}`.toLowerCase().includes(query.toLowerCase())).slice(0,6);
 const go=t=>{navigate(`/token/${t.id}`);setQuery('');setFocused(false);input.current?.blur();};
 useEffect(()=>{setFocused(false);setQuery('');},[pathname]);
 useEffect(()=>{
  const key=e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();input.current?.focus();}if(e.key==='Escape'){setFocused(false);input.current?.blur();}};
  const outside=e=>{if(!wrap.current?.contains(e.target))setFocused(false);};
  document.addEventListener('keydown',key);document.addEventListener('pointerdown',outside);
  return()=>{document.removeEventListener('keydown',key);document.removeEventListener('pointerdown',outside);};
 },[]);
 return <div className="token-search" ref={wrap}><Search size={16}/><input ref={input} value={query} data-testid="world-search" aria-label="Search tokens" placeholder="Search tokens…" aria-expanded={focused} aria-controls="token-search-results" onFocus={()=>setFocused(true)} onBlur={e=>{if(!wrap.current?.contains(e.relatedTarget))setFocused(false);}} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&matches.length)go(matches[0]);}}/>
  {query&&<button className="clear-search" data-testid="clear-search" title="Clear search" aria-label="Clear search" onClick={()=>{setQuery('');input.current?.focus();}}><X size={14}/></button>}
  {focused&&<div id="token-search-results" className="token-search-results" data-testid="search-results"><span className="search-caption" data-testid="search-caption">{query?'Search results':'In the world'}</span>{matches.length?matches.map(t=><button key={t.id} data-testid={`search-result-${t.id}`} onClick={()=>go(t)}><TokenAvatar token={t} size={32}/><span><strong>{t.name}</strong><small>${t.symbol}</small></span><span className="search-cap">{money(t.market_cap)}</span><ArrowUpRight size={14}/></button>):<p data-testid="search-no-results">No tokens found.</p>}</div>}
 </div>;
};