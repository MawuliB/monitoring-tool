import React, { useState, useEffect } from 'react';
import { LogFilter } from './LogFilter';
import { LogTable } from './LogTable';
import { LogVisualizations } from './LogVisualizations';
import { fetchLogs } from '../api/logs';

interface LogViewerProps {
    platform: string;
}

export const LogViewer: React.FC<LogViewerProps> = ({ platform }) => {
    const [logs, setLogs] = useState([]);
    const [filters, setFilters] = useState({});
    const [view, setView] = useState<'table' | 'visual'>('table');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadLogs = async () => {
        try {
            setLoading(true);
            setError(null);
            const results = await fetchLogs({ ...filters, platform });
            setLogs(results);
        } catch (err) {
            setError('Failed to fetch logs');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadLogs();
    }, [platform]); // Reload when platform changes

    const handleFilterChange = async (newFilters: any) => {
        setFilters(newFilters);
        await loadLogs();
    };

    if (loading) return <div>Loading logs...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="log-viewer">
            <LogFilter onFilterChange={handleFilterChange} />
            
            <div className="view-controls">
                <button onClick={() => setView('table')}>Table View</button>
                <button onClick={() => setView('visual')}>Visualizations</button>
            </div>

            {view === 'table' ? (
                <LogTable logs={logs} />
            ) : (
                <LogVisualizations logs={logs} />
            )}
        </div>
    );
}; 