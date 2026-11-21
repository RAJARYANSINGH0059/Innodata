import test from 'node:test';
import assert from 'node:assert/strict';
import * as api from '../../source/index.ts';

const is = api.default as any;
const a = api.assert as any;

const asciiYes: unknown[] = ['abc', '', '\0', '\n\t', '~', '\u007F', 'Hello, World! 123', ' ', '\r\n', 'a'.repeat(10_000)];
const asciiNo: unknown[] = ['é', '\u0080', '日本', '😀', 'abc😀', 'aÿb', 'abÿ', 'xĀ', '\uD83D', 'a '];
const nonStrings: unknown[] = [1, 0, null, undefined, ['a'], new String('a'), new String(''), {}, true, Symbol('a'), 1n, () => 'a', new Uint8Array([97]), /a/];

test('is.asciiString exists on default is object', () => {
	assert.equal(typeof is.asciiString, 'function');
});

test('AC1 / req 2: ASCII strings are true', () => {
	for (const value of asciiYes) {
		assert.equal(is.asciiString(value), true, JSON.stringify(value)?.slice(0, 40));
	}
});

test('every single code unit 0..127 is ASCII, 128..255 is not', () => {
	for (let code = 0; code < 128; code++) {
		assert.equal(is.asciiString(String.fromCharCode(code)), true, `U+${code.toString(16)}`);
		assert.equal(is.asciiString(`a${String.fromCharCode(code)}b`), true);
	}

	for (let code = 128; code < 256; code++) {
		assert.equal(is.asciiString(String.fromCharCode(code)), false, `U+${code.toString(16)}`);
		assert.equal(is.asciiString(`abc${String.fromCharCode(code)}`), false);
		assert.equal(is.asciiString(`${String.fromCharCode(code)}abc`), false);
	}
});

test('AC2 / req 3: non-ASCII strings are false', () => {
	for (const value of asciiNo) {
		assert.equal(is.asciiString(value), false, JSON.stringify(value));
	}
});

test('AC3 / req 1: non-strings are false', () => {
	for (const value of nonStrings) {
		assert.equal(is.asciiString(value), false, String(typeof value));
	}
});

test('is.asciiString returns strictly boolean', () => {
	assert.equal(typeof is.asciiString('a'), 'boolean');
	assert.equal(typeof is.asciiString('é'), 'boolean');
	assert.equal(typeof is.asciiString(1), 'boolean');
});

test('AC7: named export isAsciiString behaves like is.asciiString', () => {
	const fn = (api as any).isAsciiString;
	assert.equal(typeof fn, 'function');
	for (const value of [...asciiYes, ...asciiNo, ...nonStrings]) {
		assert.equal(fn(value), is.asciiString(value));
	}

	assert.equal(fn('abc'), true);
	assert.equal(fn('é'), false);
	assert.equal(fn(1), false);
});

test('AC4: assert.asciiString passes for ASCII', () => {
	assert.equal(typeof a.asciiString, 'function');
	for (const value of asciiYes) {
		assert.doesNotThrow(() => {
			a.asciiString(value);
		});
	}
});

test('AC4: assert.asciiString throws TypeError mentioning ASCII string', () => {
	assert.equal(typeof a.asciiString, 'function');
	for (const value of [...asciiNo, ...nonStrings]) {
		assert.throws(() => {
			a.asciiString(value);
		}, (error: unknown) => error instanceof TypeError && error.message.includes('ASCII string'));
	}
});

test('AC4: default message names expected type like other assertions', () => {
	assert.equal(typeof a.asciiString, 'function');
	let asciiMessage = '';
	let otherMessage = '';
	try {
		a.asciiString('é');
	} catch (error: any) {
		asciiMessage = error.message;
	}

	try {
		a.emptyString('é');
	} catch (error: any) {
		otherMessage = error.message;
	}

	assert.match(asciiMessage, /Expected value which is `ASCII string`/);
	assert.match(otherMessage, /Expected value which is `empty string`/);
});

test('AC5: custom message is used verbatim', () => {
	assert.equal(typeof a.asciiString, 'function');
	assert.throws(() => {
		a.asciiString('é', 'custom message here');
	}, (error: unknown) => error instanceof TypeError && error.message === 'custom message here');
	assert.throws(() => {
		a.asciiString(5, 'nope');
	}, (error: unknown) => error instanceof TypeError && error.message === 'nope');
	assert.doesNotThrow(() => {
		a.asciiString('abc', 'unused');
	});
});

test('AC7: named export assertAsciiString', () => {
	const fn = (api as any).assertAsciiString;
	assert.equal(typeof fn, 'function');
	assert.doesNotThrow(() => {
		fn('abc');
	});
	assert.doesNotThrow(() => {
		fn('');
	});
	assert.throws(() => {
		fn('é');
	}, (error: unknown) => error instanceof TypeError && error.message.includes('ASCII string'));
	assert.throws(() => {
		fn(1);
	}, TypeError);
	assert.throws(() => {
		fn('😀', 'msg!');
	}, (error: unknown) => error instanceof TypeError && error.message === 'msg!');
});

test('AC6: is.any with is.asciiString', () => {
	assert.equal(typeof is.asciiString, 'function');
	assert.equal(is.any(is.asciiString, 'abc'), true);
	assert.equal(is.any(is.asciiString, 'é', 'abc'), true);
	assert.equal(is.any(is.asciiString, 'é', 1), false);
	assert.equal(is.any([is.asciiString, is.number], 5), true);
	assert.equal(is.any([is.asciiString, is.number], 'é'), false);
	assert.equal(is.any(is.asciiString, '😀'), false);
});

test('AC6: is.all with is.asciiString', () => {
	assert.equal(typeof is.asciiString, 'function');
	assert.equal(is.all(is.asciiString, 'a', 'b', ''), true);
	assert.equal(is.all(is.asciiString, 'a', 'é'), false);
	assert.equal(is.all(is.asciiString, 'a', 1), false);
	assert.equal(is.all(is.asciiString, '\0', '~'), true);
});

test('AC6: assert.any with is.asciiString passes and fails with ASCII string in message', () => {
	assert.equal(typeof is.asciiString, 'function');
	assert.doesNotThrow(() => {
		a.any(is.asciiString, 'abc');
	});
	assert.doesNotThrow(() => {
		a.any(is.asciiString, 'é', 'abc');
	});
	assert.throws(() => {
		a.any(is.asciiString, 'é');
	}, (error: unknown) => error instanceof TypeError && error.message.includes('ASCII string'));
	assert.throws(() => {
		a.any(is.asciiString, 1, null);
	}, (error: unknown) => error instanceof TypeError && error.message.includes('ASCII string'));
});

test('assert.any with array of predicates lists ASCII string', () => {
	assert.equal(typeof is.asciiString, 'function');
	assert.throws(() => {
		a.any([is.asciiString, is.number], 'é');
	}, (error: unknown) => error instanceof TypeError && error.message.includes('ASCII string') && error.message.includes('number'));
});

test('assert.all with is.asciiString', () => {
	assert.equal(typeof is.asciiString, 'function');
	assert.doesNotThrow(() => {
		a.all(is.asciiString, 'a', 'b');
	});
	assert.throws(() => {
		a.all(is.asciiString, 'a', 'é');
	}, TypeError);
});
