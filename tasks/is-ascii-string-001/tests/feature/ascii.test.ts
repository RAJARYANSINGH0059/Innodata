import {test} from 'node:test';
import assert from 'node:assert/strict';
import * as api from '../../source/index.ts';

const is = api.default;
const isAssert = api.assert;
// Named exports are read lazily so that a missing export fails the AC7 test instead of failing to load the whole file.
const named = api as unknown as Record<string, (value: unknown, message?: string) => unknown>;

test('AC1 ascii strings are true', () => {
	for (const value of ['abc', '', '\0', '\n\t', '~', '\u007F', 'Hello, World! 123']) {
		assert.strictEqual(is.asciiString(value), true, JSON.stringify(value));
	}
});

test('AC2 non-ascii characters make it false', () => {
	for (const value of ['é', '\u0080', '日本', '😀', 'abc😀', 'aÿb', 'café']) {
		assert.strictEqual(is.asciiString(value), false, JSON.stringify(value));
	}
});

test('AC3 non-strings are false', () => {
	for (const value of [1, null, undefined, ['a'], new String('a'), {}, true, Symbol('a')]) { // eslint-disable-line no-new-wrappers
		assert.strictEqual(is.asciiString(value), false);
	}
});

test('AC4 assert passes for ascii and throws TypeError otherwise', () => {
	assert.doesNotThrow(() => {
		isAssert.asciiString('abc');
	});
	assert.doesNotThrow(() => {
		isAssert.asciiString('');
	});
	assert.throws(() => {
		isAssert.asciiString('é');
	}, {name: 'TypeError', message: /ASCII string/});
	assert.throws(() => {
		isAssert.asciiString(5);
	}, {name: 'TypeError', message: /ASCII string/});
});

test('AC4 default message format matches other assertions', () => {
	assert.throws(() => {
		isAssert.asciiString('é');
	}, {message: 'Expected value which is `ASCII string`, received value of type `string`.'});
});

test('AC5 custom message is used verbatim', () => {
	assert.throws(() => {
		isAssert.asciiString('é', 'custom msg');
	}, {name: 'TypeError', message: 'custom msg'});
});

test('AC6 combinators work and describe the type', () => {
	assert.strictEqual(is.any(is.asciiString, 'é', 'a'), true);
	assert.strictEqual(is.any(is.asciiString, 'é', 5), false);
	assert.strictEqual(is.all(is.asciiString, 'a', 'b'), true);
	assert.strictEqual(is.all(is.asciiString, 'a', 'é'), false);
	assert.doesNotThrow(() => {
		isAssert.any(is.asciiString, 'é', 'a');
	});
	assert.throws(() => {
		isAssert.any(is.asciiString, 'é', 5);
	}, {name: 'TypeError', message: /ASCII string/});
});

test('AC7 named exports behave like members', () => {
	assert.strictEqual(typeof named.isAsciiString, 'function');
	assert.strictEqual(typeof named.assertAsciiString, 'function');
	assert.strictEqual(named.isAsciiString('abc'), true);
	assert.strictEqual(named.isAsciiString('é'), false);
	assert.strictEqual(is.asciiString, named.isAsciiString);
	assert.strictEqual(isAssert.asciiString, named.assertAsciiString);
	assert.throws(() => {
		named.assertAsciiString('é');
	}, TypeError);
});
