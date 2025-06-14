import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from decimal import Decimal

# Add the parent directory to the path to import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from meerkatics.sdk.utils.cost import CostCalculator

class TestCostCalculator(unittest.TestCase):
    """Test suite for the CostCalculator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = CostCalculator()
        
        # Sample custom pricing for testing
        self.custom_pricing = {
            "openai": {
                "gpt-4": {
                    "prompt": Decimal("0.04"),
                    "completion": Decimal("0.08")
                },
                "gpt-3.5-turbo": {
                    "prompt": Decimal("0.0015"),
                    "completion": Decimal("0.002")
                }
            },
            "anthropic": {
                "claude-2": {
                    "prompt": Decimal("0.012"),
                    "completion": Decimal("0.036")
                }
            }
        }

    def test_default_pricing_data_structure(self):
        """Test that the default pricing data has the expected structure."""
        pricing = CostCalculator.PRICING
        
        # Check that major providers exist
        self.assertIn("openai", pricing)
        self.assertIn("anthropic", pricing)
        self.assertIn("azure", pricing)
        
        # Check structure for a specific model
        self.assertIn("gpt-4", pricing["openai"])
        self.assertIn("prompt", pricing["openai"]["gpt-4"])
        self.assertIn("completion", pricing["openai"]["gpt-4"])
        
        # Check that values are Decimal objects
        self.assertIsInstance(pricing["openai"]["gpt-4"]["prompt"], Decimal)
        self.assertIsInstance(pricing["openai"]["gpt-4"]["completion"], Decimal)

    def test_calculate_cost_openai(self):
        """Test cost calculation for OpenAI models."""
        # Test GPT-4
        cost = self.calculator.calculate_cost(
            provider="openai",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )
        
        expected_cost = (
            1000 * CostCalculator.PRICING["openai"]["gpt-4"]["prompt"] / 1000 +
            500 * CostCalculator.PRICING["openai"]["gpt-4"]["completion"] / 1000
        )
        
        self.assertAlmostEqual(cost, float(expected_cost), places=6)
        
        # Test GPT-3.5 Turbo
        cost = self.calculator.calculate_cost(
            provider="openai",
            model="gpt-3.5-turbo",
            prompt_tokens=2000,
            completion_tokens=1000
        )
        
        expected_cost = (
            2000 * CostCalculator.PRICING["openai"]["gpt-3.5-turbo"]["prompt"] / 1000 +
            1000 * CostCalculator.PRICING["openai"]["gpt-3.5-turbo"]["completion"] / 1000
        )
        
        self.assertAlmostEqual(cost, float(expected_cost), places=6)

    def test_calculate_cost_anthropic(self):
        """Test cost calculation for Anthropic models."""
        # Test Claude 2
        cost = self.calculator.calculate_cost(
            provider="anthropic",
            model="claude-2",
            prompt_tokens=5000,
            completion_tokens=2000
        )
        
        expected_cost = (
            5000 * CostCalculator.PRICING["anthropic"]["claude-2"]["prompt"] / 1000 +
            2000 * CostCalculator.PRICING["anthropic"]["claude-2"]["completion"] / 1000
        )
        
        self.assertAlmostEqual(cost, float(expected_cost), places=6)

    def test_calculate_cost_azure(self):
        """Test cost calculation for Azure OpenAI models."""
        # Test Azure GPT-4
        cost = self.calculator.calculate_cost(
            provider="azure",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )
        
        expected_cost = (
            1000 * CostCalculator.PRICING["azure"]["gpt-4"]["prompt"] / 1000 +
            500 * CostCalculator.PRICING["azure"]["gpt-4"]["completion"] / 1000
        )
        
        self.assertAlmostEqual(cost, float(expected_cost), places=6)

    def test_calculate_cost_with_custom_pricing(self):
        """Test cost calculation with custom pricing."""
        calculator = CostCalculator(custom_pricing=self.custom_pricing)
        
        # Test GPT-4 with custom pricing
        cost = calculator.calculate_cost(
            provider="openai",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )
        
        expected_cost = (
            1000 * self.custom_pricing["openai"]["gpt-4"]["prompt"] / 1000 +
            500 * self.custom_pricing["openai"]["gpt-4"]["completion"] / 1000
        )
        
        self.assertAlmostEqual(cost, float(expected_cost), places=6)

    def test_calculate_cost_unknown_provider(self):
        """Test cost calculation with an unknown provider."""
        with self.assertRaises(ValueError):
            self.calculator.calculate_cost(
                provider="unknown_provider",
                model="gpt-4",
                prompt_tokens=1000,
                completion_tokens=500
            )

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation with an unknown model."""
        with self.assertRaises(ValueError):
            self.calculator.calculate_cost(
                provider="openai",
                model="unknown_model",
                prompt_tokens=1000,
                completion_tokens=500
            )

    def test_calculate_cost_negative_tokens(self):
        """Test cost calculation with negative token counts."""
        with self.assertRaises(ValueError):
            self.calculator.calculate_cost(
                provider="openai",
                model="gpt-4",
                prompt_tokens=-1000,
                completion_tokens=500
            )
        
        with self.assertRaises(ValueError):
            self.calculator.calculate_cost(
                provider="openai",
                model="gpt-4",
                prompt_tokens=1000,
                completion_tokens=-500
            )

    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        cost = self.calculator.calculate_cost(
            provider="openai",
            model="gpt-4",
            prompt_tokens=0,
            completion_tokens=0
        )
        
        self.assertEqual(cost, 0.0)

    def test_get_model_pricing(self):
        """Test getting pricing for a specific model."""
        pricing = self.calculator.get_model_pricing("openai", "gpt-4")
        
        self.assertIsInstance(pricing, dict)
        self.assertIn("prompt", pricing)
        self.assertIn("completion", pricing)
        self.assertEqual(pricing["prompt"], CostCalculator.PRICING["openai"]["gpt-4"]["prompt"])
        self.assertEqual(pricing["completion"], CostCalculator.PRICING["openai"]["gpt-4"]["completion"])

    def test_get_model_pricing_unknown(self):
        """Test getting pricing for an unknown model."""
        with self.assertRaises(ValueError):
            self.calculator.get_model_pricing("openai", "unknown_model")

    @patch('builtins.open')
    def test_load_custom_pricing_from_file(self, mock_open):
        """Test loading custom pricing from a file."""
        # Mock the file content
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps({
            "openai": {
                "gpt-4": {
                    "prompt": 0.04,
                    "completion": 0.08
                }
            }
        })
        mock_open.return_value = mock_file
        
        # Call the method
        pricing = CostCalculator.load_custom_pricing_from_file("fake_path.json")
        
        # Check the result
        self.assertIsInstance(pricing["openai"]["gpt-4"]["prompt"], Decimal)
        self.assertEqual(pricing["openai"]["gpt-4"]["prompt"], Decimal("0.04"))
        self.assertEqual(pricing["openai"]["gpt-4"]["completion"], Decimal("0.08"))

    def test_estimate_cost_for_text(self):
        """Test estimating cost for a text string."""
        text = "This is a sample text to test the cost estimation."
        
        # Mock the token counting
        with patch('meerkatics.sdk.utils.tokenizers.TokenCounter.count_tokens') as mock_count:
            mock_count.return_value = 10  # Assume 10 tokens
            
            cost = self.calculator.estimate_cost_for_text(
                text=text,
                provider="openai",
                model="gpt-4",
                is_prompt=True
            )
            
            expected_cost = 10 * CostCalculator.PRICING["openai"]["gpt-4"]["prompt"] / 1000
            self.assertAlmostEqual(cost, float(expected_cost), places=6)

if __name__ == '__main__':
    unittest.main()
