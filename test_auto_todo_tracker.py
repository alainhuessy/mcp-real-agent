"""
Tests für Auto Todo Tracker
"""

import pytest
from tasks.auto_todo_tracker import AutoTodoTracker, TodoStatus, TodoItem


@pytest.fixture
def tracker():
    """Create a tracker instance"""
    return AutoTodoTracker("Test Task")


class TestTodoItem:
    """TodoItem Tests"""
    
    def test_todo_item_creation(self):
        """Todo item can be created"""
        todo = TodoItem(1, "Test todo", "This is a test")
        assert todo.id == 1
        assert todo.title == "Test todo"
        assert todo.status == TodoStatus.NOT_STARTED
    
    def test_todo_item_to_dict(self):
        """Todo item can be serialized"""
        todo = TodoItem(1, "Test", "Desc")
        data = todo.to_dict()
        assert data["id"] == 1
        assert data["title"] == "Test"
        assert data["status"] == "not-started"
    
    def test_todo_item_duration(self):
        """Todo item duration calculation"""
        todo = TodoItem(1, "Test", "")
        # No duration if not started/completed
        assert todo.get_duration() is None


class TestAutoTodoTracker:
    """AutoTodoTracker Tests"""
    
    def test_tracker_creation(self, tracker):
        """Tracker can be created"""
        assert tracker.task_name == "Test Task"
        assert len(tracker.todos) == 0
    
    def test_add_single_todo(self, tracker):
        """Can add single todo"""
        todo = tracker.add_todo("First todo", "Description")
        assert len(tracker.todos) == 1
        assert todo.id == 1
        assert todo.title == "First todo"
    
    def test_add_todos_from_plan(self, tracker):
        """Can add multiple todos from plan"""
        plan = ["Task 1", "Task 2", "Task 3"]
        todos = tracker.add_todos_from_plan(plan)
        assert len(tracker.todos) == 3
        assert todos[0].title == "Task 1"
    
    def test_mark_inprogress(self, tracker):
        """Can mark todo as in-progress"""
        todo = tracker.add_todo("Test")
        tracker.mark_inprogress(1)
        updated = tracker._get_todo(1)
        assert updated.status == TodoStatus.IN_PROGRESS
        assert updated.started_at is not None
    
    def test_mark_completed(self, tracker):
        """Can mark todo as completed"""
        todo = tracker.add_todo("Test")
        tracker.mark_inprogress(1)
        tracker.mark_completed(1, "Finished")
        updated = tracker._get_todo(1)
        assert updated.status == TodoStatus.COMPLETED
        assert updated.completed_at is not None
    
    def test_mark_failed(self, tracker):
        """Can mark todo as failed"""
        todo = tracker.add_todo("Test")
        tracker.mark_inprogress(1)
        tracker.mark_failed(1, "Something went wrong")
        updated = tracker._get_todo(1)
        assert updated.status == TodoStatus.FAILED
        assert updated.error_message == "Something went wrong"
    
    def test_mark_blocked(self, tracker):
        """Can mark todo as blocked"""
        todo = tracker.add_todo("Test")
        tracker.mark_blocked(1, "Waiting for dependency")
        updated = tracker._get_todo(1)
        assert updated.status == TodoStatus.BLOCKED
        assert updated.error_message == "Waiting for dependency"
    
    def test_get_summary_empty(self, tracker):
        """Get summary for empty tracker"""
        summary = tracker.get_summary()
        assert summary["total_todos"] == 0
        assert summary["completion_percentage"] == 0
    
    def test_get_summary_with_todos(self, tracker):
        """Get summary with todos"""
        tracker.add_todos_from_plan(["Task 1", "Task 2", "Task 3"])
        tracker.mark_inprogress(1)
        tracker.mark_completed(1, "Done")
        tracker.mark_failed(2, "Error")
        
        summary = tracker.get_summary()
        assert summary["total_todos"] == 3
        assert summary["completed"] == 1
        assert summary["failed"] == 1
        assert summary["completion_percentage"] == 33
    
    def test_print_todos(self, tracker, capsys):
        """Can print todos"""
        tracker.add_todos_from_plan(["Task 1", "Task 2"])
        tracker.print_todos()
        captured = capsys.readouterr()
        # Should contain table output
        assert "Todos" in captured.out or "Task 1" in captured.out
    
    def test_print_summary(self, tracker, capsys):
        """Can print summary"""
        tracker.add_todos_from_plan(["Task 1"])
        tracker.print_summary()
        captured = capsys.readouterr()
        # Should contain summary output
        assert "Summary" in captured.out or "Complete" in captured.out or "1" in captured.out


class TestAutoTodoTrackerWorkflow:
    """Integration workflow tests"""
    
    def test_complete_workflow(self, tracker):
        """Complete workflow from start to finish"""
        # Setup
        tracker.add_todos_from_plan(["Step 1", "Step 2", "Step 3"])
        assert len(tracker.todos) == 3
        
        # Execute
        tracker.mark_inprogress(1)
        assert tracker._get_todo(1).status == TodoStatus.IN_PROGRESS
        tracker.mark_completed(1)
        assert tracker._get_todo(1).status == TodoStatus.COMPLETED
        
        tracker.mark_inprogress(2)
        tracker.mark_completed(2)
        
        tracker.mark_inprogress(3)
        tracker.mark_completed(3)
        
        # Verify
        summary = tracker.get_summary()
        assert summary["completed"] == 3
        assert summary["completion_percentage"] == 100
        assert summary["status"] == "COMPLETE"
    
    def test_partial_failure_workflow(self, tracker):
        """Workflow with failures"""
        tracker.add_todos_from_plan(["Step 1", "Step 2", "Step 3"])
        
        tracker.mark_inprogress(1)
        tracker.mark_completed(1)
        
        tracker.mark_inprogress(2)
        tracker.mark_failed(2, "Network error")
        
        summary = tracker.get_summary()
        assert summary["completed"] == 1
        assert summary["failed"] == 1
        assert summary["status"] == "FAILED"
    
    def test_blocked_workflow(self, tracker):
        """Workflow with blocked tasks"""
        tracker.add_todos_from_plan(["Step 1", "Step 2", "Step 3"])
        
        tracker.mark_inprogress(1)
        tracker.mark_completed(1)
        
        tracker.mark_blocked(2, "Waiting for approval")
        
        tracker.mark_inprogress(3)
        tracker.mark_completed(3)
        
        summary = tracker.get_summary()
        assert summary["blocked"] == 1
        assert summary["completed"] == 2
        assert summary["in_progress"] == 0


class TestAutoTodoTrackerErrors:
    """Error handling tests"""
    
    def test_invalid_todo_id(self, tracker):
        """Should raise error for invalid todo ID"""
        tracker.add_todo("Test")
        with pytest.raises(ValueError):
            tracker.mark_inprogress(999)
    
    def test_get_nonexistent_todo(self, tracker):
        """Should return None for nonexistent todo"""
        result = tracker._get_todo(999)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
