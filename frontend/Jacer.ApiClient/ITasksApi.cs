namespace Jacer.ApiClient;

/// <summary>
/// Typed client for the frozen Jacer FastAPI task endpoints
/// (<c>/api/tasks/</c>). Collection routes keep their trailing slash to avoid
/// FastAPI's 307 redirect, which would otherwise drop POST/PATCH bodies.
/// </summary>
public interface ITasksApi
{
    Task<IReadOnlyList<TaskDto>> ListTasksAsync(
        TaskStatus? status = null,
        string? date = null,
        CancellationToken ct = default);

    Task<TaskDto> CreateTaskAsync(TaskCreateDto payload, CancellationToken ct = default);

    Task<TaskDto?> GetTaskAsync(string id, CancellationToken ct = default);

    Task<TaskDto> UpdateTaskAsync(string id, TaskUpdateDto payload, CancellationToken ct = default);

    /// <summary>
    /// Set (or clear, with null) a task's category. A dedicated call because
    /// clearing needs an explicit <c>category_id: null</c>, which the null-omitting
    /// partial-update DTO can't express.
    /// </summary>
    Task<TaskDto> SetCategoryAsync(string id, string? categoryId, CancellationToken ct = default);

    /// <summary>
    /// Set (or clear, with null) a task's <c>scheduled_date</c>. Clearing sends an
    /// explicit null (unschedule → back to the global backlog); a date schedules it
    /// there without touching status (day-centric placement, ADR-007).
    /// </summary>
    Task<TaskDto> SetScheduledDateAsync(string id, string? date, CancellationToken ct = default);

    /// <summary>
    /// Restore a template-origin task's definition from its originating template
    /// item and clear <c>diverged</c> (see ADR-006). Returns null if the task or
    /// its item is gone (404), or throws for other failures.
    /// </summary>
    Task<TaskDto?> ResetToTemplateAsync(string id, CancellationToken ct = default);

    Task DeleteTaskAsync(string id, CancellationToken ct = default);
}
