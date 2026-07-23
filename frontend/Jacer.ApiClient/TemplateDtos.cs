namespace Jacer.ApiClient;

/// <summary>
/// A routine template as returned by the backend. Maps to the FastAPI
/// <c>Template</c> model via snake_case serialisation (see <see cref="JacerJson"/>).
/// </summary>
public sealed record TemplateDto
{
    public required string Id { get; init; }
    public required string Name { get; init; }
    public Cadence Cadence { get; init; } = Cadence.Weekly;

    /// <summary>Anchor date (YYYY-MM-DD) for the "A" week of a fortnightly cadence; null for weekly.</summary>
    public string? WeekAStartDate { get; init; }

    public bool IsLocked { get; init; }
    public DateTimeOffset CreatedAt { get; init; }
    public DateTimeOffset UpdatedAt { get; init; }
}

/// <summary>
/// Payload for <c>POST /api/templates/</c>. Only <see cref="Name"/> is required.
/// For a fortnightly cadence the backend requires <see cref="WeekAStartDate"/>.
/// </summary>
public sealed record TemplateCreateDto
{
    public required string Name { get; init; }
    public Cadence? Cadence { get; init; }
    public string? WeekAStartDate { get; init; }
}

/// <summary>
/// Payload for <c>PATCH /api/templates/{id}</c>. Null fields are omitted so this
/// is a partial update.
/// </summary>
public sealed record TemplateUpdateDto
{
    public string? Name { get; init; }
    public Cadence? Cadence { get; init; }
    public string? WeekAStartDate { get; init; }
}

/// <summary>
/// A single template item — one recurring entry that materialises into a task.
/// Maps to the FastAPI <c>TemplateItem</c> model.
/// </summary>
public sealed record TemplateItemDto
{
    public required string Id { get; init; }
    public required string TemplateId { get; init; }

    /// <summary>Day of week, 0 = Monday … 6 = Sunday (Python's <c>date.weekday()</c>).</summary>
    public int DayOfWeek { get; init; }

    /// <summary>"A" or "B" for fortnightly templates; null for weekly. Case-sensitive per the backend.</summary>
    public string? WeekSlot { get; init; }

    public required string Title { get; init; }
    public string Description { get; init; } = "";
    public int DurationMinutes { get; init; } = 30;
    public string? DefaultTime { get; init; }
    public string? CategoryId { get; init; }
}

/// <summary>Payload for <c>POST /api/templates/{id}/items</c>.</summary>
public sealed record TemplateItemCreateDto
{
    public required int DayOfWeek { get; init; }
    public string? WeekSlot { get; init; }
    public required string Title { get; init; }
    public string? Description { get; init; }
    public int? DurationMinutes { get; init; }
    public string? DefaultTime { get; init; }
    public string? CategoryId { get; init; }
}

/// <summary>Payload for <c>PATCH /api/template-items/{id}</c> — partial update.</summary>
public sealed record TemplateItemUpdateDto
{
    public int? DayOfWeek { get; init; }
    public string? WeekSlot { get; init; }
    public string? Title { get; init; }
    public string? Description { get; init; }
    public int? DurationMinutes { get; init; }
    public string? DefaultTime { get; init; }
    public string? CategoryId { get; init; }
}

/// <summary>Response from the lock/unlock endpoints.</summary>
public sealed record LockResponseDto
{
    public required string TemplateId { get; init; }
    public bool IsLocked { get; init; }
}
