namespace Jacer.Tests;

internal static class TestData
{
    public static TaskDto Task(string title, TaskStatus status, int durationMinutes = 30) => new()
    {
        Id = Guid.NewGuid().ToString(),
        Title = title,
        Status = status,
        DurationMinutes = durationMinutes,
        CreatedAt = DateTimeOffset.UnixEpoch,
        UpdatedAt = DateTimeOffset.UnixEpoch,
    };

    public static TaskDto DivergedTask(string title, string templateOriginId = "item-1") => new()
    {
        Id = Guid.NewGuid().ToString(),
        Title = title,
        Status = TaskStatus.Today,
        DurationMinutes = 30,
        TemplateOriginId = templateOriginId,
        Diverged = true,
        CreatedAt = DateTimeOffset.UnixEpoch,
        UpdatedAt = DateTimeOffset.UnixEpoch,
    };

    public static TemplateDto Template(string id, string name, bool locked = false) => new()
    {
        Id = id,
        Name = name,
        Cadence = Cadence.Weekly,
        IsLocked = locked,
        CreatedAt = DateTimeOffset.UnixEpoch,
        UpdatedAt = DateTimeOffset.UnixEpoch,
    };

    public static TemplateItemDto Item(string id, string templateId, int dayOfWeek, string title, string? time) => new()
    {
        Id = id,
        TemplateId = templateId,
        DayOfWeek = dayOfWeek,
        Title = title,
        DurationMinutes = 30,
        DefaultTime = time,
    };
}
