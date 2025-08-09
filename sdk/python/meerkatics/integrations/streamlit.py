# Streamlit Integration for Meerkatics

import streamlit as st
from typing import Any, Dict, Optional
import time

class MeerkaticsStreamlitIntegration:
    """Streamlit integration for Meerkatics monitoring with UI components"""
    
    def __init__(self, monitor):
        self.monitor = monitor
    
    def display_metrics_sidebar(self):
        """Display Meerkatics metrics in Streamlit sidebar"""
        with st.sidebar:
            st.header("🔍 Meerkatics Monitoring")
            
            # Get recent statistics
            try:
                stats = self._get_session_stats()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Requests", stats.get('total_requests', 0))
                    st.metric("Avg Latency", f"{stats.get('avg_latency', 0):.0f}ms")
                
                with col2:
                    st.metric("Total Cost", f"${stats.get('total_cost', 0):.4f}")
                    st.metric("Error Rate", f"{stats.get('error_rate', 0):.1f}%")
                
                # Display recent errors if any
                if stats.get('recent_errors'):
                    st.error("Recent Errors:")
                    for error in stats['recent_errors'][-3:]:  # Show last 3 errors
                        st.text(f"• {error}")
                
            except Exception as e:
                st.error(f"Error fetching metrics: {e}")
    
    def display_request_details(self, request_id: str):
        """Display detailed information about a specific request"""
        try:
            # This would fetch request details from your monitoring system
            details = self._get_request_details(request_id)
            
            if details:
                st.subheader(f"Request Details: {request_id}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**Provider:**", details.get('provider', 'Unknown'))
                    st.write("**Model:**", details.get('model', 'Unknown'))
                
                with col2:
                    st.write("**Latency:**", f"{details.get('latency_ms', 0)}ms")
                    st.write("**Cost:**", f"${details.get('cost', 0):.6f}")
                
                with col3:
                    st.write("**Status:**", details.get('status', 'Unknown'))
                    st.write("**Tokens:**", details.get('total_tokens', 0))
                
                # Show prompt and response (if not redacted)
                if details.get('prompt'):
                    st.subheader("Prompt")
                    st.text_area("", details['prompt'], height=100, disabled=True)
                
                if details.get('response'):
                    st.subheader("Response")
                    st.text_area("", details['response'], height=150, disabled=True)
                
                # Show any hallucination detection results
                if details.get('hallucination_score'):
                    st.subheader("Quality Analysis")
                    score = details['hallucination_score']
                    
                    if score > 0.7:
                        st.error(f"High hallucination risk: {score:.2f}")
                    elif score > 0.4:
                        st.warning(f"Moderate hallucination risk: {score:.2f}")
                    else:
                        st.success(f"Low hallucination risk: {score:.2f}")
            
        except Exception as e:
            st.error(f"Error fetching request details: {e}")
    
    def create_monitoring_dashboard(self):
        """Create a full monitoring dashboard in Streamlit"""
        st.title("🔍 Meerkatics AI Monitoring Dashboard")
        
        # Time range selector
        time_range = st.selectbox(
            "Time Range",
            ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days"],
            index=2
        )
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        # Main metrics
        stats = self._get_dashboard_stats(time_range)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Requests", stats.get('total_requests', 0))
        with col2:
            st.metric("Average Latency", f"{stats.get('avg_latency', 0):.0f}ms")
        with col3:
            st.metric("Total Cost", f"${stats.get('total_cost', 0):.4f}")
        with col4:
            st.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
        
        # Charts
        if stats.get('time_series_data'):
            st.subheader("📊 Request Volume Over Time")
            st.line_chart(stats['time_series_data'])
        
        if stats.get('provider_breakdown'):
            st.subheader("🏢 Requests by Provider")
            st.bar_chart(stats['provider_breakdown'])
        
        if stats.get('cost_breakdown'):
            st.subheader("💰 Cost Breakdown")
            st.pie_chart(stats['cost_breakdown'])
        
        # Recent requests table
        if stats.get('recent_requests'):
            st.subheader("📋 Recent Requests")
            st.dataframe(stats['recent_requests'])
    
    def track_streamlit_interaction(self, interaction_type: str, details: Dict[str, Any]):
        """Track Streamlit-specific interactions"""
        self.monitor.track_custom_llm(
            provider='streamlit',
            model='streamlit_app',
            prompt=f"Streamlit {interaction_type}",
            response=str(details),
            usage={'total_tokens': 0},
            latency_ms=0,
            cost=0.0,
            metadata={
                'streamlit': True,
                'interaction_type': interaction_type,
                'session_id': st.session_state.get('session_id', 'unknown'),
                **details
            }
        )
    
    def _get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for current Streamlit session"""
        # This would typically fetch from your monitoring backend
        # For now, return mock data
        return {
            'total_requests': 15,
            'avg_latency': 342,
            'total_cost': 0.0234,
            'error_rate': 2.1,
            'recent_errors': []
        }
    
    def _get_request_details(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific request"""
        # This would fetch from your monitoring backend
        return None
    
    def _get_dashboard_stats(self, time_range: str) -> Dict[str, Any]:
        """Get dashboard statistics for the specified time range"""
        # This would fetch from your monitoring backend
        return {
            'total_requests': 150,
            'avg_latency': 342,
            'total_cost': 0.234,
            'success_rate': 97.8,
            'time_series_data': {},
            'provider_breakdown': {},
            'cost_breakdown': {},
            'recent_requests': []
        }
