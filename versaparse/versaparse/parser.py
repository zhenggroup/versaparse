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