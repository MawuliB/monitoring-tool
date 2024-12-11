import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LogViewer } from './components/LogViewer';
import { PlatformSelector } from './components/PlatformSelector';
import { useState } from 'react';
import './App.css';
import { PlatformCredentials } from './components/PlatformCredentials';

const queryClient = new QueryClient();

function App() {
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app-container">
        <header>
          <h1>Log Management System</h1>
        </header>
        
        <main>
          <PlatformSelector 
            onPlatformSelect={setSelectedPlatform} 
            selectedPlatform={selectedPlatform} 
          />
          
          {selectedPlatform && (
            <>
              <section className="credentials-section">
                <h2>Platform Credentials</h2>
                <PlatformCredentials platform={selectedPlatform} />
              </section>
              
              <section className="logs-section">
                <h2>Logs</h2>
                <LogViewer platform={selectedPlatform} />
              </section>
            </>
          )}
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
