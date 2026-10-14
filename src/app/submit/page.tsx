'use client';
import {useEffect,useState} from 'react';
import Link from 'next/link';
import {getSupabase} from '@/lib/supabase';
import {moments} from '@/lib/moments';

function youtubeId(value:string):string|null{
 try{const u=new URL(value);let id='';
  if(['youtu.be','www.youtu.be'].includes(u.hostname))id=u.pathname.slice(1).split('/')[0];
  else if(['youtube.com','www.youtube.com','m.youtube.com'].includes(u.hostname)){
   if(u.pathname==='/watch')id=u.searchParams.get('v')||'';
   else if(/^\/(shorts|embed|live)\//.test(u.pathname))id=u.pathname.split('/')[2];
  }
  return /^[\w-]{11}$/.test(id)?id:null;
 }catch{return null}
}
export default function SubmitPage(){
 const [momentId,setMomentId]=useState(moments[0].id);
 const [url,setUrl]=useState('');const [status,setStatus]=useState('');
 const [busy,setBusy]=useState(false);const [signedIn,setSignedIn]=useState<boolean|null>(null);
 useEffect(()=>{let mounted=true;const supabase=getSupabase();supabase.auth.getUser().then(({data})=>{if(mounted)setSignedIn(!!data.user)}).catch(()=>{if(mounted)setSignedIn(false)});
  const {data:listener}=supabase.auth.onAuthStateChange((_event,session)=>setSignedIn(!!session?.user));
  return()=>{mounted=false;listener.subscription.unsubscribe()}},[]);
 async function submit(e:React.FormEvent<HTMLFormElement>){
  e.preventDefault();setBusy(true);setStatus('');
  try{
   const id=youtubeId(url);if(!id)throw new Error('Enter a valid YouTube video link');
   const supabase=getSupabase();const {data:{user},error:authError}=await supabase.auth.getUser();
   if(authError||!user)throw new Error('Sign in before submitting a video');
   const {error}=await supabase.from('video_submissions').insert({moment_id:momentId,video_id:id,user_id:user.id});
   if(error){if(error.code==='23505')throw new Error('This video was already submitted for this moment');throw error;}
   setStatus('Submitted for review. Thanks for contributing!');setUrl('');
  }catch(err){setStatus(err instanceof Error?err.message:'Could not submit link')}
  finally{setBusy(false)}
 }
 return <main style={{maxWidth:700,margin:'0 auto',padding:'70px 24px'}}><Link href="/" style={{color:'#f26443'}}>← BACK TO THE ARCHIVE</Link><p className="eyebrow" style={{marginTop:45}}>COMMUNITY / VIDEO SUBMISSIONS</p><h1 style={{fontSize:'clamp(42px,7vw,72px)',letterSpacing:-3}}>Share a <em>moment.</em></h1><p className="intro">Submit an official, embeddable YouTube clip for moderator review. We never rehost copyrighted videos.</p>
 {signedIn===false?<p style={{marginTop:25}}>You need an account to contribute. <Link href="/login" style={{color:'#f26443'}}>Sign in with email →</Link></p>:null}
 {signedIn===true?<button onClick={async()=>{await getSupabase().auth.signOut();setSignedIn(false)}} style={{background:'none',border:0,color:'#f26443',cursor:'pointer'}}>Sign out</button>:null}
 <form onSubmit={submit} style={{display:'grid',gap:18,marginTop:32}}><label htmlFor="moment">Anime moment</label><select id="moment" value={momentId} onChange={e=>setMomentId(e.target.value)} style={{padding:16,background:'#16161b',border:'1px solid #39343c',color:'white'}}>{moments.map(m=><option key={m.id} value={m.id}>{m.anime} — {m.title}</option>)}</select><label htmlFor="video">YouTube video URL</label><input id="video" type="url" required placeholder="https://www.youtube.com/watch?v=..." value={url} onChange={e=>setUrl(e.target.value)} style={{padding:16,background:'#16161b',border:'1px solid #39343c',color:'white'}}/><button className="cta" disabled={busy||signedIn!==true} style={{border:0,justifyContent:'center'}}>{busy?'SUBMITTING…':'SUBMIT FOR REVIEW'}</button></form>{status&&<p role="status" style={{marginTop:20,color:'#f4b1a2'}}>{status}</p>}<p style={{marginTop:35,color:'#89838b',fontSize:13}}>Links are not public until reviewed. Do not submit pirated uploads.</p></main>
}
