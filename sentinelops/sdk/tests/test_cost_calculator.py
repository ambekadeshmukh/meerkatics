import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentinelops.utils.cost import CostCalculator

class TestCostCalculator(unittest.TestCase):
    """Test cases for the CostCalculator class."""

    def test_calculate_cost_openai(self):
        """Test cost calculation for OpenAI models."""
        # Test GPT-3.5 Turbo
        cost = CostCalculator.calculate_cost(
            provider="openai",
            model="gpt-3.5-turbo",
            prompt_tokens=1000,
            completion_tokens=500
        )
        # Expected: (1000/1000 * 0.0015) + (500/1000 * 0.002) = 0.0015 + 0.001 = 0.0025
        self.assertAlmostEqual(cost, 0.0025, places=6)
        
        # Test GPT-4
        cost = CostCalculator.calculate_cost(
            provider="openai",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )
        # Expected: (1000/1000 * 0.03) + (500/1000 * 0.06) = 0.03 + 0.03 = 0.06
        self.assertAlmostEqual(cost, 0.06, places=6)

    def test_calculate_cost_anthropic(self):
        """Test cost calculation for Anthropic models."""
        # Test Claude-2
        cost = CostCalculator.calculate_cost(
            provider="anthropic",
            model="claude-2",
            prompt_tokens=1000,
            completion_tokens=500
        )
        # Expected: (1000/1000 * 0.008) + (500/1000 * 0.024) = 0.008 + 0.012 = 0.02
        self.assertAlmostEqual(cost, 0.02, places=6)

    def test_calculate_cost_azure(self):
        """Test cost calculation for Azure OpenAI models."""
        # Test Azure GPT-4
        cost = CostCalculator.calculate_cost(
            provider="azure",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )
        # Should match OpenAI GPT-4 pricing
        openai_cost = CostCalculator.calculate_cost(
            provider="openai",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )
        self.assertAlmostEqual(cost, openai_cost, places=6)

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation for unknown models."""
        # Should return 0 for unknown models
        cost = CostCalculator.calculate_cost(
            provider="unknown",
            model="unknown-model",
            prompt_tokens=1000,
            completion_tokens=500
        )
        self.assertEqual(cost, 0.0)

    def test_find_similar_model_pricing(self):
        """Test finding similar model pricing."""
        # Test finding similar OpenAI model
        pricing_data = CostCalculator.PRICING
        similar_pricing = CostCalculator._find_similar_model_pricing(
            provider="openai",
            model="gpt-4-1106-preview",  # Not in the exact list
            pricing_data=pricing_data
        )
        # Should find gpt-4 pricing
        self.assertIsNotNone(similar_pricing)
        self.assertEqual(similar_pricing, pricing_data["openai"]["gpt-4"])
        
        # Test finding similar Anthropic model
        similar_pricing = CostCalculator._find_similar_model_pricing(
            provider="anthropic",
            model="claude-3-opus-20240229",  # Not in the exact list
            pricing_data=pricing_data
        )
        # Should find claude-3-opus pricing
        self.assertIsNotNone(similar_pricing)
        self.assertEqual(similar_pricing, pricing_data["anthropic"]["claude-3-opus"])

    def test_get_supported_models(self):
        """Test getting supported models."""
        supported_models = CostCalculator.get_supported_models()
        
        # Should return a dictionary
        self.assertIsInstance(supported_models, dict)
        
        # Should contain key providers
        self.assertIn("openai", supported_models)
        self.assertIn("anthropic", supported_models)
        
        # Each provider should have a list of models
        self.assertIsInstance(supported_models["openai"], list)
        self.assertGreater(len(supported_models["openai"]), 0)

    def test_update_pricing(self):
        """Test updating pricing data."""
        # Save original pricing
        original_pricing = CostCalculator.PRICING.copy()
        
        try:
            # Update with new pricing
            new_pricing = {
                "new_provider": {
                    "new_model": {"prompt": 0.1, "completion": 0.2}
                },
                "openai": {
                    "new_openai_model": {"prompt": 0.01, "completion": 0.02}
                }
            }
            
            CostCalculator.update_pricing(new_pricing)
            
            # Check new provider was added
            self.assertIn("new_provider", CostCalculator.PRICING)
            self.assertIn("new_model", CostCalculator.PRICING["new_provider"])
            
            # Check new model was added to existing provider
            self.assertIn("new_openai_model", CostCalculator.PRICING["openai"])
            
            # Test calculating cost with new pricing
            cost = CostCalculator.calculate_cost(
                provider="new_provider",
                model="new_model",
                prompt_tokens=1000,
                completion_tokens=500
            )
            # Expected: (1000/1000 * 0.1) + (500/1000 * 0.2) = 0.1 + 0.1 = 0.2
            self.assertAlmostEqual(cost, 0.2, places=6)
            
        finally:
            # Restore original pricing
            CostCalculator.PRICING = original_pricing

    def test_estimate_monthly_cost(self):
        """Test estimating monthly cost."""
        # Mock calculate_cost to return a fixed value
        with patch.object(CostCalculator, 'calculate_cost', return_value=0.1) as mock_calculate:
            monthly_cost = CostCalculator.estimate_monthly_cost(
                daily_requests=100,
                avg_prompt_tokens=1000,
                avg_completion_tokens=500,
                provider="openai",
                model="gpt-4"
            )
            
            # Should call calculate_cost with the right parameters
            mock_calculate.assert_called_once_with(
                provider="openai",
                model="gpt-4",
                prompt_tokens=100 * 1000,  # daily_requests * avg_prompt_tokens
                completion_tokens=100 * 500  # daily_requests * avg_completion_tokens
            )
            
            # Should multiply daily cost by 30
            self.assertEqual(monthly_cost, 0.1 * 30)

if __name__ == '__main__':
    unittest.main()
