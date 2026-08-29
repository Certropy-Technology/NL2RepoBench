import assert from "node:assert/strict";
import {test} from "node:test";
import {call} from "./test_client.mjs";

test("root exports the deterministic public classes and parser", () => {
  const result = call("exports");
  assert.deepEqual(result.keys, ["Client", "FTPContext", "FTPError", "FileInfo", "FileType", "enterPassiveModeIPv4", "enterPassiveModeIPv6", "parseList"]);
  assert.equal(result.rootParseList, true);
  assert.equal(result.fileInfo, true);
  assert.equal(result.client, true);
});

test("FileType preserves the numeric enum values", () => {
  assert.deepEqual(call("file-type-values"), {Unknown: 0, File: 1, Directory: 2, SymbolicLink: 3});
});

test("FileInfo has stable defaults", () => {
  assert.deepEqual(call("file-info", {name: "entry"}), {
    name: "entry", type: 0, size: 0, rawModifiedAt: "", isFile: false,
    isDirectory: false, isSymbolicLink: false, permission: {Read: 4, Write: 2, Execute: 1},
  });
});

test("FileInfo reports a regular file", () => {
  assert.equal(call("file-info", {name: "a", type: "File"}).isFile, true);
});

test("FileInfo reports a directory", () => {
  assert.equal(call("file-info", {name: "a", type: "Directory"}).isDirectory, true);
});

test("FileInfo reports a symbolic link", () => {
  assert.equal(call("file-info", {name: "a", type: "SymbolicLink"}).isSymbolicLink, true);
});

test("FileInfo date aliases rawModifiedAt", () => {
  assert.equal(call("file-info", {name: "a", date: "Jan 1 12:00"}).rawModifiedAt, "Jan 1 12:00");
});

test("control parser emits a single line response", () => {
  assert.deepEqual(call("parse-control", "200 OK"), {messages: ["200 OK"], rest: ""});
});

test("control parser normalizes CRLF and blank lines", () => {
  assert.deepEqual(call("parse-control", "200 OK\r\n\r\n"), {messages: ["200 OK"], rest: ""});
});

test("control parser groups one multiline response", () => {
  assert.deepEqual(call("parse-control", "150-Opening\r\ntext\r\n150 Done"), {messages: ["150-Opening\ntext\n150 Done"], rest: ""});
});

test("control parser emits consecutive multiline groups", () => {
  assert.deepEqual(call("parse-control", "150-A\n150 B\n200-C\n200 D"), {messages: ["150-A\n150 B", "200-C\n200 D"], rest: ""});
});

test("control parser keeps an incomplete group in rest", () => {
  assert.deepEqual(call("parse-control", "150-A\n150 B\n200-D"), {messages: ["150-A\n150 B"], rest: "200-D\n"});
});

test("control predicates classify response lines and codes", () => {
  assert.deepEqual(call("control-predicates", ["200", "200 OK", "200-Start", "99", " 200"]), {
    single: [true, true, false, false, false], multi: [false, false, true, false, false],
    completion: [true, false, false, false, true], intermediate: [false, false, false, false, false],
  });
});

test("completion and intermediate ranges include only their FTP bands", () => {
  assert.deepEqual(call("control-predicates", [199, 200, 299, 300, 399, 400]).completion, [false, true, true, false, false, false]);
  assert.deepEqual(call("control-predicates", [199, 200, 299, 300, 399, 400]).intermediate, [false, false, false, true, true, false]);
});

test("parseList detects an MLSD filename", () => {
  assert.deepEqual(call("parse-list", " filename"), [{name: "filename", type: 0, size: 0, rawModifiedAt: "", isFile: false, isDirectory: false, isSymbolicLink: false}]);
});

test("parseList reads MLSD file facts", () => {
  assert.deepEqual(call("parse-list", "size=11;type=file;modify=20181025120459; file one"), [{name: "file one", type: 1, size: 11, rawModifiedAt: "2018-10-25T12:04:59.000Z", modifiedAt: "2018-10-25T12:04:59.000Z", isFile: true, isDirectory: false, isSymbolicLink: false}]);
});

