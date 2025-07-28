// frontend/src/test/setup.js
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// This automatically runs after each test, clearing the JSDOM environment.
afterEach(() => {
  cleanup();
});