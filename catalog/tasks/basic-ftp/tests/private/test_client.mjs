import {spawnSync} from "node:child_process";
import {join} from "node:path";

const worker = String.raw`
import {createRequire} from "node:module";
import {join} from "node:path";
import {readFileSync} from "node:fs";
const require = createRequire(join(process.cwd(), "package.json"));
const api = require("basic-ftp");
function project(info) {
  const out = {name: info.name, type: info.type, size: info.size, rawModifiedAt: info.rawModifiedAt, isFile: info.isFile, isDirectory: info.isDirectory, isSymbolicLink: info.isSymbolicLink};
  for (const key of ["modifiedAt", "permissions", "hardLinkCount", "link", "group", "user", "uniqueID"]) {
    if (info[key] !== undefined) out[key] = info[key] instanceof Date ? info[key].toISOString() : info[key];
  }
  return out;
}
async function main() {
  const request = JSON.parse(readFileSync(0, "utf8"));
  let value;
  switch (request.operation) {
    case "exports": value = {keys: Object.keys(api).sort(), rootParseList: typeof api.parseList === "function", fileInfo: typeof api.FileInfo === "function", client: typeof api.Client === "function"}; break;
    case "file-type-values": value = {Unknown: api.FileType.Unknown, File: api.FileType.File, Directory: api.FileType.Directory, SymbolicLink: api.FileType.SymbolicLink}; break;
    case "file-info": { const spec = request.value; const info = new api.FileInfo(spec.name); if (spec.type !== undefined) info.type = api.FileType[spec.type]; if (spec.date !== undefined) info.date = spec.date; value = project(info); value.permission = api.FileInfo.UnixPermission; break; }
    case "parse-list": value = api.parseList(request.value).map(project); break;
    case "parse-control": value = require("basic-ftp/dist/parseControlResponse").parseControlResponse(request.value); break;
    case "control-predicates": { const parser = require("basic-ftp/dist/parseControlResponse"); value = {single: request.value.map(parser.isSingleLine), multi: request.value.map(parser.isMultiline), completion: request.value.map(parser.positiveCompletion), intermediate: request.value.map(parser.positiveIntermediate)}; break; }
    case "pasv": value = require("basic-ftp/dist/transfer").parsePasvResponse(request.value); break;
    case "epsv": value = require("basic-ftp/dist/transfer").parseEpsvResponse(request.value); break;
    case "mlsx-date": value = require("basic-ftp/dist/parseListMLSD").parseMLSxDate(request.value).toISOString(); break;
    case "string-writer": { const {StringWriter} = require("basic-ftp/dist/StringWriter"); const spec = request.value; const writer = new StringWriter(spec.max); value = await new Promise((resolve, reject) => { writer.once("error", reject); writer.once("finish", () => resolve(writer.getText(spec.encoding ?? "utf8"))); for (const chunk of spec.chunks) writer.write(Buffer.from(chunk, spec.inputEncoding ?? "utf8")); writer.end(); }); break; }
    case "client": { const client = new api.Client(request.value.timeout, request.value.options); value = {closed: client.closed, timeout: client.ftp.timeout, encoding: client.ftp.encoding, verbose: client.ftp.verbose}; client.close(); break; }
    default: throw new Error("unsupported test operation");
  }
  process.stdout.write(JSON.stringify({ok: true, value}) + "\n");
}
main().catch((error) => { process.stdout.write(JSON.stringify({ok: false, message: String(error?.message ?? error)}) + "\n"); process.exitCode = 1; });
`;

export function call(operation, value = null) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const result = spawnSync(
    "/usr/bin/timeout",
    ["35s", "/usr/sbin/runuser", "-u", "candidate", "--", process.execPath, "--no-addons", "--input-type=module", "-e", worker],
    {
      cwd: site,
      input: `${JSON.stringify({operation, value})}\n`,
      encoding: "utf8",
      env: {
        PATH: "/usr/local/bin:/usr/bin:/bin",
        HOME: join(site, "home"),
        TMPDIR: join(site, "tmp"),
        NODE_CANDIDATE_SITE: site,
      },
      maxBuffer: 256 * 1024,
      timeout: 40_000,
    },
  );
  if (result.error) throw result.error;
  let response;
  try {
    response = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response was not JSON: ${result.stderr}`);
  }
  if (!response.ok) throw new Error(response.message ?? response.error ?? "candidate call failed");
  return response.value;
}
