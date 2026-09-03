import assert from 'node:assert/strict';
import test from 'node:test';
import {callCandidate} from './test_client.mjs';

const replace = (value, useFallback) => callCandidate('replaceSymbols', [value, {useFallback}]);

test('keeps ordinary text', () => {
	assert.equal(replace('plain text', true), 'plain text');
});

test('uses terminal-derived default mode for ordinary text', () => {
	assert.equal(callCandidate('replaceSymbols', ['ordinary text']), 'ordinary text');
});

test('keeps the empty string', () => {
	assert.equal(replace('', true), '');
});

test('replaces tick and info', () => {
	assert.equal(replace('✔ ℹ', true), '√ i');
});

test('replaces warning and cross', () => {
	assert.equal(replace('⚠ ✘', true), '‼ ×');
});

test('replaces small squares', () => {
	assert.equal(replace('◻ ◼', true), '□ ■');
});

test('replaces circles', () => {
	assert.equal(replace('◯ ◉ ◌ ◎', true), '( ) (*) ( ) ( )');
});

test('replaces circle variants', () => {
	assert.equal(replace('ⓞ ⓧ Ⓘ', true), '(○) (×) (│)');
});

test('replaces radio controls', () => {
	assert.equal(replace('◉ ◯', true), '(*) ( )');
});

test('replaces checkbox controls', () => {
	assert.equal(replace('☒ ☐ ⓧ Ⓘ', true), '[×] [ ] (×) (│)');
});

test('replaces pointers and outlined triangles', () => {
	assert.equal(replace('❯ △ ◀ ▶', true), '> ∆ ◄ ►');
});

test('replaces lozenges', () => {
	assert.equal(replace('◆ ◇', true), '♦ ◊');
});

test('replaces the hamburger symbol', () => {
	assert.equal(replace('☰', true), '≡');
});

test('replaces smiley and mustache', () => {
	assert.equal(replace('㋡ ෴', true), '☺ ┌─┐');
});

test('replaces star and play', () => {
	assert.equal(replace('★ ▶', true), '✶ ►');
});

test('replaces nodejs', () => {
	assert.equal(replace('⬢', true), '♦');
});

test('replaces uncommon fraction glyphs', () => {
	assert.equal(replace('⅐ ⅑ ⅒', true), '1/7 1/9 1/10');
});

test('leaves common symbols unchanged', () => {
	assert.equal(replace('█ ▓ ▒ ░ ▀ ▄ ▌ ▐ ■ ● ․ … › ▲ ▴ ▼ ▾ ◂ ▸ ⌂ ♥ ♪ ♫ ↑ ↓ ← → ↔ ↕ ≈ ≠ ≤ ≥ ≡ ∞', true), '█ ▓ ▒ ░ ▀ ▄ ▌ ▐ ■ ● ․ … › ▲ ▴ ▼ ▾ ◂ ▸ ⌂ ♥ ♪ ♫ ↑ ↓ ← → ↔ ↕ ≈ ≠ ≤ ≥ ≡ ∞');
});

test('leaves line-drawing symbols unchanged', () => {
	assert.equal(replace('─ ━ ═ ┌ ┐ └ ┘ ┼ ╋', true), '─ ━ ═ ┌ ┐ └ ┘ ┼ ╋');
});

test('replaces repeated occurrences', () => {
	assert.equal(replace('✔✔✔\n✘✘', true), '√√√\n××');
});

test('preserves multiline boundaries', () => {
	assert.equal(replace('start\n✔ middle\nend', true), 'start\n√ middle\nend');
});

test('does not interpret replacement text as a pattern', () => {
	assert.equal(replace('before ✔ after $1', true), 'before √ after $1');
});

test('explicit false preserves all main symbols', () => {
	assert.equal(replace('✔ ⚠ ✘ ☒ ★', false), '✔ ⚠ ✘ ☒ ★');
});

test('explicit true replaces all special symbols in one string', () => {
	assert.equal(replace('✔ ℹ ⚠ ✘ ◻ ◼ ◯ ◉ ⓞ ⓧ Ⓘ ☒ ☐ ❯ △ ◀ ▶ ◆ ◇ ☰ ㋡ ෴ ★ ▶ ⬢ ⅐ ⅑ ⅒', true), '√ i ‼ × □ ■ ( ) (*) (○) (×) (│) [×] [ ] > ∆ ◄ ► ♦ ◊ ≡ ☺ ┌─┐ ✶ ► ♦ 1/7 1/9 1/10');
});
