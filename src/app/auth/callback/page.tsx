'use client';
import {useEffect,useState} from 'react';
import Link from 'next/link';
import {getSupabase} from '@/lib/supabase';
export default function Callback(){
 const [status,setStatus]=useState('Verifying your sign-in link…');
 useEffect(()=>{let mounted=true;const run=async()=>{try{
  const supabase=getSupabase();const url=new URL(window.location.href);
  const code=url.searchParams.get('code');
  const token_hash=url.searchParams.get('token_hash');
  const type=url.searchParams.get('type');
  if(code){const {error}=await supabase.auth.exchangeCodeForSession(code);if(error)throw error;}
  else if(token_hash&&type==='email'){const {error}=await supabase.auth.verifyOtp({token_hash,type:'email'});if(error)throw error;}
  else {const {data}=await supabase.auth.getSession();if(!data.session)throw new Error('Invalid or expired login link');}
  if(mounted)window.location.replace('/submit');
 }catch(err){if(mounted)setStatus(err instanceof Error?err.message:'Unable to verify login')}}
 run();return()=>{mounted=false}},[]);
 return <main style={{maxWidth:560,margin:'auto',padding:'100px 24px'}}><h1>Signing you in</h1><p role="status">{status}</p><Link href="/login" style={{color:'#f26443'}}>Back to login</Link></main>
}
