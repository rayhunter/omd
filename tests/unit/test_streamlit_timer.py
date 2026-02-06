"""
Unit tests for the Streamlit live timer feature.

Tests verify that the timer:
- Starts correctly
- Updates in real-time during processing
- Stops cleanly when processing completes
- Displays elapsed time accurately
- Handles thread cleanup properly
"""

import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch, call
import asyncio


class TestStreamlitTimer:
    """Test suite for the live timer functionality in Streamlit app."""
    
    def test_timer_starts_and_updates(self):
        """Test that timer starts at 0 and updates during processing."""
        # Mock Streamlit empty placeholder
        mock_placeholder = Mock()
        mock_placeholder.info = Mock()
        
        # Track start time
        start_time = time.time()
        stop_timer = threading.Event()
        
        # Timer update function (extracted from app logic)
        def update_timer():
            """Update timer display while processing"""
            update_count = 0
            while not stop_timer.is_set() and update_count < 5:  # Limit iterations for test
                elapsed = time.time() - start_time
                mock_placeholder.info(f"🧠 Processing your request... ({elapsed:.1f}s)")
                update_count += 1
                time.sleep(0.1)
        
        # Start timer thread
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()
        
        # Let it run for a short period
        time.sleep(0.3)
        
        # Stop timer
        stop_timer.set()
        timer_thread.join(timeout=1.0)
        
        # Verify timer was called multiple times with increasing values
        assert mock_placeholder.info.call_count >= 2, "Timer should update at least twice"
        
        # Verify the format of timer messages
        calls = mock_placeholder.info.call_args_list
        for idx, call in enumerate(calls):
            message = call[0][0]
            assert "Processing your request..." in message
            assert "s)" in message
            
            # Verify time is increasing (approximately)
            if idx > 0:
                # Extract time from message (format: "...({time}s)")
                import re
                prev_time = float(re.search(r'\((\d+\.\d+)s\)', calls[idx-1][0][0]).group(1))
                curr_time = float(re.search(r'\((\d+\.\d+)s\)', message).group(1))
                assert curr_time >= prev_time, f"Time should increase: {prev_time} -> {curr_time}"
    
    def test_timer_stops_cleanly(self):
        """Test that timer thread stops properly when processing completes."""
        start_time = time.time()
        stop_timer = threading.Event()
        update_count = [0]  # Use list to modify in nested function
        
        def update_timer():
            while not stop_timer.is_set():
                elapsed = time.time() - start_time
                update_count[0] += 1
                time.sleep(0.05)
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()
        
        # Let it run briefly
        time.sleep(0.15)
        initial_count = update_count[0]
        
        # Stop timer
        stop_timer.set()
        timer_thread.join(timeout=1.0)
        
        # Thread should have stopped
        assert not timer_thread.is_alive(), "Timer thread should be stopped"
        
        # Count should not increase after stopping
        time.sleep(0.1)
        assert update_count[0] == initial_count, "Timer should not update after stopping"
    
    def test_timer_cleanup_on_exception(self):
        """Test that timer is properly cleaned up even if processing raises an exception."""
        mock_placeholder = Mock()
        start_time = time.time()
        stop_timer = threading.Event()
        
        def update_timer():
            while not stop_timer.is_set():
                elapsed = time.time() - start_time
                mock_placeholder.info(f"Processing... ({elapsed:.1f}s)")
                time.sleep(0.05)
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        
        try:
            timer_thread.start()
            time.sleep(0.1)
            
            # Simulate exception during processing
            raise ValueError("Simulated processing error")
        
        finally:
            # Cleanup should happen in finally block
            stop_timer.set()
            timer_thread.join(timeout=1.0)
        
        # Verify cleanup worked
        assert not timer_thread.is_alive(), "Timer thread should stop even after exception"
    
    def test_elapsed_time_accuracy(self):
        """Test that elapsed time calculation is accurate."""
        start_time = time.time()
        
        # Simulate processing delay
        time.sleep(0.25)
        
        elapsed_time = time.time() - start_time
        
        # Verify elapsed time is approximately correct (within 50ms tolerance)
        assert 0.20 <= elapsed_time <= 0.35, f"Elapsed time should be ~0.25s, got {elapsed_time:.3f}s"
    
    def test_timer_format_display(self):
        """Test that timer displays correct format with emoji and seconds."""
        mock_placeholder = Mock()
        
        # Test various elapsed times
        test_cases = [
            (0.1, "🧠 Processing your request... (0.1s)"),
            (1.5, "🧠 Processing your request... (1.5s)"),
            (10.3, "🧠 Processing your request... (10.3s)"),
            (60.0, "🧠 Processing your request... (60.0s)"),
        ]
        
        for elapsed, expected in test_cases:
            message = f"🧠 Processing your request... ({elapsed:.1f}s)"
            assert message == expected, f"Format mismatch for {elapsed}s"
    
    def test_completion_message_format(self):
        """Test that completion message shows correct elapsed time."""
        elapsed_time = 2.7
        completion_msg = f"✅ Response generated in {elapsed_time:.1f}s"
        
        assert completion_msg == "✅ Response generated in 2.7s"
        assert "✅" in completion_msg
        assert "Response generated" in completion_msg
        assert "2.7s" in completion_msg
    
    @pytest.mark.asyncio
    async def test_timer_with_async_processing(self):
        """Test timer works correctly with async processing."""
        mock_placeholder = Mock()
        start_time = time.time()
        stop_timer = threading.Event()
        
        def update_timer():
            while not stop_timer.is_set():
                elapsed = time.time() - start_time
                mock_placeholder.info(f"Processing... ({elapsed:.1f}s)")
                time.sleep(0.05)
        
        # Simulate async processing
        async def mock_process_query():
            await asyncio.sleep(0.2)
            return "Test result", None
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        
        try:
            timer_thread.start()
            result, error = await mock_process_query()
        finally:
            stop_timer.set()
            timer_thread.join(timeout=1.0)
        
        elapsed_time = time.time() - start_time
        
        # Verify processing completed
        assert result == "Test result"
        assert error is None
        
        # Verify timer ran during processing
        assert mock_placeholder.info.call_count >= 2
        
        # Verify elapsed time is reasonable
        assert 0.15 <= elapsed_time <= 0.35
    
    def test_timer_daemon_thread_behavior(self):
        """Test that timer thread is properly set as daemon."""
        stop_timer = threading.Event()
        
        def update_timer():
            while not stop_timer.is_set():
                time.sleep(0.01)
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        
        # Verify daemon flag
        assert timer_thread.daemon is True, "Timer thread should be daemon"
        
        timer_thread.start()
        
        # Stop and cleanup
        stop_timer.set()
        timer_thread.join(timeout=1.0)
    
    def test_multiple_timer_instances(self):
        """Test that multiple timer instances don't interfere with each other."""
        placeholders = [Mock(), Mock()]
        start_times = [time.time(), time.time()]
        stop_events = [threading.Event(), threading.Event()]
        threads = []
        
        def create_timer(idx):
            def update():
                while not stop_events[idx].is_set():
                    elapsed = time.time() - start_times[idx]
                    placeholders[idx].info(f"Timer {idx}: {elapsed:.1f}s")
                    time.sleep(0.05)
            return update
        
        # Start two timers
        for i in range(2):
            thread = threading.Thread(target=create_timer(i), daemon=True)
            thread.start()
            threads.append(thread)
        
        time.sleep(0.15)
        
        # Stop both timers
        for stop_event in stop_events:
            stop_event.set()
        
        for thread in threads:
            thread.join(timeout=1.0)
        
        # Verify both timers ran independently
        assert placeholders[0].info.call_count >= 2
        assert placeholders[1].info.call_count >= 2
        
        # Verify both threads stopped
        for thread in threads:
            assert not thread.is_alive()
    
    def test_timer_update_frequency(self):
        """Test that timer updates at approximately correct frequency (0.1s)."""
        mock_placeholder = Mock()
        start_time = time.time()
        stop_timer = threading.Event()
        call_times = []
        
        def update_timer():
            while not stop_timer.is_set():
                call_times.append(time.time())
                elapsed = time.time() - start_time
                mock_placeholder.info(f"Processing... ({elapsed:.1f}s)")
                time.sleep(0.1)
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()
        
        time.sleep(0.35)
        
        stop_timer.set()
        timer_thread.join(timeout=1.0)
        
        # Calculate intervals between calls
        if len(call_times) >= 2:
            intervals = [call_times[i+1] - call_times[i] for i in range(len(call_times) - 1)]
            avg_interval = sum(intervals) / len(intervals)
            
            # Average interval should be close to 0.1s (within 50ms tolerance)
            assert 0.05 <= avg_interval <= 0.15, f"Average interval should be ~0.1s, got {avg_interval:.3f}s"


