'use client';
import {useState} from 'react';
import Link from 'next/link';
type Anime={source:string;id:string;title:string;episodes:number|null;url:string|null;image:string|null};
type Result={results:Anime[];unavailable_providers:string[]};
export default function Discover(){
 const [q,setQ]=useState('Naruto');const [data,setData]=useState<Result|null>(null);const [busy,setBusy]=useState(false);const [error,setError]=useState('');
 async function search(e:React.FormEvent<HTMLFormElement>){
  e.preventDefault();setBusy(true);setError('');setData(null);
  try{const api=process.env.NEXT_PUBLIC_API_URL;
   if(!api)throw new Error('Anime search API is not configured for this deployment.');
   const res=await fetch(api.replace(/\/$/,'')+'/api/anime/search?'+new URLSearchParams({q,provider:'all',limit:'5'}),{cache:'no-store'});
   if(!res.ok)throw new Error(res.status===429?'Search rate limit reached. Wait 10 seconds and retry.':'Anime API returned '+res.status);
   const body:Result=await res.json();setData(body);
  }catch(e){setError(e instanceof Error?e.message:'Search failed. Please retry.')}finally{setBusy(false)}
 }
 return <main style={{maxWidth:1050,margin:'0 auto',padding:'56px 24px 100px'}}>
  <Link href="/" style={{color:'#f26443'}}>← BACK TO HYPEFRAME</Link>
  <p className="eyebrow" style={{marginTop:50}}>FREE API / ANIME CATALOG</p>
  <h1 style={{fontSize:'clamp(44px,7vw,78px)',letterSpacing:-3}}>Discover <em>anime.</em></h1>
  <p className="intro">Search anime titles through Jikan, AniList and Kitsu. These are catalog listings, not playable clips.</p>
  <form onSubmit={search} style={{display:'flex',gap:12,margin:'30px 0',flexWrap:'wrap'}}>
   <input aria-label="Anime title" minLength={2} maxLength={100} required value={q} onChange={e=>setQ(e.target.value)} placeholder="Search anime..." style={{flex:'1 1 240px',padding:16,background:'#16161b',border:'1px solid #39343c',color:'white'}}/>
   <button className="cta" style={{border:0}} disabled={busy}>{busy?'SEARCHING…':'SEARCH CATALOG'}</button>
  </form>
  {error&&<p role="alert" style={{color:'#f4b1a2'}}>{error}</p>}
  {data&&<><p role="status">{data.results.length} catalog results {data.unavailable_providers.length>0?' · Unavailable providers: '+data.unavailable_providers.join(', '):''}</p>
   <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))',gap:20,marginTop:24}}>
   {data.results.map(a=><article key={a.source+'-'+a.id} style={{border:'1px solid #39343c',padding:18,background:'#16161b'}}>
    {a.image&&<img src={a.image} alt={a.title+' cover'} loading="lazy" style={{width:'100%',height:230,objectFit:'contain'}}/>}
    <p className="eyebrow" style={{marginTop:16}}>{a.source.toUpperCase()}</p><h2 style={{fontSize:20}}>{a.title}</h2>
    <p>{a.episodes==null?'Episodes unknown':a.episodes+' episodes'}</p>
    {a.url&&<a href={a.url} target="_blank" rel="noopener noreferrer" style={{color:'#f26443'}}>VIEW SOURCE ↗</a>}
   </article>)}
   </div>{data.results.length===0&&<p>No results found. Try a different title.</p>}</>}
  <p style={{marginTop:50,color:'#89838b'}}>Video playback is not available yet. Submitted YouTube links remain pending review; Hypeframe does not host copyrighted footage.</p>
 </main>
}
