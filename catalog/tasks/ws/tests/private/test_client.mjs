import { spawnSync } from 'node:child_process';

const NODE = '/usr/local/bin/node';
const MAX_OUTPUT = 512 * 1024;

const ADAPTER = String.raw`
import { createServer } from 'node:http';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const MAX_REQUEST = 64 * 1024;
const requestBytes = readFileSync(0);
if (requestBytes.byteLength > MAX_REQUEST) throw new Error('request-too-large');
const request = JSON.parse(requestBytes.toString('utf8'));
if (!request || typeof request !== 'object' || Array.isArray(request)) {
  throw new Error('request-must-be-object');
}

const require = createRequire(pathToFileURL(join(process.cwd(), 'package.json')));
const cjs = require('ws');
const packageRoot = join(process.cwd(), 'node_modules', 'ws');
const packageJson = JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8'));
const rootExport = packageJson.exports?.['.'];
const importEntry = typeof rootExport === 'string'
  ? rootExport
  : rootExport?.import ?? packageJson.module ?? packageJson.main;
if (typeof importEntry !== 'string' || !importEntry.startsWith('./') || importEntry.includes('..')) {
  throw new Error('unsafe-package-entry');
}
const esm = await import(pathToFileURL(join(packageRoot, importEntry)).href);
const WebSocket = esm.WebSocket ?? esm.default ?? cjs.WebSocket ?? cjs;
const WebSocketServer = esm.WebSocketServer ?? cjs.WebSocketServer ?? cjs.Server;
const createWebSocketStream = esm.createWebSocketStream ?? cjs.createWebSocketStream;
const extension = esm.extension ?? cjs.extension;
const subprotocol = esm.subprotocol ?? cjs.subprotocol;

function once(emitter, name, timeout = 4000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      cleanup();
      reject(new Error('timeout:' + name));
    }, timeout);
    function cleanup() {
      clearTimeout(timer);
      emitter.removeListener(name, onEvent);
      emitter.removeListener('error', onError);
    }
    function onEvent(...args) {
      cleanup();
      resolve(args);
    }
    function onError(error) {
      cleanup();
      reject(error);
    }
    emitter.once(name, onEvent);
    if (name !== 'error') emitter.once('error', onError);
  });
}

async function openServer(options = {}) {
  const server = new WebSocketServer({
    host: '127.0.0.1',
    port: 0,
    ...options,
  });
  await once(server, 'listening');
  return server;
}

async function closeServer(server) {
  if (server.clients) {
    for (const client of server.clients) {
      if (client.readyState !== WebSocket.CLOSED) client.terminate();
    }
  }
  if (server._state === 2) return;
  await new Promise((resolve) => server.close(() => resolve()));
}

function endpoint(server, pathname = '/') {
  return 'ws://127.0.0.1:' + server.address().port + pathname;
}

function errorShape(fn) {
  try {
    fn();
    return null;
  } catch (error) {
    return {
      name: error?.constructor?.name ?? 'Error',
      message: String(error?.message ?? error),
    };
  }
}

async function inventory() {
  return {
    package: {
      name: packageJson.name,
      version: packageJson.version,
      main: packageJson.main,
      browser: packageJson.browser,
      importEntry,
    },
    exports: {
      default: typeof esm.default,
      WebSocket: typeof esm.WebSocket,
      WebSocketServer: typeof esm.WebSocketServer,
      createWebSocketStream: typeof esm.createWebSocketStream,
      Receiver: typeof esm.Receiver,
      Sender: typeof esm.Sender,
      PerMessageDeflate: typeof esm.PerMessageDeflate,
      extension: typeof esm.extension,
      subprotocol: typeof esm.subprotocol,
    },
    aliases: {
      cjsDefaultWebSocket: cjs === cjs.WebSocket,
      server: cjs.Server === cjs.WebSocketServer,
      esmDefaultWebSocket: esm.default === esm.WebSocket,
    },
    constants: {
      CONNECTING: WebSocket.CONNECTING,
      OPEN: WebSocket.OPEN,
      CLOSING: WebSocket.CLOSING,
      CLOSED: WebSocket.CLOSED,
    },
    methods: {
      websocket: ['addEventListener', 'removeEventListener', 'close', 'pause', 'ping', 'pong', 'resume', 'send', 'terminate']
        .filter((name) => typeof WebSocket.prototype[name] === 'function'),
      server: ['address', 'close', 'handleUpgrade', 'shouldHandle']
        .filter((name) => typeof WebSocketServer.prototype[name] === 'function'),
    },
  };
}

async function echo(payload) {
  const server = await openServer({
    path: payload.path ?? undefined,
    perMessageDeflate: payload.perMessageDeflate ?? false,
    handleProtocols: payload.selectLastProtocol
      ? (protocols) => [...protocols].at(-1)
      : undefined,
  });
  try {
    const connection = once(server, 'connection');
    const protocols = payload.protocols ?? undefined;
    const client = protocols
      ? new WebSocket(endpoint(server, payload.path ?? '/'), protocols, {
        perMessageDeflate: payload.perMessageDeflate ?? false,
        headers: { 'x-contract': 'ws-task' },
      })
      : new WebSocket(endpoint(server, payload.path ?? '/'), {
        perMessageDeflate: payload.perMessageDeflate ?? false,
        headers: { 'x-contract': 'ws-task' },
      });
    if (payload.binaryType) client.binaryType = payload.binaryType;
    const [serverSocket, request] = await connection;
    await once(client, 'open');
    const serverMessage = once(serverSocket, 'message');
    const clientMessage = once(client, 'message');
    const outbound = payload.binaryBase64
      ? Buffer.from(payload.binaryBase64, 'base64')
      : payload.text;
    client.send(outbound);
    const [received, isBinary] = await serverMessage;
    serverSocket.send(received, { binary: isBinary });
    const [echoed, echoedBinary] = await clientMessage;
    const beforeClose = {
      clientReadyState: client.readyState,
      serverReadyState: serverSocket.readyState,
      clients: server.clients?.size ?? null,
      protocol: client.protocol,
      serverProtocol: serverSocket.protocol,
      extensions: client.extensions,
      requestHeader: request.headers['x-contract'],
      url: client.url,
    };
    const closeEvent = once(client, 'close');
    serverSocket.close(1000, 'complete');
    const [closeCode, closeReason] = await closeEvent;
    return {
      beforeClose,
      message: {
        serverBinary: isBinary,
        clientBinary: echoedBinary,
        text: echoedBinary ? null : String(echoed),
        base64: echoedBinary ? Buffer.from(echoed).toString('base64') : null,
        valueType: echoed?.constructor?.name ?? typeof echoed,
      },
      close: {
        code: closeCode,
        reason: closeReason.toString(),
        readyState: client.readyState,
      },
    };
  } finally {
    await closeServer(server);
  }
}

async function pingPong() {
  const server = await openServer();
  try {
    const connection = once(server, 'connection');
    const client = new WebSocket(endpoint(server));
    const [serverSocket] = await connection;
    await once(client, 'open');
    const clientPing = once(client, 'ping');
    const serverPong = once(serverSocket, 'pong');
    serverSocket.ping('probe');
    const [[pingData], [pongData]] = await Promise.all([clientPing, serverPong]);
    const clientClosed = once(client, 'close');
    const serverClosed = once(serverSocket, 'close');
    client.terminate();
    await Promise.all([clientClosed, serverClosed]);
    return {
      ping: pingData.toString(),
      pong: pongData.toString(),
      serverState: serverSocket.readyState,
    };
  } finally {
    await closeServer(server);
  }
}

async function broadcast() {
  const server = await openServer();
  try {
    const firstConnection = once(server, 'connection');
    const first = new WebSocket(endpoint(server));
    await firstConnection;
    await once(first, 'open');
    const secondConnection = once(server, 'connection');
    const second = new WebSocket(endpoint(server));
    await secondConnection;
    await once(second, 'open');
    const firstMessage = once(first, 'message');
    const secondMessage = once(second, 'message');
    for (const socket of server.clients) socket.send('broadcast');
    const [[a], [b]] = await Promise.all([firstMessage, secondMessage]);
    const tracked = server.clients.size;
    first.terminate();
    second.terminate();
    await Promise.all([once(first, 'close'), once(second, 'close')]);
    return { messages: [a.toString(), b.toString()], tracked };
  } finally {
    await closeServer(server);
  }
}

async function streamRoundTrip() {
  const server = await openServer();
  try {
    const connection = once(server, 'connection');
    const client = new WebSocket(endpoint(server));
    const [serverSocket] = await connection;
    const clientStream = createWebSocketStream(client);
    const serverStream = createWebSocketStream(serverSocket);
    const incoming = once(serverStream, 'data');
    clientStream.write(Buffer.from('stream-data'));
    const [chunk] = await incoming;
    const outgoing = once(clientStream, 'data');
    serverStream.write(Buffer.from('reply:' + chunk.toString()));
    const [reply] = await outgoing;
    clientStream.destroy();
    serverStream.destroy();
    return {
      received: chunk.toString(),
      reply: reply.toString(),
      duplex: typeof clientStream.write === 'function' && typeof clientStream.read === 'function',
    };
  } finally {
    await closeServer(server);
  }
}

async function manualUpgrade() {
  const httpServer = createServer();
  const server = new WebSocketServer({ noServer: true });
  httpServer.on('upgrade', (request, socket, head) => {
    server.handleUpgrade(request, socket, head, (websocket) => {
      server.emit('connection', websocket, request);
    });
  });
  await new Promise((resolve) => httpServer.listen(0, '127.0.0.1', resolve));
  try {
    const connection = once(server, 'connection');
    const client = new WebSocket('ws://127.0.0.1:' + httpServer.address().port + '/manual');
    const [serverSocket, request] = await connection;
    await once(client, 'open');
    const clientMessage = once(client, 'message');
    serverSocket.send('upgraded');
    const [message] = await clientMessage;
    client.terminate();
    await once(client, 'close');
    return { message: message.toString(), path: request.url, noServerAddressError: errorShape(() => server.address()) };
  } finally {
    await closeServer(server);
    await new Promise((resolve) => httpServer.close(() => resolve()));
  }
}

async function eventTarget() {
  const server = await openServer();
  try {
    const connection = once(server, 'connection');
    const client = new WebSocket(endpoint(server));
    const events = [];
    const duplicate = () => events.push('open');
    client.addEventListener('open', duplicate);
    client.addEventListener('open', duplicate);
    client.onmessage = (event) => events.push('onmessage:' + event.data.toString());
    client.addEventListener('message', (event) => events.push('message:' + event.data.toString()));
    const [serverSocket] = await connection;
    await once(client, 'open');
    const message = once(client, 'message');
    serverSocket.send('event-data');
    await message;
    const removable = () => events.push('removed');
    client.addEventListener('close', removable);
    client.removeEventListener('close', removable);
    const closed = once(client, 'close');
    serverSocket.close(1000);
    await closed;
    return events;
  } finally {
    await closeServer(server);
  }
}

async function maxPayload() {
  const server = await openServer({ maxPayload: 4 });
  try {
    const connection = once(server, 'connection');
    const client = new WebSocket(endpoint(server));
    const [serverSocket] = await connection;
    await once(client, 'open');
    const serverError = once(serverSocket, 'error');
    const clientClose = once(client, 'close');
    client.send('12345');
    const [[error], [code]] = await Promise.all([serverError, clientClose]);
    return { errorCode: error.code, closeCode: code };
  } finally {
    await closeServer(server);
  }
}

async function stateTransitions() {
  const server = await openServer();
  try {
    const connection = once(server, 'connection');
    const client = new WebSocket(endpoint(server));
    const connecting = client.readyState;
    const earlySend = errorShape(() => client.send('too-early'));
    const [serverSocket] = await connection;
    await once(client, 'open');
    const open = client.readyState;
    const initiallyPaused = client.isPaused;
    client.pause();
    const paused = client.isPaused;
    client.resume();
    const resumed = client.isPaused;
    const invalidCode = errorShape(() => client.close(999));
    const longReason = errorShape(() => client.close(1000, 'x'.repeat(124)));
    const closed = once(client, 'close');
    serverSocket.close(1000);
    await closed;
    return {
      connecting,
      open,
      closed: client.readyState,
      earlySend,
      initiallyPaused,
      paused,
      resumed,
      invalidCode,
      longReason,
    };
  } finally {
    await closeServer(server);
  }
}

async function serverShape() {
  const missing = errorShape(() => new WebSocketServer({}));
  const conflicting = errorShape(() => new WebSocketServer({ port: 0, noServer: true }));
  const duplicateProtocol = errorShape(() => new WebSocket('ws://127.0.0.1', ['chat', 'chat']));
  const server = await openServer({ path: '/socket' });
  try {
    const address = server.address();
    return {
      missing,
      conflicting,
      duplicateProtocol,
      address: { address: address.address, family: address.family, portType: typeof address.port },
      path: {
        exact: server.shouldHandle({ url: '/socket' }),
        query: server.shouldHandle({ url: '/socket?x=1' }),
        wrong: server.shouldHandle({ url: '/other' }),
      },
    };
  } finally {
    await closeServer(server);
  }
}

async function extensionOperation(payload) {
  if (payload.action === 'parse') return extension.parse(payload.value);
  if (payload.action === 'format') return extension.format(payload.value);
  throw new Error('extension-action-not-allowlisted');
}

async function subprotocolOperation(payload) {
  return [...subprotocol.parse(payload.value)];
}

const operations = {
  inventory,
  echo,
  pingPong,
  broadcast,
  streamRoundTrip,
  manualUpgrade,
  eventTarget,
  maxPayload,
  stateTransitions,
  serverShape,
  extension: extensionOperation,
  subprotocol: subprotocolOperation,
};

if (typeof request.operation !== 'string' || !(request.operation in operations)) {
  throw new Error('operation-not-allowlisted');
}

try {
  const value = await operations[request.operation](request.payload ?? {});
  process.stdout.write(JSON.stringify({ ok: true, value }) + '\n');
} catch (error) {
  process.stdout.write(JSON.stringify({
    ok: false,
    exceptionType: error?.constructor?.name ?? 'Error',
    message: String(error?.message ?? error).slice(0, 4096),
  }) + '\n');
  process.exitCode = 1;
}
`;

