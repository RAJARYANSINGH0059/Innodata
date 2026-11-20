import {test} from 'node:test';
import assert from 'node:assert/strict';
import is, {assert as isAssert} from '../../source/index.ts';

test('existing string predicates unchanged', () => {
	assert.strictEqual(is.string('é'), true);
	assert.strictEqual(is.emptyString(''), true);
	assert.strictEqual(is.whitespaceString(' '), true);
	assert.strictEqual(is.nonEmptyString('é'), true);
	assert.strictEqual(is.numericString('12'), true);
});

test('existing assertion message format unchanged', () => {
	assert.throws(() => {
		isAssert.whitespaceString('x');
	}, {name: 'TypeError', message: 'Expected value which is `whitespace string`, received value of type `string`.'});
});

test('any/all combinators still work with existing predicates', () => {
	assert.strictEqual(is.any(is.string, 1, 'a'), true);
	assert.strictEqual(is.all(is.string, 'a', 1), false);
});
