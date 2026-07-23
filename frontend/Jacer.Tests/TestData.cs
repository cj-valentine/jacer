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
}
