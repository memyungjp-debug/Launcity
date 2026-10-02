import React from 'react';
import {BrowserRouter,Routes,Route,Navigate,Link,useLocation} from 'react-router-dom';
import {WalletProvider} from './context/WalletContext';
import {RealmProvider} from './context/RealmContext';
import {WorldProvider,useWorld} from './context/WorldContext';
import {ExplorationShell} from './components/world/ExplorationShell';
import {Toaster} from './components/ui/sonner';
import World from './pages/World';
import TokenDashboard from './pages/TokenDashboard';
import Launch from './pages/Launch';
import Bounties from './pages/Bounties';
import Leaderboard from './pages/Leaderboard';
import Community from './pages/Community';
import Profile from './pages/Profile';
import Home from './pages/Home';
import About from './pages/About';
import Docs from './pages/Docs';
import Communities from './pages/Communities';
import './App.css';
import './pump.css';
import './social.css';
import './community-extras.css';
import './spatial.css';
import './entry.css';
import './invitations.css';

function LegacyRedirect(){
 const {pathname,search,hash}=useLocation();
 const destination=pathname.replace(/^\/showcase/, '') || '/world';
 return <Navigate to={`${destination}${search}${hash}`} replace/>;
}
function Experience(){
 const {world,loading,reload}=useWorld();
 return <ExplorationShell><Routes>
  <Route path="/" element={<Home/>}/>
  <Route path="/about" element={<About/>}/>
  <Route path="/docs" element={<Docs/>}/>
  <Route path="/community" element={<Communities/>}/>
  <Route path="/world" element={<World/>}/>
  <Route path="/showcase/*" element={<LegacyRedirect/>}/>
  <Route path="/token/:id" element={<TokenDashboard reloadWorld={reload}/>}/>
  <Route path="/leaderboard" element={<Leaderboard world={world} loading={loading}/>}/>
  <Route path="/community/:id" element={<Community/>}/>
  <Route path="/community/:id/post/:postId" element={<Community/>}/>
  <Route path="/profile/:wallet" element={<Profile/>}/>
  <Route path="/launch" element={<Launch reloadWorld={reload}/>}/>
  <Route path="/bounties" element={<Bounties tokens={world?.tokens||[]}/>}/>
  <Route path="*" element={<div className="not-found" data-testid="not-found"><h1 data-testid="not-found-title">Uncharted territory.</h1><Link to="/world" data-testid="return-world-404">Return to the world →</Link></div>}/>
 </Routes></ExplorationShell>;
}
export default function App(){return <BrowserRouter><WalletProvider><RealmProvider><WorldProvider><Experience/></WorldProvider></RealmProvider><Toaster theme="dark" position="bottom-center" richColors/></WalletProvider></BrowserRouter>;}