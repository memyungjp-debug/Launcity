import React,{useEffect,useRef,useState,useCallback} from 'react';
import {RealmLink as Link,useRealm} from '../../context/RealmContext';
import {MessageSquare,ArrowUpRight,UserCircle2,LockKeyhole,RefreshCw} from 'lucide-react';
import {errorMessage,shortAddress} from '../../lib/api';
import {useWallet} from '../../context/WalletContext';
import {Empty,Loading} from '../Shared';
import {PostComposer} from './PostComposer';
import {PostCard} from './PostCard';

export const TokenCommunity=({token,compact=false})=>{
 const {api}=useRealm();
 const {wallet,connect}=useWallet();
 const [tab,setTab]=useState('all'),[items,setItems]=useState([]),[activity,setActivity]=useState([]),[stats,setStats]=useState(null);
 const [cursor,setCursor]=useState(null),[loading,setLoading]=useState(true),[error,setError]=useState('');
 const generation=useRef(0);
 const load=useCallback(async(append=false,after=null)=>{
  const request=++generation.current;
  if(!token.community_enabled){setLoading(false);return;}
  setLoading(true);
  try{
   const [summary,result]=await Promise.all([
    api.get(`/communities/${token.id}`),
    tab==='activity'?api.get('/activity',{params:{token_id:token.id}}):api.get(`/communities/${token.id}/feed`,{params:{tab,...(after?{cursor:after}:{})}})
   ]);
   if(request!==generation.current)return;
   setStats(summary.data);
   if(tab==='activity'){setActivity(result.data);setCursor(null);}
   else{setItems(old=>append?Array.from(new Map([...old,...result.data.items].map(p=>[p.event_id,p])).values()):result.data.items);setCursor(result.data.next_cursor);}
   setError('');
  }catch(e){if(request===generation.current)setError(errorMessage(e));}
  finally{if(request===generation.current)setLoading(false);}
 },[token.id,token.community_enabled,tab,api]);
 useEffect(()=>{const counter=generation;setItems([]);setActivity([]);setCursor(null);load();return()=>{counter.current++;};},[load,wallet]);
 if(!token.community_enabled)return <Empty icon={LockKeyhole} title="A community starts with a NEXUS launch." text="Only confirmed NEXUS tokens have a community." testId="community-nexus-only"><Link to="/launch" data-testid="community-launch-token" className="text-cta">Launch through NEXUS<ArrowUpRight size={14}/></Link></Empty>;
 const update=post=>setItems(old=>old.map(p=>p.id===post.id?{...p,...post,event_id:p.event_id,reposted_by:p.reposted_by}:p));
 return <div className="token-social-community" data-testid="token-social-community">
  <div className="social-community-top"><span data-testid="community-token-heading"><MessageSquare size={15}/>{token.symbol} community</span>{wallet?<Link to={`/profile/${wallet}`} data-testid="community-my-profile"><UserCircle2 size={15}/>My profile</Link>:<button data-testid="community-connect" onClick={connect}>Connect wallet</button>}{compact&&<Link data-testid="open-full-community" to={`/community/${token.id}`}>Open community<ArrowUpRight size={14}/></Link>}<button data-testid="community-refresh" aria-label="Refresh community" title="Refresh community" disabled={loading} onClick={()=>load()}><RefreshCw size={14} className={loading?'spin':''}/></button></div>
  {stats&&<div className="social-community-stats"><span data-testid="community-post-count">{stats.posts} posts</span><span data-testid="community-member-count">{stats.members} contributors</span><span data-testid="community-announcement-count">{stats.announcements} announcements</span></div>}
  <PostComposer token={token} onPosted={()=>load()}/>
  <div className="social-feed-tabs">{[['all','Community'],['following','Following'],['announcements','Announcements'],['activity','Activity']].map(([key,name])=><button key={key} data-testid={`community-feed-${key}`} className={tab===key?'active':''} onClick={()=>setTab(key)}>{name}</button>)}</div>
  {error?<div className="social-error" role="alert" data-testid="community-feed-error">{error}<button data-testid="retry-community-feed" onClick={()=>load()}>Try again</button></div>:loading&&!items.length&&!activity.length?<Loading text="Loading community…"/>:tab==='activity'?<div className="history-list" data-testid="community-activity-list">{activity.length?activity.map(event=><div key={event.id} data-testid={`community-activity-${event.id}`}><span className="status-dot"/><span>{event.post_id?<Link data-testid={`activity-post-${event.id}`} to={`/community/${token.id}/post/${event.post_id}`}>{event.text}</Link>:event.text}<small><Link data-testid={`activity-author-${event.id}`} to={`/profile/${event.wallet}`}>{shortAddress(event.wallet)}</Link> · {new Date(event.created_at).toLocaleString()}</small></span></div>):<Empty icon={MessageSquare} title="No activity yet." testId="community-activity-empty"/>}</div>:items.length?items.map(post=><PostCard key={post.event_id} post={post} onChange={update} onDeleted={()=>load()}/>):<Empty icon={MessageSquare} title={tab==='following'?'Your circle starts here.':tab==='announcements'?'No announcements yet.':'Be the first voice in this territory.'} testId="social-feed-empty"/>}
  {cursor&&<button className="social-load-more" data-testid="community-load-more" disabled={loading} onClick={()=>load(true,cursor)}>{loading?'Loading…':'Load more'}</button>}
 </div>;
};