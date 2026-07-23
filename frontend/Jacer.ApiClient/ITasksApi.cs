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

    Task DeleteTaskAsync(string id, CancellationToken ct = default);
}
