import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meerkatics.utils.tokenizers import TokenCounter

class TestTokenCounter(unittest.TestCase):
    """Test cases for the TokenCounter class."""

    def test_estimate_tokens_string(self):
        """Test the fallback token estimation for strings."""
        text = "This is a test string that should be roughly 12 tokens."
        count = TokenCounter.estimate_tokens(text)
        # Roughly 4 chars per token
        self.assertAlmostEqual(count, len(text) // 4, delta=2)

    def test_estimate_tokens_messages(self):
        """Test the fallback token estimation for message lists."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me about token counting."}
        ]
        count = TokenCounter.estimate_tokens(messages)
        # Should be greater than zero
        self.assertGreater(count, 0)

    @patch('tiktoken.encoding_for_model')
    def test_count_openai_tokens_string(self, mock_encoding_for_model):
        """Test counting tokens for OpenAI with a string."""
        # Mock the encoding
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_encoding_for_model.return_value = mock_encoding

        count = TokenCounter.count_openai_tokens("Test string", "gpt-4")
        
        # Should call encode once
        mock_encoding.encode.assert_called_once_with("Test string")
        # Should return the length of the encoded list
        self.assertEqual(count, 5)

    @patch('tiktoken.encoding_for_model')
    def test_count_openai_tokens_messages(self, mock_encoding_for_model):
        """Test counting tokens for OpenAI with message list."""
        # Mock the encoding
        mock_encoding = MagicMock()
        mock_encoding.encode.side_effect = lambda x: [0] * (len(x) // 2)  # Simplified token count
        mock_encoding_for_model.return_value = mock_encoding

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me about token counting."}
        ]
        
        count = TokenCounter.count_openai_tokens(messages, "gpt-4")
        
        # Should be greater than 0
        self.assertGreater(count, 0)
        # Should call encode multiple times (once for each message component)
        self.assertGreater(mock_encoding.encode.call_count, 2)

    @patch('tiktoken.get_encoding')
    def test_count_anthropic_tokens(self, mock_get_encoding):
        """Test counting tokens for Anthropic models."""
        # Mock the encoding
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5, 6, 7, 8]  # 8 tokens
        mock_get_encoding.return_value = mock_encoding

        count = TokenCounter.count_anthropic_tokens("Test Anthropic string", "claude-2")
        
        # Should call get_encoding with cl100k_base
        mock_get_encoding.assert_called_once_with("cl100k_base")
        # Should call encode once
        mock_encoding.encode.assert_called_once_with("Test Anthropic string")
        # Should return the length of the encoded list
        self.assertEqual(count, 8)

    @patch('transformers.AutoTokenizer.from_pretrained')
    def test_count_huggingface_tokens(self, mock_from_pretrained):
        """Test counting tokens for Hugging Face models."""
        # Mock the tokenizer
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [101, 2, 3, 4, 5, 102]  # 6 tokens
        mock_from_pretrained.return_value = mock_tokenizer

        count = TokenCounter.count_huggingface_tokens("Test HF string", "gpt2")
        
        # Should call from_pretrained once
        mock_from_pretrained.assert_called_once_with("gpt2")
        # Should call encode once
        mock_tokenizer.encode.assert_called_once_with("Test HF string")
        # Should return the length of the encoded list
        self.assertEqual(count, 6)

    def test_count_tokens_router(self):
        """Test the main count_tokens router function."""
        with patch.object(TokenCounter, 'count_openai_tokens', return_value=10) as mock_openai, \
             patch.object(TokenCounter, 'count_anthropic_tokens', return_value=12) as mock_anthropic, \
             patch.object(TokenCounter, 'count_huggingface_tokens', return_value=15) as mock_hf, \
             patch.object(TokenCounter, 'estimate_tokens', return_value=8) as mock_estimate:
            
            # Test OpenAI routing
            count = TokenCounter.count_tokens("test", "openai", "gpt-4")
            mock_openai.assert_called_once()
            self.assertEqual(count, 10)
            
            # Test Anthropic routing
            count = TokenCounter.count_tokens("test", "anthropic", "claude-2")
            mock_anthropic.assert_called_once()
            self.assertEqual(count, 12)
            
            # Test HuggingFace routing
            count = TokenCounter.count_tokens("test", "huggingface", "gpt2")
            mock_hf.assert_called_once()
            self.assertEqual(count, 15)
            
            # Test fallback
            count = TokenCounter.count_tokens("test", "unknown", "model")
            mock_estimate.assert_called_once()
            self.assertEqual(count, 8)

if __name__ == '__main__':
    unittest.main()
