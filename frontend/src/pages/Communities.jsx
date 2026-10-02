import React,{useCallback,useEffect,useState} from 'react';
import {useSearchParams} from 'react-router-dom';
import {Users,MessageSquare,RefreshCw} from 'lucide-react';
import {Tabs,TabsList,TabsTrigger,TabsContent} from '../components/ui/tabs';
import {CommunityDirectory} from '../components/community/CommunityDirectory';
import {WorldFeed} from '../components/community/WorldFeed';
import {SiteFooter} from '../components/SiteFooter';
import {Loading} from '../components/Shared';
import {api,errorMessage} from '../lib/api';

export default function Communities(){
 const [params,setParams]=useSearchParams(),[communities,setCommunities]=useState([]),[loading,setLoading]=useState(true),[error,setError]=useState('');
 const view=params.get('view')==='feed'?'feed':'directory';
 const load=useCallback(async()=>{setLoading(true);setError('');try{const {data}=await api.get('/communities');setCommunities(data);}catch(e){setError(errorMessage(e));}finally{setLoading(false);}},[]);
 useEffect(()=>{load();},[load]);
 return <main className="communities-page" data-testid="communities-page"><div className="section-wrap community-hub-content"><header className="community-hub-heading"><span className="section-kicker" data-testid="community-hub-kicker">THE PEOPLE MAKE THE WORLD</span><h1 data-testid="community-hub-title">Find your people.</h1><p data-testid="community-hub-description">A place for every token. A conversation worth joining.</p></header><Tabs value={view} onValueChange={v=>setParams(v==='feed'?{view:'feed'}:{})} className="community-hub-tabs"><TabsList className="community-view-tabs" data-testid="community-view-tabs"><TabsTrigger value="directory" data-testid="community-view-directory"><Users size={15}/>Communities</TabsTrigger><TabsTrigger value="feed" data-testid="community-view-feed"><MessageSquare size={15}/>All posts</TabsTrigger></TabsList><TabsContent value="directory" data-testid="community-directory-panel">{error?<div className="social-error" role="alert" data-testid="directory-error">{error}<button data-testid="directory-retry" onClick={load}><RefreshCw size={14}/>Try again</button></div>:loading?<Loading text="Finding communities…"/>:<CommunityDirectory communities={communities}/>}</TabsContent><TabsContent value="feed" data-testid="community-all-posts-panel"><WorldFeed/></TabsContent></Tabs></div><SiteFooter/></main>;
}