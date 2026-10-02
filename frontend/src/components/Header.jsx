import React from 'react';
import {Link,useLocation} from 'react-router-dom';
import {Layers3,Wallet,BookOpen} from 'lucide-react';
import {useWallet} from '../context/WalletContext';
import {shortAddress} from '../lib/api';
import {PrimaryNavigation} from './PrimaryNavigation';
import {TokenSearch} from './TokenSearch';

export const Header=({tokens=[]})=>{
 const {wallet,connect}=useWallet(),{pathname}=useLocation();
 const inWorld=pathname==='/world';
 return <header className={`nexus-header ${inWorld?'with-world-search':''}`} data-testid="site-header">
  <Link to="/" className="nexus-brand" aria-label="NEXUS home" data-testid="brand-home"><Layers3 size={28} strokeWidth={2}/><span>NEXUS<span className="brand-period">.</span></span></Link>
  <PrimaryNavigation/>
  <div className="nexus-header-actions">
   {inWorld?<TokenSearch tokens={tokens}/>:<Link className="header-docs" to="/docs" data-testid="header-docs"><BookOpen size={15}/><span>Docs</span></Link>}
   <button className="connect-cta" data-testid="connect-wallet-button" onClick={connect} aria-label={wallet?'Manage wallet':'Connect wallet'}><Wallet size={16}/><span>{wallet?shortAddress(wallet):'Connect wallet'}</span></button>
   {wallet&&<Link className="my-profile-link" to={`/profile/${wallet}`} data-testid="my-profile-link">Profile</Link>}
  </div>
 </header>;
};