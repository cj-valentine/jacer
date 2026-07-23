namespace Jacer.ApiClient;

/// <summary>
/// Mirrors the backend <c>TaskStatus</c> literal: backlog | today | scheduled | done.
/// Serialised as snake_case lower (single words → lowercase) to match the FastAPI
/// contract. The enum-to-string conversion is configured globally in
/// <see cref="JacerJson.Options"/>, so no per-member attribute is needed.
/// </summary>
public enum TaskStatus
{
    Backlog,
    Today,
    Scheduled,
    Done,
}
