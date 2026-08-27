import {createWriteStream, renameSync, rmSync, statSync} from 'node:fs';
import {get} from 'node:https';

const revision = '2a4378bdc2eac9cf7d0cdfe0a52b1b25f779806a';
const url = `https://codeload.github.com/yargs/yargs/tar.gz/${revision}`;
const output = process.argv[2];
const maximumBytes = 4 * 1024 * 1024;

if (!output) throw new Error('output path is required');
const temporary = `${output}.partial`;
rmSync(temporary, {force: true});

await new Promise((resolve, reject) => {
  const request = get(url, {
    headers: {'User-Agent': 'nl2repobench-oracle'},
    timeout: 30_000,
  }, response => {
    if (response.statusCode !== 200) {
      response.resume();
      reject(new Error(`source fetch returned HTTP ${response.statusCode}`));
      return;
    }
    let received = 0;
    const outputStream = createWriteStream(temporary, {flags: 'wx', mode: 0o400});
    response.on('data', chunk => {
      received += chunk.length;
      if (received > maximumBytes) request.destroy(new Error('source archive exceeds size limit'));
    });
    response.on('error', reject);
    outputStream.on('error', reject);
    outputStream.on('finish', resolve);
    response.pipe(outputStream);
  });
  request.on('timeout', () => request.destroy(new Error('source fetch timed out')));
  request.on('error', reject);
});

if (statSync(temporary).size < 1024) throw new Error('source archive is unexpectedly small');
renameSync(temporary, output);