test("parseList reads MLSD directory facts and permissions", () => {
  assert.deepEqual(call("parse-list", "size=11;type=dir;unix.mode=0755;modify=20190218120006; folder"), [{name: "folder", type: 2, size: 11, rawModifiedAt: "2019-02-18T12:00:06.000Z", modifiedAt: "2019-02-18T12:00:06.000Z", isFile: false, isDirectory: true, isSymbolicLink: false, permissions: {user: 7, group: 5, world: 5}}]);
});

test("parseList ignores MLSD current and parent directories", () => {
  assert.deepEqual(call("parse-list", "type=cdir; .\ntype=pdir; ..\ntype=dir; ."), []);
});

test("parseList parses an explicit MLSD symbolic link", () => {
  assert.deepEqual(call("parse-list", "type=OS.unix=slink:/actual/target; filename"), [{name: "filename", type: 3, size: 0, rawModifiedAt: "", isFile: false, isDirectory: false, isSymbolicLink: true, link: "/actual/target"}]);
});

test("parseList resolves MLSD links by unique id", () => {
  const result = call("parse-list", "type=OS.unix=symlink;unique=1234; link\ntype=file;unique=1234; target");
  assert.equal(result[0].link, "target");
  assert.equal(result[0].uniqueID, "1234");
});

test("parseList omits an MLSD target outside the listed directory", () => {
  const result = call("parse-list", "type=OS.unix=symlink;unique=1234; link\ntype=file;unique=1234; /outside/target");
  assert.deepEqual(result.map((item) => item.name), ["link"]);
  assert.equal(result[0].link, "/outside/target");
});

test("parseList honors named MLSD owner and group over numeric fallback", () => {
  const result = call("parse-list", "UNIX.ownername=alice;UNIX.groupname=staff;UNIX.owner=11;UNIX.group=22; file");
  assert.equal(result[0].user, "alice");
  assert.equal(result[0].group, "staff");
});

test("parseList parses a Unix listing", () => {
  const result = call("parse-list", "-rw-r--r--+ 1 patrick staff 1057 Dec 11 14:35 LICENSE.txt\ndrw-r-xr-x 5 patrick staff 170 Dec 11 17:24 lib");
  assert.deepEqual(result.map((item) => ({name: item.name, type: item.type, size: item.size, permissions: item.permissions})), [
    {name: "LICENSE.txt", type: 1, size: 1057, permissions: {user: 6, group: 4, world: 4}},
    {name: "lib", type: 2, size: 170, permissions: {user: 6, group: 5, world: 5}},
  ]);
});

test("parseList ignores Unix dot entries", () => {
  const result = call("parse-list", "drwxr-xr-x 2 root root 0 Jan 1 00:00 .\ndrwxr-xr-x 2 root root 0 Jan 1 00:00 ..\n-rw-r--r-- 1 root root 3 Jan 1 00:00 file");
  assert.deepEqual(result.map((item) => item.name), ["file"]);
});

test("parseList parses a DOS directory and file", () => {
  const result = call("parse-list", "12-05-96  05:03PM       <DIR>          myDir\n11-14-97  04:21PM                  953 MYFILE.INI");
  assert.deepEqual(result.map((item) => ({name: item.name, type: item.type, size: item.size, raw: item.rawModifiedAt})), [
    {name: "myDir", type: 2, size: 0, raw: "12-05-96 05:03PM"},
    {name: "MYFILE.INI", type: 1, size: 953, raw: "11-14-97 04:21PM"},
  ]);
});

test("parseList returns an empty array for blank and total-only input", () => {
  assert.deepEqual(call("parse-list", " \r\ntotal 0\r\n  "), []);
});

test("parseList rejects an unknown format", () => {
  assert.throws(() => call("parse-list", "not an FTP listing"), /only supports MLSD, Unix- or DOS-style/);
});

