from log_analysis import LogAnalyzer
from datetime import datetime, timedelta

analyzer = LogAnalyzer()

# Generate report for last 24 hours
end_time = datetime.now()
start_time = end_time - timedelta(hours=24)

# Generate and export summary
summary = analyzer.generate_summary(start_time=start_time)
json_path = analyzer.export_summary(summary)

# Create visualizations
analyzer.create_visualizations(start_time=start_time)