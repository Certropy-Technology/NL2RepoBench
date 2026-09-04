import assert from 'node:assert/strict'
import test from 'node:test'
import {construct, surface} from './test_client.mjs'

test('public surface exposes only the named class', () => {
  const value = surface()
  assert.deepEqual(value.exports, ['VFileMessage'])
  assert.equal(value.isClass, true)
})

test('basic string reason creates an Error-like message', () => {
  const value = construct({reason: 'Foo'})
  assert.equal(value.isError, true)
  assert.deepEqual({name:value.name, message:value.message, reason:value.reason, file:value.file, fatal:value.fatal, stackFirst:value.stackFirst, string:value.string}, {name:'1:1', message:'Foo', reason:'Foo', file:'', fatal:undefined, stackFirst:'', string:'1:1: Foo'})
})

test('empty reason formats without a trailing separator', () => assert.equal(construct({reason:''}).string, '1:1'))
test('point sets place and starting coordinates', () => {
  const value = construct({reason:'x', second:{line:2,column:3}})
  assert.deepEqual({line:value.line,column:value.column,place:value.place,name:value.name,string:value.string}, {line:2,column:3,place:{line:2,column:3},name:'2:3',string:'2:3: x'})
})
test('position sets range formatting', () => {
  const value = construct({reason:'x', second:{start:{line:2,column:3},end:{line:2,column:5}}})
  assert.deepEqual({line:value.line,column:value.column,name:value.name,string:value.string}, {line:2,column:3,name:'2:3-2:5',string:'2:3-2:5: x'})
  assert.deepEqual(value.place, {start:{line:2,column:3},end:{line:2,column:5}})
})
test('node uses its position and records itself as ancestor', () => {
  const node = {type:'x',position:{start:{line:2,column:3},end:{line:2,column:5}}}
  const value = construct({reason:'x',second:node})
  assert.equal(value.ancestorsLength, 1)
  assert.deepEqual(value.place, node.position)
})
test('node without position has default display location', () => {
  const value = construct({reason:'x',second:{type:'x'}})
  assert.deepEqual({name:value.name,string:value.string,ancestorsLength:value.ancestorsLength}, {name:'1:1',string:'1:1: x',ancestorsLength:1})
})
test('explicit options set source rule and place', () => {
  const value = construct({reason:'x',second:{place:{line:4,column:5},source:'s',ruleId:'r'}})
  assert.deepEqual({source:value.source,ruleId:value.ruleId,line:value.line,column:value.column}, {source:'s',ruleId:'r',line:4,column:5})
})
test('ancestors infer place from final ancestor', () => {
  const value = construct({reason:'x',second:{ancestors:[{type:'x',position:{start:{line:6,column:7},end:{line:6,column:8}}}]}})
  assert.deepEqual({line:value.line,column:value.column,place:value.place,ancestorsLength:value.ancestorsLength}, {line:6,column:7,place:{start:{line:6,column:7},end:{line:6,column:8}},ancestorsLength:1})
})
test('rule-only origin is assigned to ruleId', () => assert.deepEqual([construct({reason:'x',second:'charlie'}).source,construct({reason:'x',second:'charlie'}).ruleId], [undefined,'charlie']))
test('source and rule origin split at the first colon', () => assert.deepEqual([construct({reason:'x',second:'delta:echo'}).source,construct({reason:'x',second:'delta:echo'}).ruleId], ['delta','echo']))
test('legacy third origin is accepted with node parent', () => {
  const value = construct({reason:'x',second:{type:'x'},origin:'delta:echo'})
  assert.deepEqual([value.source,value.ruleId,value.ancestorsLength], ['delta','echo',1])
})
test('legacy third origin is accepted with position', () => {
  const value = construct({reason:'x',second:{line:2,column:3},origin:'delta:echo'})
  assert.deepEqual([value.source,value.ruleId,value.name], ['delta','echo','2:3'])
})
test('explicit options take precedence over legacy origin', () => {
  const value = construct({reason:'x',second:{source:'explicit',ruleId:'rule'},origin:'legacy:ignored'})
  assert.deepEqual([value.source,value.ruleId], ['explicit','rule'])
})
test('Error cause copies message and preserves first stack line', () => {
  const value = construct({cause:{name:'ReferenceError',message:'oops'}})
  assert.deepEqual({message:value.message,reason:value.reason,cause:value.cause,stackFirst:value.stackFirst,string:value.string}, {message:'oops',reason:'oops',cause:{name:'ReferenceError',message:'oops'},stackFirst:'ReferenceError: oops',string:'1:1: oops'})
})
test('Error cause can be combined with origin', () => {
  const value = construct({cause:{name:'Error',message:'bad'},second:'src:rule'})
  assert.deepEqual([value.source,value.ruleId,value.cause.message], ['src','rule','bad'])
})
test('cause option is retained for a string reason', () => {
  const value = construct({reason:'wrapped',second:{cause:{name:'Error',message:'inner'}}})
  assert.deepEqual([value.message,value.cause], ['wrapped',{name:'Error',message:'inner'}])
})
test('place option supports a point', () => assert.deepEqual(construct({reason:'x',second:{place:{line:8,column:9}}}).place, {line:8,column:9}))
test('place option supports a position', () => assert.equal(construct({reason:'x',second:{place:{start:{line:8,column:9},end:{line:8,column:10}}}}).name, '8:9-8:10'))
test('well-known metadata starts undefined', () => {
  const value = construct({reason:'x'})
  assert.deepEqual([value.actual,value.expected,value.note,value.url], [undefined,undefined,undefined,undefined])
})
test('source and rule options may be independently supplied', () => assert.deepEqual([construct({reason:'x',second:{source:'s'}}).source,construct({reason:'x',second:{ruleId:'r'}}).ruleId], ['s','r']))
test('multiline reason is preserved', () => assert.deepEqual([construct({reason:'foo\nbar'}).message,construct({reason:'foo\nbar'}).string], ['foo\nbar','1:1: foo\nbar']))
test('null second argument is harmless', () => assert.equal(construct({reason:'x',second:null}).string, '1:1: x'))
test('null origin is harmless', () => assert.equal(construct({reason:'x',origin:null}).ruleId, undefined))
test('input remains unchanged after construction', () => assert.equal(construct({reason:'x',second:{type:'x',position:{start:{line:1,column:1},end:{line:1,column:2}}}}).inputUnchanged, true))
test('repeated construction is deterministic', () => {
  const request = {reason:'x',second:{start:{line:2,column:3},end:{line:2,column:4}}}
  assert.deepEqual(construct(request), construct(request))
})
test('undefined-style omitted options use defaults', () => assert.deepEqual([construct({reason:'x'}).line,construct({reason:'x'}).column,construct({reason:'x'}).place], [undefined,undefined,undefined]))
test('origin with an empty rule is normalized to undefined', () => assert.equal(construct({reason:'x',second:'source:'}).ruleId, undefined))
test('origin colon split preserves later colons in rule', () => assert.deepEqual([construct({reason:'x',second:'source:rule:detail'}).source,construct({reason:'x',second:'source:rule:detail'}).ruleId], ['source','rule:detail']))
test('node position can be a point-like position fallback', () => assert.deepEqual(construct({reason:'x',second:{type:'x',position:{line:3,column:4}}}).place, {line:3,column:4}))
test('file is always the empty string by default', () => assert.equal(construct({reason:'x'}).file, ''))
test('fatal is informationally undefined by default', () => assert.equal(construct({reason:'x'}).fatal, undefined))
test('string form uses the formatted name', () => assert.equal(construct({reason:'x',second:{line:10,column:2}}).string, '10:2: x'))
test('ancestor option preserves array length', () => assert.equal(construct({reason:'x',second:{ancestors:[{type:'a'},{type:'b'}]}}).ancestorsLength, 2))
test('constructor remains synchronous', () => assert.equal(typeof construct({reason:'x'}).string, 'string'))
