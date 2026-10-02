import React,{useCallback,useEffect,useRef,useState} from 'react';
import {Link} from 'react-router-dom';
import {MessageSquare,RefreshCw,ArrowUpRight} from 'lucide-react';
import {api,errorMessage} from '../../lib/api';
import {useWallet} from '../../context/WalletContext';
import {Empty,Loading} from '../Shared';
import {PostCard} from './PostCard';

export const WorldFeed=()=>{
 const {wallet}=useWallet(),[items,setItems]=useState([]),[cursor,setCursor]=useState(null),[loading,setLoading]=useState(true),[error,setError]=useState('');
 const generation=useRef(0);
 const load=useCallback(async(after=null)=>{
  const request=++generation.current;setLoading(true);setError('');
  try{const {data}=await api.get('/social/feed',{params:after?{cursor:after}:{}});if(request!==generation.current)return;
   setItems(old=>after?Array.from(new Map([...old,...data.items].map(p=>[p.event_id,p])).values()):data.items);setCursor(data.next_cursor);
  }catch(e){if(request===generation.current)setError(errorMessage(e));}finally{if(request===generation.current)setLoading(false);}
 },[]);
 useEffect(()=>{const ref=generation;setItems([]);setCursor(null);load();return()=>{ref.current++;};},[load,wallet]);
 const update=post=>setItems(old=>old.map(p=>p.id===post.id?{...p,...post,event_id:p.event_id,reposted_by:p.reposted_by}:p));
 return <div className="world-feed-layout" data-testid="world-community-feed"><section className="world-feed-posts"><div className="world-feed-toolbar"><span data-testid="world-feed-caption">Latest from every community</span><button onClick={()=>load()} disabled={loading} data-testid="world-feed-refresh" title="Refresh feed" aria-label="Refresh feed"><RefreshCw size={15} className={loading?'spin':''}/></button></div>{error?<div className="social-error" role="alert" data-testid="world-feed-error">{error}<button data-testid="world-feed-retry" onClick={()=>load()}>Try again</button></div>:loading&&!items.length?<Loading text="Loading conversations…"/>:items.length?items.map(p=><PostCard key={p.event_id} post={p} showToken onChange={update} onDeleted={()=>load()}/>):<Empty icon={MessageSquare} title="Every conversation starts somewhere." text="Visit a token community and be the first to say something." testId="world-feed-empty"><Link to="/community" className="quiet-link" data-testid="feed-browse-communities">Find a community<ArrowUpRight size={14}/></Link></Empty>}{cursor&&<button className="social-load-more" disabled={loading} data-testid="world-feed-load-more" onClick={()=>load(cursor)}>{loading?'Loading…':'Load more posts'}</button>}</section><aside className="feed-aside"><span className="section-kicker" data-testid="feed-aside-label">ONE WORLD. MANY VOICES.</span><h2 data-testid="feed-aside-title">Start with your people.</h2><p data-testid="feed-aside-description">Open a token community to share an idea, ask a question, or join a conversation.</p><Link to="/community" className="quiet-link" data-testid="feed-aside-directory">Browse communities<ArrowUpRight size={15}/></Link></aside></div>;
};