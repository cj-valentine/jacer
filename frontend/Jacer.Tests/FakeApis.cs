namespace Jacer.Tests;

/// <summary>In-memory <see cref="ITasksApi"/> double that applies updates, so the
/// board's behaviour (reschedule, complete, category, delete) can be asserted.</summary>
internal sealed class FakeTasksApi(IEnumerable<TaskDto> tasks) : ITasksApi
{
    public List<TaskDto> Tasks { get; } = tasks.ToList();
    public List<string> Deleted { get; } = [];
    public List<TaskCreateDto> Created { get; } = [];

    public Task<IReadOnlyList<TaskDto>> ListTasksAsync(TaskStatus? status = null, string? date = null, CancellationToken ct = default) =>
        Task.FromResult<IReadOnlyList<TaskDto>>(Tasks.ToList());

    public Task<TaskDto> CreateTaskAsync(TaskCreateDto payload, CancellationToken ct = default)
    {
        Created.Add(payload);
        var t = new TaskDto
        {
            Id = Guid.NewGuid().ToString(),
            Title = payload.Title,
            Description = payload.Description ?? "",
            Status = payload.Status ?? TaskStatus.Backlog,
            DurationMinutes = payload.DurationMinutes ?? 30,
            CategoryId = payload.CategoryId,
            ScheduledTime = payload.ScheduledTime,
            ScheduledDate = payload.ScheduledDate,
            CreatedAt = DateTimeOffset.UnixEpoch,
            UpdatedAt = DateTimeOffset.UnixEpoch,
        };
        Tasks.Add(t);
        return Task.FromResult(t);
    }

    public Task<TaskDto?> GetTaskAsync(string id, CancellationToken ct = default) =>
        Task.FromResult(Tasks.FirstOrDefault(t => t.Id == id));

    public Task<TaskDto> UpdateTaskAsync(string id, TaskUpdateDto p, CancellationToken ct = default)
    {
        var i = Tasks.FindIndex(t => t.Id == id);
        var t = Tasks[i] with
        {
            Title = p.Title ?? Tasks[i].Title,
            Description = p.Description ?? Tasks[i].Description,
            DurationMinutes = p.DurationMinutes ?? Tasks[i].DurationMinutes,
            Status = p.Status ?? Tasks[i].Status,
            ScheduledTime = p.ScheduledTime ?? Tasks[i].ScheduledTime,
            ScheduledDate = p.ScheduledDate ?? Tasks[i].ScheduledDate,
        };
        Tasks[i] = t;
        return Task.FromResult(t);
    }

    public Task<TaskDto> SetCategoryAsync(string id, string? categoryId, CancellationToken ct = default)
    {
        var i = Tasks.FindIndex(t => t.Id == id);
        Tasks[i] = Tasks[i] with { CategoryId = categoryId };
        return Task.FromResult(Tasks[i]);
    }

    public Task<TaskDto> SetScheduledDateAsync(string id, string? date, CancellationToken ct = default)
    {
        var i = Tasks.FindIndex(t => t.Id == id);
        Tasks[i] = Tasks[i] with { ScheduledDate = date };
        return Task.FromResult(Tasks[i]);
    }

    public Task<TaskDto?> ResetToTemplateAsync(string id, CancellationToken ct = default) =>
        Task.FromResult(Tasks.FirstOrDefault(t => t.Id == id));

    public Task DeleteTaskAsync(string id, CancellationToken ct = default)
    {
        Tasks.RemoveAll(t => t.Id == id);
        Deleted.Add(id);
        return Task.CompletedTask;
    }
}

internal sealed class FakeDaysApi : IDaysApi
{
    public Task<IReadOnlyList<TaskDto>> GetDayTasksAsync(string date, CancellationToken ct = default) =>
        Task.FromResult<IReadOnlyList<TaskDto>>([]);

    public Task<MaterialiseResponseDto> MaterialiseDayAsync(string date, CancellationToken ct = default) =>
        Task.FromResult(new MaterialiseResponseDto { Date = date });

    public Task<HorizonMaterialiseResponseDto> MaterialiseHorizonAsync(int days = 14, string? start = null, CancellationToken ct = default) =>
        Task.FromResult(new HorizonMaterialiseResponseDto { StartDate = start ?? "2026-01-01", Days = days });
}

internal sealed class FakeCategoriesApi(IEnumerable<CategoryDto> categories) : ICategoriesApi
{
    public List<CategoryDto> Categories { get; } = categories.ToList();
    public List<CategoryCreateDto> Created { get; } = [];

    public Task<IReadOnlyList<CategoryDto>> ListCategoriesAsync(CancellationToken ct = default) =>
        Task.FromResult<IReadOnlyList<CategoryDto>>(Categories.ToList());

    public Task<IReadOnlyList<string>> GetPaletteAsync(CancellationToken ct = default) =>
        Task.FromResult<IReadOnlyList<string>>(["#5B7B9A", "#6E8B6E", "#B07156"]);

    public Task<CategoryDto> CreateCategoryAsync(CategoryCreateDto payload, CancellationToken ct = default)
    {
        Created.Add(payload);
        var c = new CategoryDto { Id = Guid.NewGuid().ToString(), Name = payload.Name, Colour = payload.Colour ?? "#5B7B9A" };
        Categories.Add(c);
        return Task.FromResult(c);
    }

    public Task<CategoryDto> UpdateCategoryAsync(string id, CategoryUpdateDto payload, CancellationToken ct = default) =>
        Task.FromResult(Categories.First(c => c.Id == id));

    public Task DeleteCategoryAsync(string id, CancellationToken ct = default)
    {
        Categories.RemoveAll(c => c.Id == id);
        return Task.CompletedTask;
    }
}
