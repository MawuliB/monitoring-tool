import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path
from log_storage import LogStorage

class LogAnalyzer:
    """Analyzes logs and generates reports with visualizations."""
    
    def __init__(self, db_path: str = 'logs.db'):
        self.storage = LogStorage(db_path)
        
    def generate_summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        source_type: Optional[str] = None
    ) -> Dict:
        """Generate a summary of log data."""
        logs = self.storage.query_logs(
            start_time=start_time,
            end_time=end_time,
            source_type=source_type,
            limit=10000  # Increased limit for analysis
        )
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(logs)
        if df.empty:
            return {"error": "No logs found for the specified period"}
            
        # Convert timestamp strings to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        summary = {
            "period": {
                "start": df['timestamp'].min().isoformat(),
                "end": df['timestamp'].max().isoformat()
            },
            "total_logs": len(df),
            "by_source": df['source_type'].value_counts().to_dict(),
            "by_level": df['level'].value_counts().to_dict(),
            "logs_per_hour": df.groupby(df['timestamp'].dt.hour)['id'].count().to_dict(),
            "recent_errors": df[df['level'].str.upper() == 'ERROR'].tail(5)[['timestamp', 'message']].to_dict('records')
        }
        
        return summary
    
    def export_summary(
        self,
        summary: Dict,
        format: str = 'json',
        output_dir: str = 'reports'
    ) -> str:
        """Export summary to file."""
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format.lower() == 'json':
            output_path = f"{output_dir}/log_summary_{timestamp}.json"
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)
        else:  # CSV
            output_path = f"{output_dir}/log_summary_{timestamp}.csv"
            df = pd.DataFrame([summary])
            df.to_csv(output_path, index=False)
            
        return output_path
    
    def create_visualizations(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        output_dir: str = 'reports'
    ):
        """Create various visualizations of log data."""
        logs = self.storage.query_logs(
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )
        
        df = pd.DataFrame(logs)
        if df.empty:
            return
            
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        Path(output_dir).mkdir(exist_ok=True)
        
        # 1. Logs by Source Type
        fig_sources = px.pie(
            df,
            names='source_type',
            title='Log Distribution by Source'
        )
        fig_sources.write_html(f"{output_dir}/logs_by_source.html")
        
        # 2. Logs Over Time
        df_time = df.groupby(df['timestamp'].dt.date).size().reset_index()
        df_time.columns = ['date', 'count']
        
        fig_timeline = px.line(
            df_time,
            x='date',
            y='count',
            title='Log Volume Over Time'
        )
        fig_timeline.write_html(f"{output_dir}/logs_timeline.html")
        
        # 3. Log Levels Distribution (Fixed)
        level_counts = df['level'].value_counts().reset_index()
        level_counts.columns = ['level', 'count']
        
        fig_levels = px.bar(
            level_counts,
            x='level',
            y='count',
            title='Distribution of Log Levels'
        )
        fig_levels.write_html(f"{output_dir}/log_levels.html")
        
        # 4. Heatmap of Log Activity
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day_name()
        
        activity_matrix = pd.crosstab(df['day'], df['hour'])
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=activity_matrix.values,
            x=activity_matrix.columns,
            y=activity_matrix.index,
            colorscale='Viridis'
        ))
        fig_heatmap.update_layout(
            title='Log Activity Heatmap by Hour and Day',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week'
        )
        fig_heatmap.write_html(f"{output_dir}/activity_heatmap.html")

def main():
    """Generate log analysis report and visualizations."""
    analyzer = LogAnalyzer()
    
    # Set time range for analysis
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)  # Last 7 days
    
    # Generate summary
    summary = analyzer.generate_summary(
        start_time=start_time,
        end_time=end_time
    )
    
    # Export summary
    json_path = analyzer.export_summary(summary, format='json')
    print(f"Summary exported to: {json_path}")
    
    # Create visualizations
    analyzer.create_visualizations(
        start_time=start_time,
        end_time=end_time
    )
    print(f"Visualizations created in: reports/")
    
    # Print key metrics
    print("\nKey Metrics:")
    print(f"Total Logs: {summary['total_logs']}")
    print("\nLogs by Source:")
    for source, count in summary['by_source'].items():
        print(f"  {source}: {count}")
    print("\nRecent Errors:")
    for error in summary['recent_errors']:
        print(f"  {error['timestamp']}: {error['message'][:100]}...")

if __name__ == '__main__':
    main() 