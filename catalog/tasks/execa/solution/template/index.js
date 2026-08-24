import {spawn, spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const stripNewline = value => value.replace(/\r?\n$/, '');
const toPath = value => value instanceof URL ? fileURLToPath(value) : value;
const quote = value => /[\s"'\\$`]/.test(value) ? `'${String(value).replaceAll("'", "'\\''")}'` : String(value);
const formatCommand = (file, args) => [file, ...args].map(quote).join(' ');

export class ExecaError extends Error {
	constructor(message, fields = {}) {
		super(message);
		this.name = 'ExecaError';
		Object.assign(this, fields);
	}
}

export class ExecaSyncError extends ExecaError {
	constructor(message, fields = {}) {
		super(message, fields);
		this.name = 'ExecaSyncError';
	}
}

export function parseCommandString(command) {
	const result = [];
	let token = '';
	let escaping = false;
	for (const character of command.trim()) {
		if (escaping) {
			token += character;
			escaping = false;
		} else if (character === '\\') {
			escaping = true;
		} else if (/\s/.test(character)) {
			if (token) {
				result.push(token);
				token = '';
			}
		} else {
			token += character;
		}
	}
	if (escaping) token += '\\';
	if (token) result.push(token);
	return result;
}

const normalize = (file, args, options = {}) => {
	const actualFile = toPath(file);
	const actualArgs = Array.isArray(args) ? args.map(String) : [];
	const env = options.extendEnv === false ? {...options.env} : {...process.env, ...options.env};
	return {file: actualFile, args: actualArgs, options, env, command: formatCommand(actualFile, actualArgs)};
};

const resultFields = ({file, args, options, env, command}, stdout, stderr, exitCode, signal, timedOut, durationMs) => ({
	command,
	escapedCommand: command,
	cwd: options.cwd ?? process.cwd(),
	durationMs,
	failed: exitCode !== 0 || signal !== null || timedOut,
	timedOut,
	isCanceled: false,
	isGracefullyCanceled: false,
	isTerminated: signal !== null,
	isMaxBuffer: false,
	isForcefullyTerminated: false,
	exitCode,
	signal,
	stdout: options.stripFinalNewline === false ? stdout : stripNewline(stdout),
	stderr: options.stripFinalNewline === false ? stderr : stripNewline(stderr),
	stdio: [undefined, stdout, stderr],
	ipcOutput: [],
	pipedFrom: [],
});

const failure = (result, sync = false) => {
	const reason = result.timedOut ? 'timed out' : result.signal ? `killed by ${result.signal}` : `failed with exit code ${result.exitCode}`;
	const ErrorClass = sync ? ExecaSyncError : ExecaError;
	return new ErrorClass(`Command ${reason}: ${result.escapedCommand}`, {
		...result,
		name: sync ? 'ExecaSyncError' : 'ExecaError',
		shortMessage: `Command ${reason}: ${result.escapedCommand}`,
		originalMessage: result.stderr || '',
	});
};

const resolveInvocation = (file, args, options) => {
	if (Array.isArray(file)) {
		const values = [...file];
		const command = values.map(value => String(value)).join(' ');
		return normalize(parseCommandString(command)[0], parseCommandString(command).slice(1), options);
	}
	return normalize(file, args, options);
};

function createTag(method) {
	return function (...parameters) {
		if (Array.isArray(parameters[0]) && parameters[0].raw !== undefined) {
			const strings = parameters[0];
			let command = strings[0];
			for (let index = 1; index < strings.length; index++) command += String(parameters[index]) + strings[index];
			return method(command);
		}
		return method(...parameters);
	};
}

export function execa(file, args = [], options = {}) {
	if (Array.isArray(file)) return createTag(execa)(file, ...args);
	const invocation = resolveInvocation(file, args, options);
	const started = performance.now();
	const child = spawn(invocation.file, invocation.args, {
		cwd: options.cwd,
		env: invocation.env,
		shell: options.shell === true,
		stdio: ['pipe', 'pipe', 'pipe'],
	});
	let stdout = '';
	let stderr = '';
	let timedOut = false;
	let timer;
	const promise = new Promise((resolve, reject) => {
		child.stdout.setEncoding('utf8');
		child.stderr.setEncoding('utf8');
		child.stdout.on('data', chunk => { stdout += chunk; });
		child.stderr.on('data', chunk => { stderr += chunk; });
		if (options.input !== undefined) child.stdin.end(options.input);
		else child.stdin.end();
		if (options.timeout > 0) timer = setTimeout(() => { timedOut = true; child.kill('SIGTERM'); }, options.timeout);
		child.on('error', error => reject(error));
		child.on('close', (exitCode, signal) => {
			if (timer) clearTimeout(timer);
			const result = resultFields(invocation, stdout, stderr, exitCode, signal, timedOut, performance.now() - started);
			if (result.failed && options.reject !== false) reject(failure(result));
			else resolve(result);
		});
	});
	promise.child = child;
	return promise;
}

export function execaSync(file, args = [], options = {}) {
	const invocation = resolveInvocation(file, args, options);
	const started = performance.now();
	const child = spawnSync(invocation.file, invocation.args, {
		cwd: options.cwd,
		env: invocation.env,
		shell: options.shell === true,
		input: options.input,
		encoding: 'utf8',
		timeout: options.timeout,
	});
	const result = resultFields(invocation, child.stdout ?? '', child.stderr ?? '', child.status, child.signal, child.error?.code === 'ETIMEDOUT', performance.now() - started);
	if (result.failed && options.reject !== false) throw failure(result, true);
	return result;
}

export function execaNode(scriptPath, args = [], options = {}) {
	return execa(process.execPath, [toPath(scriptPath), ...args], options);
}

export const $ = execa;
