using System.Net;
using System.Net.Http.Json;

namespace Jacer.ApiClient;

/// <inheritdoc cref="ITasksApi"/>
public sealed class TasksApiClient(HttpClient http) : ITasksApi
{
    // Collection route keeps its trailing slash on purpose — see ITasksApi.
    private const string Collection = "api/tasks/";

    public async Task<IReadOnlyList<TaskDto>> ListTasksAsync(
        TaskStatus? status = null,
        string? date = null,
        CancellationToken ct = default)
    {
        var query = new List<string>();
        if (status is not null)
        {
            query.Add($"status={status.ToString()!.ToLowerInvariant()}");
        }
        if (date is not null)
        {
            query.Add($"date={Uri.EscapeDataString(date)}");
        }

        var url = query.Count > 0 ? $"{Collection}?{string.Join("&", query)}" : Collection;
        var result = await http.GetFromJsonAsync<List<TaskDto>>(url, JacerJson.Options, ct);
        return result ?? [];
    }

    public async Task<TaskDto> CreateTaskAsync(TaskCreateDto payload, CancellationToken ct = default)
    {
        var response = await http.PostAsJsonAsync(Collection, payload, JacerJson.Options, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<TaskDto>(JacerJson.Options, ct))!;
    }

    public async Task<TaskDto?> GetTaskAsync(string id, CancellationToken ct = default)
    {
        var response = await http.GetAsync($"api/tasks/{id}", ct);
        if (response.StatusCode == HttpStatusCode.NotFound)
        {
            return null;
        }
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<TaskDto>(JacerJson.Options, ct);
    }

    public async Task<TaskDto> UpdateTaskAsync(string id, TaskUpdateDto payload, CancellationToken ct = default)
    {
        var response = await http.PatchAsJsonAsync($"api/tasks/{id}", payload, JacerJson.Options, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<TaskDto>(JacerJson.Options, ct))!;
    }

    public async Task DeleteTaskAsync(string id, CancellationToken ct = default)
    {
        var response = await http.DeleteAsync($"api/tasks/{id}", ct);
        response.EnsureSuccessStatusCode();
    }
}
