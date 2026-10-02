import React,{useCallback,useEffect,useRef,useState} from 'react';
import {useParams} from 'react-router-dom';
import {RealmLink as Link,useRealm} from '../context/RealmContext';
import {ArrowLeft,UserRound,UserPlus,Check,Settings2} from 'lucide-react';
import {toast} from 'sonner';
import {errorMessage,shortAddress} from '../lib/api';
import {useWallet} from '../context/WalletContext';
import {ActionButton,Loading,Empty} from '../components/Shared';
import {ProfileAvatar,AuthorLink} from '../components/community/SocialIdentity';
import {ProfileEditor} from '../components/community/ProfileEditor';
import {PostCard} from '../components/community/PostCard';
import {Dialog,DialogContent,DialogTitle,DialogDescription} from '../components/ui/dialog';
export default function Profile(){
 const {api}=useRealm();
 const {wallet:address}=useParams(),{wallet,authenticate,connect}=useWallet(),[profile,setProfile]=useState(null),[items,setItems]=useState([]),[cursor,setCursor]=useState(null),[tab,setTab]=useState('posts'),[editing,setEditing]=useState(false),[error,setError]=useState(''),[busy,setBusy]=useState(false),[connections,setConnections]=useState(null);
 const generation=useRef(0),[loadingFeed,setLoadingFeed]=useState(false);
 const load=useCallback(async(append=false,after=null)=>{
  const request=++generation.current;setLoadingFeed(true);
  try{const [p,posts]=await Promise.all([api.get(`/profiles/${address}`),api.get(`/profiles/${address}/posts`,{params:{tab,...(after?{cursor:after}:{})}})]);
   if(request!==generation.current)return;setProfile(p.data);setItems(old=>append?Array.from(new Map([...old,...posts.data.items].map(item=>[item.event_id,item])).values()):posts.data.items);setCursor(posts.data.next_cursor);setError('');
  }catch(e){if(request===generation.current)setError(errorMessage(e));}finally{if(request===generation.current)setLoadingFeed(false);}
 },[address,tab,api]);
 useEffect(()=>{const counter=generation;setProfile(null);setItems([]);setCursor(null);setError('');setConnections(null);setEditing(false);load();return()=>{counter.current++;};},[load,wallet]);
 const follow=async()=>{if(!wallet){connect();return;}setBusy(true);try{await authenticate();setProfile((await api.post(`/profiles/${address}/follow`,{active:!profile.viewer_follows})).data);}catch(e){toast.error(errorMessage(e));}finally{setBusy(false);}};
 const showConnections=async kind=>{try{const {data}=await api.get(`/profiles/${address}/connections`,{params:{kind}});setConnections({kind,items:data});}catch(e){toast.error(errorMessage(e));}};
 if(error)return <main className="content-page"><Empty icon={UserRound} title={error} testId="profile-page-error"/></main>;
 if(!profile)return <main className="content-page"><Loading text="Loading profile…"/></main>;
 return <main className="content-page social-page" data-testid="profile-page">
 <div className="page-breadcrumb"><Link to="/world" data-testid="profile-back-world"><ArrowLeft size={15}/>World</Link><span>/</span><span data-testid="profile-scope">Community profile</span></div>
 <section className="social-profile-header"><div className="social-profile-top"><ProfileAvatar profile={profile} size={76}/>{wallet===address?<ActionButton data-testid="edit-profile" className="social-outline-action" onClick={()=>setEditing(true)}><Settings2 size={14}/>Edit profile</ActionButton>:<ActionButton data-testid="follow-user" className={profile.viewer_follows?'social-outline-action':''} disabled={busy} onClick={follow}>{profile.viewer_follows?<Check size={14}/>:<UserPlus size={14}/>}{profile.viewer_follows?'Following':'Follow'}</ActionButton>}</div>
 <h1 data-testid="profile-name">{profile.display_name}</h1><span className="social-profile-handle" data-testid="profile-username">{profile.handle?`@${profile.handle}`:shortAddress(address)}</span><p data-testid="profile-bio-text">{profile.bio}</p><span className="social-profile-wallet" data-testid="profile-wallet">{shortAddress(address)} · Solana</span>
 <div className="social-profile-stats"><button data-testid="profile-following-count" onClick={()=>showConnections('following')}><strong>{profile.following}</strong> Following</button><button data-testid="profile-followers-count" onClick={()=>showConnections('followers')}><strong>{profile.followers}</strong> Followers</button></div></section>
 <div className="social-feed-tabs">{['posts','reposts'].map(key=><button key={key} data-testid={`profile-tab-${key}`} className={tab===key?'active':''} onClick={()=>setTab(key)}>{key==='posts'?'Posts':'Reposts'}</button>)}</div>
 {items.length?items.map(post=><PostCard key={post.event_id} post={post} showToken onChange={updated=>setItems(old=>old.map(p=>p.id===updated.id?{...p,...updated,event_id:p.event_id,reposted_by:p.reposted_by}:p))} onDeleted={()=>load()}/>):<Empty icon={UserRound} title={tab==='posts'?'No posts yet.':'No reposts yet.'} text="Community contributions appear here." testId="profile-feed-empty"/>}{cursor&&<button data-testid="profile-load-more" className="social-load-more" disabled={loadingFeed} onClick={()=>load(true,cursor)}>{loadingFeed?'Loading…':'Load more'}</button>}
 <ProfileEditor profile={profile} open={editing} onOpenChange={setEditing} onSaved={setProfile}/><Dialog open={!!connections} onOpenChange={value=>{if(!value)setConnections(null);}}><DialogContent className="nexus-dialog" data-testid="profile-connections-dialog"><DialogTitle>{connections?.kind==='followers'?'Followers':'Following'}</DialogTitle><DialogDescription>People in this community circle.</DialogDescription>{connections?.items.length?connections.items.map(p=><div className="social-connection" key={p.wallet}><ProfileAvatar profile={p}/><span onClick={()=>setConnections(null)}><AuthorLink profile={p} testId={`connection-${p.wallet}`}/></span></div>):<Empty icon={UserRound} title="No connections yet." testId="profile-connections-empty"/>}</DialogContent></Dialog>
 </main>;
}