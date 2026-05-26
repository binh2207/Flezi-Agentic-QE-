import { test } from '../../fixtures';

test('harness smoke placeholder', async ({}, testInfo) => {
  testInfo.skip(
    true,
    'No smoke specs yet. Run harness-engineering to generate feature tests.',
  );
});
