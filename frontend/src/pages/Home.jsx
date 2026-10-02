import React from 'react';
import {Link} from 'react-router-dom';
import {ArrowUpRight,ArrowRight,Globe2,Plus,Layers3} from 'lucide-react';
import {useWorld} from '../context/WorldContext';
import {TokenAvatar} from '../components/Shared';
import {SiteFooter} from '../components/SiteFooter';
import {ProductPreviews} from '../components/home/ProductPreviews';

export default function Home(){
 const {world}=useWorld();
 return <main className="home-page" data-testid="home-page">
  <section className="home-hero" aria-labelledby="home-title">
   <img className="home-world-image" src="/previews/world-scene.jpg" alt="An aerial view of the NEXUS token city" data-testid="home-world-image" fetchPriority="high"/>
   <div className="hero-shade"/>
   <div className="hero-content"><div className="home-eyebrow" data-testid="home-eyebrow"><span className="status-dot"/>TOKEN LAUNCHPAD<span className="eyebrow-rule"/>BUILT ON SOLANA</div>
    <h1 id="home-title" data-testid="home-title">NEXUS<br/><span>A launchpad where every token gets a place.</span></h1>
    <p data-testid="home-positioning">Launch a token through NEXUS<br className="desktop-break"/> and it becomes part of the World.</p>
    <div className="hero-actions"><Link to="/world" className="primary-cta" data-testid="home-enter-world"><Globe2 size={18}/>Enter World<ArrowUpRight size={17}/></Link><Link to="/launch" className="secondary-cta" data-testid="home-launch-token"><Plus size={18}/>Launch Token</Link></div>
    <span className="hero-powered" data-testid="home-launch-provider">Launches powered by <strong>Pump.fun</strong></span>
   </div>
   <Link to="/world" className="hero-world-caption" data-testid="home-world-preview-link"><span className="preview-cross">+</span><span>WORLD PREVIEW<small>The NEXUS World</small></span><ArrowUpRight size={17}/></Link>
  </section>
  <section className="world-members-band" data-testid="home-world-members"><div className="members-label"><span className="status-dot"/><span data-testid="home-token-strip-title">Tokens in the World</span></div><div className="home-token-list">{world?.tokens.map(t=><Link to={`/token/${t.id}`} key={t.id} data-testid={`home-token-${t.id}`}><TokenAvatar token={t} size={26}/><span>{t.symbol}</span></Link>)}</div><Link to="/world" className="members-explore" data-testid="home-explore-all">Explore all<ArrowRight size={15}/></Link></section>
  <ProductPreviews/>
  <section className="home-philosophy"><div className="section-wrap philosophy-inner"><div><span className="section-kicker" data-testid="home-about-kicker">WHY NEXUS</span><h2 data-testid="home-about-heading">A place people<br/>can return to.</h2></div><div><p data-testid="home-about-description">After launch, most tokens become another name on a chart or feed. NEXUS gives each token a place people can discover and return to.</p><Link to="/about" className="quiet-link" data-testid="home-read-about">About NEXUS<ArrowUpRight size={16}/></Link></div><Layers3 className="philosophy-mark" size={76} strokeWidth={.9} aria-hidden="true"/></div></section>
  <section className="home-community-callout section-wrap"><div><span className="section-kicker" data-testid="home-community-kicker">TOKEN COMMUNITIES</span><h2 data-testid="home-community-heading">Talk with the community.</h2><p data-testid="home-community-description">Each token has its own community page.</p></div><div className="callout-actions"><Link to="/community" className="primary-cta" data-testid="home-discover-community">Find a community<ArrowUpRight size={16}/></Link><Link to="/docs" className="quiet-link" data-testid="home-read-docs">Start with the Docs<ArrowRight size={15}/></Link></div></section>
  <SiteFooter/>
 </main>;
}