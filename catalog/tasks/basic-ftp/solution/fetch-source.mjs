import {createWriteStream, renameSync, rmSync, statSync} from "node:fs";
import {get} from "node:https";

const revision = "9cbc5cf23cb2b62231bc1822a868138e4772d4e5";
const url = `https://codeload.github.com/patrickjuchli/basic-ftp/tar.gz/${revision}`;
const output = process.argv[2];
const maxBytes = 4 * 1024 * 1024;
if (!output) throw new Error("source archive output is required");
const temporary = `${output}.partial`;
rmSync(temporary, {force: true});

await new Promise((resolve, reject) => {
  const request = get(url, {headers: {"User-Agent": "nl2repobench-oracle"}, timeout: 30_000}, (response) => {
    if (response.statusCode !== 200) {
      response.resume();
      reject(new Error(`source fetch returned HTTP ${response.statusCode}`));
      return;
    }
    let received = 0;
    const stream = createWriteStream(temporary, {flags: "wx", mode: 0o400});
    response.on("data", (chunk) => {
      received += chunk.length;
      if (received > maxBytes) request.destroy(new Error("source archive exceeds bound"));
    });
    response.on("error", reject);
    stream.on("error", reject);
    stream.on("finish", resolve);
    response.pipe(stream);
  });
  request.on("timeout", () => request.destroy(new Error("source fetch timed out")));
  request.on("error", reject);
});
if (statSync(temporary).size < 1024) throw new Error("source archive is unexpectedly small");
renameSync(temporary, output);