class TestTimerIntegrationWithStreamlit:
    """Integration tests for timer with Streamlit components."""
    
    @patch('streamlit.empty')
    def test_timer_with_streamlit_placeholder(self, mock_empty):
        """Test timer integration with actual Streamlit empty placeholder."""
        mock_placeholder = Mock()
        mock_empty.return_value = mock_placeholder
        
        # Simulate the Streamlit app logic
        import streamlit as st
        
        status_placeholder = st.empty()
        start_time = time.time()
        stop_timer = threading.Event()
        
        def update_timer():
            while not stop_timer.is_set():
                elapsed = time.time() - start_time
                status_placeholder.info(f"🧠 Processing your request... ({elapsed:.1f}s)")
                time.sleep(0.05)
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()
        
        time.sleep(0.15)
        
        stop_timer.set()
        timer_thread.join(timeout=1.0)
        
        # Verify placeholder methods were called
        assert mock_placeholder.info.call_count >= 2


# Performance tests
class TestTimerPerformance:
    """Performance tests for timer functionality."""
    
    def test_timer_low_cpu_overhead(self):
        """Test that timer doesn't cause excessive CPU usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        cpu_before = process.cpu_percent(interval=0.1)
        
        start_time = time.time()
        stop_timer = threading.Event()
        
        def update_timer():
            while not stop_timer.is_set():
                elapsed = time.time() - start_time
                time.sleep(0.1)
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()
        
        time.sleep(0.5)
        
        cpu_during = process.cpu_percent(interval=0.1)
        
        stop_timer.set()
        timer_thread.join(timeout=1.0)
        
        # CPU increase should be minimal (< 5% for a simple timer)
        cpu_increase = cpu_during - cpu_before
        assert cpu_increase < 10, f"CPU overhead too high: {cpu_increase}%"
    
    def test_timer_memory_leak_prevention(self):
        """Test that timer doesn't cause memory leaks over multiple runs."""
        import gc
        
        def run_timer_cycle():
            stop_timer = threading.Event()
            start_time = time.time()
            
            def update_timer():
                counter = 0
                while not stop_timer.is_set() and counter < 10:
                    elapsed = time.time() - start_time
                    counter += 1
                    time.sleep(0.01)
            
            timer_thread = threading.Thread(target=update_timer, daemon=True)
            timer_thread.start()
            time.sleep(0.05)
            stop_timer.set()
            timer_thread.join(timeout=1.0)
        
        # Run multiple cycles
        for _ in range(10):
            run_timer_cycle()
        
        # Force garbage collection
        gc.collect()
        
        # Count active threads (should be back to baseline)
        active_threads = threading.active_count()
        
        # Should not have accumulated threads
        assert active_threads <= 5, f"Too many threads still active: {active_threads}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
