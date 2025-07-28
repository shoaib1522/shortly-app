// frontend/src/test/App.test.jsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from '../App';

// We must mock the global 'fetch' function for our unit test.
beforeEach(() => {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve([]), // Return an empty array for the initial load
    })
  );
});

describe('App', () => {
  it('renders the main heading and form elements', async () => {
    render(<App />);
    
    // Check if the main heading is on the page
    const heading = await screen.findByRole('heading', { name: /Shortly/i });
    expect(heading).toBeInTheDocument();

    // Check if the input field is present
    const input = screen.getByPlaceholderText(/Enter a long URL/i);
    expect(input).toBeInTheDocument();
    
    // Check if the button is present
    const button = screen.getByRole('button', { name: /Shorten!/i });
    expect(button).toBeInTheDocument();
  });
});