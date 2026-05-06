import pandas as pd
import io

class VersaData:
    """A class to parse and handle VersaStudio .par files."""
    def __init__(self, filepath):
        self.filepath = filepath
        self.metadata = {}
        self.data = pd.DataFrame()
        self._parse()

    def _parse(self):
        data_lines = []
        headers = []
        current_section = None
        
        with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line: 
                    continue
                
                # Detect start of a section
                if line.startswith('<') and line.endswith('>') and not line.startswith('</') and not line.startswith('<?'):
                    current_section = line[1:-1]
                    if current_section not in self.metadata:
                        self.metadata[current_section] = {}
                    continue
                
                # Detect end of a section
                if line.startswith('</') and line.endswith('>'):
                    current_section = None
                    continue
                
                # Process contents
                if current_section:
                    if current_section.startswith('Segment'):
                        if line.startswith('Definition='):
                            raw_headers = line.split('=', 1)[1].split(',')
                            headers = [h.strip() for h in raw_headers]
                        elif '=' in line:
                            key, val = line.split('=', 1)
                            self.metadata[current_section][key.strip()] = val.strip()
                        else:
                            data_lines.append(line)
                            
                    elif current_section == 'DockingLayout':
                        continue
                        
                    elif '=' in line:
                        key, val = line.split('=', 1)
                        self.metadata[current_section][key.strip()] = val.strip()

        # Convert to DataFrame
        if data_lines:
            data_str = '\n'.join(data_lines)
            self.data = pd.read_csv(io.StringIO(data_str), header=None, names=headers)

    def get_segments_list(self):
        """Returns a list of unique segment numbers."""
        if 'Segment #' in self.data.columns:
            return self.data['Segment #'].unique().tolist()
        return []

    def get_segment(self, segment_number):
        """Returns a DataFrame of just the requested segment."""
        if 'Segment #' not in self.data.columns:
            raise ValueError("No 'Segment #' column found.")
            
        segment_data = self.data[self.data['Segment #'] == segment_number].copy()
        return segment_data

    def get_combined_segments(self, segments=None):
        """Returns a DataFrame combining the specified segments.
        
        Args:
            segments (list of int, tuple of (start, end), range, or None): 
                - List of segment numbers to combine (e.g., [1, 2, 3])
                - Tuple of (start, end) for inclusive range (e.g., (2, 44) for segments 2 to 44)
                - range object (e.g., range(2, 45))
                - If None, returns all segments combined.
        
        Returns:
            pd.DataFrame: Combined DataFrame with data from the specified segments.
        """
        if segments is None:
            return self.data.copy()
        
        # Handle different input types
        if isinstance(segments, tuple) and len(segments) == 2 and all(isinstance(x, int) for x in segments):
            start, end = segments
            segments = range(start, end + 1)
        elif isinstance(segments, range):
            pass  # already a range
        elif isinstance(segments, list):
            pass  # already a list
        else:
            raise ValueError("segments must be a list, tuple (start, end), range, or None")
        
        dfs = []
        for seg in segments:
            dfs.append(self.get_segment(seg))
        
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        else:
            return pd.DataFrame()

    def filter_data(self, conditions):
        """Filters the data DataFrame based on the given conditions.
        
        Args:
            conditions (dict): Dictionary where keys are column names and values are conditions.
                Conditions can be:
                - scalar: exact match (e.g., {'Segment #': 2})
                - tuple (min, max): inclusive range (e.g., {'E(V)': (-1.0, 1.0)})
                - callable: function that returns bool (e.g., {'Frequency(Hz)': lambda x: x > 0})
        
        Returns:
            pd.DataFrame: Filtered DataFrame.
        """
        df = self.data.copy()
        for column, condition in conditions.items():
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found in data")
            
            if callable(condition):
                mask = df[column].apply(condition)
            elif isinstance(condition, tuple) and len(condition) == 2:
                min_val, max_val = condition
                mask = (df[column] >= min_val) & (df[column] <= max_val)
            else:
                mask = df[column] == condition
            
            df = df[mask]
        
        return df

    def get_time_range_data(self, start_time, end_time, time_column='Elapsed Time(s)'):
        """Returns data within the specified time range.
        
        Args:
            start_time (float): Start time in seconds.
            end_time (float): End time in seconds.
            time_column (str): Name of the time column (default: 'Elapsed Time(s)').
        
        Returns:
            pd.DataFrame: Filtered DataFrame with data in the time range.
        """
        return self.filter_data({time_column: (start_time, end_time)})

    def get_summary_stats(self, group_by_segment=True):
        """Returns summary statistics of the data.
        
        Args:
            group_by_segment (bool): If True, group stats by segment number.
        
        Returns:
            pd.DataFrame: Summary statistics.
        """
        if group_by_segment and 'Segment #' in self.data.columns:
            return self.data.groupby('Segment #').describe()
        else:
            return self.data.describe()