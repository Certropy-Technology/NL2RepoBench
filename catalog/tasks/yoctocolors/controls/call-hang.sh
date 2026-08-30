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
const hang = () => { while (true) {} };
export {
  hang as reset, hang as bold, hang as dim, hang as italic, hang as underline,
  hang as underlineDouble, hang as underlineCurly, hang as underlineDotted,
  hang as underlineDashed, hang as overline, hang as inverse, hang as hidden,
  hang as strikethrough, hang as black, hang as red, hang as green, hang as yellow,
  hang as blue, hang as magenta, hang as cyan, hang as white, hang as gray,
  hang as bgBlack, hang as bgRed, hang as bgGreen, hang as bgYellow, hang as bgBlue,
  hang as bgMagenta, hang as bgCyan, hang as bgWhite, hang as bgGray,
  hang as redBright, hang as greenBright, hang as yellowBright, hang as blueBright,
  hang as magentaBright, hang as cyanBright, hang as whiteBright, hang as bgRedBright,
  hang as bgGreenBright, hang as bgYellowBright, hang as bgBlueBright,
  hang as bgMagentaBright, hang as bgCyanBright, hang as bgWhiteBright,
  hang as underlineBlack, hang as underlineRed, hang as underlineGreen,
  hang as underlineYellow, hang as underlineBlue, hang as underlineMagenta,
  hang as underlineCyan, hang as underlineWhite, hang as underlineGray,
  hang as underlineRedBright, hang as underlineGreenBright,
  hang as underlineYellowBright, hang as underlineBlueBright,
  hang as underlineMagentaBright, hang as underlineCyanBright,
  hang as underlineWhiteBright,
};
JS
: > index.d.ts
: > base.d.ts
