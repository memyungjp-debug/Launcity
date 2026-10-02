import {useCallback,useEffect,useRef,useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {toast} from 'sonner';
import {api,errorMessage,colors} from '../lib/api';
import {newMintSigner,signNexusLaunch,uploadImage} from '../lib/nexusLaunch';
import {useWallet} from '../context/WalletContext';

export const useNexusLaunch=reloadWorld=>{
 const {wallet,provider,connect,authenticate}=useWallet(),navigate=useNavigate();
 const [form,setForm]=useState({name:'',symbol:'',description:'',district:'meme',color:colors.meme});
 const [image,setImage]=useState(null),[prepared,setPrepared]=useState(null),[pending,setPending]=useState(null);
 const [busy,setBusy]=useState(false),[uploading,setUploading]=useState(false),[error,setError]=useState(''),[step,setStep]=useState('');
 const signer=useRef(null),checking=useRef(false),currentWallet=useRef(wallet);
 currentWallet.current=wallet;
 const storageKey=wallet?`nexus-launch-session:${wallet}`:null;
 const clearPending=useCallback(id=>{if(storageKey)localStorage.removeItem(storageKey);if(id)sessionStorage.removeItem(`nexus-signed:${id}`);setPending(null);setPrepared(null);signer.current=null;},[storageKey]);
 useEffect(()=>{setPrepared(null);signer.current=null;setImage(null);setError('');setStep('');setPending(storageKey?localStorage.getItem(storageKey):null);},[storageKey]);
 const finishLaunch=useCallback(async data=>{clearPending(data.id);await reloadWorld();toast.success(`${data.symbol} is now a NEXUS token`);navigate(`/token/${data.token_id}`);},[clearPending,reloadWorld,navigate]);
 const receive=useCallback(async data=>{
  if(data.status==='confirmed'){await finishLaunch(data);return;}
  if(['failed','expired'].includes(data.status)){clearPending(data.id);setStep('');setError(data.error || 'Launch did not confirm. Prepare a new launch.');return;}
  setStep(data.status==='submitted'?'Waiting for Solana confirmation':data.status==='prepared'?'Signed transaction has not been submitted':data.status);
  if(data.status==='prepared'&&!signer.current&&!sessionStorage.getItem(`nexus-signed:${data.id}`)){clearPending(data.id);setError('The unsigned launch was not submitted. You can prepare a new launch.');}
  else if(data.error)setError(data.error);
 },[clearPending,finishLaunch]);
 const checkStatus=useCallback(async()=>{
  if(!pending||checking.current)return;
  checking.current=true;
  try{const {data}=await api.get(`/pump/launches/${pending}`);if(currentWallet.current===wallet)await receive(data);}
  catch(e){if(currentWallet.current===wallet){setError(errorMessage(e));if(e.response?.status===404)clearPending(pending);}}
  finally{checking.current=false;}
 },[pending,wallet,receive,clearPending]);
 useEffect(()=>{
  if(!pending||!wallet||sessionStorage.getItem('nexus-wallet')!==wallet)return;
  checkStatus();const timer=setInterval(checkStatus,5000);return()=>clearInterval(timer);
 },[pending,wallet,checkStatus]);
 const recover=async()=>{setBusy(true);setError('');try{await authenticate();await checkStatus();}catch(e){setError(errorMessage(e));}finally{setBusy(false);}};
 const retrySubmission=async()=>{
  setBusy(true);setError('');
  try{await authenticate();const transaction_base64=sessionStorage.getItem(`nexus-signed:${pending}`);if(!transaction_base64)throw new Error('Check launch status before preparing another transaction.');const {data}=await api.post(`/pump/launches/${pending}/submit`,{transaction_base64},{timeout:90000});await receive(data);}
  catch(e){setError(errorMessage(e));}finally{setBusy(false);}
 };
 const field=key=>e=>{setForm(old=>({...old,[key]:e.target.value}));setPrepared(null);signer.current=null;};
 const chooseImage=async e=>{
  const file=e.target.files?.[0];if(!file)return;setUploading(true);setError('');const owner=wallet;
  try{await authenticate();const uploaded=await uploadImage(file,'token-image');if(currentWallet.current===owner){setImage(uploaded);setPrepared(null);signer.current=null;}}
  catch(e){setError(errorMessage(e));}finally{setUploading(false);e.target.value='';}
 };
 const submit=async e=>{
  e.preventDefault();if(!wallet){connect();return;}setBusy(true);setError('');const owner=wallet;
  try{
   await authenticate();if(!image)throw new Error('Upload your token image first');
   if(!prepared){
    setStep('Preparing official Pump.fun transaction');const mint=newMintSigner();signer.current=mint;
    const {data}=await api.post('/pump/launches/prepare',{...form,image_id:image.id,mint:mint.publicKey.toBase58()},{timeout:90000});
    if(currentWallet.current!==owner)return;setPrepared(data);setStep('Review and approve the launch');
   }else{
    setStep('Approve in your wallet');const transaction_base64=await signNexusLaunch(prepared,signer.current,provider);
    if(currentWallet.current!==owner)throw new Error('Wallet changed. Nothing was submitted.');
    sessionStorage.setItem(`nexus-signed:${prepared.id}`,transaction_base64);localStorage.setItem(storageKey,prepared.id);setPending(prepared.id);setStep('Submitting to Solana');
    const {data}=await api.post(`/pump/launches/${prepared.id}/submit`,{transaction_base64},{timeout:90000});
    if(currentWallet.current===owner)await receive(data);
   }
  }catch(e){setError(errorMessage(e));}finally{setBusy(false);}
 };
 return {wallet,connect,form,setForm,image,prepared,pending,busy,uploading,error,step,field,chooseImage,submit,recover,retrySubmission,canRetry:!!(pending&&sessionStorage.getItem(`nexus-signed:${pending}`))};
};