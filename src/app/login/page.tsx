'use client';
import {useState} from 'react';
import Link from 'next/link';
import {getSupabase} from '@/lib/supabase';
export default function Login(){
 const [email,setEmail]=useState('');const [status,setStatus]=useState('');const [busy,setBusy]=useState(false);
 async function login(e:React.FormEvent<HTMLFormElement>){e.preventDefault();setBusy(true);setStatus('');
  try{const {error}=await getSupabase().auth.signInWithOtp({email,emailRedirectTo:window.location.origin+'/auth/callback'});if(error)throw error;setStatus('Check your email for a secure sign-in link.')}
  catch(err){setStatus(err instanceof Error?err.message:'Unable to send login link')}
  finally{setBusy(false)}
 }
 return <main style={{maxWidth:540,margin:'auto',padding:'90px 24px'}}><Link href="/" style={{color:'#f26443'}}>← HYPEFRAME</Link><h1 style={{fontSize:56,marginTop:40}}>Join the community.</h1><p>Sign in with a secure email link. No password needed.</p><form onSubmit={login} style={{display:'grid',gap:20,marginTop:30}}><label htmlFor="email">Email address</label><input id="email" type="email" required value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" style={{padding:16,background:'#16161b',border:'1px solid #39343c',color:'white'}}/><button disabled={busy} className="cta" style={{border:0}}>{busy?'SENDING…':'EMAIL ME A SIGN-IN LINK'}</button></form><p role="status" style={{marginTop:24}}>{status}</p></main>
}
