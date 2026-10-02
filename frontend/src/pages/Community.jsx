import React,{useCallback,useEffect,useRef,useState} from 'react';
import {useParams} from 'react-router-dom';
import {RealmLink as Link,useRealm,useRealmNavigate} from '../context/RealmContext';
import {ArrowLeft,MessageSquare} from 'lucide-react';
import {errorMessage} from '../lib/api';
import {useWallet} from '../context/WalletContext';
import {TokenAvatar,Loading,Empty} from '../components/Shared';
import {TokenCommunity} from '../components/community/TokenCommunity';
import {PostComposer} from '../components/community/PostComposer';
import {PostCard} from '../components/community/PostCard';
import {CommunityInvite} from '../components/community/CommunityInvite';

export default function Community(){
 const {id,postId}=useParams(),{wallet}=useWallet(),navigate=useRealmNavigate(),{api}=useRealm();
 const [token,setToken]=useState(null),[post,setPost]=useState(null),[replies,setReplies]=useState([]),[error,setError]=useState('');
 const generation=useRef(0);
 useEffect(()=>{let alive=true;setToken(null);setError('');api.get(`/tokens/${id}`).then(r=>{if(alive)setToken(r.data);}).catch(e=>{if(alive)setError(errorMessage(e));});return()=>{alive=false;};},[id,api]);
 const loadThread=useCallback(async()=>{
  const request=++generation.current;
  try{
   const [root,list]=await Promise.all([api.get(`/social/posts/${postId}`),api.get(`/social/posts/${postId}/replies`)]);
   if(request!==generation.current)return;
   if(root.data.token_id!==id)throw new Error('This post belongs to another community');
   setPost(root.data);setReplies(list.data);setError('');
  }catch(e){if(request===generation.current)setError(errorMessage(e));}
 },[postId,id,api]);
 useEffect(()=>{const counter=generation;setPost(null);setReplies([]);if(postId)loadThread();return()=>{counter.current++;};},[postId,loadThread,wallet]);
 if(error)return <main className="content-page"><Empty icon={MessageSquare} title={error} testId="community-page-error"><Link to={`/token/${id}`} data-testid="community-error-back" className="text-cta">Back to Token Hub</Link></Empty></main>;
 if(!token)return <main className="content-page"><Loading/></main>;
 return <main className="content-page social-page" data-testid="community-page"><div className="page-breadcrumb"><Link to={`/token/${id}`} data-testid="community-back-hub"><ArrowLeft size={15}/>Token Hub</Link><span>/</span><Link to={`/community/${id}`} data-testid="community-root-link">{token.symbol} Community</Link>{postId&&<><span>/</span><span data-testid="conversation-breadcrumb">Conversation</span></>}</div><div className="social-page-heading"><TokenAvatar token={token} size={48}/><div><span className="eyebrow" data-testid="community-eyebrow">NEXUS COMMUNITY</span><h1 data-testid="community-page-title">{token.name}</h1></div><div className="community-heading-actions">{token.community_enabled&&<CommunityInvite key={token.id} token={token}/>}<Link data-testid="community-token-hub" to={`/token/${id}`}>Token Hub ↗</Link></div></div>
 {!token.community_enabled?<TokenCommunity token={token}/>:postId?<section className="social-thread" data-testid="social-thread">{post?<><PostCard post={post} onChange={setPost} onDeleted={()=>navigate(`/community/${id}`)}/>{!post.deleted&&<PostComposer token={token} parentId={post.id} onPosted={loadThread}/>}<h2 className="social-reply-heading" data-testid="thread-reply-count">Replies · {replies.length}</h2>{replies.map(r=><PostCard key={r.id} post={r} onChange={updated=>setReplies(old=>old.map(x=>x.id===updated.id?updated:x))} onDeleted={loadThread}/>)}</>:<Loading text="Opening conversation…"/>}</section>:<TokenCommunity token={token}/>}
 </main>;
}