function invoke(operation, payload = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM',
    '--kill-after=5s',
    '20s',
    'runuser',
    '-u',
    'candidate',
    '--',
    '/usr/bin/prlimit',
    '--cpu=20',
    '--nproc=48',
    '--nofile=256',
    '--',
    'env',
    '-i',
    'PATH=/usr/local/bin:/usr/bin:/bin',
    `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`,
    'WS_NO_BUFFER_UTIL=1',
    'WS_NO_UTF_8_VALIDATE=1',
    NODE,
    '--no-addons',
    '--input-type=module',
    '--eval',
    ADAPTER,
  ], {
    cwd: site,
    input: JSON.stringify({ operation, payload }),
    encoding: 'utf8',
    timeout: 25_000,
    maxBuffer: MAX_OUTPUT,
  });
  if (result.error || !result.stdout) {
    throw new Error(`candidate child failed: ${result.error?.message ?? result.stderr ?? 'no output'}`);
  }
  try {
    return JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout.slice(0, 2048)}`);
  }
}

export function callCandidate(operation, payload = {}) {
  const response = invoke(operation, payload);
  if (!response.ok) throw new Error(`${response.exceptionType}: ${response.message}`);
  return response.value;
}

export function callCandidateError(operation, payload = {}) {
  const response = invoke(operation, payload);
  if (response.ok) throw new Error('candidate operation unexpectedly succeeded');
  return response;
}
