'use client';
import {useState} from 'react';
type Video={video_id:string;title:string;channel:string;status:string};
export default function ClipPreview({anime,moment}:{anime:string;moment:string}){
 const [videos,setVideos]=useState<Video[]>([]);const [active,setActive]=useState<string|null>(null);
 const [error,setError]=useState('');const [busy,setBusy]=useState(false);const [loaded,setLoaded]=useState(false);
 async function discover(){
  setBusy(true);setError('');setLoaded(false);
  try{const api=process.env.NEXT_PUBLIC_API_URL;if(!api)throw new Error('Video API is not configured');
   const query=new URLSearchParams({anime,moment,limit:'3'});
   const response=await fetch(api.replace(/\/$/,'')+'/api/videos/discover?'+query,{cache:'no-store'});
   const body=await response.json();
   if(!response.ok)throw new Error(response.status===503?'Video discovery is not configured on the running backend. Check Render YOUTUBE_API_KEY and deployment.':typeof body.detail==='string'?body.detail:'Video search unavailable');
   setVideos(Array.isArray(body.results)?body.results:[]);setLoaded(true);
  }catch(e){setError(e instanceof Error?e.message:'Video search unavailable')}finally{setBusy(false)}
 }
 return <div style={{marginTop:12}}>
  <button type="button" onClick={discover} disabled={busy} style={{padding:'9px 13px',background:'#f26443',color:'#08090d',border:0,borderRadius:4,cursor:'pointer',fontWeight:700}}>{busy?'SEARCHING…':'▶ FIND CLIPS'}</button>
  {error&&<p role="alert" style={{color:'#f4b1a2',fontSize:12}}>{error}</p>}
  {loaded&&videos.length===0&&<p style={{fontSize:12}}>No embeddable YouTube videos found for this moment.</p>}
  {videos.length>0&&<div style={{display:'grid',gap:9,marginTop:12}}>
   <p style={{fontSize:12,color:'#a8a3a9'}}>YouTube search previews · not reviewed or endorsed by Hypeframe. Check the channel and rights before sharing.</p>
   {videos.map(v=><div key={v.video_id} style={{border:'1px solid #353038',padding:8}}>
    <button type="button" onClick={()=>setActive(active===v.video_id?null:v.video_id)} style={{background:'none',color:'#eee',border:0,textAlign:'left',cursor:'pointer',fontSize:13}}>{active===v.video_id?'▾ CLOSE':'▶ PLAY'} · {v.title} — {v.channel}</button>
    {active===v.video_id&&<iframe title={v.title} src={'https://www.youtube-nocookie.com/embed/'+v.video_id} loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerPolicy="strict-origin-when-cross-origin" allowFullScreen style={{display:'block',marginTop:8,width:'100%',aspectRatio:'16 / 9',border:0}}/>}
   </div>)}
  </div>}
 </div>
}
