#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"yoctocolors","version":"2.2.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"sideEffects":false,"engines":{"node":">=18"},"files":["index.js","index.d.ts","base.js","base.d.ts"]}
JSON
cat > package-lock.json <<'JSON'
{"name":"yoctocolors","version":"2.2.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"yoctocolors","version":"2.2.0"}}}
JSON
cat > index.js <<'JS'
export * from './base.js';
export * as default from './base.js';
JS
cat > base.js <<'JS'
const blocked = async () => fetch('https://example.invalid/should-be-blocked');
export {
  blocked as reset, blocked as bold, blocked as dim, blocked as italic,
  blocked as underline, blocked as underlineDouble, blocked as underlineCurly,
  blocked as underlineDotted, blocked as underlineDashed, blocked as overline,
  blocked as inverse, blocked as hidden, blocked as strikethrough,
  blocked as black, blocked as red, blocked as green, blocked as yellow,
  blocked as blue, blocked as magenta, blocked as cyan, blocked as white,
  blocked as gray, blocked as bgBlack, blocked as bgRed, blocked as bgGreen,
  blocked as bgYellow, blocked as bgBlue, blocked as bgMagenta, blocked as bgCyan,
  blocked as bgWhite, blocked as bgGray, blocked as redBright,
  blocked as greenBright, blocked as yellowBright, blocked as blueBright,
  blocked as magentaBright, blocked as cyanBright, blocked as whiteBright,
  blocked as bgRedBright, blocked as bgGreenBright, blocked as bgYellowBright,
  blocked as bgBlueBright, blocked as bgMagentaBright, blocked as bgCyanBright,
  blocked as bgWhiteBright, blocked as underlineBlack, blocked as underlineRed,
  blocked as underlineGreen, blocked as underlineYellow, blocked as underlineBlue,
  blocked as underlineMagenta, blocked as underlineCyan, blocked as underlineWhite,
  blocked as underlineGray, blocked as underlineRedBright,
  blocked as underlineGreenBright, blocked as underlineYellowBright,
  blocked as underlineBlueBright, blocked as underlineMagentaBright,
  blocked as underlineCyanBright, blocked as underlineWhiteBright,
};
JS
: > index.d.ts
: > base.d.ts
