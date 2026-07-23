namespace Jacer.ApiClient;

/// <summary>Response from <c>POST /api/days/{date}/materialise</c>.</summary>
public sealed record MaterialiseResponseDto
{
    public required string Date { get; init; }
    public int CreatedCount { get; init; }
    public IReadOnlyList<string> CreatedTaskIds { get; init; } = [];
}

/// <summary>Response from <c>POST /api/days/horizon/materialise</c>.</summary>
public sealed record HorizonMaterialiseResponseDto
{
    public required string StartDate { get; init; }
    public int Days { get; init; }
    public int CreatedCount { get; init; }
    public IReadOnlyList<string> CreatedTaskIds { get; init; } = [];
}
