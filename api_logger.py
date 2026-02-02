import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class OpenAILogger:
    """Pretty logger for OpenAI API requests and responses"""
    
    def __init__(self, log_dir: str = "./api_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create a daily log file
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"openai_api_{today}.log"
        
    def _format_messages(self, messages: list) -> str:
        """Format messages array for readability"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # Truncate very long content for readability
            if len(content) > 500:
                content = content[:500] + f"... [truncated, total length: {len(content)}]"
            
            formatted.append(f"    [{role.upper()}]:\n{self._indent(content, 6)}")
        
        return "\n".join(formatted)
    
    def _indent(self, text: str, spaces: int) -> str:
        """Indent text by specified number of spaces"""
        indent = " " * spaces
        return "\n".join(indent + line for line in text.split("\n"))
    
    def _format_json(self, data: Any, indent: int = 2) -> str:
        """Format JSON data with indentation"""
        try:
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except:
            return str(data)
    
    def log_request(
        self,
        operation: str,
        model: str,
        messages: Optional[list] = None,
        input_text: Optional[str] = None,
        **kwargs
    ) -> str:
        """Log an API request and return a request ID for correlation"""
        request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        log_entry = [
            "=" * 100,
            f"🔵 REQUEST [{request_id}] - {timestamp}",
            "=" * 100,
            f"Operation: {operation}",
            f"Model: {model}",
        ]
        
        # Add operation-specific details
        if messages:
            log_entry.append("\n📨 Messages:")
            log_entry.append(self._format_messages(messages))
        
        if input_text:
            truncated = input_text[:500]
            if len(input_text) > 500:
                truncated += f"... [truncated, total length: {len(input_text)}]"
            log_entry.append(f"\n📝 Input Text:\n{self._indent(truncated, 2)}")
        
        # Add any additional parameters
        if kwargs:
            log_entry.append(f"\n⚙️  Parameters:")
            log_entry.append(self._indent(self._format_json(kwargs), 2))
        
        log_entry.append("\n")
        
        # Write to file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n".join(log_entry) + "\n")
        
        return request_id
    
    def log_response(
        self,
        request_id: str,
        response: Any,
        error: Optional[Exception] = None
    ):
        """Log an API response correlated with its request"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        log_entry = [
            f"🟢 RESPONSE [{request_id}] - {timestamp}",
            "-" * 100,
        ]
        
        if error:
            log_entry.append(f"❌ ERROR: {str(error)}")
            log_entry.append(f"Error Type: {type(error).__name__}")
        else:
            # Handle different response types
            if hasattr(response, 'choices'):
                # Chat completion response
                log_entry.append(f"Model: {response.model}")
                log_entry.append(f"Usage:")
                log_entry.append(f"  - Prompt tokens: {response.usage.prompt_tokens}")
                log_entry.append(f"  - Completion tokens: {response.usage.completion_tokens}")
                log_entry.append(f"  - Total tokens: {response.usage.total_tokens}")
                
                for i, choice in enumerate(response.choices):
                    log_entry.append(f"\n💬 Choice {i}:")
                    content = choice.message.content
                    
                    # Try to pretty-print JSON responses
                    if content and content.strip().startswith('{'):
                        try:
                            parsed = json.loads(content)
                            log_entry.append(self._indent(self._format_json(parsed), 2))
                        except:
                            log_entry.append(self._indent(content, 2))
                    else:
                        # Truncate very long text responses
                        if len(content) > 1000:
                            content = content[:1000] + f"... [truncated, total length: {len(content)}]"
                        log_entry.append(self._indent(content, 2))
            
            elif hasattr(response, 'data'):
                # Embedding response
                log_entry.append(f"Model: {response.model}")
                log_entry.append(f"Embeddings generated: {len(response.data)}")
                log_entry.append(f"Dimensions: {len(response.data[0].embedding) if response.data else 'N/A'}")
                log_entry.append(f"Usage:")
                log_entry.append(f"  - Prompt tokens: {response.usage.prompt_tokens}")
                log_entry.append(f"  - Total tokens: {response.usage.total_tokens}")
            
            else:
                # Generic response
                log_entry.append(self._indent(str(response), 2))
        
        log_entry.append("=" * 100)
        log_entry.append("\n")
        
        # Write to file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n".join(log_entry) + "\n")
    
    def log_summary(self, operation: str, duration_ms: float):
        """Log a brief summary of an operation"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        summary = f"⏱️  [{timestamp}] {operation} completed in {duration_ms:.2f}ms\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(summary)


# Global logger instance
_logger = None

def get_logger() -> OpenAILogger:
    """Get or create the global logger instance"""
    global _logger
    if _logger is None:
        log_dir = os.getenv("OPENAI_LOG_DIR", "./api_logs")
        _logger = OpenAILogger(log_dir)
    return _logger