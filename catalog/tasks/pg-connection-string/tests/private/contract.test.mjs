import assert from "node:assert/strict";
import test from "node:test";
import { call, value } from "./test_client.mjs";

function pick(object, keys) {
  return Object.fromEntries(keys.filter((key) => Object.hasOwn(object, key)).map((key) => [key, object[key]]));
}

test("root-export", () => assert.deepEqual(value("parse", ["pg://u:p@host:5432/db"]), {
  user: "u", password: "p", host: "host", port: "5432", database: "db",
}));
test("tcp-basic", () => assert.deepEqual(value("parse", ["postgres://brian:pw@boom:381/lala"]), {
  user: "brian", password: "pw", host: "boom", port: "381", database: "lala",
}));
test("relative-database", () => assert.equal(value("parse", ["different_db_on_default_host"]).database, "different_db_on_default_host"));
test("literal-space", () => assert.equal(value("parse", ["postgres://localhost/post gres"]).database, "post gres"));
test("encoded-space", () => assert.equal(value("parse", ["postgres://localhost/post%20gres"]).database, "post gres"));
test("credential-decoding", () => assert.deepEqual(value("parse", ["pg://bi%25na%25%25ry%20:s%40f%23@localhost/db"]), {
  user: "bi%na%%ry ", password: "s@f#", host: "localhost", port: "", database: "db",
}));
test("query-precedence", () => assert.deepEqual(value("parse", ["pg://u:p@url/db?user=query&port=1&port=2"]), {
  user: "query", password: "p", host: "url", port: "2", database: "db",
}));
test("null-database", () => assert.equal(value("parse", ["pg://myhost/"]).database, null));
test("socket-path", () => assert.deepEqual(value("parse", ["/const/run/"]), { host: "/const/run/" }));
test("socket-path-db", () => assert.deepEqual(value("parse", ["/const/run/ mydb"]), { host: "/const/run/", database: "mydb" }));
test("socket-url", () => assert.deepEqual(pick(value("parse", ["socket:/some%20path/?db=my%2Bdb&encoding=utf8"]), ["user", "password", "host", "database", "client_encoding"]), {
  user: "", password: "", host: "/some path/", database: "my+db", client_encoding: "utf8",
}));
test("socket-url-user", () => assert.deepEqual(pick(value("parse", ["socket://brian:pw@/const/run/?db=mydb"]), ["user", "password", "host", "database", "client_encoding"]), {
  user: "brian", password: "pw", host: "/const/run/", database: "mydb", client_encoding: null,
}));
test("encoded-socket", () => assert.equal(value("parse", ["pg://u:p@%2Funix%2Fsocket/db"]).host, "/unix/socket"));
test("ssl-true", () => assert.equal(value("parse", ["pg:///?ssl=1"]).ssl, true));
test("ssl-false", () => assert.equal(value("parse", ["pg:///?ssl=0"]).ssl, false));
test("ssl-direct", () => assert.equal(value("parse", ["pg:///?sslnegotiation=direct"]).ssl, true));
test("ssl-direct-explicit", () => assert.deepEqual(pick(value("parse", ["pg:///?sslnegotiation=direct&sslmode=require"]), ["ssl"]).ssl, {}));
test("ssl-disable", () => assert.equal(value("parse", ["pg:///?sslmode=disable"]).ssl, false));
test("ssl-no-verify", () => assert.deepEqual(pick(value("parse", ["pg:///?sslmode=no-verify"]), ["ssl"]).ssl, { rejectUnauthorized: false }));
test("ssl-require", () => assert.deepEqual(pick(value("parse", ["pg:///?sslmode=require"]), ["ssl"]).ssl, {}));
test("libpq-prefer", () => assert.deepEqual(pick(value("parse", ["pg:///?sslmode=prefer&uselibpqcompat=true"]), ["ssl"]).ssl, { rejectUnauthorized: false }));
test("libpq-require", () => assert.deepEqual(pick(value("parse", ["pg:///?sslmode=require", { useLibpqCompat: true }]), ["ssl"]).ssl, { rejectUnauthorized: false }));
test("libpq-verify-ca-error", () => assert.equal(call("parse", ["pg:///?sslmode=verify-ca", { useLibpqCompat: true }]).ok, false));
test("libpq-verify-full", () => assert.deepEqual(pick(value("parse", ["pg:///?sslmode=verify-full", { useLibpqCompat: true }]), ["ssl"]).ssl, {}));
test("libpq-conflict", () => assert.equal(call("parse", ["pg:///?uselibpqcompat=true", { useLibpqCompat: true }]).ok, false));
test("custom-param", () => assert.equal(value("parse", ["pg:///?application_name=TheApp"]).application_name, "TheApp"));
test("host-override", () => assert.equal(value("parse", ["pg://u:p@localhost/db?host=/unix/socket"]).host, "/unix/socket"));
test("port-query", () => assert.equal(value("parse", ["postgres:///?host=localhost&port=1234"]).port, "1234"));
test("client-basic", () => assert.deepEqual(value("toClientConfig", [{ user: "b", host: "h", port: "381", database: "d" }]), {
  user: "b", host: "h", port: 381, database: "d",
}));
test("client-empty-port", () => assert.equal(Object.hasOwn(value("toClientConfig", [{ port: "" }]), "port"), false));
test("client-invalid-port", () => assert.equal(call("toClientConfig", [{ port: "bogus" }]).ok, false));
test("client-ssl-bool", () => assert.equal(value("toClientConfig", [{ ssl: false }]).ssl, false));
test("client-ssl-object", () => assert.deepEqual(value("toClientConfig", [{ ssl: { cert: null, key: "k" } }]).ssl, { key: "k" }));
test("client-falsy-ssl", () => assert.deepEqual(value("toClientConfig", [{ ssl: { rejectUnauthorized: false } }]).ssl, { rejectUnauthorized: false }));
test("parse-into-client", () => assert.deepEqual(value("parseIntoClientConfig", ["postgres://brian:pw@boom:381/lala"]), {
  user: "brian", password: "pw", host: "boom", port: 381, database: "lala",
}));
test("invalid-url", () => {
  const secret = "g#4624$@F$#v`";
  const result = call("parse", [`postgres://user:${secret}@localhost:5432/db%`]);
  assert.equal(result.ok, false);
  assert.equal(JSON.stringify(result).includes(secret), false);
});
