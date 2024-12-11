import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from unified_logs import UnifiedLogReader

class LogAggregator:
    """Aggregates logs from multiple sources into a single JSON file."""

    def __init__(
        self,
        aws_region: str = 'us-east-1',
        aws_profile: str = None
    ):
        self.reader = UnifiedLogReader(
            aws_region=aws_region,
            aws_profile=aws_profile
        )

    def collect_local_logs(
        self,
        log_paths: List[str],
        is_json: bool = False
    ) -> List[Dict[str, Any]]:
        """Collect logs from local files."""
        logs = []
        
        for path in log_paths:
            try:
                entries = list(self.reader.get_local_logs(
                    log_path=path,
                    is_json=is_json
                ))
                
                logs.extend([{
                    'source': 'local',
                    'file_path': str(path),
                    'timestamp': datetime.now().isoformat(),
                    'content': entry
                } for entry in entries])
                
            except Exception as e:
                logs.append({
                    'source': 'local',
                    'file_path': str(path),
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                })
                
        return logs

    def collect_cloud_logs(
        self,
        log_groups: List[str],
        hours_back: int = 1
    ) -> List[Dict[str, Any]]:
        """Collect logs from CloudWatch."""
        logs = []
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        for group in log_groups:
            try:
                entries = list(self.reader.get_cloud_logs(
                    log_group=group,
                    start_time=start_time,
                    end_time=end_time
                ))
                
                logs.extend([{
                    'source': 'cloudwatch',
                    'log_group': group,
                    'timestamp': entry.timestamp.isoformat(),
                    'stream': entry.log_stream,
                    'content': entry.message
                } for entry in entries])
                
            except Exception as e:
                logs.append({
                    'source': 'cloudwatch',
                    'log_group': group,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                })
                
        return logs

    def aggregate_logs(
        self,
        local_paths: List[str],
        cloud_groups: List[str],
        output_file: str,
        hours_back: int = 1,
        local_is_json: bool = False
    ) -> None:
        """
        Aggregate logs from all sources and save to a JSON file.
        
        Args:
            local_paths: List of local log file paths
            cloud_groups: List of CloudWatch log group names
            output_file: Path to save the aggregated JSON file
            hours_back: Hours of logs to retrieve from CloudWatch
            local_is_json: Whether local logs are in JSON format
        """
        all_logs = []
        
        # Collect local logs
        if local_paths:
            all_logs.extend(self.collect_local_logs(
                log_paths=local_paths,
                is_json=local_is_json
            ))
            
        # Collect cloud logs
        if cloud_groups:
            all_logs.extend(self.collect_cloud_logs(
                log_groups=cloud_groups,
                hours_back=hours_back
            ))
            
        # Save to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                'aggregated_at': datetime.now().isoformat(),
                'logs': all_logs
            }, f, indent=2) 