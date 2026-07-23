namespace Jacer.ApiClient;

/// <summary>
/// A task as returned by the backend. Field names map to the FastAPI <c>Task</c>
/// model via snake_case serialisation (see <see cref="JacerJson"/>).
/// </summary>
public sealed record TaskDto
{
    public required string Id { get; init; }
    public required string Title { get; init; }
    public string Description { get; init; } = "";
    public int DurationMinutes { get; init; } = 30;
    public TaskStatus Status { get; init; } = TaskStatus.Backlog;
    public string? CategoryId { get; init; }
    public string? ScheduledTime { get; init; }
    public string? ScheduledDate { get; init; }
    public bool IsCompleted { get; init; }
    public string? TemplateOriginId { get; init; }
    public string? InstanceDate { get; init; }
    public bool Diverged { get; init; }
    public DateTimeOffset CreatedAt { get; init; }
    public DateTimeOffset UpdatedAt { get; init; }
}

/// <summary>
/// Payload for <c>POST /api/tasks/</c>. Only <see cref="Title"/> is required;
/// unset fields are omitted so the backend applies its own defaults
/// (status=backlog, duration_minutes=30). The optional placement/category
/// fields let a deleted task be recreated faithfully for undo (all already part
/// of the frozen backend <c>TaskCreate</c> contract).
/// </summary>
public sealed record TaskCreateDto
{
    public required string Title { get; init; }
    public string? Description { get; init; }
    public TaskStatus? Status { get; init; }
    public int? DurationMinutes { get; init; }
    public string? CategoryId { get; init; }
    public string? ScheduledTime { get; init; }
    public string? ScheduledDate { get; init; }
}

/// <summary>
/// Payload for <c>PATCH /api/tasks/{id}</c>. All fields are nullable and
/// null fields are omitted from the request, so this performs a partial update.
/// </summary>
public sealed record TaskUpdateDto
{
    public string? Title { get; init; }
    public string? Description { get; init; }
    public int? DurationMinutes { get; init; }
    public TaskStatus? Status { get; init; }
    public string? ScheduledTime { get; init; }
    public string? ScheduledDate { get; init; }
    public bool? IsCompleted { get; init; }
}
