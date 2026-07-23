using System.Net.Http.Json;

namespace Jacer.ApiClient;

/// <inheritdoc cref="IDaysApi"/>
public sealed class DaysApiClient(HttpClient http) : IDaysApi
{
    public async Task<IReadOnlyList<TaskDto>> GetDayTasksAsync(string date, CancellationToken ct = default)
    {
        var result = await http.GetFromJsonAsync<List<TaskDto>>(
            $"api/days/{Uri.EscapeDataString(date)}", JacerJson.Options, ct);
        return result ?? [];
    }

    public async Task<MaterialiseResponseDto> MaterialiseDayAsync(string date, CancellationToken ct = default)
    {
        var response = await http.PostAsync(
            $"api/days/{Uri.EscapeDataString(date)}/materialise", null, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<MaterialiseResponseDto>(JacerJson.Options, ct))!;
    }

    public async Task<HorizonMaterialiseResponseDto> MaterialiseHorizonAsync(
        int days = 14,
        string? start = null,
        CancellationToken ct = default)
    {
        var query = new List<string> { $"days={days}" };
        if (start is not null)
        {
            query.Add($"start={Uri.EscapeDataString(start)}");
        }
        var url = $"api/days/horizon/materialise?{string.Join("&", query)}";

        var response = await http.PostAsync(url, null, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<HorizonMaterialiseResponseDto>(JacerJson.Options, ct))!;
    }
}
