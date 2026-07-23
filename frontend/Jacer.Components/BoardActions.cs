namespace Jacer.Components;

/// <summary>
/// Reschedule a task to a date (or unschedule it back to the global backlog when
/// <see cref="Date"/> is null). Sets <c>scheduled_date</c>; the day-centric board
/// keys placement off that, never off status (ADR-007).
/// </summary>
public readonly record struct TaskReschedule(string TaskId, string? Date);

/// <summary>Assign a task to a category, or clear it (<see cref="CategoryId"/> null).</summary>
public readonly record struct CategoryAssignment(string TaskId, string? CategoryId);

/// <summary>An in-place edit of a task's title.</summary>
public readonly record struct TaskTitleEdit(string TaskId, string Title);
