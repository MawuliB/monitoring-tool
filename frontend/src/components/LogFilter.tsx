import React, { useState } from 'react';

interface LogFilterProps {
    onFilterChange: (filters: any) => void;
}

export const LogFilter: React.FC<LogFilterProps> = ({ onFilterChange }) => {
    const [keyword, setKeyword] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onFilterChange({ keyword });
    };

    return (
        <form onSubmit={handleSubmit} className="log-filter">
            <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Search logs..."
            />
            <button type="submit">Search</button>
        </form>
    );
};