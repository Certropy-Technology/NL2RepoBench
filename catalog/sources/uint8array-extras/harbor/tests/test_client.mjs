import {spawnSync} from 'node:child_process';
const run = (exportName,args) => {
 const site=process.env.NODE_CANDIDATE_SITE;
 const r=spawnSync('/usr/bin/timeout',['--kill-after=5s','35s','runuser','-u','candidate','--','/usr/bin/prlimit','--cpu=35','--nproc=64','--nofile=128','--','env','-i','PATH=/usr/local/bin:/usr/bin:/bin',`HOME=${site}/home`,`TMPDIR=${site}/tmp`,'NODE_ALLOWED_PACKAGE=uint8array-extras','/usr/local/bin/node','--no-addons','/tests/runtime/node/candidate_runner.mjs'],{cwd:site,input:`${JSON.stringify({package:'uint8array-extras',export:exportName,args})}\n`,encoding:'utf8',timeout:40000,maxBuffer:262144});
 if (r.error || ![0,1].includes(r.status)) throw new Error(`candidate transport failed: ${r.stderr||r.error}`);
 return JSON.parse(r.stdout);
};
export const call=(name,args)=>run(name,args);
