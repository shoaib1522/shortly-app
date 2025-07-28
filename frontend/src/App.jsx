// frontend/src/App.jsx
import { useState } from 'react';
import './App.css';

// For local dev, this points to our FastAPI server.
// In the unified Docker container, this will be a relative path.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [originalUrl, setOriginalUrl] = useState('');
  const [shortUrl, setShortUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleShorten = async (e) => {
    e.preventDefault();
    setError('');
    setShortUrl('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/shorten`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: originalUrl }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Use the detail message from FastAPI's HTTPException
        throw new Error(data.detail || 'Invalid URL or server error.');
      }
      
      setShortUrl(data.short_url);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header>
        <h1>Shortly</h1>
        <p>Your friendly, fast, and reliable URL Shortener</p>
      </header>
      <main>
        <form onSubmit={handleShorten}>
          <input
            type="url"
            value={originalUrl}
            onChange={(e) => setOriginalUrl(e.target.value)}
            placeholder="Enter a long URL to make it short..."
            required
            aria-label="URL to shorten"
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Shortening...' : 'Shorten!'}
          </button>
        </form>

        {shortUrl && (
          <div className="result">
            <p>Success! Here is your short URL:</p>
            <a href={shortUrl} target="_blank" rel="noopener noreferrer">
              {shortUrl}
            </a>
          </div>
        )}

        {error && <p className="error">Error: {error}</p>}
      </main>
    </div>
  );
}

export default App;