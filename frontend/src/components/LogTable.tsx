import React from 'react';

interface LogTableProps {
    logs: any[];
}

export const LogTable: React.FC<LogTableProps> = ({ logs }) => {
    return (
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
                {logs.map((log, index) => (
                    <tr key={index}>
                        <td>{log.timestamp}</td>
                        <td>{log.message}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}; 