using System.Text.Json;
using System.Text.Json.Serialization;

namespace Jacer.ApiClient;

/// <summary>
/// Shared serialisation settings for talking to the Jacer FastAPI backend.
/// The backend uses snake_case field names and lowercase string enums, so we
/// map property names with <see cref="JsonNamingPolicy.SnakeCaseLower"/> and
/// register a matching enum converter. <see cref="JsonIgnoreCondition.WhenWritingNull"/>
/// lets the partial-update DTOs (PATCH) send only the fields that were set.
/// </summary>
public static class JacerJson
{
    public static readonly JsonSerializerOptions Options = new(JsonSerializerDefaults.Web)
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        Converters = { new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower) },
    };

    /// <summary>
    /// Like <see cref="Options"/> but writes nulls. Needed for the rare PATCH that
    /// must send an explicit <c>null</c> to clear a field (e.g. un-assigning a
    /// category) rather than omitting it — omission means "leave unchanged".
    /// </summary>
    public static readonly JsonSerializerOptions WriteNulls = new(JsonSerializerDefaults.Web)
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        DefaultIgnoreCondition = JsonIgnoreCondition.Never,
        Converters = { new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower) },
    };
}
