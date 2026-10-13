'use client';
import {useState} from 'react';
import Link from 'next/link';
import {moments} from '@/lib/moments';

export default function SubmitPage(){
 const [momentId,setMomentId]=useState(moments[0].id);
 const [url,setUrl]=useState('');
 const [status,setStatus]=useState('');
 const [busy,setBusy]=useState(false);
 async function submit(e:React.FormEvent<HTMLFormElement>){
  e.preventDefault();setBusy(true);setStatus('');
  const api=process.env.NEXT_PUBLIC_API_URL;
  if(!api){setStatus('Video submissions require a connected Python API.');setBusy(false);return}
  try{const response=await fetch(api.replace(/\/$/,'')+'/api/video-submissions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({moment_id:momentId,url})});
  const data=await response.json();if(!response.ok)throw new Error(data.detail||'Submission failed');setStatus('Link submitted for moderator review. It will not appear until approved.');setUrl('')}
  catch(err){setStatus(err instanceof Error?err.message:'Could not submit link')}
  finally{setBusy(false)}
 }
 return <main style={{maxWidth:700,margin:'0 auto',padding:'70px 24px'}}><Link href="/" style={{color:'#f26443'}}>← BACK TO THE ARCHIVE</Link><p className="eyebrow" style={{marginTop:45}}>COMMUNITY / VIDEO SUBMISSIONS</p><h1 style={{fontSize:'clamp(42px,7vw,72px)',letterSpacing:-3}}>Share a <em>moment.</em></h1><p className="intro">Found an official, embeddable anime clip? Submit its YouTube link for review. We never rehost copyrighted videos.</p><form onSubmit={submit} style={{display:'grid',gap:18,marginTop:32}}><label htmlFor="moment">Anime moment</label><select id="moment" value={momentId} onChange={e=>setMomentId(e.target.value)} style={{padding:16,background:'#16161b',border:'1px solid #39343c',color:'white'}}>{moments.map(m=><option key={m.id} value={m.id}>{m.anime} — {m.title}</option>)}</select><label htmlFor="video">YouTube video URL</label><input id="video" type="url" required placeholder="https://www.youtube.com/watch?v=..." value={url} onChange={e=>setUrl(e.target.value)} style={{padding:16,background:'#16161b',border:'1px solid #39343c',color:'white'}}/><button className="cta" disabled={busy} style={{border:0,justifyContent:'center'}}>{busy?'SUBMITTING…':'SUBMIT FOR REVIEW'}</button></form>{status&&<p role="status" style={{marginTop:20,color:'#f4b1a2'}}>{status}</p>}<p style={{marginTop:35,color:'#89838b',fontSize:13}}>Submissions are held for moderation. Do not submit pirated uploads or links that violate rights.</p></main>
}