test("PASV parsing joins the address bytes and calculates the port", () => {
  assert.deepEqual(call("pasv", "227 Entering Passive Mode (192,168,1,100,10,229)"), {host: "192.168.1.100", port: 2789});
});

test("PASV parsing masks port components to one byte", () => {
  assert.deepEqual(call("pasv", "227 Entering Passive Mode (1,2,3,4,266,511)"), {host: "1.2.3.4", port: 2815});
});

test("PASV parsing rejects malformed responses", () => {
  assert.throws(() => call("pasv", "227 no address"), /Can't parse response to 'PASV'/);
});

test("EPSV parsing accepts pipe delimiters", () => {
  assert.equal(call("epsv", "229 Entering Extended Passive Mode (|||6446|)"), 6446);
});

test("EPSV parsing accepts IBM delimiter characters", () => {
  assert.equal(call("epsv", "229 Entering Extended Passive Mode (!!!2121!)"), 2121);
});

test("EPSV parsing rejects a non-numeric port", () => {
  assert.throws(() => call("epsv", "229 Entering Extended Passive Mode (|||abc|)"), /port is not a number/);
});

test("MLSx dates parse as UTC ISO timestamps", () => {
  assert.equal(call("mlsx-date", "19991005213102"), "1999-10-05T21:31:02.000Z");
});

test("MLSx dates preserve milliseconds", () => {
  assert.equal(call("mlsx-date", "19980615100045.014"), "1998-06-15T10:00:45.014Z");
});

test("StringWriter concatenates Buffer chunks", () => {
  assert.equal(call("string-writer", {chunks: ["hello ", "world"]}), "hello world");
});

test("StringWriter handles a UTF-8 code point split across chunks", () => {
  assert.equal(call("string-writer", {chunks: ["caf", "é", " 😀"]}), "café 😀");
});

test("StringWriter decodes with the requested encoding", () => {
  assert.equal(call("string-writer", {chunks: ["abc"], encoding: "ascii"}), "abc");
});

test("StringWriter rejects bytes beyond its maximum", () => {
  assert.throws(() => call("string-writer", {chunks: ["1234"], max: 3}), /Maximum bytes exceeded/);
});

test("Client starts closed with default FTP settings", () => {
  assert.deepEqual(call("client", {timeout: undefined}), {closed: true, timeout: 30000, encoding: "utf8", verbose: false});
});

test("Client stores an explicit timeout", () => {
  assert.equal(call("client", {timeout: 1250}).timeout, 1250);
});

test("Client close is safe before any connection", () => {
  assert.equal(call("client", {timeout: 0}).closed, true);
});

test("parseList preserves entry order across MLSD records", () => {
  const result = call("parse-list", "type=file;unique=a; first\ntype=dir;unique=b; second");
  assert.deepEqual(result.map((item) => item.name), ["first", "second"]);
});

test("parseList reads MLSD sizd as directory size", () => {
  assert.equal(call("parse-list", "sizd=4096; filename")[0].size, 4096);
});

test("parseList reads Unix hard-link count and owner metadata", () => {
  const result = call("parse-list", "-rw------- 2 1001 1001 487 Feb 25 19:03 package.json")[0];
  assert.deepEqual({user: result.user, group: result.group, hardLinkCount: result.hardLinkCount}, {user: "1001", group: "1001", hardLinkCount: 2});
});

test("parseList extracts a Unix symbolic-link target", () => {
  const result = call("parse-list", "lrwxrwxrwx 1 root root 7 Jan 1 00:00 current -> release")[0];
  assert.deepEqual({name: result.name, type: result.type, link: result.link}, {name: "current", type: 3, link: "release"});
});

test("control parser accepts a closing response without a message", () => {
  assert.deepEqual(call("parse-control", "200-A\n200-B\n200"), {messages: ["200-A\n200-B\n200"], rest: ""});
});
