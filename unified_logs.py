from typing import Iterator, Dict, Optional, Union
from datetime import datetime
from pathlib import Path
from cloud import CloudWatchLogsReader, LogEvent
from log_reader import LogReader

class UnifiedLogReader:
    """A unified interface for retrieving logs from multiple sources."""

    def __init__(
        self,
        aws_region: Optional[str] = None,
        aws_profile: Optional[str] = None
    ):
        """
        Initialize the unified log reader.

        Args:
            aws_region: AWS region for CloudWatch logs
            aws_profile: AWS profile name for credentials
        """
        self.cloud_reader = CloudWatchLogsReader(
            region_name=aws_region,
            profile_name=aws_profile
        )
        
    def get_local_logs(
        self,
        log_path: Union[str, Path],
        pattern: Optional[str] = None,
        is_json: bool = False
    ) -> Iterator[Dict]:
        """
        Retrieve logs from local files.

        Args:
            log_path: Path to log file
            pattern: Regex pattern for parsing text logs
            is_json: Whether the log file is in JSON format

        Returns:
            Iterator of log entries
        """
        reader = LogReader(log_path)
        if is_json:
            return reader.read_json()
        return reader.read_plain_text(pattern)

    def get_cloud_logs(
        self,
        log_group: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        filter_pattern: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Iterator[LogEvent]:
        """
        Retrieve logs from CloudWatch.

        Args:
            log_group: CloudWatch log group name
            start_time: Start time for log retrieval
            end_time: End time for log retrieval
            filter_pattern: CloudWatch filter pattern
            limit: Maximum number of events to retrieve

        Returns:
            Iterator of CloudWatch log events
        """
        return self.cloud_reader.get_log_events(
            log_group_name=log_group,
            start_time=start_time,
            end_time=end_time,
            filter_pattern=filter_pattern,
            limit=limit
        )

    def tail_logs(
        self,
        source: str,
        **kwargs
    ) -> Iterator[Union[Dict, LogEvent]]:
        """
        Tail logs from either local or cloud source.

        Args:
            source: Either 'local' or 'cloud'
            **kwargs: Source-specific parameters

        Returns:
            Iterator of log entries
        """
        if source.lower() == 'cloud':
            return self.cloud_reader.tail_logs(**kwargs)
        elif source.lower() == 'local':
            # Implement local file tailing if needed
            raise NotImplementedError("Local file tailing not implemented yet")
        else:
            raise ValueError("Source must be either 'local' or 'cloud'") 