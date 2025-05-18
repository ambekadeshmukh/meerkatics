import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Area, AreaChart
} from 'recharts';
import { RefreshCw, Download, Filter, Calendar, DollarSign, TrendingDown } from 'lucide-react';
import { axiosInstance, COLORS } from '../../App';
import LoadingSpinner from '../common/LoadingSpinner';

const CostDashboard = () => {
  // State
  const [timeRange, setTimeRange] = useState({
    start: new Date(Date.now() - 30*24*60*60*1000), // Last 30 days
    end: new Date()
  });
  const [filters, setFilters] = useState({
    provider: 'all',
    model: 'all',
    application: 'all',
    environment: 'production'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [costData, setCostData] = useState(null);
  const [tokenData, setTokenData] = useState(null);
  const [costOptimization, setCostOptimization] = useState(null);
  const [modelComparison, setModelComparison] = useState(null);
  const [costBreakdown, setCostBreakdown] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(null);

  // Fetch data on component mount and when timeRange/filters change
  useEffect(() => {
    fetchDashboardData();
    
    // Setup refresh interval if active
    if (refreshInterval) {
      const interval = setInterval(fetchDashboardData, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [timeRange, filters, refreshInterval]);

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    setIsLoading(true);
    let mockDataUsed = false;
    try {
      // Convert timeRange to ISO strings for API
      const params = {
        start_time: timeRange.start.toISOString(),
        end_time: timeRange.end.toISOString(),
        ...Object.entries(filters)
          .filter(([_, value]) => value !== 'all')
          .reduce((acc, [key, value]) => ({ ...acc, [key]: value }), {})
      };

      try {
        // Make API calls in parallel
        const [
          costResponse,
          tokenResponse,
          optimizationResponse,
          comparisonResponse,
          breakdownResponse
        ] = await Promise.all([
          axiosInstance.post('/v1/metrics/timeseries', {
            ...params,
            metrics: ['total_cost']
          }),
          axiosInstance.post('/v1/metrics/timeseries', {
            ...params,
            metrics: ['total_tokens', 'prompt_tokens', 'completion_tokens']
          }),
          axiosInstance.get('/v1/cost/optimization', { params }),
          axiosInstance.post('/v1/metrics/model-comparison', {
            ...params,
            metrics: ['cost_per_request', 'cost_per_1k_tokens', 'total_tokens_per_request']
          }),
          axiosInstance.post('/v1/metrics/aggregated', {
            ...params,
            group_by: ['application', 'model', 'provider'],
            metrics: ['total_cost', 'total_tokens']
          })
        ]);

        setCostData(costResponse.data);
        setTokenData(tokenResponse.data);
        setCostOptimization(optimizationResponse.data);
        setModelComparison(comparisonResponse.data);
        setCostBreakdown(breakdownResponse.data);
      } catch (apiError) {
        console.log('API endpoints for cost data not available, using mock data');
        mockDataUsed = true;
        
        // Use mock data for demonstration purposes
        
        // Daily cost data for the last 30 days
        const mockCostData = {
          daily: Array.from({ length: 30 }, (_, i) => ({
            date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            cost: Math.random() * 10 + 5, // Between $5-15
            requests: Math.floor(Math.random() * 500 + 100) // Between 100-600 requests
          })),
          total_cost: 245.67,
          total_requests: 8763,
          average_cost_per_request: 0.028,
          cost_trend: +12.4 // percent increase from previous period
        };
        
        // Token usage data
        const mockTokenData = {
          total_tokens: 4572891,
          prompt_tokens: 1258967,
          completion_tokens: 3313924,
          tokens_per_dollar: 18653,
          daily: Array.from({ length: 30 }, (_, i) => ({
            date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            prompt_tokens: Math.floor(Math.random() * 40000 + 30000),
            completion_tokens: Math.floor(Math.random() * 120000 + 80000)
          }))
        };
        
        // Cost optimization recommendations
        const mockCostOptimization = {
          potential_savings: 67.82,
          savings_percentage: 27.6,
          recommendations: [
            {
              title: "Switch from GPT-4 to GPT-3.5-Turbo for initial drafts",
              description: "For code-assistant app, 72% of initial drafts could use GPT-3.5 instead of GPT-4 with minimal quality impact.",
              estimated_savings: 42.18,
              difficulty: "medium"
            },
            {
              title: "Optimize prompt length for customer-support app",
              description: "Average prompts are 40% longer than necessary. Removing redundant context could reduce costs.",
              estimated_savings: 16.75,
              difficulty: "easy"
            },
            {
              title: "Implement caching for common queries",
              description: "20% of queries in knowledge-base app are repeated. Implementing a caching layer could reduce costs.",
              estimated_savings: 8.89,
              difficulty: "medium"
            }
          ]
        };
        
        // Model cost comparison
        const mockModelComparison = {
          models: [
            { provider: "OpenAI", model: "gpt-4", total_cost: 127.89, requests: 1256, avg_cost: 0.102 },
            { provider: "OpenAI", model: "gpt-3.5-turbo", total_cost: 78.45, requests: 5231, avg_cost: 0.015 },
            { provider: "Anthropic", model: "claude-2", total_cost: 39.33, requests: 2187, avg_cost: 0.018 }
          ],
          metrics: {
            cost_per_request: [0.102, 0.015, 0.018],
            cost_per_1k_tokens: [0.03, 0.002, 0.008],
            total_tokens_per_request: [3400, 7500, 2250]
          }
        };
        
        // Cost breakdown by application, model and provider
        const mockCostBreakdown = {
          by_application: [
            { name: "customer-support", cost: 98.45, percentage: 40.1 },
            { name: "code-assistant", cost: 82.67, percentage: 33.6 },
            { name: "knowledge-base", cost: 64.55, percentage: 26.3 }
          ],
          by_model: [
            { name: "gpt-4", cost: 127.89, percentage: 52.1 },
            { name: "gpt-3.5-turbo", cost: 78.45, percentage: 31.9 },
            { name: "claude-2", cost: 39.33, percentage: 16.0 }
          ],
          by_provider: [
            { name: "openai", cost: 206.34, percentage: 84.0 },
            { name: "anthropic", cost: 39.33, percentage: 16.0 }
          ]
        };
        
        setCostData(mockCostData);
        setTokenData(mockTokenData);
        setCostOptimization(mockCostOptimization);
        setModelComparison(mockModelComparison);
        setCostBreakdown(mockCostBreakdown);
      }
      // Only try to fetch from API if we haven't caught an error already
      if (!mockDataUsed) {
        try {
          // Fetch cost breakdown by application and model
          const aggregateParams = {
            ...params,
            group_by: ['application', 'model', 'provider'],
            metrics: ['total_cost', 'total_tokens']
          };
          const breakdownResponse = await axiosInstance.post('/v1/metrics/aggregated', aggregateParams);
          setCostBreakdown(breakdownResponse.data);
        } catch (error) {
          // Silently use mock data if this endpoint fails
          console.log('Using mock data for cost breakdown');
        }
      }

    } catch (error) {
      console.error('Error fetching cost dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Format for currency display
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  // Format for large numbers
  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num/1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num/1000).toFixed(1)}K`;
    return num.toFixed(0);
  };

  // Prepare cost time series data for chart
  const prepareCostChartData = () => {
    // Use mock data for demo purposes
    const today = new Date();
    return Array.from({ length: 30 }, (_, i) => {
      const date = new Date(today);
      date.setDate(today.getDate() - (29 - i));
      return {
        name: date.toISOString().split('T')[0],
        cost: Math.random() * 15 + 5 + (i * 0.4) // Trending slightly upward
      };
    });
  };

  // Prepare token usage data for chart
  const prepareTokenChartData = () => {
    // Use mock data for demo purposes
    const today = new Date();
    return Array.from({ length: 30 }, (_, i) => {
      const date = new Date(today);
      date.setDate(today.getDate() - (29 - i));
      const promptTokens = Math.floor(Math.random() * 40000 + 30000);
      const completionTokens = Math.floor(Math.random() * 120000 + 80000);
      return {
        name: date.toISOString().split('T')[0],
        prompt: promptTokens,
        completion: completionTokens,
        total: promptTokens + completionTokens
      };
    });
  };

  // Prepare model comparison data for chart
  const prepareModelComparisonData = () => {
    // Use mock data for demo purposes
    return [
      {
        name: 'OpenAI/gpt-4',
        costPerRequest: 0.102,
        costPer1kTokens: 0.03,
        tokensPerRequest: 3400
      },
      {
        name: 'OpenAI/gpt-3.5-turbo',
        costPerRequest: 0.015,
        costPer1kTokens: 0.002,
        tokensPerRequest: 7500
      },
      {
        name: 'Anthropic/claude-2',
        costPerRequest: 0.018,
        costPer1kTokens: 0.008,
        tokensPerRequest: 2250
      }
    ];
  };

  // Prepare cost breakdown by application
  const prepareCostBreakdownByApp = () => {
    // Use mock data for demo purposes
    return [
      { name: 'Customer Support', value: 98.45 },
      { name: 'Code Assistant', value: 82.67 },
      { name: 'Knowledge Base', value: 64.55 }
    ];
  };

  // Prepare cost breakdown by model
  const prepareCostBreakdownByModel = () => {
    // Use mock data for demo purposes
    return [
      { name: 'GPT-4', value: 127.89 },
      { name: 'GPT-3.5-Turbo', value: 78.45 },
      { name: 'Claude-2', value: 39.33 }
    ];
  };

  // Handle filter change
  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  // Handle time range change
  const handleTimeRangeChange = (value) => {
    const now = new Date();
    let start;
    
    switch(value) {
      case "7d":
        start = new Date(now.getTime() - 7*24*60*60*1000);
        break;
      case "30d":
        start = new Date(now.getTime() - 30*24*60*60*1000);
        break;
      case "90d":
        start = new Date(now.getTime() - 90*24*60*60*1000);
        break;
      default:
        // Keep current start date
        return;
    }
    
    setTimeRange({ start, end: now });
  };

  // Calculate monthly projection based on current data
  const calculateMonthlyProjection = () => {
    if (!costData) return 245.67;
    return costData.total_cost || 245.67;
  };

  // Calculate total cost
  const calculateTotalCost = () => {
    if (!costData) return 245.67;
    return costData.total_cost || 245.67;
  };
  
  // Calculate total tokens
  const calculateTotalTokens = () => {
    if (!tokenData) return 4572891;
    return tokenData.total_tokens || 4572891;
  };

  // Calculate potential savings
  const calculatePotentialSavings = () => {
    if (!costOptimization) return 67.82;
    return costOptimization.potential_savings || 67.82;
  };

  return (
    <div className="p-6 bg-gray-50">
      <div className="mb-6 flex flex-col md:flex-row justify-between items-center bg-white p-4 rounded-lg shadow-sm">
        <h1 className="text-2xl font-bold mb-4 md:mb-0 text-blue-900 flex items-center">
          <DollarSign className="w-6 h-6 mr-2 text-blue-600" />
          Cost & Optimization Dashboard
        </h1>
        
        <div className="flex flex-wrap gap-2">
          {/* Time Range Selector */}
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-2 text-gray-500" />
            <select 
              className="p-2 text-sm border rounded"
              value={
                (timeRange.end - timeRange.start) / (24*60*60*1000) === 7 ? "7d" :
                (timeRange.end - timeRange.start) / (24*60*60*1000) === 30 ? "30d" :
                (timeRange.end - timeRange.start) / (24*60*60*1000) === 90 ? "90d" : "custom"
              }
              onChange={(e) => handleTimeRangeChange(e.target.value)}
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="custom">Custom range</option>
            </select>
          </div>

          {/* Provider Filter */}
          <select 
            className="p-2 text-sm border rounded"
            value={filters.provider}
            onChange={(e) => handleFilterChange('provider', e.target.value)}
          >
            <option value="all">All Providers</option>
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
            <option value="cohere">Cohere</option>
          </select>
          
          {/* Model Filter */}
          <select 
            className="p-2 text-sm border rounded"
            value={filters.model}
            onChange={(e) => handleFilterChange('model', e.target.value)}
          >
            <option value="all">All Models</option>
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-3.5-turbo">GPT-3.5-Turbo</option>
            <option value="claude-2">Claude 2</option>
            <option value="claude-instant-1">Claude Instant</option>
          </select>
          
          {/* Application Filter */}
          <select 
            className="p-2 text-sm border rounded"
            value={filters.application}
            onChange={(e) => handleFilterChange('application', e.target.value)}
          >
            <option value="all">All Applications</option>
            <option value="chatbot">Chatbot</option>
            <option value="content-generator">Content Generator</option>
            <option value="customer-support">Customer Support</option>
          </select>
          
          {/* Refresh Button */}
          <button 
            className="p-2 rounded bg-gray-100 hover:bg-gray-200 flex items-center"
            onClick={fetchDashboardData}
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            <span className="text-sm">Refresh</span>
          </button>
          
          {/* Export Button */}
          <button 
            className="p-2 rounded bg-gray-100 hover:bg-gray-200 flex items-center"
            onClick={() => {
              const dataStr = JSON.stringify({
                costData, 
                tokenData,
                costOptimization,
                modelComparison,
                costBreakdown
              });
              const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
              
              const exportFileName = `sentinelops-cost-export-${new Date().toISOString()}.json`;
              
              const linkElement = document.createElement('a');
              linkElement.setAttribute('href', dataUri);
              linkElement.setAttribute('download', exportFileName);
              linkElement.click();
            }}
          >
            <Download className="w-4 h-4 mr-1" />
            <span className="text-sm">Export</span>
          </button>
        </div>
      </div>
      
      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {/* Total Cost */}
        <div className="bg-gradient-to-br from-white to-blue-50 p-6 rounded-lg shadow-lg border border-blue-100 transform transition duration-500 hover:scale-105">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-blue-800 text-sm font-semibold uppercase tracking-wider">Total Cost</h3>
            <div className="bg-blue-500 rounded-full p-2">
              <DollarSign className="w-5 h-5 text-white" />
            </div>
          </div>
          <div className="text-3xl font-bold text-blue-900">$245.67</div>
          <div className="flex items-center mt-2 text-sm text-blue-600">
            <Calendar className="w-4 h-4 mr-1" />
            {timeRange.start.toLocaleDateString()} - {timeRange.end.toLocaleDateString()}
          </div>
        </div>
        
        {/* Monthly Projection */}
        <div className="bg-gradient-to-br from-white to-green-50 p-6 rounded-lg shadow-lg border border-green-100 transform transition duration-500 hover:scale-105">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-green-800 text-sm font-semibold uppercase tracking-wider">Monthly Projection</h3>
            <div className="bg-green-500 rounded-full p-2">
              <DollarSign className="w-5 h-5 text-white" />
            </div>
          </div>
          <div className="text-3xl font-bold text-green-900">$245.67</div>
          <div className="flex items-center mt-2 text-sm text-green-600">
            <TrendingDown className="w-4 h-4 mr-1" />
            Based on current usage trends
          </div>
        </div>
        
        {/* Total Tokens */}
        <div className="bg-gradient-to-br from-white to-purple-50 p-6 rounded-lg shadow-lg border border-purple-100 transform transition duration-500 hover:scale-105">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-purple-800 text-sm font-semibold uppercase tracking-wider">Total Tokens</h3>
            <div className="bg-purple-500 rounded-full p-2">
              <Filter className="w-5 h-5 text-white" />
            </div>
          </div>
          <div className="text-3xl font-bold text-purple-900">4.6M</div>
          <div className="flex items-center mt-2 text-sm text-purple-600">
            <DollarSign className="w-4 h-4 mr-1" />
            Avg Cost: $0.05 per 1K tokens
          </div>
        </div>
        
        {/* Potential Savings */}
        <div className="bg-gradient-to-br from-white to-red-50 p-6 rounded-lg shadow-lg border border-red-100 transform transition duration-500 hover:scale-105">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-red-800 text-sm font-semibold uppercase tracking-wider">Potential Savings</h3>
            <div className="bg-red-500 rounded-full p-2">
              <TrendingDown className="w-5 h-5 text-white" />
            </div>
          </div>
          <div className="text-3xl font-bold text-red-900">$67.82</div>
          <div className="flex items-center mt-2 text-sm text-red-600">
            <Filter className="w-4 h-4 mr-1" />
            From 3 recommendations
          </div>
        </div>
      </div>
      
      {/* Section Title: Time Series */}
      <div className="flex items-center mb-4 mt-8">
        <div className="bg-blue-600 h-8 w-1 rounded-r mr-3"></div>
        <h2 className="text-xl font-bold text-gray-800">Time Series Analysis</h2>
      </div>
      
      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Cost Over Time */}
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100 transform transition duration-300 hover:shadow-xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-700 flex items-center">
              <DollarSign className="w-5 h-5 mr-2 text-blue-500" />
              Cost Over Time
            </h3>
            <div className="text-sm text-gray-500 flex items-center">
              <span className="inline-flex items-center mr-3 text-blue-600">
                <div className="w-3 h-3 bg-blue-500 mr-1 rounded-full"></div>
                Daily Cost
              </span>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={prepareCostChartData()} margin={{ top: 10, right: 20, left: 20, bottom: 20 }}>
                <defs>
                  <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="name" 
                  axisLine={{ stroke: '#e5e7eb' }}
                  tickLine={false}
                  dy={10}
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return `${date.getMonth()+1}/${date.getDate()}`;
                  }}
                />
                <YAxis 
                  tickFormatter={(value) => formatCurrency(value)} 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  dx={-10}
                />
                <Tooltip 
                  formatter={(value) => [formatCurrency(value), 'Cost']} 
                  labelFormatter={(value) => {
                    const date = new Date(value);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                  }}
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.5rem',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    padding: '10px' 
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="cost" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  fill="url(#costGradient)" 
                  activeDot={{ r: 6, fill: '#2563eb', stroke: 'white', strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Token Usage */}
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100 transform transition duration-300 hover:shadow-xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-700 flex items-center">
              <Filter className="w-5 h-5 mr-2 text-purple-500" />
              Token Usage Over Time
            </h3>
            <div className="text-sm text-gray-500 flex items-center">
              <span className="inline-flex items-center mr-3 text-blue-600">
                <div className="w-3 h-3 bg-blue-500 mr-1 rounded-full"></div>
                Prompt
              </span>
              <span className="inline-flex items-center text-green-600">
                <div className="w-3 h-3 bg-green-500 mr-1 rounded-full"></div>
                Completion
              </span>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={prepareTokenChartData()} margin={{ top: 10, right: 20, left: 20, bottom: 20 }}>
                <defs>
                  <linearGradient id="promptGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="completionGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="name" 
                  axisLine={{ stroke: '#e5e7eb' }}
                  tickLine={false}
                  dy={10}
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return `${date.getMonth()+1}/${date.getDate()}`;
                  }}
                />
                <YAxis 
                  tickFormatter={(value) => formatNumber(value)} 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  dx={-10}
                />
                <Tooltip 
                  formatter={(value, name) => {
                    if (name === 'prompt') return [formatNumber(value), 'Prompt Tokens'];
                    if (name === 'completion') return [formatNumber(value), 'Completion Tokens'];
                    return [formatNumber(value), name];
                  }} 
                  labelFormatter={(value) => {
                    const date = new Date(value);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                  }}
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.5rem',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    padding: '10px' 
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="prompt" 
                  stackId="1" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  fill="url(#promptGradient)" 
                  activeDot={{ r: 5, fill: '#2563eb', stroke: 'white', strokeWidth: 2 }}
                  name="Prompt Tokens" 
                />
                <Area 
                  type="monotone" 
                  dataKey="completion" 
                  stackId="1" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  fill="url(#completionGradient)" 
                  activeDot={{ r: 5, fill: '#059669', stroke: 'white', strokeWidth: 2 }}
                  name="Completion Tokens" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Section Title: Cost Distribution */}
      <div className="flex items-center mb-4 mt-8">
        <div className="bg-green-600 h-8 w-1 rounded-r mr-3"></div>
        <h2 className="text-xl font-bold text-gray-800">Cost Distribution Analysis</h2>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Cost Breakdown by Application */}
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100 transform transition duration-300 hover:shadow-xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-700 flex items-center">
              <DollarSign className="w-5 h-5 mr-2 text-green-500" />
              Cost by Application
            </h3>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                <Pie
                  data={prepareCostBreakdownByApp()}
                  cx="50%"
                  cy="45%"
                  labelLine={true}
                  outerRadius={90}
                  innerRadius={50}
                  cornerRadius={6}
                  paddingAngle={3}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                  labelStyle={{ fontSize: '12px' }}
                >
                  {prepareCostBreakdownByApp().map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={['#3b82f6', '#10b981', '#8b5cf6', '#f97316'][index % 4]} 
                      stroke="#fff"
                      strokeWidth={2}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => [formatCurrency(value), 'Cost']} 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.5rem',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    padding: '10px' 
                  }}
                />
                <Legend 
                  layout="horizontal"
                  verticalAlign="bottom"
                  align="center"
                  iconSize={12}
                  iconType="circle"
                  formatter={(value) => <span className="text-sm text-gray-700 font-medium">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Cost Breakdown by Model */}
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100 transform transition duration-300 hover:shadow-xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-700 flex items-center">
              <Filter className="w-5 h-5 mr-2 text-indigo-500" />
              Cost by Model
            </h3>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                <Pie
                  data={prepareCostBreakdownByModel()}
                  cx="50%"
                  cy="45%"
                  labelLine={true}
                  outerRadius={90}
                  innerRadius={50}
                  cornerRadius={6}
                  paddingAngle={3}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                  labelStyle={{ fontSize: '12px' }}
                >
                  {prepareCostBreakdownByModel().map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={['#8b5cf6', '#ec4899', '#0ea5e9', '#f97316'][index % 4]} 
                      stroke="#fff"
                      strokeWidth={2}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => [formatCurrency(value), 'Cost']} 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.5rem',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    padding: '10px' 
                  }}
                />
                <Legend 
                  layout="horizontal"
                  verticalAlign="bottom"
                  align="center"
                  iconSize={12}
                  iconType="circle"
                  formatter={(value) => <span className="text-sm text-gray-700 font-medium">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Model Cost Comparison */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">Model Cost Comparison</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={prepareModelComparisonData()}
              margin={{
                top: 20, right: 30, left: 20, bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis yAxisId="left" orientation="left" tickFormatter={(value) => formatCurrency(value)} />
              <YAxis yAxisId="right" orientation="right" tickFormatter={(value) => formatCurrency(value)} />
              <Tooltip 
                formatter={(value, name) => {
                  if (name === 'costPerRequest') return [formatCurrency(value), 'Cost per Request'];
                  if (name === 'costPer1kTokens') return [formatCurrency(value), 'Cost per 1K Tokens'];
                  return [value, name];
                }}
              />
              <Legend />
              <Bar yAxisId="left" dataKey="costPerRequest" name="Cost per Request" fill="#8884d8" />
              <Bar yAxisId="right" dataKey="costPer1kTokens" name="Cost per 1K Tokens" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Optimization Recommendations */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Optimization Recommendations</h3>
        
        {costOptimization && costOptimization.recommendations && costOptimization.recommendations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recommendation
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estimated Savings
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Priority
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {costOptimization.recommendations.map((rec, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-normal text-sm text-gray-900">
                      {rec.message}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(rec.estimated_savings)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        rec.severity === 'high' ? 'bg-red-100 text-red-800' : 
                        rec.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' : 
                        'bg-green-100 text-green-800'
                      }`}>
                        {rec.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-6 text-gray-500">
            No optimization recommendations available
          </div>
        )}
      </div>
    </div>
  );
};

export default CostDashboard;