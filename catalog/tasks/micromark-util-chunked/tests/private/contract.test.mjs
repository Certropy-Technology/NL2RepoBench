import assert from 'node:assert/strict'
import test from 'node:test'
import {invoke} from './test_client.mjs'

const splice = (list, start, remove, items) => invoke({operation:'splice', list, start, remove, items})
const push = (list, items) => invoke({operation:'push', list, items})

test('public-export::splice-is-callable', () => assert.deepEqual(splice([1], 0, 0, []).list, [1]))
test('public-export::push-is-callable', () => assert.deepEqual(push([1], [2]).result, [1, 2]))

test('splice-semantics::returns-undefined', () => assert.equal(splice([1], 0, 0, []).result, undefined))
test('splice-semantics::no-delete-no-insert', () => assert.deepEqual(splice([5,4,3], 0, 0, []).list, [5,4,3]))
test('splice-semantics::delete-and-insert', () => assert.deepEqual(splice([5,4,3,2,1], 1, 2, [9,99,999]).list, [5,9,99,999,2,1]))
test('splice-semantics::negative-start', () => assert.deepEqual(splice([5,4,3,2,1], -3, 2, [9]).list, [5,4,9,1]))
test('splice-semantics::too-negative-start-clamps-zero', () => assert.deepEqual(splice([1,2,3], -100, 1, [8]).list, [8,2,3]))
test('splice-semantics::large-positive-start-clamps-end', () => assert.deepEqual(splice([1,2], 100, 3, [3]).list, [1,2,3]))
test('splice-semantics::negative-remove-is-zero', () => assert.deepEqual(splice([1,2], 1, -4, [7]).list, [1,7,2]))
test('splice-semantics::remove-past-end', () => assert.deepEqual(splice([1,2,3], 1, 99, []).list, [1]))
test('splice-semantics::insertion-order', () => assert.deepEqual(splice(['a','d'], 1, 0, ['b','c']).list, ['a','b','c','d']))
test('splice-semantics::mixed-json-values', () => assert.deepEqual(splice([0], 1, 0, [null,{x:1},[2]]).list, [0,null,{x:1},[2]]))

test('push-semantics::appends-items', () => assert.deepEqual(push([1,2], [3,4]).result, [1,2,3,4]))
test('push-semantics::nonempty-returns-list', () => assert.equal(push([1], [2]).sameAsList, true))
test('push-semantics::nonempty-does-not-return-items', () => assert.equal(push([1], [2]).sameAsItems, false))
test('push-semantics::empty-returns-items', () => assert.equal(push([], [2]).sameAsItems, true))
test('push-semantics::empty-does-not-return-list', () => assert.equal(push([], [2]).sameAsList, false))
test('push-semantics::empty-items', () => assert.deepEqual(push([1], []).result, [1]))

test('large-arrays::splice-10001-items', () => {const values=Array.from({length:10001},(_,i)=>i); const r=splice([42,43],1,0,values).list; assert.equal(r.length,10003); assert.deepEqual(r.slice(0,3),[42,0,1]); assert.deepEqual(r.slice(-3),[9999,10000,43])})
test('large-arrays::splice-removes-before-chunks', () => {const values=Array.from({length:10001},(_,i)=>i); const r=splice([42,10,11,43],1,2,values).list; assert.equal(r.length,10003); assert.equal(r[0],42); assert.equal(r.at(-1),43)})
test('large-arrays::push-preserves-order', () => {const values=Array.from({length:10001},(_,i)=>i); const r=push([-1],values).result; assert.equal(r.length,10002); assert.equal(r[0],-1); assert.equal(r.at(-1),10000)})

test('determinism::splice-repeatable', () => assert.deepEqual(splice([1,2,3],1,1,[9]).list, splice([1,2,3],1,1,[9]).list))
test('determinism::push-repeatable', () => assert.deepEqual(push([1],[2,3]).result, push([1],[2,3]).result))
test('determinism::input-items-not-reordered', () => {const items=[3,2,1]; const r=push([0],items); assert.deepEqual(r.result,[0,3,2,1])})
