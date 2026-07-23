namespace Jacer.ApiClient;

/// <summary>
/// Typed client for the frozen Jacer day endpoints under <c>/api/days</c>:
/// reading a day's tasks and driving materialisation (single day or a horizon).
/// Materialisation is idempotent server-side.
/// </summary>
public interface IDaysApi
{
    /// <summary>Tasks scheduled on (or instanced to) <paramref name="date"/> (YYYY-MM-DD).</summary>
    Task<IReadOnlyList<TaskDto>> GetDayTasksAsync(string date, CancellationToken ct = default);

    /// <summary>Materialise locked templates for a single day.</summary>
    Task<MaterialiseResponseDto> MaterialiseDayAsync(string date, CancellationToken ct = default);

    /// <summary>Materialise the next <paramref name="days"/> days from today (or <paramref name="start"/>).</summary>
    Task<HorizonMaterialiseResponseDto> MaterialiseHorizonAsync(
        int days = 14,
        string? start = null,
        CancellationToken ct = default);
}
