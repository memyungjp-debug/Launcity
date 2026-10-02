import React,{useEffect,useRef,useState} from 'react';
import {Share2,Copy,Check,Link2} from 'lucide-react';
import {toast} from 'sonner';
import {Dialog,DialogContent,DialogTitle,DialogDescription} from '../ui/dialog';
import {TokenAvatar} from '../Shared';

export const CommunityInvite=({token})=>{
 const [open,setOpen]=useState(false),[copied,setCopied]=useState(false),[sharing,setSharing]=useState(false),[message,setMessage]=useState('');
 const timer=useRef(),input=useRef(),alive=useRef(true);
 const url=new URL(`/community/${encodeURIComponent(token.id)}`,window.location.origin).href;
 const id=`community-invite-${token.id}`;
 const payload={title:`${token.name} community | NEXUS`,text:`Join the ${token.name} ($${token.symbol}) community on NEXUS.`,url};
 const nativeShare=typeof navigator.share==='function';
 useEffect(()=>{alive.current=true;return()=>{alive.current=false;clearTimeout(timer.current);};},[]);
 const copy=async()=>{
  clearTimeout(timer.current);setMessage('');setCopied(false);
  try{
   if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
   await navigator.clipboard.writeText(url);
   if(!alive.current)return;
   setCopied(true);toast.success('Community link copied');
   timer.current=setTimeout(()=>{if(alive.current)setCopied(false);},2200);
  }catch{
   if(!alive.current)return;
   setMessage('Clipboard access is unavailable. Select and copy the link below.');setOpen(true);
   requestAnimationFrame(()=>{input.current?.focus();input.current?.select();});
  }
 };
 const share=async()=>{
  setMessage('');
  if(!nativeShare){setOpen(true);return;}
  setSharing(true);
  try{await navigator.share(payload);}
  catch(error){if(alive.current&&error?.name!=='AbortError'){setMessage('Sharing is unavailable in this browser. You can still copy the link.');setOpen(true);}}
  finally{if(alive.current)setSharing(false);}
 };
 return <>
  <div className="community-invite-actions" data-testid={`${id}-actions`}>
   <button type="button" className="invite-share-button" data-testid={`${id}-share`} disabled={sharing} onClick={share}><Share2 size={14}/><span>Share</span></button>
   <button type="button" className="invite-copy-button" data-testid={`${id}-copy`} onClick={copy}>{copied?<Check size={14}/>:<Copy size={14}/>}<span aria-live="polite" data-testid={`${id}-copy-status`}>{copied?'Copied':'Copy link'}</span></button>
  </div>
  <Dialog open={open} onOpenChange={value=>{setOpen(value);if(!value)setMessage('');}}><DialogContent className="nexus-dialog community-invite-dialog" data-testid={`${id}-dialog`} onOpenAutoFocus={e=>{e.preventDefault();input.current?.focus();input.current?.select();}}>
   <DialogTitle data-testid={`${id}-title`}>Invite your people.</DialogTitle>
   <DialogDescription data-testid={`${id}-description`}>The {token.name} community on NEXUS.</DialogDescription>
   <div className="invite-token-identity"><TokenAvatar token={token} size={44}/><div><strong data-testid={`${id}-token-name`}>{token.name}</strong><span data-testid={`${id}-token-symbol`}>${token.symbol}</span></div></div>
   <label className="invite-link-label" htmlFor={`${id}-url`} data-testid={`${id}-label`}>Community link</label>
   <div className="invite-link-field"><Link2 size={15}/><input id={`${id}-url`} ref={input} readOnly value={url} data-testid={`${id}-url`} onFocus={e=>e.target.select()} onClick={e=>e.currentTarget.select()}/></div>
   {message&&<p className="invite-message" role="status" data-testid={`${id}-message`}>{message}</p>}
   <div className="invite-dialog-actions">{nativeShare&&<button type="button" className="invite-share-button" disabled={sharing} onClick={share} data-testid={`${id}-native-share`}><Share2 size={15}/>Share</button>}<button type="button" className="primary-cta" onClick={copy} data-testid={`${id}-dialog-copy`}>{copied?<Check size={15}/>:<Copy size={15}/>}<span aria-live="polite" data-testid={`${id}-dialog-copy-status`}>{copied?'Copied':'Copy link'}</span></button></div>
  </DialogContent></Dialog>
 </>;
};